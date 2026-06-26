#!/usr/bin/env python3
"""PDF 处理器 - 文字型 PDF 提取 + 扫描件 OCR"""
import os, sys

def extract_text(pdf_path: str) -> str:
    """从文字型 PDF 提取文字（不需要 OCR）"""
    try:
        import fitz  # pymupdf
        doc = fitz.open(pdf_path)
        text = []
        for i, page in enumerate(doc):
            page_text = page.get_text()
            if page_text.strip():
                text.append(f"--- 第 {i+1} 页 ---\n{page_text}")
        return "\n\n".join(text)
    except ImportError:
        # fallback: pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                text = []
                for i, page in enumerate(pdf.pages):
                    t = page.extract_text()
                    if t:
                        text.append(f"--- 第 {i+1} 页 ---\n{t}")
                return "\n\n".join(text)
        except ImportError:
            return "[需要安装 pymupdf 或 pdfplumber]"

def ocr_pdf(pdf_path: str, engine="marker", pages=None) -> str:
    """对扫描件 PDF 进行 OCR"""
    from .ocr_engine import get_engine
    eng = get_engine(engine)

    if engine == "baidu" and pages:
        # 百度 OCR 可以指定页码
        import fitz
        doc = fitz.open(pdf_path)
        all_text = []
        for i in pages:
            if i < len(doc):
                pix = doc[i].get_pixmap(dpi=200)
                img = f"/tmp/_page_{i}.png"
                pix.save(img)
                text = eng.recognize_image(img)
                all_text.append(f"--- 第 {i+1} 页 ---\n{text}")
                os.remove(img)
        return "\n\n".join(all_text)

    return eng.recognize_pdf(pdf_path)

def is_scanned(pdf_path: str) -> bool:
    """判断 PDF 是否为扫描件（几乎没有可选文字）"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        total_chars = 0
        for page in doc[:3]:  # 检查前 3 页
            total_chars += len(page.get_text().strip())
        return total_chars < 50  # 每页平均不到 17 个字就是扫描件
    except:
        return True  # 无法判断时默认当扫描件处理
