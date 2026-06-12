import logging
from dataclasses import dataclass
from typing import Any


@dataclass
class BehaviorConfig:
    poll_interval_ms: int = 100
    poll_max_retry: int = 50

    def __post_init__(self):
        if self.poll_interval_ms < 10:
            logging.warning("poll_interval_ms=%d < 10, 使用默认值 100", self.poll_interval_ms)
            self.poll_interval_ms = 10
        if self.poll_max_retry < 1:
            logging.warning("poll_max_retry=%d < 1, 使用默认值 50", self.poll_max_retry)
            self.poll_max_retry = 50

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "BehaviorConfig":
        return cls(
            poll_interval_ms=d.get("poll_interval_ms", 100),
            poll_max_retry=d.get("poll_max_retry", 50),
        )
