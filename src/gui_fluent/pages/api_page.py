from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import ScrollArea, LineEdit, PasswordLineEdit
from qfluentwidgets import SwitchSettingCard
from qfluentwidgets import PrimaryPushButton, InfoBar
from qfluentwidgets import FluentIcon as FIF

from app import TaskManager
from app.utils import global_config, save_config
from ..i18n import tr


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

        self.title = QLabel(tr("API"))
        self.title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(self.title)

        self.lbl_key = QLabel(tr("API Key"))
        self.lbl_key.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.lbl_key)
        self.api_key = PasswordLineEdit()
        self.api_key.setText(oa.get("api_key", ""))
        self.api_key.setPlaceholderText("sk-...")
        layout.addWidget(self.api_key)

        self.lbl_url = QLabel(tr("Base URL"))
        self.lbl_url.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.lbl_url)
        self.base_url = LineEdit()
        self.base_url.setText(oa.get("base_url", "https://api.moonshot.cn/v1"))
        layout.addWidget(self.base_url)

        self.lbl_model = QLabel(tr("Model"))
        self.lbl_model.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.lbl_model)
        self.model = LineEdit()
        self.model.setText(oa.get("model", "kimi-k2-0905-preview"))
        layout.addWidget(self.model)

        self.vision = SwitchSettingCard(
            FIF.VIEW, tr("Vision"),
            tr("Enable multi-modal image input")
        )
        self.vision.setChecked(oa.get("enable_vision", False))
        layout.addWidget(self.vision)

        self.btn = PrimaryPushButton(FIF.SAVE, tr("Save"))
        self.btn.setMinimumHeight(40)
        self.btn.clicked.connect(self._on_save)
        layout.addWidget(self.btn)

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
        InfoBar.success(tr("Saved"), tr("API config saved"), parent=self)

    def retranslate(self):
        self.title.setText(tr("API"))
        self.lbl_key.setText(tr("API Key"))
        self.lbl_url.setText(tr("Base URL"))
        self.lbl_model.setText(tr("Model"))
        self.vision.setTitle(tr("Vision"))
        self.vision.setContent(tr("Enable multi-modal image input"))
        self.btn.setText(tr("Save"))
