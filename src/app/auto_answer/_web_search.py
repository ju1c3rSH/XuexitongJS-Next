"""网络搜索模块, 为答题提供参考资料"""

import logging
import time

from ddgs import DDGS


def search_for_questions(questions: list[dict], max_results: int = 3) -> str:
    """为题目搜索相关参考资料, 返回格式化的搜索结果字符串"""

    all_results: list[str] = []
    seen: set[str] = set()

    for q in questions:
        query: str = q["题干"][:50]
        try:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=max_results)
                for r in results:
                    title: str = r.get("title", "")
                    body: str = r.get("body", "")
                    if title and title not in seen:
                        seen.add(title)
                        all_results.append(f"- {title}: {body}")
            time.sleep(1)
        except Exception as e:
            logging.warning("搜索失败: %s", e)
            continue

    logging.info("搜索完成, 共获取 %d 条参考资料", len(all_results))
    return "\n".join(all_results) if all_results else ""
