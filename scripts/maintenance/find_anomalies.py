# -*- coding: utf-8 -*-
import sys
import test_full_da_extract as t

for x in t.all_extracted:
    if not x['sku']:
        print("None SKU:", x)
    if not x['name']:
        print("Empty Name:", x)
