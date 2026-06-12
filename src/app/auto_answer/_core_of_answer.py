"""答题逻辑核心, 调用OpenAI接口获取答案"""

import json
import logging
import time
from pathlib import Path
from typing import Any

from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletionMessageParam

from ..utils import global_config
from ._prompt_builder import build_system_prompt, build_vision_messages, resolve_placeholders
from ._web_search import search_for_questions


def get_openai_client(config: dict[str, str]) -> tuple[OpenAI, str]:
    """获取OpenAI客户端和模型设置"""
    api_key: str = config.get("api_key", "")
    base_url: str = config.get("base_url", "")
    model: str = config.get("model", "")

    client: OpenAI = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )
    return client, model


def chat_with_openai(
    messages: list[ChatCompletionMessageParam], model: str | None = None
) -> str:
    """OpenAI交互接口"""

    client: OpenAI
    default_model: str
    client, default_model = get_openai_client(global_config.get("openai", {}))
    if model is None:
        model = default_model
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        timeout=40,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}},
        response_format={"type": "json_object"},
    )
    logging.info("Input Messages: %s", messages)
    logging.info("Reasoning Content: %s", completion.choices[0].message.reasoning_content)
    content = completion.choices[0].message.content
    if not content:
        raise ValueError("AI returned empty content")
    return content


def answer_questions_batch(
    questions: list[dict[str, str]],
    image_refs: list[dict[str, Any]] | None = None,
    retry: int = 3,
) -> str:
    """批量请求AI回答题目, 返回JSON字符串, 多次失败则返回默认答案A的JSON"""

    search_context: str = ""
    course_config = global_config.get("auto_course", {})
    if course_config.get("enable_search", True):
        max_results: int = course_config.get("search_max_results", 3)
        search_context = search_for_questions(questions, max_results)

    system_prompt: str = build_system_prompt(search_context)

    openai_config = global_config.get("openai", {})
    if openai_config.get("enable_vision", False) and bool(image_refs):
        messages = build_vision_messages(questions, image_refs)
    else:
        prompt: str = "".join(
            f"{idx}. 题干:{resolve_placeholders(q.get('题干',''), image_refs or [])}\n"
            f"选项:{[resolve_placeholders(o, image_refs or []) for o in q.get('选项',[])]}\n"
            for idx, q in enumerate(questions, 1)
        )
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

    for i in range(retry):
        logging.info("第 %d 次请求中...", i + 1)
        try:
            response = chat_with_openai(messages)
            data = json.loads(response)
            if not isinstance(data.get("answers"), list):
                raise ValueError("响应缺少 answers 数组")
            logging.info("批量请求成功")
            return response
        except (ConnectionError, OpenAIError, TimeoutError,
                json.JSONDecodeError, ValueError) as e:
            logging.warning("第 %d 次请求失败: %s", i + 1, e)

    logging.error("多次请求失败, 使用默认答案A")
    defaults = [
        {"question_id": str(q.get("题号", idx + 1)), "answer": "A"}
        for idx, q in enumerate(questions)
    ]
    return json.dumps({"answers": defaults}, ensure_ascii=False)


def answer_questions_file(
    input_json_path: Path,
    output_json_path: Path,
    image_refs: list[dict[str, Any]] | None = None,
    batch_size: int = 10,
) -> None:
    """从文件读取题目, 批量请求AI并写入带答案的json"""

    with input_json_path.open(encoding="utf-8") as f:
        questions: list[dict[str, str]] = json.load(f)

    for batch_start in range(0, len(questions), batch_size):
        batch: list[dict[str, str]] = questions[batch_start : batch_start + batch_size]
        logging.info(
            "正在批量回答第 %d~%d 题",
            batch_start + 1,
            min(batch_start + batch_size, len(questions)),
        )
        batch_answer: str = answer_questions_batch(batch, image_refs)
        logging.info("AI批量答案: %s", batch_answer)
        data = json.loads(batch_answer)
        q_map = {}
        for item in data.get("answers", []):
            q_map[str(item.get("question_id", ""))] = item.get("answer", "")
        for q in batch:
            q["AI答案"] = q_map.get(str(q.get("题号", "")), "ERROR")
        time.sleep(2)
    with output_json_path.open("w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=4)
    logging.info("已生成 %s", output_json_path)


def extract_simple_answers(input_json_path: Path, output_json_path: Path) -> None:
    """简化答案, 生成最终json"""
    with input_json_path.open(encoding="utf-8") as f:
        questions: list[dict[str, str]] = json.load(f)

    result: list[dict[str, str]] = [
        {"question_id": q["题号"], "answer": q.get("AI答案", "")}
        for q in questions
        if "AI答案" in q
    ]

    with output_json_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    logging.info("已生成 %s", output_json_path)
