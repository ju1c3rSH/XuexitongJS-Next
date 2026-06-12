from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import ScrollArea, LineEdit, PasswordLineEdit
from qfluentwidgets import SettingCardGroup, SettingCard, SwitchSettingCard

from app import TaskManager


class ApiPage(ScrollArea):
    def __init__(self, backend: TaskManager, parent=None):
        super().__init__(parent)
        self.backend = backend
        self._setup_ui()

    def _setup_ui(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(36, 20, 36, 20)
        layout.setSpacing(16)

        title = QLabel("API Configuration")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        label = QLabel("API Key, Base URL and Model settings")
        label.setStyleSheet("color: #888;")
        layout.addWidget(label)

        layout.addStretch()
        self.setWidget(view)
        self.setWidgetResizable(True)
