"""自动化答题模块"""

__all__ = ["answer_questions"]

import json
import logging
from pathlib import Path

import aiofiles

from ..config import ConfigProvider
from ..utils import get_path_config as get_path
from ._core_of_answer import answer_questions_file, extract_simple_answers
from ._create_map import create_font_mapping
from ._depry_question import decode_questions
from ._extract_html import extract_font_from_html, extract_questions_from_html
from ._image_processor import ImageProcessor


async def answer_questions() -> None:
    """答题完整流程"""
    std_font_path: Path = get_path(True, "std_font")

    html_path: Path = get_path(False, "original_questions")
    ttf_path: Path = get_path(False, "obf_font")
    mapping_json_path: Path = get_path(False, "obf_mapping")
    questions_path: Path = get_path(False, "questions")
    decoded_json_path: Path = get_path(False, "decoded")
    answered_json_path: Path = get_path(False, "qa_pairs")
    simplified_json_path: Path = get_path(False, "answers")

    async with aiofiles.open(html_path, encoding="utf-8") as f:
        raw: str = await f.read()

    img_save_dir: Path = get_path(False, "question_images")

    if raw.strip().startswith("{"):
        quiz_data: dict = json.loads(raw)
        font_base64: str = quiz_data.get("fontBase64", "")
        if font_base64:
            ttf_path.write_bytes(base64.b64decode(font_base64))
            logging.info("font-cxsecret 已从 quizData 解码")
        else:
            extract_font_from_html(raw, ttf_path)

        img_html = "<html><body>"
        for img in quiz_data.get("images", []):
            img_html += f'<img src="{img["src"]}">'
        img_html += "</body></html>"
        processor = ImageProcessor(img_save_dir)
        _, image_refs = await processor.process(img_html)

        questions = []
        for q in quiz_data.get("questions", []):
            questions.append({
                "题号": q.get("num", ""),
                "题型": q.get("type", ""),
                "题干": q.get("stem", ""),
                "选项": q.get("options", []),
            })
        async with aiofiles.open(questions_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(questions, ensure_ascii=False, indent=2))
        logging.info("题目已保存到 %s, 共 %d 题",
                     questions_path, len(questions))
    else:
        extract_font_from_html(raw, ttf_path)
        processor = ImageProcessor(img_save_dir)
        processed_html, image_refs = await processor.process(raw)
        questions = extract_questions_from_html(processed_html)
        async with aiofiles.open(questions_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(questions, ensure_ascii=False, indent=2))
        logging.info("题目已保存到 %s, 共 %d 题",
                     questions_path, len(questions))
    create_font_mapping(ttf_path, std_font_path, mapping_json_path)
    decode_questions(questions_path, decoded_json_path, mapping_json_path)

    quiz_cfg = ConfigProvider.get_quiz()
    ai_cfg = ConfigProvider.get_ai()
    answer_questions_file(decoded_json_path, answered_json_path, image_refs,
                          quiz_cfg=quiz_cfg, ai_cfg=ai_cfg)
    extract_simple_answers(answered_json_path, simplified_json_path)
