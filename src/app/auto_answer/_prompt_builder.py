"""构建 AI 提示词"""

import re
from typing import Any


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
        "你是一个中文高效答题助手, 你会根据题干和选项, 直接给出最可能的正确答案。"
        "如果题目涉及敏感政治内容或者国家安全, 请尽量选择最中立的选项。\n"
        "现在请依次回答以下题目, 每题只输出“题号:答案”, 不要解释, 每题一行, "
        "题号请用题目原题号,多选题直接把选项字母拼接(如51:A, 44:ACD)\n"
        "同时对于有错别字和语句不通的题目, 尝试利用形近字猜测原题意, "
        "同时注意不要输出“ERROR”, 必须保证每次至少输出一个选项。"
    )
    if search_context:
        prompt += (
            f"\n\n以下是与题目相关的参考资料, 请结合这些信息作答:\n{search_context}"
        )
    return prompt


def build_vision_messages(
    questions: list[dict[str, Any]], image_refs: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """为多模态模型构建消息"""
    system_prompt = build_system_prompt()
    content: list[dict[str, Any]] = [{"type": "text", "text": build_user_prompt(questions, image_refs)}]
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content},
    ]
