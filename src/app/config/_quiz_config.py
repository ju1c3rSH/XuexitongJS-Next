import logging
from dataclasses import dataclass
from typing import Any


@dataclass
class QuizConfig:
    batch_size: int = 10
    retry_count: int = 3
    api_timeout: int = 120

    def __post_init__(self):
        if self.batch_size < 1:
            logging.warning("batch_size=%d < 1, 使用默认值 10", self.batch_size)
            self.batch_size = 10
        if self.retry_count < 0:
            logging.warning("retry_count=%d < 0, 使用默认值 3", self.retry_count)
            self.retry_count = 3
        if self.api_timeout < 5:
            logging.warning("api_timeout=%d < 5, 使用默认值 120", self.api_timeout)
            self.api_timeout = 120

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "QuizConfig":
        return cls(
            batch_size=d.get("batch_size", 10),
            retry_count=d.get("retry_count", 3),
            api_timeout=d.get("api_timeout", 120),
        )
