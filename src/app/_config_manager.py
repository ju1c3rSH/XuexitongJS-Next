"""配置读写模块"""
import logging
from typing import Any

from .utils import global_config, save_config


class Configuration:
    """全局配置读写类"""

    def set_config(self, keys: list[str], value: Any):
        """设置配置"""
        NUMERIC_KEYS = {
            "batch_size", "retry_count", "api_timeout",
            "poll_interval_ms", "poll_max_retry", "speed",
            "temperature", "max_tokens",
        }
        key_str = '.'.join(keys)
        if keys[-1] in NUMERIC_KEYS and not isinstance(value, (int, float)):
            try:
                value = float(value) if '.' in str(value) else int(value)
            except (ValueError, TypeError):
                logging.error("[%s]应为数值，收到: %s (%s)", key_str, value, type(value).__name__)
                return

        tmp: dict = global_config
        for key in keys[:-1]:
            if key not in tmp or not isinstance(tmp[key], dict):
                tmp[key] = {}
            tmp = tmp[key]
        if keys[-1] in tmp and not isinstance(tmp[keys[-1]], value.__class__):
            logging.warning(
                "[%s]出现类型变化: %s -> %s",
                '.'.join(keys),
                tmp[keys[-1]].__class__.__name__,
                value.__class__.__name__
            )
        tmp[keys[-1]] = value

    def get_config(self, *keys: str) -> Any:
        """获取配置"""
        tmp: dict | Any = global_config
        for key in keys:
            if isinstance(tmp, dict) and key in tmp:
                tmp = tmp[key]
            else:
                logging.warning("[%s]不在配置字典中", '.'.join(keys))
                return ""

        logging.info("成功获取[%s]: %s (%s)", '.'.join(keys), tmp, tmp.__class__.__name__)
        return tmp

    def commit_config(self):
        """提交配置至配置文件"""
        save_config()
