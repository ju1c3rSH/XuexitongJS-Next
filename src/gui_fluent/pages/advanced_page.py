from pathlib import Path
import shutil

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from qfluentwidgets import ScrollArea, LineEdit, SpinBox, Slider
from qfluentwidgets import SwitchSettingCard, InfoBar, MessageBox
from qfluentwidgets import FluentIcon as FIF

from app import TaskManager
from app.utils import global_config, save_config, init_config, static_path


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

        title = QLabel("高级配置")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel("调整答题、行为与网络的详细参数，修改后自动保存。")
        desc.setStyleSheet("color: #888; font-size: 13px;")
        layout.addWidget(desc)

        # --- 答题 ---
        lbl = QLabel("答题设置")
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 12px;")
        layout.addWidget(lbl)

        q_cfg = global_config.get("quiz", {})
        self._batch = self._spin_row(layout, "批处理大小 (batch_size)", q_cfg.get("batch_size", 10), 1, 50)
        self._retry = self._spin_row(layout, "重试次数 (retry_count)", q_cfg.get("retry_count", 3), 0, 10)
        self._timeout = self._spin_row(layout, "API 超时 (api_timeout, 秒)", q_cfg.get("api_timeout", 40), 10, 300)

        # --- 行为 ---
        lbl2 = QLabel("行为设置")
        lbl2.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 12px;")
        layout.addWidget(lbl2)

        ac = global_config.get("auto_course", {})
        self._poll = self._spin_row(layout, "轮询间隔 (poll_interval, ms)", ac.get("poll_interval_ms", 100), 50, 1000)
        self._retry_max = self._spin_row(layout, "最大重试 (poll_max_retry)", ac.get("poll_max_retry", 50), 5, 200)

        speed = ac.get("speed", 2.0)
        self._speed_lbl = QLabel(f"倍速: {speed}x")
        self._speed_lbl.setStyleSheet("font-size: 14px;")
        layout.addWidget(self._speed_lbl)
        self._speed = Slider()
        self._speed.setRange(50, 400)
        self._speed.setValue(int(speed * 100))
        self._speed.valueChanged.connect(lambda v: self._speed_lbl.setText(f"倍速: {v/100:.2f}x"))
        layout.addWidget(self._speed)

        # --- AI 高级 ---
        lbl3 = QLabel("AI 高级")
        lbl3.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 12px;")
        layout.addWidget(lbl3)

        oa = global_config.get("openai", {})
        self._temp = self._spin_row(layout, "Temperature (x100)", int(oa.get("temperature", 0.7) * 100), 0, 200)
        self._max_tok = self._spin_row(layout, "Max Tokens", oa.get("max_tokens", 4096), 256, 65536)

        # --- 网络 ---
        lbl4 = QLabel("网络")
        lbl4.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 12px;")
        layout.addWidget(lbl4)

        nw = global_config.get("network", {})
        proxy_val = nw.get("proxy", "")
        lbl_p = QLabel("HTTP 代理")
        lbl_p.setStyleSheet("font-size: 14px;")
        layout.addWidget(lbl_p)
        self._proxy = LineEdit()
        self._proxy.setText(proxy_val)
        layout.addWidget(self._proxy)

        domains_val = nw.get("fallback_domains", [])
        lbl_d = QLabel("备用域名 (逗号分隔)")
        lbl_d.setStyleSheet("font-size: 14px;")
        layout.addWidget(lbl_d)
        self._domains = LineEdit()
        self._domains.setText(", ".join(domains_val))
        layout.addWidget(self._domains)

        # --- 自动保存信号 ---
        for w in [self._batch, self._retry, self._timeout, self._poll, self._retry_max]:
            w.valueChanged.connect(self._auto_save)
        self._speed.valueChanged.connect(self._auto_save)
        self._temp.valueChanged.connect(self._auto_save)
        self._max_tok.valueChanged.connect(self._auto_save)

        # --- 恢复默认 ---
        layout.addSpacing(20)
        reset_btn = QPushButton("恢复默认设置")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f; color: white; border-radius: 8px;
                padding: 14px; font-size: 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #b71c1c; }
        """)
        reset_btn.clicked.connect(self._on_reset)
        layout.addWidget(reset_btn)

        layout.addStretch()
        self.setWidget(view)
        self.setWidgetResizable(True)

    def _spin_row(self, layout, label, value, lo, hi):
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 14px;")
        layout.addWidget(lbl)
        sp = SpinBox()
        sp.setRange(lo, hi)
        sp.setValue(int(value))
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

        nw = global_config.setdefault("network", {})
        nw["proxy"] = self._proxy.text()
        nw["fallback_domains"] = [d.strip() for d in self._domains.text().split(",") if d.strip()]

        save_config()

    def _on_reset(self):
        m = MessageBox("确认重置", "所有配置将恢复为默认值，确定继续？", self)
        m.yesButton.setText("确定")
        m.cancelButton.setText("取消")
        if not m.exec():
            return

        src = static_path("src", "resources", "toml", "default_config.toml")
        dst = Path.cwd() / "config.toml"
        shutil.copy2(str(src), str(dst))

        init_config()
        InfoBar.success("已重置", "配置已恢复为默认值", parent=self)
        self._setup_ui()
