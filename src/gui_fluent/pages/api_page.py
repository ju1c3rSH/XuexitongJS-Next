from PyQt5.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import ScrollArea, LineEdit, PasswordLineEdit
from qfluentwidgets import SwitchSettingCard
from qfluentwidgets import PrimaryPushButton, InfoBar
from qfluentwidgets import FluentIcon as FIF

from app import TaskManager
from app.utils import global_config, save_config


class ApiPage(ScrollArea):
    def __init__(self, backend: TaskManager, parent=None):
        super().__init__(parent)
        self.backend = backend
        self._setup_ui()

    def _setup_ui(self):
        oa = global_config.get("openai", {})

        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(36, 20, 36, 20)
        layout.setSpacing(16)

        self.api_key = PasswordLineEdit()
        self.api_key.setText(oa.get("api_key", ""))
        self.api_key.setPlaceholderText("sk-...")

        self.base_url = LineEdit()
        self.base_url.setText(oa.get("base_url", "https://api.moonshot.cn/v1"))

        self.model = LineEdit()
        self.model.setText(oa.get("model", "kimi-k2-0905-preview"))

        self.vision = SwitchSettingCard(
            FIF.VIEW, "Enable Vision",
            "Send images to multi-modal models"
        )
        self.vision.setChecked(oa.get("enable_vision", False))

        layout.addWidget(self.api_key)
        layout.addWidget(self.base_url)
        layout.addWidget(self.model)
        layout.addWidget(self.vision)

        btn = PrimaryPushButton(FIF.SAVE, "Save")
        btn.clicked.connect(self._on_save)
        layout.addWidget(btn)

        layout.addStretch()
        self.setWidget(view)
        self.setWidgetResizable(True)

    def _on_save(self):
        oa = global_config.setdefault("openai", {})
        oa["api_key"] = self.api_key.text()
        oa["base_url"] = self.base_url.text()
        oa["model"] = self.model.text()
        oa["enable_vision"] = self.vision.isChecked()
        save_config()
        InfoBar.success("Saved", "API config saved", parent=self)
