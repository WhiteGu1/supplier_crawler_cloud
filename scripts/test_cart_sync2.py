# -*- coding: utf-8 -*-
import requests, json, sys, re
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

def test_bella_nonce():
    print("=== Testing Bella Central Store API Nonce ===")
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    # GET cart to receive Nonce
    r = s.get("https://bellacentral.com.ar/wp-json/wc/store/v1/cart")
    print("Cart GET status:", r.status_code)
    nonce = r.headers.get("Nonce")
    print("Nonce from headers:", nonce)
    if nonce:
        headers = {"Nonce": nonce, "Content-Type": "application/json"}
        # Try add item
        r_add = s.post("https://bellacentral.com.ar/wp-json/wc/store/v1/cart/add-item", 
                       headers=headers, json={"id": 205674, "quantity": 1})
        print("Add item with nonce status:", r_add.status_code)
        print("Add item response:", r_add.text[:300])

def test_sfpanda_form():
    print("\n=== Testing sfpanda Product Form ===")
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    r = s.get("https://sfpanda.com.ar/productos")
    soup = BeautifulSoup(r.text, 'html.parser')
    form = soup.select_one("form[action*='/cart/add']")
    if form:
        print("Form action:", form.get("action"))
        print("Form inputs:", [(inp.get("name"), inp.get("value")) for inp in form.select("input")])
        # Submit the actual form
        action_url = "https://sfpanda.com.ar" + form.get("action")
        data = {}
        for inp in form.select("input"):
            if inp.get("name"):
                data[inp.get("name")] = inp.get("value") or "1"
        data["qty"] = "2"
        headers = {
            "Referer": "https://sfpanda.com.ar/productos",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01"
        }
        r_post = s.post(action_url, data=data, headers=headers)
        print("sfpanda submit status:", r_post.status_code)
        print("sfpanda submit response:", r_post.text[:300])

def test_osa_with_cookies():
    print("\n=== Testing OSA with Session Cookies ===")
    import pymysql
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='admin123', database='supplier_crawler')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT selectors FROM suppliers WHERE id=5")
    row = cur.fetchone()
    conn.close()
    selectors = json.loads(row['selectors']) if row and row['selectors'] else {}
    manual_cookies = selectors.get('manual_cookies', '')
    
    cookies = {}
    for part in manual_cookies.split(';'):
        if '=' in part:
            k, v = part.strip().split('=', 1)
            cookies[k] = v
            
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.osadistribuidora.com.ar/productos/"
    })
    s.cookies.update(cookies)
    
    # Check cart or a product page
    r_check = s.get("https://www.osadistribuidora.com.ar/carrito/", timeout=10)
    print("OSA cart page status:", r_check.status_code, "Length:", len(r_check.text))
    # Try adding Plato FENIX DURAX (variant 152161309)
    r_add = s.post("https://www.osadistribuidora.com.ar/comprar/", 
                   data={"add_to_cart": "152161309", "quantity": "24"},
                   allow_redirects=False, timeout=10)
    print("OSA add status:", r_add.status_code, "Location:", r_add.headers.get("Location"))

if __name__ == '__main__':
    test_bella_nonce()
    test_sfpanda_form()
    test_osa_with_cookies()
