import json, urllib.request

with open('scripts/missing_comparison.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("".join(lines[:10]))
print("Total lines:", len(lines))
