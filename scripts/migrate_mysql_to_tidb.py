# -*- coding: utf-8 -*-
"""
Pure-Python streaming migrator from local MySQL to TiDB Cloud Starter (TLS port 4000).
- Preserves exact live schema via SHOW CREATE TABLE (rewriting MySQL 8 collation for TiDB compatibility)
- Streams all 8 tables in batches with keyset pagination and FOREIGN_KEY_CHECKS=0
- Resets AUTO_INCREMENT counters and verifies exact row counts per table

Usage:
  python scripts/migrate_mysql_to_tidb.py --dry-run
  python scripts/migrate_mysql_to_tidb.py \
      --src-host 127.0.0.1 --src-port 3306 --src-user root --src-password admin123 \
      --dst-host gateway01.us-east-1.prod.aws.tidbcloud.com --dst-port 4000 \
      --dst-user <USER> --dst-password <PASS> --dst-db supplier_crawler --truncate
"""
import argparse
import os
import re
import sys
import time

import certifi
import mysql.connector

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TABLES_ORDER = [
    "suppliers",
    "products",
    "product_categories",
    "price_history",
    "crawl_logs",
    "favorites",
    "cart_items",
    "system_settings",
]

PK_COL = {
    "suppliers": "id",
    "products": "id",
    "product_categories": "id",
    "price_history": "id",
    "crawl_logs": "id",
    "favorites": "id",
    "cart_items": "id",
    "system_settings": None,
}


def sanitize_ddl_for_tidb(ddl: str, database: str = "") -> str:
    """Adapt MySQL 8 SHOW CREATE TABLE output for TiDB Cloud Serverless."""
    out = ddl
    out = re.sub(r"^CREATE TABLE\s+", "CREATE TABLE IF NOT EXISTS ", out, flags=re.IGNORECASE)
    out = out.replace("COLLATE=utf8mb4_0900_ai_ci", "COLLATE=utf8mb4_unicode_ci")
    out = out.replace("COLLATE utf8mb4_0900_ai_ci", "COLLATE utf8mb4_unicode_ci")
    out = re.sub(r"\s+AUTO_INCREMENT=\d+", "", out)
    # Remove any explicit schema prefix on REFERENCES if present
    if database:
        out = out.replace(f"`{database}`.", "")
    return out


def connect_mysql(host, port, user, password, database, use_ssl=False, ssl_ca=None):
    kwargs = dict(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        use_unicode=True,
        use_pure=True,
        connection_timeout=20,
        autocommit=False,
    )
    if use_ssl or ("tidbcloud" in (host or "").lower()):
        kwargs["ssl_ca"] = ssl_ca or certifi.where()
        kwargs["ssl_verify_cert"] = True
    return mysql.connector.connect(**kwargs)


def create_database_if_missing(host, port, user, password, database, use_ssl=False, ssl_ca=None):
    kwargs = dict(
        host=host,
        port=int(port),
        user=user,
        password=password,
        charset="utf8mb4",
        use_unicode=True,
        use_pure=True,
        connection_timeout=20,
        autocommit=True,
    )
    if use_ssl or ("tidbcloud" in (host or "").lower()):
        kwargs["ssl_ca"] = ssl_ca or certifi.where()
        kwargs["ssl_verify_cert"] = True
    conn = mysql.connector.connect(**kwargs)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cur.close()
    conn.close()


def migrate(args):
    t0 = time.time()
    src_conn = connect_mysql(
        args.src_host, args.src_port, args.src_user, args.src_password, args.src_db, use_ssl=False
    )
    src_cur = src_conn.cursor()

    print(f"[Source] {args.src_host}:{args.src_port}/{args.src_db}")
    ddls = {}
    src_counts = {}
    for tbl in TABLES_ORDER:
        src_cur.execute(f"SHOW CREATE TABLE `{tbl}`")
        raw_ddl = src_cur.fetchone()[1]
        ddls[tbl] = sanitize_ddl_for_tidb(raw_ddl, args.src_db)
        src_cur.execute(f"SELECT COUNT(*) FROM `{tbl}`")
        src_counts[tbl] = int(src_cur.fetchone()[0])
        print(f"  - {tbl:<20}: {src_counts[tbl]:>8} rows")

    if args.dry_run:
        print("\n[Dry Run] Target TiDB connection skipped. Sanitized DDLs preview:")
        for tbl in TABLES_ORDER:
            first_line = ddls[tbl].splitlines()[0]
            print(f"  {tbl}: {first_line} ... ({len(ddls[tbl])} chars)")
        src_cur.close()
        src_conn.close()
        return True

    if not args.dst_host or not args.dst_user:
        raise ValueError("Missing --dst-host or --dst-user (set DB_HOST / DB_USER env or CLI flags).")

    create_database_if_missing(
        args.dst_host, args.dst_port, args.dst_user, args.dst_password, args.dst_db,
        use_ssl=args.dst_ssl, ssl_ca=args.dst_ssl_ca,
    )
    dst_conn = connect_mysql(
        args.dst_host, args.dst_port, args.dst_user, args.dst_password, args.dst_db,
        use_ssl=True if "tidbcloud" in args.dst_host.lower() else args.dst_ssl,
        ssl_ca=args.dst_ssl_ca,
    )
    dst_cur = dst_conn.cursor()
    dst_cur.execute("SET FOREIGN_KEY_CHECKS = 0")

    try:
        for tbl in TABLES_ORDER:
            dst_cur.execute(ddls[tbl])
        dst_conn.commit()

        if args.truncate:
            print("\n[Target] Truncating destination tables in reverse FK order...")
            for tbl in reversed(TABLES_ORDER):
                dst_cur.execute(f"TRUNCATE TABLE `{tbl}`")
            dst_conn.commit()

        for tbl in TABLES_ORDER:
            total_rows = src_counts[tbl]
            print(f"\n[Copy] {tbl} ({total_rows} rows)...", flush=True)
            if total_rows == 0:
                continue

            src_cur.execute(f"SHOW COLUMNS FROM `{tbl}`")
            cols = [r[0] for r in src_cur.fetchall()]
            col_list = ", ".join(f"`{c}`" for c in cols)
            placeholders = ", ".join(["%s"] * len(cols))
            insert_verb = "INSERT IGNORE" if not args.truncate else "INSERT"
            insert_sql = f"{insert_verb} INTO `{tbl}` ({col_list}) VALUES ({placeholders})"

            pk = PK_COL[tbl]
            copied = 0
            if pk:
                last_pk = -1
                while True:
                    src_cur.execute(
                        f"SELECT {col_list} FROM `{tbl}` WHERE `{pk}` > %s ORDER BY `{pk}` ASC LIMIT %s",
                        (last_pk, args.batch_size),
                    )
                    rows = src_cur.fetchall()
                    if not rows:
                        break
                    pk_idx = cols.index(pk)
                    last_pk = rows[-1][pk_idx]
                    dst_cur.executemany(insert_sql, rows)
                    dst_conn.commit()
                    copied += len(rows)
                    print(f"  {tbl}: {copied}/{total_rows} ({copied * 100 / total_rows:.1f}%)", flush=True)

                dst_cur.execute(f"SELECT COALESCE(MAX(`{pk}`), 0) FROM `{tbl}`")
                max_id = int(dst_cur.fetchone()[0])
                if max_id > 0:
                    dst_cur.execute(f"ALTER TABLE `{tbl}` AUTO_INCREMENT = {max_id + 1}")
                    dst_conn.commit()
            else:
                src_cur.execute(f"SELECT {col_list} FROM `{tbl}`")
                rows = src_cur.fetchall()
                if rows:
                    dst_cur.executemany(insert_sql, rows)
                    dst_conn.commit()
                    copied = len(rows)
                    print(f"  {tbl}: {copied}/{total_rows} (100.0%)", flush=True)

        print("\n[Verify] Comparing source vs TiDB row counts:")
        all_ok = True
        for tbl in TABLES_ORDER:
            dst_cur.execute(f"SELECT COUNT(*) FROM `{tbl}`")
            dst_cnt = int(dst_cur.fetchone()[0])
            ok = dst_cnt == src_counts[tbl]
            if not ok:
                all_ok = False
            mark = "OK" if ok else "MISMATCH"
            print(f"  - {tbl:<20}: src={src_counts[tbl]:>8} dst={dst_cnt:>8} [{mark}]")

        print(f"\nCompleted in {time.time() - t0:.1f}s. Parity={all_ok}")
        return all_ok
    finally:
        try:
            dst_cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        except Exception:
            pass
        dst_cur.close()
        dst_conn.close()
        src_cur.close()
        src_conn.close()


def parse_args():
    p = argparse.ArgumentParser(description="Migrate local MySQL supplier_crawler DB to TiDB Cloud")
    p.add_argument("--src-host", default=os.getenv("SRC_DB_HOST", "127.0.0.1"))
    p.add_argument("--src-port", type=int, default=int(os.getenv("SRC_DB_PORT", "3306")))
    p.add_argument("--src-user", default=os.getenv("SRC_DB_USER", "root"))
    p.add_argument("--src-password", default=os.getenv("SRC_DB_PASSWORD", ""))
    p.add_argument("--src-db", default=os.getenv("SRC_DB_NAME", "supplier_crawler"))

    p.add_argument("--dst-host", default=os.getenv("DB_HOST", ""))
    p.add_argument("--dst-port", type=int, default=int(os.getenv("DB_PORT", "4000")))
    p.add_argument("--dst-user", default=os.getenv("DB_USER", ""))
    p.add_argument("--dst-password", default=os.getenv("DB_PASSWORD", ""))
    p.add_argument("--dst-db", default=os.getenv("DB_NAME", "supplier_crawler"))
    p.add_argument("--dst-ssl", action="store_true", default=True)
    p.add_argument("--dst-ssl-ca", default=os.getenv("DB_SSL_CA", ""))

    p.add_argument("--batch-size", type=int, default=1000)
    p.add_argument("--truncate", action="store_true", help="Truncate target tables before inserting")
    p.add_argument("--dry-run", action="store_true", help="Inspect source tables and TiDB DDLs without connecting to target")
    return p.parse_args()


if __name__ == "__main__":
    ok = migrate(parse_args())
    sys.exit(0 if ok else 1)
