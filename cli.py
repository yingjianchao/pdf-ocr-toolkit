#!/usr/bin/env python3
"""PDF-OCR-Toolkit 命令行界面"""
import argparse, sys, os
sys.path.insert(0, os.path.dirname(__file__))

def main():
    p = argparse.ArgumentParser(description="📄 PDF/OCR 文档处理工具")
    sub = p.add_subparsers(dest="cmd")

    # OCR 识别
    s1 = sub.add_parser("scan", help="扫描件 PDF OCR 识别")
    s1.add_argument("file", help="PDF 文件路径")
    s1.add_argument("--engine", default="marker", choices=["marker", "baidu"])
    s1.add_argument("-o", "--output", help="输出文件路径")
    s1.add_argument("--pages", help="页码范围 (如 1-10)")

    # 文字提取
    s2 = sub.add_parser("extract", help="从文字型 PDF 提取文字")
    s2.add_argument("file", help="PDF 文件路径")
    s2.add_argument("-o", "--output", help="输出文件路径")

    # 批量处理
    s3 = sub.add_parser("batch", help="批量处理目录")
    s3.add_argument("dir", help="输入目录")
    s3.add_argument("--output", "-o", default="./output", help="输出目录")
    s3.add_argument("--engine", default="marker", choices=["marker", "baidu"])

    # 图片 OCR
    s4 = sub.add_parser("ocr", help="图片 OCR 识别")
    s4.add_argument("file", help="图片文件路径")
    s4.add_argument("--engine", default="baidu", choices=["marker", "baidu"])
    s4.add_argument("-o", "--output", help="输出文件路径")

    args = p.parse_args()

    if args.cmd == "scan":
        from src.pdf_processor import ocr_pdf
        pages = None
        if args.pages:
            parts = args.pages.split("-")
            pages = list(range(int(parts[0])-1, int(parts[1])))
        text = ocr_pdf(args.file, args.engine, pages)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f: f.write(text)
            print(f"✅ 已保存到 {args.output}")
        else:
            print(text)

    elif args.cmd == "extract":
        from src.pdf_processor import extract_text
        text = extract_text(args.file)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f: f.write(text)
            print(f"✅ 已保存到 {args.output}")
        else:
            print(text)

    elif args.cmd == "batch":
        from src.batch_processor import batch_process
        batch_process(args.dir, args.output, args.engine)

    elif args.cmd == "ocr":
        from src.ocr_engine import get_engine
        eng = get_engine(args.engine)
        text = eng.recognize_image(args.file)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f: f.write(text)
            print(f"✅ 已保存到 {args.output}")
        else:
            print(text)

    else:
        p.print_help()

if __name__ == "__main__":
    main()
