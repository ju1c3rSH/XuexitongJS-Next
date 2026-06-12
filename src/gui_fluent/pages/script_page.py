from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import ScrollArea, PrimaryPushButton, InfoBar
from qfluentwidgets import SettingCardGroup, SwitchSettingCard
from qfluentwidgets import FluentIcon as FIF

from app import TaskManager


class ScriptPage(ScrollArea):
    def __init__(self, backend: TaskManager, parent=None):
        super().__init__(parent)
        self.backend = backend
        self._busy = False
        self._setup_ui()

    def _setup_ui(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(16)

        title = QLabel("Script")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(title)

        self.btn_launch = PrimaryPushButton(FIF.PLAY, "Launch Browser")
        self.btn_launch.setMinimumHeight(44)
        self.btn_launch.clicked.connect(self._on_launch)
        layout.addWidget(self.btn_launch)

        self.btn_inject = PrimaryPushButton(FIF.SEND, "Inject Script")
        self.btn_inject.setMinimumHeight(44)
        self.btn_inject.clicked.connect(self._on_inject)
        self.btn_inject.setEnabled(False)
        layout.addWidget(self.btn_inject)

        self.btn_mouse = PrimaryPushButton(FIF.ZOOM, "Start Mouse")
        self.btn_mouse.setMinimumHeight(44)
        self.btn_mouse.clicked.connect(self._on_mouse)
        self.btn_mouse.setEnabled(False)
        layout.addWidget(self.btn_mouse)

        group = SettingCardGroup("Behavior", view)
        self.sw_keep = SwitchSettingCard(
            FIF.UPDATE, "Keep Login",
            "Restore cookies on startup"
        )
        group.addSettingCard(self.sw_keep)

        self.sw_speed = SwitchSettingCard(
            FIF.SPEED_HIGH, "Force Speed",
            "Override playback rate"
        )
        group.addSettingCard(self.sw_speed)
        layout.addWidget(group)

        layout.addStretch()
        self.setWidget(view)
        self.setWidgetResizable(True)

    def _guard(self) -> bool:
        if self._busy:
            InfoBar.warning("Busy", "Task in progress", parent=self)
            return False
        return True

    def _on_launch(self):
        if not self._guard():
            return
        self._busy = True
        self.btn_launch.setEnabled(False)
        self.btn_launch.setText("Launching...")

        def done(jid, r):
            self._busy = False
            self.btn_launch.setEnabled(True)
            self.btn_launch.setText("Launch Browser")
            self.btn_inject.setEnabled(True)
            InfoBar.success("Done", "Browser launched", parent=self)
            self.backend.finished.disconnect(done)

        self.backend.finished.connect(done)
        self.backend.dispatch("launch_driver", [])

    def _on_inject(self):
        if not self._guard():
            return
        self._busy = True
        self.btn_inject.setEnabled(False)
        self.btn_inject.setText("Injecting...")

        def done(jid, r):
            self._busy = False
            self.btn_inject.setEnabled(True)
            self.btn_inject.setText("Inject Script")
            self.btn_mouse.setEnabled(True)
            InfoBar.success("Done", "Script injected", parent=self)
            self.backend.finished.disconnect(done)

        self.backend.finished.connect(done)
        self.backend.dispatch("launch_script", [])

    def _on_mouse(self):
        if not self._guard():
            return
        self.backend.dispatch("pretend_active", [])
        InfoBar.info("Active", "Mouse simulation started", parent=self)
