"""图片下载、OCR 识别、回嵌 HTML"""

import asyncio
import base64
import logging
from pathlib import Path
from typing import Any

import aiohttp
from bs4 import BeautifulSoup
from bs4.element import Tag

from ._ocr_engine import OcrEngine


class ImageProcessor:
    def __init__(self, save_dir: Path):
        self._save_dir = save_dir
        self._save_dir.mkdir(parents=True, exist_ok=True)
        self._semaphore = asyncio.Semaphore(5)
        self._engine = OcrEngine.get_instance()

    async def process(self, raw_html: str) -> tuple[str, list[dict[str, Any]]]:
        """返回 (处理后的HTML, ImageRef列表)"""
        soup = BeautifulSoup(raw_html, "html.parser")
        img_tags = soup.find_all("img")
        if not img_tags:
            return raw_html, []

        seen: dict[str, int] = {}
        refs: list[dict[str, Any]] = []

        for tag in img_tags:
            src = tag.get("src", "")
            if not src:
                continue
            if src in seen:
                tag.replace_with(f"[图片#{seen[src]}]")
                continue
            idx = len(refs)
            seen[src] = idx
            tag.replace_with(f"[图片#{idx}]")
            refs.append({
                "index": idx,
                "url": src,
                "local_path": "",
                "ocr_text": "",
                "is_latex": "/ananas/latex/" in src
                    or (isinstance(tag, Tag) and "ans-formula-moudle" in tag.get("class", [])),
            })

        async with aiohttp.ClientSession() as session:
            tasks = [self._process_one(ref, session) for ref in refs]
            await asyncio.gather(*tasks, return_exceptions=True)

        return str(soup), refs

    async def _process_one(
        self, ref: dict[str, Any], session: aiohttp.ClientSession
    ) -> None:
        try:
            async with self._semaphore:
                img_bytes = await self._download(ref["url"], session)
                if img_bytes is None:
                    return
                file_name = f"img_{ref['index']}.png"
                file_path = self._save_dir / file_name
                file_path.write_bytes(img_bytes)
                ref["local_path"] = str(file_path)
                ref["ocr_text"] = await self._engine.recognize(
                    img_bytes, ref["is_latex"]
                )
        except Exception as e:
            logging.warning("图片 %d 处理失败: %s", ref["index"], e)

    async def _download(
        self, url: str, session: aiohttp.ClientSession
    ) -> bytes | None:
        if url.startswith("data:image"):
            try:
                return base64.b64decode(url.split(",", 1)[1])
            except Exception:
                return None
        url = self._normalize_url(url)
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(10)) as resp:
                return await resp.read()
        except Exception:
            return None

    @staticmethod
    def _normalize_url(url: str) -> str:
        if url.startswith("//"):
            return "https:" + url
        if url.startswith("/ananas/"):
            return "https://mooc1.chaoxing.com" + url
        return url
