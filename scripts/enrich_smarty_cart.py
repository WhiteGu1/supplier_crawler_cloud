# -*- coding: utf-8 -*-
import sys, os, re, requests
from bs4 import BeautifulSoup
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler')
cur = conn.cursor(pymysql.cursors.DictCursor)

# 1. Enrich SmartyCart items (Trapoman 3, benabi 4)
cur.execute("""
    SELECT DISTINCT p.id, p.supplier_id, p.name, p.sku, p.product_url, s.name as s_name, s.list_url
    FROM cart_items c
    JOIN products p ON c.product_id = p.id
    JOIN suppliers s ON p.supplier_id = s.id
    WHERE p.supplier_id IN (3, 4)
""")
smarty_items = cur.fetchall()
print(f"Found {len(smarty_items)} SmartyCart items in cart to enrich.")

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

for it in smarty_items:
    pid = it["id"]
    s_name = it["s_name"]
    list_url = it["list_url"]
    m = re.search(r'/token/([a-f0-9]+)', list_url)
    if not m:
        continue
    token = m.group(1)
    kw = (it["sku"] or "").strip() or it["name"][:30]
    try:
        search_url = f"https://catalog.smarty.com.ar/token/{token}?keyword={requests.utils.quote(kw)}"
        r = session.get(search_url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        card = soup.select_one("div.item")
        if card:
            # prod_id
            inp_id = card.select_one("input.id, input[data-product-id]")
            prod_id = inp_id.get("data-product-id") or inp_id.get("value") if inp_id else ""
            if not prod_id:
                c_id = card.get("id") or ""
                if c_id.startswith("item_"):
                    prod_id = c_id.replace("item_", "").strip()
            
            # min & step
            inp_qty = card.select_one("input.quantity")
            min_q = 1
            pkg_q = 1
            if inp_qty:
                try: min_q = int(inp_qty.get("min") or 1)
                except: pass
                try: pkg_q = int(inp_qty.get("step") or 1)
                except: pass
            
            card_text = card.get_text(" ", strip=True)
            m_paq = re.search(r'Paquete:\s*(\d+)', card_text, re.I)
            m_bulto = re.search(r'Bulto:\s*(\d+)', card_text, re.I)
            if pkg_q <= 1:
                if m_paq: pkg_q = int(m_paq.group(1))
                elif m_bulto: pkg_q = int(m_bulto.group(1))

            prod_url = f"https://catalog.smarty.com.ar/token/{token}/{prod_id}" if prod_id else None
            
            # Update DB
            cur.execute("""
                UPDATE products 
                SET min_qty=%s, package_qty=%s, product_url=IFNULL(product_url, %s)
                WHERE id=%s
            """, (min_q, pkg_q, prod_url, pid))
            conn.commit()
            print(f"[{s_name}] {it['name'][:25]} -> ID:{prod_id} min={min_q} pkg={pkg_q}")
    except Exception as e:
        print(f"Error {kw}: {e}")

conn.close()
print("SmartyCart enrichment completed!")
