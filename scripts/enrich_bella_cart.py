# -*- coding: utf-8 -*-
import sys, os, re, requests, asyncio, aiohttp
from bs4 import BeautifulSoup
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler')
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("""
    SELECT DISTINCT p.id, p.name, p.sku, p.product_url
    FROM cart_items c
    JOIN products p ON c.product_id = p.id
    WHERE p.supplier_id = 18 AND p.product_url IS NOT NULL
""")
items = cur.fetchall()
print(f"Found {len(items)} Bella Central items in cart to enrich.")

async def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    sem = asyncio.Semaphore(10)
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async def process_item(it):
            async with sem:
                url = it["product_url"]
                pid = it["id"]
                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                        if resp.status == 200:
                            html = await resp.text()
                            # Find add-to-cart ID
                            m = re.search(r'name=["\']add-to-cart["\']\s+value=["\'](\d+)["\']', html)
                            wc_id = m.group(1) if m else None
                            if not wc_id:
                                m2 = re.search(r'postid-(\d+)', html)
                                wc_id = m2.group(1) if m2 else ""
                            
                            # Find min and step
                            m_min = re.search(r'name=["\']quantity["\'][^>]*min=["\'](\d+)["\']', html)
                            m_step = re.search(r'name=["\']quantity["\'][^>]*step=["\'](\d+)["\']', html)
                            
                            min_q = int(m_min.group(1)) if m_min else 1
                            pkg_q = int(m_step.group(1)) if m_step else 1
                            
                            # Update DB
                            cur.execute("""
                                UPDATE products 
                                SET min_qty=%s, package_qty=%s, sku=IF(sku IS NULL OR sku='', %s, sku)
                                WHERE id=%s
                            """, (min_q, pkg_q, wc_id, pid))
                            conn.commit()
                            print(f"[Bella] {it['name'][:30]} -> WC_ID:{wc_id} min={min_q} pkg={pkg_q}")
                except Exception as e:
                    print(f"Err {it['name'][:20]}: {e}")

        await asyncio.gather(*[process_item(it) for it in items])

asyncio.run(main())
conn.close()
print("Bella Central enrichment completed!")
