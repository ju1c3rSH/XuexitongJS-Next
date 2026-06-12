from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit
from qfluentwidgets import ScrollArea, PrimaryPushButton, InfoBar
from qfluentwidgets import SettingCardGroup, SwitchSettingCard
from qfluentwidgets import FluentIcon as FIF

from app import TaskManager
from app.utils import global_config, save_config
from ..i18n import tr
from ..widgets.log_handler import LogSignal, LogHandler
import logging


class ScriptPage(ScrollArea):
    def __init__(self, backend: TaskManager, parent=None):
        super().__init__(parent)
        self.backend = backend
        self._busy = False
        self._setup_ui()

        self._log_signal = LogSignal()
        self._log_signal.message.connect(self._append_log)

        log_fmt = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'
        )
        self._log_handler = LogHandler(self._log_signal)
        self._log_handler.setFormatter(log_fmt)
        logging.getLogger().addHandler(self._log_handler)

    def _setup_ui(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(16)

        self.title = QLabel(tr("Script"))
        self.title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(self.title)

        self.btn_launch = PrimaryPushButton(FIF.PLAY, tr("Launch Browser"))
        self.btn_launch.setMinimumHeight(44)
        self.btn_launch.clicked.connect(self._on_launch)
        layout.addWidget(self.btn_launch)

        self.btn_inject = PrimaryPushButton(FIF.SEND, tr("Inject Script"))
        self.btn_inject.setMinimumHeight(44)
        self.btn_inject.clicked.connect(self._on_inject)
        self.btn_inject.setEnabled(False)
        layout.addWidget(self.btn_inject)

        self.btn_mouse = PrimaryPushButton(FIF.ZOOM, tr("Start Mouse"))
        self.btn_mouse.setMinimumHeight(44)
        self.btn_mouse.clicked.connect(self._on_mouse)
        self.btn_mouse.setEnabled(False)
        layout.addWidget(self.btn_mouse)

        self.group = SettingCardGroup(tr("Behavior"), view)

        ac = global_config.get("auto_course", {})
        self.sw_keep = SwitchSettingCard(
            FIF.UPDATE, tr("Keep Login"),
            tr("Restore cookies on startup")
        )
        self.sw_keep.setChecked(ac.get("restore_cookies", True))
        self.sw_keep.checkedChanged.connect(self._auto_save)
        self.group.addSettingCard(self.sw_keep)

        self.sw_speed = SwitchSettingCard(
            FIF.SPEED_HIGH, tr("Force Speed"),
            tr("Override playback rate")
        )
        self.sw_speed.setChecked(ac.get("force_speed", False))
        self.sw_speed.checkedChanged.connect(self._auto_save)
        self.group.addSettingCard(self.sw_speed)
        layout.addWidget(self.group)

        # --- Logcat ---
        lbl_log = QLabel(tr("Logcat"))
        lbl_log.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 12px;")
        layout.addWidget(lbl_log)

        self._log_view = QPlainTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setMaximumBlockCount(2000)
        self._log_view.setMinimumHeight(160)
        self._log_view.setStyleSheet(
            "font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace; font-size: 12px;"
        )
        layout.addWidget(self._log_view, stretch=1)
        self.setWidget(view)
        self.setWidgetResizable(True)

    def _guard(self) -> bool:
        if self._busy:
            InfoBar.warning(tr("Busy"), tr("Task in progress"), parent=self)
            return False
        return True

    def _on_launch(self):
        if not self._guard():
            return
        self._busy = True
        self.btn_launch.setEnabled(False)
        self.btn_launch.setText(tr("Launching..."))

        def done(jid, r):
            self._busy = False
            self.btn_launch.setEnabled(True)
            self.btn_launch.setText(tr("Launch Browser"))
            self.btn_inject.setEnabled(True)
            InfoBar.success(tr("Done"), tr("Browser launched"), parent=self)
            self.backend.finished.disconnect(done)

        self.backend.finished.connect(done)
        self.backend.dispatch("launch_driver", [])

    def _on_inject(self):
        if not self._guard():
            return
        self._busy = True
        self.btn_inject.setEnabled(False)
        self.btn_inject.setText(tr("Injecting..."))

        def done(jid, r):
            self._busy = False
            self.btn_inject.setEnabled(True)
            self.btn_inject.setText(tr("Inject Script"))
            self.btn_mouse.setEnabled(True)
            InfoBar.success(tr("Done"), tr("Script injected"), parent=self)
            self.backend.finished.disconnect(done)

        self.backend.finished.connect(done)
        self.backend.dispatch("launch_script", [])

    def _on_mouse(self):
        if not self._guard():
            return
        self.backend.dispatch("pretend_active", [])
        InfoBar.info(tr("Active"), tr("Mouse simulation started"), parent=self)

    def _auto_save(self):
        ac = global_config.setdefault("auto_course", {})
        ac["restore_cookies"] = self.sw_keep.isChecked()
        ac["force_speed"] = self.sw_speed.isChecked()
        save_config()

    def _append_log(self, msg: str):
        self._log_view.appendPlainText(msg)
        sb = self._log_view.verticalScrollBar()
        sb.setValue(sb.maximum())

    def retranslate(self):
        self.title.setText(tr("Script"))
        self.btn_launch.setText(tr("Launch Browser"))
        self.btn_inject.setText(tr("Inject Script"))
        self.btn_mouse.setText(tr("Start Mouse"))
        self.group.setTitle(tr("Behavior"))
        self.sw_keep.setTitle(tr("Keep Login"))
        self.sw_keep.setContent(tr("Restore cookies on startup"))
        self.sw_speed.setTitle(tr("Force Speed"))
        self.sw_speed.setContent(tr("Override playback rate"))
