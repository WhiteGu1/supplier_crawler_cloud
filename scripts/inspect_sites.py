# -*- coding: utf-8 -*-
import sys, re, json, requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

def test_diego():
    print("=== Testing Diego ===")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get("https://distrinimay.com.ar/cat/", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("div.divprod, div.divprodnuevos, div.divprodofer")
        print(f"Diego total cards on /cat/: {len(cards)}")
        for c in cards[:5]:
            code = c.select_one(".fcod")
            des = c.select_one(".fdes")
            impo = c.select_one(".fimpo")
            frac = c.select_one(".ffrac")
            input_cant = c.select_one("input.fcant")
            btn = c.select_one("button[onclick*='comprar'], button.fcompra")
            print(f"  Code: {code.get_text(strip=True) if code else None}")
            print(f"  Name: {des.get_text(strip=True) if des else None}")
            print(f"  Price: {impo.get_text(strip=True) if impo else None}")
            print(f"  Frac el: {frac} | frac attr: {frac.get('frac') if frac else None} | text: {frac.get_text(strip=True) if frac else None}")
            if input_cant:
                print(f"  Input: {input_cant.attrs}")
            if btn:
                print(f"  Btn: {btn.attrs}")
            print("---")
    except Exception as e:
        print("Diego error:", e)

def test_smarty_benabi_trapoman():
    print("\n=== Testing SmartyCart (benabi) ===")
    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://catalog.smarty.com.ar/token/2192d3e59b1ab02da4b38da25b981f657af0e020"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("div.item")
        print(f"Smarty total cards: {len(cards)}")
        for c in cards[:5]:
            title = c.select_one("h5.item-name")
            sku = c.select_one(".reference")
            price = c.select_one(".item-price")
            # Look for bulto, paquete, min-quantity, etc.
            text = c.get_text(" ", strip=True)
            print(f"  Name: {title.get_text(strip=True) if title else None}")
            print(f"  SKU: {sku.get_text(strip=True) if sku else None}")
            print(f"  Data attrs: {c.attrs}")
            # Find inputs or buttons
            inputs = c.select("input")
            for inp in inputs:
                print(f"    Input: {inp.attrs}")
            # Search for Bulto / Paquete in card text
            m_bulto = re.search(r'Bulto:\s*(\d+)', text, re.I)
            m_paq = re.search(r'Paquete:\s*(\d+)', text, re.I)
            m_min = re.search(r'(?:M[ií]nimo|Min):\s*(\d+)', text, re.I)
            print(f"  Matches: Bulto={m_bulto.group(1) if m_bulto else None}, Paq={m_paq.group(1) if m_paq else None}, Min={m_min.group(1) if m_min else None}")
            print("---")
    except Exception as e:
        print("Smarty error:", e)

def test_sfpanda():
    print("\n=== Testing sfpanda ===")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get("https://sfpanda.com.ar/productos", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("article.product-block[data-product-id]")
        print(f"sfpanda total cards: {len(cards)}")
        for c in cards[:5]:
            title = c.select_one("a.product-block__anchor")
            price = c.select_one("span.product-block__price")
            inp = c.select_one("input.product-block__input")
            btn = c.select_one("form[action*='/cart/add']")
            print(f"  Name: {title.get_text(strip=True) if title else None}")
            print(f"  Price: {price.get_text(strip=True) if price else None}")
            if inp:
                print(f"  Input attrs: {inp.attrs}")
            if btn:
                print(f"  Form action: {btn.get('action')}")
            print("---")
    except Exception as e:
        print("sfpanda error:", e)

def test_osa():
    print("\n=== Testing OSA ===")
    # OSA is Tiendanube. Let's see some OSA products from DB
    import pymysql
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT id, name, sku, price, product_url, description FROM products WHERE supplier_id=5 AND product_url IS NOT NULL LIMIT 5")
    rows = cur.fetchall()
    print(f"OSA sample DB products: {len(rows)}")
    for r in rows:
        print(f"  ID: {r['id']}, Name: {r['name']}, URL: {r['product_url']}")
        desc = r['description'] or ''
        m_bulto = re.search(r'(?:bulto|pack|caja)[\s:]*(\d+)', desc, re.I)
        m_unid = re.search(r'(\d+)\s*(?:unidades|u\b|unid)', desc, re.I)
        print(f"    Desc preview: {desc[:100]}")
        print(f"    Bulto match: {m_bulto.group(0) if m_bulto else None}, Unid match: {m_unid.group(0) if m_unid else None}")
    conn.close()

if __name__ == '__main__':
    test_diego()
    test_smarty_benabi_trapoman()
    test_sfpanda()
    test_osa()
