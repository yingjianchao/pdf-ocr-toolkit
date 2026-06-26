#!/usr/bin/env python3
"""百度 OCR API 完整客户端 - 支持多种识别模式"""
import requests, base64, os

class BaiduOCR:
    BASE = "https://aip.baidubce.com/rest/2.0/ocr/v1"

    def __init__(self, api_key=None, secret_key=None):
        self.api_key = api_key or os.environ.get("BAIDU_OCR_API_KEY")
        self.secret_key = secret_key or os.environ.get("BAIDU_OCR_SECRET_KEY")
        self._token = None

    @property
    def token(self):
        if not self._token:
            r = requests.get("https://aip.baidubce.com/oauth/2.0/token", params={
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.secret_key
            })
            self._token = r.json()["access_token"]
        return self._token

    def _post(self, endpoint, image_path, extra=None):
        with open(image_path, "rb") as f:
            img = base64.b64encode(f.read()).decode()
        data = {"image": img, "language_type": "CHN_ENG"}
        if extra:
            data.update(extra)
        r = requests.post(f"{self.BASE}/{endpoint}",
                         params={"access_token": self.token},
                         headers={"Content-Type": "application/x-www-form-urlencoded"},
                         data=data)
        return r.json()

    def general(self, img): return self._post("general_basic", img)
    def accurate(self, img): return self._post("accurate_basic", img)
    def table(self, img): return self._post("table", img)
    def idcard(self, img, side="front"): return self._post("idcard", img, {"id_card_side": side})
    def bankcard(self, img): return self._post("bankcard", img)
    def numbers(self, img): return self._post("numbers", img)
    def handwriting(self, img): return self._post("handwriting", img)

    def recognize(self, img, mode="accurate"):
        """统一接口"""
        func = getattr(self, mode, self.accurate)
        result = func(img)
        words = result.get("words_result", [])
        return "\n".join(w["words"] for w in words)
