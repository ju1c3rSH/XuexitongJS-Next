from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import ScrollArea, ComboBox, LineEdit
from qfluentwidgets import PrimaryPushButton, InfoBar
from qfluentwidgets import FluentIcon as FIF

from app import TaskManager
from app.utils import global_config, save_config
from ..i18n import tr, set_language


class SettingsPage(ScrollArea):
    def __init__(self, backend: TaskManager, parent=None):
        super().__init__(parent)
        self.backend = backend
        self._setup_ui()

    def _setup_ui(self):
        ac = global_config.get("auto_course", {})

        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(16)

        self.title = QLabel(tr("Settings"))
        self.title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(self.title)

        self.lbl1 = QLabel(tr("Browser Engine"))
        self.lbl1.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.lbl1)
        self.browser = ComboBox()
        self.browser.addItems(["Auto", "Chrome", "Edge", "Firefox"])
        current = ac.get("browser", "")
        idx = max(0, ["Auto", "Chrome", "Edge", "Firefox"].index(current)) if current in ["Auto", "Chrome", "Edge", "Firefox"] else 0
        self.browser.setCurrentIndex(idx)
        layout.addWidget(self.browser)

        self.lbl_lang = QLabel(tr("Language"))
        self.lbl_lang.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.lbl_lang)
        self.lang = ComboBox()
        self.lang.addItems(["English", "中文"])
        ui_cfg = global_config.get("ui", {})
        cur_lang = ui_cfg.get("language", "en")
        self.lang.setCurrentIndex(0 if cur_lang == "en" else 1)
        self.lang.currentIndexChanged.connect(self._on_language_changed)
        layout.addWidget(self.lang)

        self.lbl2 = QLabel(tr("Home URL"))
        self.lbl2.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.lbl2)
        self.home_url = LineEdit()
        self.home_url.setText(ac.get("home_url", ""))
        layout.addWidget(self.home_url)

        self.lbl3 = QLabel(tr("History URL"))
        self.lbl3.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.lbl3)
        self.history_url = LineEdit()
        self.history_url.setText(ac.get("history_url", ""))
        layout.addWidget(self.history_url)

        self.lbl4 = QLabel(tr("HTTP Proxy"))
        self.lbl4.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.lbl4)
        self.proxy = LineEdit()
        self.proxy.setPlaceholderText("http://127.0.0.1:8080")
        layout.addWidget(self.proxy)

        self.btn = PrimaryPushButton(FIF.SAVE, tr("Save"))
        self.btn.setMinimumHeight(40)
        self.btn.clicked.connect(self._on_save)
        layout.addWidget(self.btn)

        layout.addStretch()
        self.setWidget(view)
        self.setWidgetResizable(True)

    def _on_save(self):
        ac = global_config.setdefault("auto_course", {})
        ac["browser"] = self.browser.currentText()
        ac["home_url"] = self.home_url.text()
        ac["history_url"] = self.history_url.text()
        save_config()
        InfoBar.success(tr("Saved"), tr("Settings saved"), parent=self)

    def _on_language_changed(self, idx: int):
        lang = "en" if idx == 0 else "zh"
        ui = global_config.setdefault("ui", {})
        ui["language"] = lang
        save_config()
        set_language(lang)

    def retranslate(self):
        self.title.setText(tr("Settings"))
        self.lbl1.setText(tr("Browser Engine"))
        self.lbl_lang.setText(tr("Language"))
        self.lbl2.setText(tr("Home URL"))
        self.lbl3.setText(tr("History URL"))
        self.lbl4.setText(tr("HTTP Proxy"))
        self.btn.setText(tr("Save"))
