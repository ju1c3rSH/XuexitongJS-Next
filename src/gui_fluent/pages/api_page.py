from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
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
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(16)

        title = QLabel("API 配置")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(title)

        lbl_key = QLabel("API Key")
        lbl_key.setStyleSheet("font-size: 14px;")
        layout.addWidget(lbl_key)
        self.api_key = PasswordLineEdit()
        self.api_key.setText(oa.get("api_key", ""))
        self.api_key.setPlaceholderText("sk-...")
        layout.addWidget(self.api_key)

        lbl_url = QLabel("Base URL")
        lbl_url.setStyleSheet("font-size: 14px;")
        layout.addWidget(lbl_url)
        self.base_url = LineEdit()
        self.base_url.setText(oa.get("base_url", "https://api.moonshot.cn/v1"))
        layout.addWidget(self.base_url)

        lbl_model = QLabel("Model")
        lbl_model.setStyleSheet("font-size: 14px;")
        layout.addWidget(lbl_model)
        self.model = LineEdit()
        self.model.setText(oa.get("model", "kimi-k2-0905-preview"))
        layout.addWidget(self.model)

        self.vision = SwitchSettingCard(
            FIF.VIEW, "多模态视觉", "向多模态模型发送图片"
        )
        self.vision.setChecked(oa.get("enable_vision", False))
        layout.addWidget(self.vision)

        btn = PrimaryPushButton(FIF.SAVE, "保存")
        btn.setMinimumHeight(40)
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
        InfoBar.success("已保存", "API 配置已保存", parent=self)
