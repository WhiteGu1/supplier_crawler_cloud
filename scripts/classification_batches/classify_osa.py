# -*- coding: utf-8 -*-
"""osa 38条按名称分类"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

# 基于名称的分类
classifications = {
    12205: '餐饮用品',   # Bombilla Coco Espiral - 马黛茶吸管
    12311: '厨房炊具',   # Filtro Para Café de Tela
    12400: '厨房炊具',   # Filtro de papel cuadrado Air fryer
    12411: '餐饮用品',   # Bombilla chata de acero
    12486: '厨房餐具',   # Pinza de Fiambre Acero
    12492: '厨房餐具',   # Fuente Oval
    12505: '厨房炊具',   # Espumadera de Alambre
    12575: '厨房炊具',   # Canasto Freidor
    12578: '厨房餐具',   # Pico para botella de aceite
    12606: '厨房炊具',   # Rejilla repostera
    12694: '清洁用品',   # Cepillo limpia inodoro
    12768: '厨房炊具',   # Molde muffin silicona x 12
    12771: '厨房餐具',   # Azucarera porcelana
    12780: '厨房炊具',   # Molde muffin de silicona x 6
    12791: '厨房炊具',   # Molde Muffin x 12 antiadherente
    13020: '餐饮用品',   # Bombilla chata COLOR
    13044: '厨房炊具',   # Molinillo de café
    13068: '厨房炊具',   # Batidor de Alambre
    13120: '厨房炊具',   # Canasto Freidor Cuadrado
    13257: '厨房餐具',   # Tabla plástica PLEGABLE
    13278: '厨房炊具',   # Canasto Freidor Solo
    13409: '厨房餐具',   # Cuenco Americano 600 ML
    13438: '厨房餐具',   # Canasto Rectangular GASTRONÓMICO
    13587: '厨房炊具',   # Flanera de silicona
    13691: '厨房炊具',   # Olla de acero con colador
    13797: '厨房餐具',   # Set salero ypimentero
    13857: '厨房炊具',   # Flanera de silicona
    13870: '厨房餐具',   # Posa Torta Redondo
    13926: '厨房餐具',   # Posa Torta cuadrado
    13975: '厨房储物',   # Bowl con Tapa Plastica
    13978: '餐饮用品',   # Set x 7 accesorios cocteleria
    14161: '厨房餐具',   # Juego de Niño * 3 de Acero
    14244: '装饰品',     # Maceta Holanda color
    14447: '餐饮用品',   # Jarro Mug 330 CC Cerámica
    15259: '厨房炊具',   # Sarten profunda cerámico granito
    15260: '厨房炊具',   # Bifera cerámico granito
    15261: '厨房炊具',   # Bifera granito forjado
    15262: '厨房炊具',   # Cacerola granito forjado
}

conn = pymysql.connect(host='localhost', port=3306, user='root',
    password='admin123', database='supplier_crawler', charset='utf8mb4')
cur = conn.cursor()

updated = 0
for pid, cat in classifications.items():
    cur.execute("UPDATE products SET category=%s WHERE id=%s", (cat, pid))
    updated += cur.rowcount

conn.commit()
print(f"osa: 更新 {updated}/{len(classifications)} 条")

# Verify
cur.execute("""
    SELECT COUNT(*) FROM products
    WHERE supplier_id=5 AND (category IS NULL OR category='')
    AND image_local IS NOT NULL AND image_local != ''
""")
remaining = cur.fetchone()[0]
print(f"osa 剩余有图未分类: {remaining}")

conn.close()
