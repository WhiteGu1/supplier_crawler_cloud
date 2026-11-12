import openpyxl
import os

folder = r'C:\Users\Administrator\Downloads'
for f in os.listdir(folder):
    if f.endswith('.xlsx') and 'Bella' in f:
        path = os.path.join(folder, f)
        wb = openpyxl.load_workbook(path, data_only=True)
        sheet = wb.active
        clean_name = f.encode('ascii', 'replace').decode('ascii')
        print(f"=== {clean_name} ({sheet.title}) ===")
        for r in range(1, 10):
            row_vals = [sheet.cell(r, c).value for c in range(1, 10)]
            print(f"Row {r}: {row_vals}")
        print(f"Total rows: {sheet.max_row}\n")
