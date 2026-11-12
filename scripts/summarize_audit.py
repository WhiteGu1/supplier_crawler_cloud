# -*- coding: utf-8 -*-
import json

with open("scripts/bella_cart_audit_result.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Total Bella Items:", data["total_bella_items"])
print("Compliant Box:", data["compliant_box_count"])
print("Compliant Pack:", data["compliant_pack_count"])
print("Non Compliant:", data["non_compliant_count"])
print("Single Unit:", data["single_unit_count"])

# 列出所有不合规商品
non_comp = [it for it in data["items"] if "❌" in it["compliance"]]
print(f"\nAll {len(non_comp)} non-compliant items:")
for i, it in enumerate(non_comp, 1):
    print(f"{i}. [{it['sku']}] {it['name']} | 当前加购: {it['cart_qty']} | 装盒规格: {it['box_qty']} | {it['raw_desc']} -> 建议: {it['rec_qty']}")

# 列出符合小包但不成整盒的商品
pack_comp = [it for it in data["items"] if "非整盒" in it["compliance"]]
print(f"\nAll {len(pack_comp)} pack-compliant items:")
for i, it in enumerate(pack_comp, 1):
    print(f"{i}. [{it['sku']}] {it['name']} | 当前加购: {it['cart_qty']} | 整盒: {it['box_qty']} (小包: {it['sub_pack_qty']}) | {it['raw_desc']} -> 建议整盒: {it['rec_qty']}")
