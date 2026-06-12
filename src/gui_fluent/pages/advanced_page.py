from pathlib import Path
import shutil

from PyQt5.QtCore import QLocale
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont
from qfluentwidgets import ScrollArea, LineEdit, SpinBox, Slider
from qfluentwidgets import SwitchSettingCard, InfoBar, MessageBox
from qfluentwidgets import FluentIcon as FIF

from app import TaskManager
from app.utils import global_config, save_config, init_config, static_path
from ..i18n import tr


class AdvancedPage(ScrollArea):
    def __init__(self, backend: TaskManager, parent=None):
        super().__init__(parent)
        self.backend = backend
        self._setup_ui()

    def _setup_ui(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(14)

        self.title = QLabel(tr("Advanced"))
        self.title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(self.title)

        self.desc = QLabel(tr("Fine-tune quiz, behavior and network parameters. Auto-saved."))
        self.desc.setStyleSheet("color: #888; font-size: 13px;")
        layout.addWidget(self.desc)

        # --- Quiz ---
        self.lbl_quiz = QLabel(tr("Quiz"))
        self.lbl_quiz.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 12px;")
        layout.addWidget(self.lbl_quiz)

        q_cfg = global_config.get("quiz", {})
        self._batch = self._spin_row(layout, tr("Batch Size"), q_cfg.get("batch_size", 10), 1, 50)
        self._retry = self._spin_row(layout, tr("Retry Count"), q_cfg.get("retry_count", 3), 0, 10)
        self._timeout = self._spin_row(layout, tr("API Timeout (s)"), q_cfg.get("api_timeout", 40), 10, 300)

        # --- Behavior ---
        self.lbl_behavior = QLabel(tr("Behavior"))
        self.lbl_behavior.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 12px;")
        layout.addWidget(self.lbl_behavior)

        ac = global_config.get("auto_course", {})
        self._poll = self._spin_row(layout, tr("Poll Interval (ms)"), ac.get("poll_interval_ms", 100), 50, 1000)
        self._retry_max = self._spin_row(layout, tr("Max Retries"), ac.get("poll_max_retry", 50), 5, 200)

        speed = ac.get("speed", 2.0)
        self._speed_lbl = QLabel(f"Speed: {speed}x")
        self._speed_lbl.setFont(QFont("Microsoft YaHei", 9))
        self._speed_lbl.setStyleSheet("font-size: 14px;")
        layout.addWidget(self._speed_lbl)
        self._speed = Slider()
        self._speed.setRange(50, 400)
        self._speed.setValue(int(speed * 100))
        self._speed.valueChanged.connect(lambda v: self._speed_lbl.setText(f"Speed: {v/100:.2f}x"))
        self._speed.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(self._speed)

        # --- AI ---
        self.lbl_ai = QLabel(tr("AI"))
        self.lbl_ai.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 12px;")
        layout.addWidget(self.lbl_ai)

        oa = global_config.get("openai", {})
        self._temp = self._spin_row(layout, tr("Temperature (x100)"), int(float(oa.get("temperature", 0.7)) * 100), 0, 200)
        self._max_tok = self._spin_row(layout, tr("Max Tokens"), oa.get("max_tokens", 4096), 256, 65536)

        self.sw_thinking = SwitchSettingCard(
            FIF.ROBOT, tr("Enable Thinking"),
            tr("When enabled, temperature and max_tokens use model defaults (recommended)")
        )
        self.sw_thinking.setChecked(oa.get("enable_thinking", True))
        self.sw_thinking.checkedChanged.connect(self._on_thinking_toggled)
        self.sw_thinking.checkedChanged.connect(self._auto_save)
        layout.addWidget(self.sw_thinking)

        self._thinking_note = QLabel(
            tr("Note: When Thinking is ON, temperature and max_tokens are IGNORED by the model.")
        )
        self._thinking_note.setStyleSheet("color: #999; font-size: 11px; margin-bottom: 8px;")
        layout.addWidget(self._thinking_note)
        self._update_thinking_ui(oa.get("enable_thinking", True))

        # --- Network ---
        self.lbl_network = QLabel(tr("Network"))
        self.lbl_network.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 12px;")
        layout.addWidget(self.lbl_network)

        nw = global_config.get("network", {})
        proxy_val = nw.get("proxy", "")
        self.lbl_proxy = QLabel(tr("HTTP Proxy"))
        self.lbl_proxy.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.lbl_proxy)
        self._proxy = LineEdit()
        self._proxy.setText(proxy_val)
        self._proxy.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(self._proxy)

        domains_val = nw.get("fallback_domains", [])
        self.lbl_domains = QLabel(tr("Fallback Domains (comma-separated)"))
        self.lbl_domains.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.lbl_domains)
        self._domains = LineEdit()
        self._domains.setText(", ".join(domains_val))
        self._domains.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(self._domains)

        # --- 自动保存信号 ---
        for w in [self._batch, self._retry, self._timeout, self._poll, self._retry_max]:
            w.valueChanged.connect(self._auto_save)
        self._speed.valueChanged.connect(self._auto_save)
        self._temp.valueChanged.connect(self._auto_save)
        self._max_tok.valueChanged.connect(self._auto_save)

        # --- 恢复默认 ---
        layout.addSpacing(20)
        self.reset_btn = QPushButton(tr("Reset to Defaults"))
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f; color: white; border-radius: 8px;
                padding: 14px; font-size: 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #b71c1c; }
        """)
        self.reset_btn.clicked.connect(self._on_reset)
        layout.addWidget(self.reset_btn)

        layout.addStretch()
        self.setWidget(view)
        self.setWidgetResizable(True)

    def _on_thinking_toggled(self, enabled: bool):
        self._update_thinking_ui(enabled)

    def _update_thinking_ui(self, enabled: bool):
        self._temp.setEnabled(not enabled)
        self._max_tok.setEnabled(not enabled)
        self._thinking_note.setVisible(enabled)

    def _spin_row(self, layout, label, value, lo, hi):
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 14px;")
        layout.addWidget(lbl)
        sp = SpinBox()
        sp.setRange(lo, hi)
        sp.setValue(int(float(value)))
        sp.setFont(QFont("Microsoft YaHei", 9))
        sp.setLocale(QLocale.c())
        sp.wheelEvent = lambda event: None
        layout.addWidget(sp)
        return sp

    def _auto_save(self):
        q = global_config.setdefault("quiz", {})
        q["batch_size"] = self._batch.value()
        q["retry_count"] = self._retry.value()
        q["api_timeout"] = self._timeout.value()

        ac = global_config.setdefault("auto_course", {})
        ac["poll_interval_ms"] = self._poll.value()
        ac["poll_max_retry"] = self._retry_max.value()
        ac["speed"] = self._speed.value() / 100.0

        oa = global_config.setdefault("openai", {})
        oa["temperature"] = self._temp.value() / 100.0
        oa["max_tokens"] = self._max_tok.value()
        oa["enable_thinking"] = self.sw_thinking.isChecked()

        nw = global_config.setdefault("network", {})
        nw["proxy"] = self._proxy.text()
        nw["fallback_domains"] = [d.strip() for d in self._domains.text().split(",") if d.strip()]

        save_config()

    def _on_reset(self):
        m = MessageBox(tr("Confirm"), tr("Reset all settings to defaults?"), self)
        m.yesButton.setText(tr("Reset"))
        m.cancelButton.setText(tr("Cancel"))
        if not m.exec():
            return

        src = static_path("src", "resources", "toml", "default_config.toml")
        dst = Path.cwd() / "config.toml"
        shutil.copy2(str(src), str(dst))

        init_config()
        InfoBar.success(tr("Reset"), tr("Settings restored to defaults"), parent=self)
        self._setup_ui()

    def retranslate(self):
        self.title.setText(tr("Advanced"))
        self.desc.setText(tr("Fine-tune quiz, behavior and network parameters. Auto-saved."))
        self.lbl_quiz.setText(tr("Quiz"))
        self.lbl_behavior.setText(tr("Behavior"))
        self.lbl_ai.setText(tr("AI"))
        self.lbl_network.setText(tr("Network"))
        self.lbl_proxy.setText(tr("HTTP Proxy"))
        self.lbl_domains.setText(tr("Fallback Domains (comma-separated)"))
        self.sw_thinking.setTitle(tr("Enable Thinking"))
        self.sw_thinking.setContent(tr("When enabled, temperature and max_tokens use model defaults (recommended)"))
        self._thinking_note.setText(
            tr("Note: When Thinking is ON, temperature and max_tokens are IGNORED by the model.")
        )
        self.reset_btn.setText(tr("Reset to Defaults"))
