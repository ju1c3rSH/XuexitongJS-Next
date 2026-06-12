"""轻量级 i18n 支持

提供 tr(key) 函数用于所有页面取翻译文本。
语言切换通过 LanguageManager 信号广播到所有子页面。
"""

import json
import os
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal


class _LanguageManager(QObject):
    languageChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._data: dict[str, dict[str, str]] = {}
        self._current: str = "en"
        self._load()

    def tr(self, key: str) -> str:
        entry = self._data.get(key)
        if entry is None:
            return key
        return entry.get(self._current, key)

    def set_language(self, lang: str):
        if lang == self._current:
            return
        self._current = lang
        self.languageChanged.emit(lang)

    @property
    def current(self) -> str:
        return self._current

    def _load(self):
        path = Path(os.path.dirname(__file__)) / "translations.json"
        if path.exists():
            with path.open(encoding="utf-8") as f:
                self._data = json.load(f)


_manager = _LanguageManager()


def tr(key: str) -> str:
    return _manager.tr(key)


def set_language(lang: str):
    _manager.set_language(lang)


def current_language() -> str:
    return _manager.current
