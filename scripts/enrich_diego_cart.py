"""
scripts/enrich_diego_cart.py
补全购物车中 Diego 商品的 sku, min_qty, package_qty, product_url
"""
import os
import re
import sys
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_manager import DatabaseManager


def main():
    db = DatabaseManager(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "admin123"),
        database=os.getenv("DB_NAME", "supplier_crawler"),
    )

    items = [i for i in db.get_cart_items() if i.get("supplier_id") == 2 or (i.get("supplier_name") or "").lower() == "diego"]
    print(f"Found {len(items)} Diego items in cart to enrich.")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    })

    enriched = 0
    with db.connection() as conn:
        cursor = conn.cursor()
        for item in items:
            p_id = item.get("product_id")
            sku = (item.get("sku") or "").strip()
            img_url = item.get("image_url") or ""

            # 提取 Diego 的 codigo (如 /catalogo/493.jpg)
            cod = sku
            if not cod:
                m = re.search(r'/catalogo/(\d+)\.', img_url)
                if m:
                    cod = m.group(1)

            if not cod:
                print(f"Cannot extract code for item: {item.get('name')}")
                continue

            # 请求 Diego API 获取商品数据与 fraccion
            try:
                resp = session.post(
                    "https://distrinimay.com.ar/jsyphp/buscarprod.php",
                    data={"filtror": "", "filtro": "", "filtrocod": cod},
                    timeout=10
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and len(data) > 0:
                        prod = data[0]
                        frac = int(prod.get("fraccion") or 1)
                        if frac < 1:
                            frac = 1
                        prod_url = f"https://distrinimay.com.ar/cat/#prod-{cod}"

                        cursor.execute(
                            """
                            UPDATE products 
                            SET sku = %s, min_qty = %s, package_qty = %s, product_url = COALESCE(product_url, %s)
                            WHERE id = %s
                            """,
                            (cod, frac, frac, prod_url, p_id)
                        )
                        conn.commit()
                        enriched += 1
                        print(f"[Diego] ID:{p_id} -> Cod:{cod} frac/pkg={frac}")
                    else:
                        print(f"[Diego] No data for Cod:{cod}")
                else:
                    print(f"[Diego] HTTP {resp.status_code} for Cod:{cod}")
            except Exception as e:
                print(f"[Diego] Error fetching Cod:{cod}: {e}")

            time.sleep(0.1)

    print(f"Diego enrichment completed! Enriched {enriched}/{len(items)} items.")


if __name__ == "__main__":
    main()
