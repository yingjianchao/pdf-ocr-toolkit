#!/usr/bin/env python3
"""OCR 引擎抽象层 - 支持 marker-pdf 本地识别和百度 OCR API"""
from abc import ABC, abstractmethod
import os, base64

class OCREngine(ABC):
    """OCR 引擎基类"""
    @abstractmethod
    def recognize_image(self, image_path: str) -> str:
        """识别单张图片，返回文字"""
        pass

    @abstractmethod
    def recognize_pdf(self, pdf_path: str) -> str:
        """识别 PDF 文件，返回文字"""
        pass


class MarkerOCREngine(OCREngine):
    """基于 marker-pdf 的本地 OCR（离线，免费，支持 90+ 语言）"""
    def __init__(self):
        try:
            from marker.converters.pdf import PdfConverter
            from marker.config.parser import ConfigParser
            self._available = True
        except ImportError:
            self._available = False
            print("⚠️  marker-pdf 未安装: pip install marker-pdf")

    def recognize_image(self, image_path: str) -> str:
        if not self._available:
            return "[marker-pdf 未安装]"
        # marker-pdf 主要处理 PDF，图片需要先转 PDF
        from PIL import Image
        img = Image.open(image_path)
        pdf_path = image_path.rsplit(".", 1)[0] + "_temp.pdf"
        img.save(pdf_path, "PDF")
        result = self.recognize_pdf(pdf_path)
        os.remove(pdf_path)
        return result

    def recognize_pdf(self, pdf_path: str) -> str:
        if not self._available:
            return "[marker-pdf 未安装]"
        from marker.converters.pdf import PdfConverter
        from marker.config.parser import ConfigParser
        converter = PdfConverter(config=ConfigParser({"output_format": "text"}))
        rendered = converter(pdf_path)
        return rendered.text


class BaiduOCREngine(OCREngine):
    """百度 OCR API（在线，每天 500 次免费）"""
    def __init__(self, api_key=None, secret_key=None):
        self.api_key = api_key or os.environ.get("BAIDU_OCR_API_KEY", "")
        self.secret_key = secret_key or os.environ.get("BAIDU_OCR_SECRET_KEY", "")
        self._token = None

    def _get_token(self):
        if self._token:
            return self._token
        import requests
        r = requests.get("https://aip.baidubce.com/oauth/2.0/token", params={
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        })
        self._token = r.json().get("access_token")
        return self._token

    def recognize_image(self, image_path: str, mode="accurate_basic") -> str:
        import requests
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        r = requests.post(
            f"https://aip.baidubce.com/rest/2.0/ocr/v1/{mode}",
            params={"access_token": self._get_token()},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"image": img_b64, "language_type": "CHN_ENG"}
        )
        result = r.json()
        words = result.get("words_result", [])
        return "\n".join(w["words"] for w in words)

    def recognize_pdf(self, pdf_path: str) -> str:
        # PDF 需要逐页转图片再识别
        import fitz  # pymupdf
        doc = fitz.open(pdf_path)
        all_text = []
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=200)
            img_path = f"/tmp/_ocr_page_{i}.png"
            pix.save(img_path)
            text = self.recognize_image(img_path)
            all_text.append(f"--- 第 {i+1} 页 ---\n{text}")
            os.remove(img_path)
        return "\n\n".join(all_text)


def get_engine(name="marker"):
    """获取 OCR 引擎实例"""
    if name == "marker":
        return MarkerOCREngine()
    elif name == "baidu":
        return BaiduOCREngine()
    else:
        raise ValueError(f"未知引擎: {name}")
