"""配置提供者 — 从 global_config 读取并构建类型化配置对象

所有 dataclass 不直接依赖 global_config，通过 from_dict(dict) 注入。
ConfigProvider 负责桥接 global_config 与类型安全配置。
配置为热更新：每次调用都从 global_config 最新值重新构建。
"""

from app.utils import global_config

from ._quiz_config import QuizConfig
from ._ai_config import AIConfig
from ._behavior_config import BehaviorConfig

__all__ = ["ConfigProvider", "QuizConfig", "AIConfig", "BehaviorConfig"]


class ConfigProvider:

    @staticmethod
    def get_quiz() -> QuizConfig:
        return QuizConfig.from_dict(global_config.get("quiz", {}))

    @staticmethod
    def get_ai() -> AIConfig:
        return AIConfig.from_dict(global_config.get("openai", {}))

    @staticmethod
    def get_behavior() -> BehaviorConfig:
        return BehaviorConfig.from_dict(global_config.get("auto_course", {}))
