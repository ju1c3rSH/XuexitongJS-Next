from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from qfluentwidgets import ScrollArea, PrimaryPushButton
from qfluentwidgets import SettingCardGroup, SwitchSettingCard
from qfluentwidgets import FluentIcon as FIF

from app import TaskManager


class ScriptPage(ScrollArea):
    def __init__(self, backend: TaskManager, parent=None):
        super().__init__(parent)
        self.backend = backend
        self._setup_ui()

    def _setup_ui(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(36, 20, 36, 20)
        layout.setSpacing(16)

        layout.addWidget(PrimaryPushButton(FIF.PLAY, "Launch Browser"))
        layout.addWidget(PrimaryPushButton(FIF.SEND, "Inject Script"))
        layout.addWidget(PrimaryPushButton(FIF.ZOOM, "Mouse Simulation"))

        group = SettingCardGroup("Behavior", view)
        group.addSettingCard(SwitchSettingCard(
            FIF.UPDATE, "Keep Login",
            "Restore cookies on startup"
        ))
        group.addSettingCard(SwitchSettingCard(
            FIF.SPEED_HIGH, "Force Speed",
            "Override video playback speed"
        ))
        layout.addWidget(group)
        layout.addStretch()

        self.setWidget(view)
        self.setWidgetResizable(True)
