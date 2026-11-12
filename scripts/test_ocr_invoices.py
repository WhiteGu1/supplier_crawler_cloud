import os
from rapidocr_onnxruntime import RapidOCR

ocr = RapidOCR()
folder = r'C:\Users\Administrator\Downloads\bella central发票'
files = sorted(os.listdir(folder))

for idx, f in enumerate(files):
    filepath = os.path.join(folder, f)
    print(f"\n=================== IMAGE {idx+1}: {f[:30]}... ===================")
    result, elapse = ocr(filepath)
    if result:
        print(f"Detected {len(result)} text boxes in {elapse}s")
        # Print first 10 and last 10 lines
        lines = [r[1] for r in result]
        print("Header lines:")
        for line in lines[:8]:
            print("  ", line)
        print("...")
        print("Trailer lines:")
        for line in lines[-8:]:
            print("  ", line)
    else:
        print("No text detected!")
