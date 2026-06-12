from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel
from qfluentwidgets import ScrollArea, ComboBox, LineEdit

from app import TaskManager


class SettingsPage(ScrollArea):
    def __init__(self, backend: TaskManager, parent=None):
        super().__init__(parent)
        self.backend = backend
        self._setup_ui()

    def _setup_ui(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(36, 20, 36, 20)
        layout.setSpacing(16)

        lbl = QLabel("Browser Engine")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl)
        cb = ComboBox()
        cb.addItems(["Auto", "Chrome", "Edge", "Firefox"])
        layout.addWidget(cb)

        lbl2 = QLabel("HTTP Proxy")
        lbl2.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl2)
        le = LineEdit()
        le.setPlaceholderText("Optional: http://127.0.0.1:8080")
        layout.addWidget(le)

        layout.addStretch()
        self.setWidget(view)
        self.setWidgetResizable(True)
