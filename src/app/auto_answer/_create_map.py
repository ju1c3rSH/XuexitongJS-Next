"""生成字体映射的工具, 通过 OCR 识别字形"""
# pyright: reportAttributeAccessIssue=false
import concurrent.futures
import io
import json
import logging
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from ._ocr_engine import OcrEngine


def glyph_to_img(ttf_path: Path, char, size=256):
    """将单个字形渲染为图像"""
    font = ImageFont.truetype(ttf_path, size)
    bbox = font.getbbox(char)
    if bbox:
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        img_size = max(width, height) + 20
    else:
        img_size = size
    img = Image.new('L', (img_size, img_size), 255)
    draw = ImageDraw.Draw(img)
    draw.text(((img_size - width) // 2 - bbox[0] if bbox else 0,
               (img_size - height) // 2 - bbox[1] if bbox else 0),
              char, font=font, fill=0)
    return img


def ocr_recognize(img: Image.Image) -> str | None:
    """OCR 识别单个字符图像"""
    engine = OcrEngine.get_instance()
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    text = engine.recognize_sync(buf.getvalue())
    if text and len(text) >= 1:
        return text[0]
    return None


def enc_worker(enc_code: int, enc_font_path: Path) -> tuple[str, str] | None:
    """通过 OCR 识别加密字体字形对应的真正字符"""
    enc_char = chr(enc_code)
    img = glyph_to_img(enc_font_path, enc_char)
    recognized = ocr_recognize(img)
    if recognized is not None:
        return (enc_char, recognized)
    return None


def create_font_mapping(
    enc_font_path: Path,
    std_font_path: Path,  # noqa: ARG001 — 保留以维持 API 兼容
    output_json: Path,
) -> dict[str, str]:
    """生成加密字体到真实字符的映射 (基于 OCR 识别)"""
    enc_font: TTFont = TTFont(enc_font_path)
    enc_cmap = enc_font["cmap"].getBestCmap()
    OcrEngine.get_instance()

    mapping: dict[str, str] = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(enc_worker, enc_code, enc_font_path): enc_code
            for enc_code in enc_cmap
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                mapping[result[0]] = result[1]

    logging.info("字体映射完成: 共 %d 个字形, 成功映射 %d 个", len(enc_cmap), len(mapping))

    if output_json:
        with output_json.open("w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        logging.info("映射已保存到 %s", output_json)
    return mapping
