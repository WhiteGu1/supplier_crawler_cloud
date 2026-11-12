# -*- coding: utf-8 -*-
import requests, json, sys, re

sys.stdout.reconfigure(encoding='utf-8')

def test_smarty_cart_add():
    print("=== Testing SmartyCart Add to Cart ===")
    # benabi token: 2192d3e59b1ab02da4b38da25b981f657af0e020
    # From earlier: Espatula De Silicona 58512, product-id=4036431, min=24, step=24
    url = "https://catalog.smarty.com.ar/Carts/add_item/"
    token = "2192d3e59b1ab02da4b38da25b981f657af0e020"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://catalog.smarty.com.ar/token/{token}",
    }
    data = {
        "token": token,
        "quantity_data[0][product_id]": "4036431",
        "quantity_data[0][quantity]": "24",
        "do-lookup-cart-html": "0"
    }
    s = requests.Session()
    r = s.post(url, data=data, headers=headers, timeout=10)
    print("Smarty add status:", r.status_code)
    print("Smarty add response text:", r.text[:300])
    
    # Check cart URL
    cart_url = f"https://catalog.smarty.com.ar/token/{token}/cart"
    r_cart = s.get(cart_url, headers=headers, timeout=10)
    print("Smarty cart status:", r_cart.status_code)
    # Check if product is in cart
    if "58512" in r_cart.text or "4036431" in r_cart.text or "Espatula" in r_cart.text:
        print("SUCCESS! Product found in Smarty cart.")
    else:
        print("Note: check cart content:", r_cart.text[:200])

def test_diego_cart_add():
    print("\n=== Testing Diego Add to Cart ===")
    cookies = {'PHPSESSID': '5pk36qcku3uph1f9lggbq6mlft'}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://distrinimay.com.ar/cat/",
    }
    # Produ 689, frac=48, desc="Curita Dismar x10", importe=...
    url = "https://distrinimay.com.ar/jsyphp/carrito.php"
    data = {
        "produ": "689",
        "cantidad": "48",
        "descripcion": "Curita Dismar x10",
        "importe": "500",
        "accion": "compra"
    }
    s = requests.Session()
    s.cookies.update(cookies)
    r = s.post(url, data=data, headers=headers, timeout=10)
    print("Diego add status:", r.status_code)
    print("Diego add response:", r.text)

def test_sfpanda_cart_add():
    print("\n=== Testing sfpanda Add to Cart ===")
    s = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://sfpanda.com.ar/productos",
        "X-Requested-With": "XMLHttpRequest"
    }
    # Test product 37700711, qty=2
    url = "https://sfpanda.com.ar/cart/add/37700711"
    data = {"qty": "2"}
    r = s.post(url, data=data, headers=headers, timeout=10)
    print("sfpanda add status:", r.status_code)
    print("sfpanda add response:", r.text[:300])

def test_bella_central_cart_add():
    print("\n=== Testing Bella Central Add to Cart ===")
    s = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json"
    }
    # Product 205674, qty=1
    url = "https://bellacentral.com.ar/wp-json/wc/store/v1/cart/add-item"
    data = {"id": 205674, "quantity": 1}
    r = s.post(url, json=data, headers=headers, timeout=10)
    print("Bella Central add status:", r.status_code)
    print("Bella Central add response:", r.text[:300])
    # Also test standard WC query param: ?add-to-cart=205674&quantity=1
    r_std = s.get("https://bellacentral.com.ar/?add-to-cart=205674&quantity=1", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    print("Bella Central std param status:", r_std.status_code, "Final URL:", r_std.url)

def test_osa_cart_add():
    print("\n=== Testing OSA Add to Cart ===")
    s = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.osadistribuidora.com.ar/productos/copa-windsord-nadir/"
    }
    # Variant id 46644709, qty=12
    url = "https://www.osadistribuidora.com.ar/comprar/"
    data = {
        "add_to_cart": "46644709",
        "quantity": "12"
    }
    r = s.post(url, data=data, headers=headers, timeout=10, allow_redirects=False)
    print("OSA add status:", r.status_code)
    print("OSA Location header:", r.headers.get("Location"))
    if r.headers.get("Location"):
        r_cart = s.get(r.headers.get("Location"), headers=headers, timeout=10)
        print("OSA Cart page status:", r_cart.status_code)

if __name__ == "__main__":
    test_smarty_cart_add()
    test_diego_cart_add()
    test_sfpanda_cart_add()
    test_bella_central_cart_add()
    test_osa_cart_add()
