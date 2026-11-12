import os
import json
from rapidocr_onnxruntime import RapidOCR

ocr = RapidOCR()
folder = r'C:\Users\Administrator\Downloads\bella central发票'
files = sorted(os.listdir(folder))

all_pages = []

for idx, f in enumerate(files):
    filepath = os.path.join(folder, f)
    result, elapse = ocr(filepath)
    boxes = []
    if result:
        for box, text, score in result:
            boxes.append({
                'text': text,
                'score': float(score),
                'box': box
            })
    all_pages.append({
        'page_index': idx + 1,
        'filename': f,
        'boxes': boxes
    })

with open('scripts/invoice_ocr_full.json', 'w', encoding='utf-8') as f:
    json.dump(all_pages, f, ensure_ascii=False, indent=2)

print("Saved OCR result to scripts/invoice_ocr_full.json")
