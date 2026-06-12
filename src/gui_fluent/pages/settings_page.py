from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import ScrollArea, ComboBox, LineEdit
from qfluentwidgets import PrimaryPushButton, InfoBar
from qfluentwidgets import FluentIcon as FIF

from app import TaskManager
from app.utils import global_config, save_config


class SettingsPage(ScrollArea):
    def __init__(self, backend: TaskManager, parent=None):
        super().__init__(parent)
        self.backend = backend
        self._setup_ui()

    def _setup_ui(self):
        ac = global_config.get("auto_course", {})

        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(36, 20, 36, 20)
        layout.setSpacing(16)

        lbl1 = QLabel("Browser Engine")
        lbl1.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl1)
        self.browser = ComboBox()
        self.browser.addItems(["Auto", "Chrome", "Edge", "Firefox"])
        current = ac.get("browser", "Auto")
        if current:
            idx = max(0, ["Auto", "Chrome", "Edge", "Firefox"].index(current))
            self.browser.setCurrentIndex(idx)
        layout.addWidget(self.browser)

        lbl2 = QLabel("Home URL")
        lbl2.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl2)
        self.home_url = LineEdit()
        self.home_url.setText(ac.get("home_url", ""))
        layout.addWidget(self.home_url)

        lbl3 = QLabel("History URL")
        lbl3.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl3)
        self.history_url = LineEdit()
        self.history_url.setText(ac.get("history_url", ""))
        layout.addWidget(self.history_url)

        lbl4 = QLabel("HTTP Proxy")
        lbl4.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl4)
        self.proxy = LineEdit()
        self.proxy.setPlaceholderText("http://127.0.0.1:8080")
        layout.addWidget(self.proxy)

        btn = PrimaryPushButton(FIF.SAVE, "Save")
        btn.clicked.connect(self._on_save)
        layout.addWidget(btn)

        layout.addStretch()
        self.setWidget(view)
        self.setWidgetResizable(True)

    def _on_save(self):
        ac = global_config.setdefault("auto_course", {})
        ac["browser"] = self.browser.currentText()
        ac["home_url"] = self.home_url.text()
        ac["history_url"] = self.history_url.text()
        save_config()
        InfoBar.success("Saved", "Settings saved", parent=self)
