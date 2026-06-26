#!/usr/bin/env python3
"""批量处理器 - 处理整个目录的 PDF/图片"""
import os, sys, time
from pathlib import Path

SUPPORTED = {".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}

def scan_dir(input_dir: str) -> list:
    """扫描目录中的可处理文件"""
    files = []
    for f in sorted(Path(input_dir).rglob("*")):
        if f.suffix.lower() in SUPPORTED:
            files.append(str(f))
    return files

def batch_process(input_dir: str, output_dir: str, engine="marker", fmt="txt"):
    """批量处理目录"""
    from .pdf_processor import extract_text, ocr_pdf, is_scanned
    from .ocr_engine import get_engine

    os.makedirs(output_dir, exist_ok=True)
    files = scan_dir(input_dir)
    print(f"📁 找到 {len(files)} 个文件")

    eng = get_engine(engine)
    results = []

    for i, fpath in enumerate(files, 1):
        fname = Path(fpath).stem
        out_path = os.path.join(output_dir, f"{fname}.{fmt}")
        print(f"[{i}/{len(files)}] 处理: {Path(fpath).name} ...", end=" ")

        start = time.time()
        try:
            if fpath.lower().endswith(".pdf"):
                if is_scanned(fpath):
                    text = eng.recognize_pdf(fpath)
                else:
                    text = extract_text(fpath)
            else:
                text = eng.recognize_image(fpath)

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)

            elapsed = time.time() - start
            chars = len(text)
            print(f"✅ {chars} 字 ({elapsed:.1f}秒)")
            results.append({"file": fpath, "chars": chars, "time": elapsed, "output": out_path})
        except Exception as e:
            print(f"❌ {e}")
            results.append({"file": fpath, "error": str(e)})

    # 汇总
    total_chars = sum(r.get("chars", 0) for r in results)
    total_time = sum(r.get("time", 0) for r in results)
    errors = sum(1 for r in results if "error" in r)
    print(f"\n📊 完成: {len(results)} 个文件, {total_chars} 字, {total_time:.1f}秒, {errors} 个错误")

    return results
