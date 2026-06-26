#!/usr/bin/env python3
"""使用示例"""
from src.ocr_engine import get_engine
from src.pdf_processor import extract_text, ocr_pdf, is_scanned

# 1. 判断 PDF 类型
pdf = "document.pdf"
if is_scanned(pdf):
    print("这是扫描件，需要 OCR")
    text = ocr_pdf(pdf, engine="marker")
else:
    print("这是文字型 PDF，直接提取")
    text = extract_text(pdf)

print(text[:500])

# 2. 用百度 OCR 识别图片
engine = get_engine("baidu")
text = engine.recognize_image("photo.jpg")
print(text)

# 3. 批量处理
from src.batch_processor import batch_process
results = batch_process("./scanned_pdfs/", "./output/", engine="marker")
