import os
import pandas as pd

folder = r'C:\Users\Administrator\Downloads\xls'
out_lines = []
for fname in sorted(os.listdir(folder)):
    fpath = os.path.join(folder, fname)
    out_lines.append(f"\n==================== {fname} (size={os.path.getsize(fpath)}) ====================")
    df = pd.read_excel(fpath, header=None)
    out_lines.append(f"Shape: {df.shape}")
    for idx, row in df.iterrows():
        vals = [str(v).strip() if pd.notna(v) else '' for v in row.values]
        if any(vals):
            line = " | ".join(f"C{c}:{v}" for c, v in enumerate(vals) if v)
            out_lines.append(f"R{idx:02d}: {line}")

with open('scripts/xls_dump.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))
print(f"Wrote {len(out_lines)} lines to scripts/xls_dump.txt")
