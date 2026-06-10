"""共享 OCR 引擎: ddddocr + 可选 LaTeX OCR"""

import asyncio
import logging
import threading
from io import BytesIO

import ddddocr
from PIL import Image

HAS_LATEX = False
_latex_ocr_cls = None
try:
    from pix2tex.cli import LatexOCR  # type: ignore[import-untyped]
    _latex_ocr_cls = LatexOCR
    HAS_LATEX = True
except ImportError:
    pass


class OcrEngine:
    _instance = None

    @classmethod
    def get_instance(cls) -> "OcrEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._lock = threading.Lock()
        self._ocr = ddddocr.DdddOcr(show_ad=False)
        self._latex_ocr = None
        if HAS_LATEX:
            try:
                self._latex_ocr = _latex_ocr_cls()
            except Exception as e:
                logging.warning("LaTeX OCR 初始化失败: %s", e)

    @property
    def has_latex(self) -> bool:
        return self._latex_ocr is not None

    def recognize_sync(self, img_bytes: bytes) -> str:
        with self._lock:
            return self._ocr.classification(img_bytes) or ""

    async def recognize(self, img_bytes: bytes, is_latex: bool = False) -> str:
        loop = asyncio.get_running_loop()
        if is_latex and self._latex_ocr:
            try:
                img = Image.open(BytesIO(img_bytes))
                result = await loop.run_in_executor(None, self._latex_ocr, img)
                if result:
                    return result
            except Exception:
                pass
        return await loop.run_in_executor(None, self.recognize_sync, img_bytes)
