import logging
from dataclasses import dataclass
from typing import Any


@dataclass
class AIConfig:
    temperature: float = 0.7
    max_tokens: int = 4096
    enable_thinking: bool = True

    def __post_init__(self):
        if not (0 <= self.temperature <= 2):
            logging.warning("temperature=%s 超出 [0,2], 使用默认值 0.7", self.temperature)
            self.temperature = 0.7
        if self.max_tokens < 128:
            logging.warning("max_tokens=%d < 128, 使用默认值 4096", self.max_tokens)
            self.max_tokens = 4096

    def get_api_temperature(self) -> float | None:
        """开启 thinking 时返回 None（API 忽略 temperature）"""
        return None if self.enable_thinking else self.temperature

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "AIConfig":
        return cls(
            temperature=d.get("temperature", 0.7),
            max_tokens=d.get("max_tokens", 4096),
            enable_thinking=d.get("enable_thinking", True),
        )
