# 📄 PDF-OCR-Toolkit — 文档处理工具集

扫描件 PDF → 文字、图片 OCR 识别、批量文档转换。

## 功能

| 模块 | 说明 |
|------|------|
| `ocr_engine.py` | OCR 引擎抽象层（marker-pdf / 百度 OCR） |
| `baidu_ocr.py` | 百度 OCR API 客户端 |
| `pdf_processor.py` | PDF 文字提取 + 扫描件 OCR |
| `batch_processor.py` | 批量处理目录下的 PDF/图片 |

## 快速开始

```bash
pip install -r requirements.txt

# 识别单个 PDF
python cli.py scan document.pdf

# 批量处理
python cli.py batch ./scanned-pdfs/ --output ./output/

# 百度 OCR 识别图片
python cli.py ocr photo.jpg --engine baidu

# PDF 文字提取（非扫描件）
python cli.py extract text-book.pdf
```

## 环境变量

```bash
export BAIDU_OCR_API_KEY=your_api_key
export BAIDU_OCR_SECRET_KEY=your_secret_key
```

## License

MIT
