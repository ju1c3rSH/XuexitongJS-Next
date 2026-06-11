"""构建 AI 提示词"""

import base64
import mimetypes
import re
from io import BytesIO
from typing import Any

from PIL import Image


def resolve_placeholders(text: str, image_refs: list[dict[str, Any]]) -> str:
    """将文本中的 [图片#N] 替换为 OCR 识别结果或原标记"""
    def repl(m: re.Match) -> str:
        idx = int(m.group(1))
        if idx < len(image_refs):
            ref = image_refs[idx]
            ocr = ref.get("ocr_text", "")
            if ocr:
                return f"[{ocr}]"
        return m.group(0)
    return re.sub(r"\[图片#(\d+)\]", repl, text)


def build_user_prompt(
    questions: list[dict[str, Any]], image_refs: list[dict[str, Any]]
) -> str:
    lines: list[str] = []
    for idx, q in enumerate(questions, 1):
        stem = resolve_placeholders(q.get("题干", ""), image_refs)
        opts = [
            resolve_placeholders(o, image_refs) for o in q.get("选项", [])
        ]
        lines.append(f"{idx}. 题干:{stem}\n选项:{opts}\n")
    return "".join(lines)


def build_system_prompt(search_context: str = "") -> str:
    prompt = (
        "## Role\n"
        "You are a professional exam assistant. Reason step by step internally, "
        "then output the final answer.\n\n"
        "## Internal Reasoning (invisible, for analysis only)\n"
        "For each question:\n"
        "1. Identify type: single-choice / multi-choice / true-false.\n"
        "2. Restore garbled text from font obfuscation before reasoning.\n"
        "3. Analyze each option independently — why correct or wrong.\n"
        "4. Cross-check for contradictions.\n"
        "5. If uncertain, use elimination; never skip.\n"
        "6. Verify answer fits the question type.\n\n"
        "## Output Format\n"
        "Output ONLY valid JSON (no markdown fences, no extra text):\n\n"
        '{"answers": [{"question_id": "1", "answer": "A"}, '
        '{"question_id": "2", "answer": "ACD"}]}\n\n'
        "- question_id: original question number (string)\n"
        "- Single-choice: single letter e.g. \"A\"\n"
        "- Multi-choice: concatenated letters e.g. \"ACD\"\n"
        "- True/False: \"对\" or \"错\"\n"
    )
    if search_context:
        prompt += f"\n\nReference materials:\n{search_context}"
    return prompt


def _extract_indices(text: str) -> set[int]:
    return {int(m.group(1)) for m in re.finditer(r"\[图片#(\d+)\]", text)}


def _load_image_b64(path: str, max_dim: int = 1024) -> str | None:
    try:
        img = Image.open(path)
        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            img = img.resize(
                (int(img.width * ratio), int(img.height * ratio))
            )
        mime, _ = mimetypes.guess_type(path)
        if mime is None:
            mime = "image/png"
        buf = BytesIO()
        img.save(buf, format=img.format or "PNG")
        return f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def build_vision_messages(
    questions: list[dict[str, Any]], image_refs: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """为多模态模型构建消息（按题干→图片→选项→图片 的顺序交错排列）"""
    content: list[dict[str, Any]] = []
    for idx, q in enumerate(questions, 1):
        stem = q.get("题干", "")
        opts = q.get("选项", [])

        stem_resolved = resolve_placeholders(stem, image_refs)
        content.append({"type": "text", "text": f"{idx}. 题干:{stem_resolved}"})
        for n in sorted(_extract_indices(stem)):
            if n < len(image_refs):
                b64 = _load_image_b64(image_refs[n].get("local_path", ""))
                if b64:
                    content.append({"type": "image_url", "image_url": {"url": b64}})

        for oi, opt in enumerate(opts):
            opt_resolved = resolve_placeholders(opt, image_refs)
            label = chr(65 + oi)
            content.append({"type": "text", "text": f"选项{label}: {opt_resolved}"})
            for n in sorted(_extract_indices(opt)):
                if n < len(image_refs):
                    b64 = _load_image_b64(image_refs[n].get("local_path", ""))
                    if b64:
                        content.append({"type": "image_url", "image_url": {"url": b64}})

    return [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": content},
    ]
