from PyQt5.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import ScrollArea, PrimaryPushButton, InfoBar
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

        self.btn_launch = PrimaryPushButton(FIF.PLAY, "Launch Browser")
        self.btn_launch.clicked.connect(self._on_launch)
        layout.addWidget(self.btn_launch)

        self.btn_inject = PrimaryPushButton(FIF.SEND, "Inject Script")
        self.btn_inject.clicked.connect(self._on_inject)
        layout.addWidget(self.btn_inject)

        self.btn_mouse = PrimaryPushButton(FIF.ZOOM, "Mouse Simulation")
        self.btn_mouse.clicked.connect(self._on_mouse)
        layout.addWidget(self.btn_mouse)

        group = SettingCardGroup("Behavior", view)
        group.addSettingCard(SwitchSettingCard(
            FIF.UPDATE, "Keep Login", "Restore cookies on startup"))
        group.addSettingCard(SwitchSettingCard(
            FIF.SPEED_HIGH, "Force Speed", "Override video playback speed"))
        layout.addWidget(group)

        layout.addStretch()
        self.setWidget(view)
        self.setWidgetResizable(True)

    def _on_launch(self):
        jid = self.backend.dispatch("launch_driver", [])
        self.backend.finished.connect(lambda jid2, r:
            InfoBar.success("Done", "Browser launched", parent=self) if jid == jid2 else None)

    def _on_inject(self):
        self.backend.dispatch("launch_script", [])

    def _on_mouse(self):
        self.backend.dispatch("pretend_active", [])
