"""
scripts/check_and_add_diego_items.py
Match the 51 items from the invoice against Diego products in DB.
"""
import os
import re
import sys
import json
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_manager import DatabaseManager

INVOICE_ITEMS = [
    {"qty": 24, "cod": "45", "desc": "Adhesivo T/Plasti x100grs Tintoreto", "price": 664.0},
    {"qty": 24, "cod": "46", "desc": "Adhesivo T/Plasti x250grs Tintoreto", "price": 1225.0},
    {"qty": 48, "cod": "43", "desc": "Adhesivo T/Plasti x30grs Tintoreto", "price": 214.0},
    {"qty": 12, "cod": "131", "desc": "Adhesivo VOLIGOMA ch x30ml", "price": 1467.0},
    {"qty": 12, "cod": "132", "desc": "Adhesivo VOLIGOMA gr x50ml", "price": 2388.0},
    {"qty": 30, "cod": "290", "desc": "Anilina Colibri NEGRA", "price": 1785.0},
    {"qty": 10, "cod": "493", "desc": "Block dibujo BLANCO N°5 x20hjs", "price": 1488.0},
    {"qty": 200, "cod": "690", "desc": "Boligrafo Bic fino Azul", "price": 499.0},
    {"qty": 100, "cod": "22", "desc": "Boligrafo Bic opaco AZUL", "price": 433.0},
    {"qty": 100, "cod": "366", "desc": "Boligrafo Bic opaco NEGRO", "price": 433.0},
    {"qty": 36, "cod": "219", "desc": "Cinta embalar Candela x100mts Tte-c/Desc.", "price": 1682.0},
    {"qty": 48, "cod": "29", "desc": "Corrector Filgo", "price": 259.0},
    {"qty": 96, "cod": "456", "desc": "Corrector FILGO cuerpo pastel 7ml", "price": 182.0},
    {"qty": 60, "cod": "243", "desc": "Cuter gr", "price": 236.0},
    {"qty": 12, "cod": "95", "desc": "Encendedor cocina Makao 22cm", "price": 1841.0},
    {"qty": 48, "cod": "299", "desc": "Esponja lisa Make", "price": 302.0},
    {"qty": 4, "cod": "192", "desc": "Gas garrafa anafe MOTA", "price": 2550.0},
    {"qty": 2, "cod": "453", "desc": "Goma de borrar FILGO L/T DUOTEK x36u", "price": 7634.0},
    {"qty": 2, "cod": "399", "desc": "Goma de borrar FILGO LAPIZ pinto x40u", "price": 3363.0},
    {"qty": 1, "cod": "526", "desc": "Guante descartable nitrilo negro x100 (S-M-L)", "price": 7487.0},
    {"qty": 12, "cod": "347", "desc": "Guante domestico STEFF Ch-Med-Gr", "price": 1222.0},
    {"qty": 12, "cod": "271", "desc": "Hilo algodón bobina", "price": 1580.0},
    {"qty": 30, "cod": "267", "desc": "Hilo algodón med", "price": 265.0},
    {"qty": 10, "cod": "343", "desc": "Hilo coser eco x12 BLANCO", "price": 1307.0},
    {"qty": 20, "cod": "344", "desc": "Hilo coser eco x12 NEGRO", "price": 1307.0},
    {"qty": 10, "cod": "256", "desc": "Hilo coser eco x12 SURTIDO", "price": 1307.0},
    {"qty": 6, "cod": "149", "desc": "Inflador Bici 2 picos", "price": 2810.0},
    {"qty": 30, "cod": "123", "desc": "La gotita", "price": 1559.0},
    {"qty": 30, "cod": "124", "desc": "La gotita gel", "price": 2150.0},
    {"qty": 20, "cod": "436", "desc": "Lampara Hi-Power 50w Luz Dia Candela -c/Desc.", "price": 5326.0},
    {"qty": 20, "cod": "596", "desc": "Lampara Hi-Power 70w Luz dia Candela-c/Desc.", "price": 9338.0},
    {"qty": 24, "cod": "140", "desc": "Naipe Habana x50", "price": 2330.0},
    {"qty": 6, "cod": "138", "desc": "Naipe poker x2 estuche plastico", "price": 1407.0},
    {"qty": 72, "cod": "197", "desc": "Pelotas Pulpo Nº2 Rayada - 5,5cm -c/Desc.", "price": 952.0},
    {"qty": 24, "cod": "199", "desc": "Pelotas Pulpo Nº4 Rayada - 10cm", "price": 1974.0},
    {"qty": 20, "cod": "542", "desc": "Pila Candela 2032 litio", "price": 285.0},
    {"qty": 6, "cod": "74", "desc": "Piñata gr Candela 72\"", "price": 1811.0},
    {"qty": 36, "cod": "375", "desc": "Pistola silicona Candela fina 10w-c/Desc.", "price": 3137.0},
    {"qty": 24, "cod": "402", "desc": "Pistola silicona Candela gruesa 40w-c/Desc.", "price": 4416.0},
    {"qty": 6, "cod": "128", "desc": "Poxipol", "price": 5247.0},
    {"qty": 12, "cod": "125", "desc": "Poxiran", "price": 3643.0},
    {"qty": 6, "cod": "164", "desc": "Tanza 1,5mm x10mts Makao", "price": 782.0},
    {"qty": 6, "cod": "165", "desc": "Tanza 2,5mm x10mts Makao", "price": 1179.0},
    {"qty": 6, "cod": "166", "desc": "Tanza 3mm x10mts Makao", "price": 1625.0},
    {"qty": 30, "cod": "88", "desc": "Tapon botella de tomate", "price": 188.0},
    {"qty": 24, "cod": "258", "desc": "Tijera 6\"", "price": 529.0},
    {"qty": 48, "cod": "454", "desc": "Tijera escolar FILGO", "price": 416.0},
    {"qty": 250, "cod": "671", "desc": "Trapo paño amarillo 38x40 economico", "price": 273.0},
    {"qty": 24, "cod": "561", "desc": "Trapo rejilla doble pabilo 35x45 GANGA", "price": 520.0},
    {"qty": 36, "cod": "425", "desc": "Trapo rejilla liviana pabilo 35x40 GANGA", "price": 299.0},
    {"qty": 6, "cod": "126", "desc": "Unipox", "price": 1947.0},
]

def main():
    db = DatabaseManager('localhost', 3306, 'root', 'admin123', 'supplier_crawler')
    
    with db.connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, sku, name, price, image_url, min_qty, package_qty FROM products WHERE supplier_id = 2")
        diego_prods = cur.fetchall()

    print(f"Total Diego products in DB: {len(diego_prods)}")

    # Index Diego products by sku and by code from image_url
    by_sku = {}
    by_img_code = {}
    for p in diego_prods:
        sku = (p.get("sku") or "").strip()
        if sku:
            by_sku[sku] = p
        img_url = p.get("image_url") or ""
        m = re.search(r'/catalogo/(\d+)\.', img_url)
        if m:
            by_img_code[m.group(1)] = p

    found = []
    missing_in_db = []

    for item in INVOICE_ITEMS:
        cod = str(item["cod"])
        p = by_sku.get(cod) or by_img_code.get(cod)
        if p:
            found.append((item, p))
        else:
            missing_in_db.append(item)

    print(f"Matched in DB: {len(found)} / {len(INVOICE_ITEMS)}")
    if missing_in_db:
        print(f"Missing in DB: {len(missing_in_db)}")
        for m in missing_in_db:
            print(f"  Cod: {m['cod']} | {m['desc']}")

if __name__ == "__main__":
    main()
