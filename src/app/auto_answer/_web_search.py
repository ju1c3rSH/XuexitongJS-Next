"""网络搜索模块, 为答题提供参考资料"""

import logging
import time

import httpx
from bs4 import BeautifulSoup, Comment
from ddgs import DDGS


def _fetch_page_content(url: str, max_length: int = 2000) -> str:
    """抓取URL页面并提取正文文本, 失败时返回空字符串"""
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup.find_all(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()
        text = soup.get_text(separator="\n", strip=True)
        return text[:max_length] if text else ""
    except Exception:
        return ""


def search_for_questions(questions: list[dict], max_results: int = 10) -> str:
    """为题目搜索相关参考资料, 返回格式化的搜索结果字符串"""

    all_results: list[str] = []
    seen: set[str] = set()

    for q in questions:
        query: str = q["题干"][:100]
        try:
            with DDGS() as ddgs:
                results = ddgs.text(
                    query,
                    max_results=max_results,
                    safesearch="on",
                    backend="google,duckduckgo",
                    region="zh-cn",
                )
                for r in results:
                    title: str = r.get("title", "")
                    body: str = r.get("body", "")
                    href: str = r.get("href", "")
                    if title and title not in seen:
                        seen.add(title)
                        content = _fetch_page_content(href) if href else ""
                        if content:
                            logging.info("搜索到结果(已抓取): **%s** (%d字)", title, len(content))
                            all_results.append(f"- **{title}**: {content}")
                        else:
                            logging.info("搜索到结果(摘要): **%s**: %s", title, body)
                            all_results.append(f"- **{title}**: {body}\n  (来源: {href})")
            time.sleep(1)
        except Exception as e:
            logging.warning("搜索失败: %s", e)
            continue

    logging.info("搜索完成, 共获取 %d 条参考资料", len(all_results))
    return "\n".join(all_results) if all_results else ""
