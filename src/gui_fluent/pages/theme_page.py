from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QButtonGroup
from qfluentwidgets import ScrollArea, setTheme, setThemeColor, Theme, RadioButton

from app.utils import global_config, save_config


THEME_NAMES = ["aoguchi", "ink", "gummy", "prussian", "regal", "rosmarinus", "silence", "vandyke", "vira"]
THEME_LABELS = {
    "aoguchi": "青口", "ink": "墨染", "gummy": "软糖",
    "prussian": "普鲁士", "regal": "帝政", "rosmarinus": "迷迭香",
    "silence": "寂静", "vandyke": "棕褐", "vira": "炫彩",
}
THEME_COLORS = {
    "aoguchi": "#6bb3b7", "ink": "#ffffff", "gummy": "#fc6076",
    "prussian": "#003153", "regal": "#60efdb", "rosmarinus": "#7c5ca8",
    "silence": "#000000", "vandyke": "#8d5742", "vira": "#89ddff",
}


def apply_theme(name: str):
    color = THEME_COLORS.get(name, "#6bb3b7")
    setThemeColor(color)


class ThemePage(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        cfg = global_config.get("ui", {})
        current = cfg.get("theme", "aoguchi")
        fluent_mode = cfg.get("fluent_mode", "auto")

        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(16)

        title = QLabel("主题设置")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(title)

        lbl = QLabel("Fluent 主题模式")
        lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl)

        self.rb_light = RadioButton("浅色")
        self.rb_dark = RadioButton("深色")
        self.rb_auto = RadioButton("跟随系统")
        mode_group = QButtonGroup(self)
        mode_group.addButton(self.rb_light)
        mode_group.addButton(self.rb_dark)
        mode_group.addButton(self.rb_auto)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(24)
        mode_row.addWidget(self.rb_light)
        mode_row.addWidget(self.rb_dark)
        mode_row.addWidget(self.rb_auto)
        layout.addLayout(mode_row)

        if fluent_mode == "light":
            self.rb_light.setChecked(True)
        elif fluent_mode == "dark":
            self.rb_dark.setChecked(True)
        else:
            self.rb_auto.setChecked(True)

        mode_group.buttonClicked.connect(self._on_mode_changed)

        lbl2 = QLabel("自定义配色")
        lbl2.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(lbl2)

        grid = QVBoxLayout()
        grid.setSpacing(12)
        for i, name in enumerate(THEME_NAMES):
            if i % 3 == 0:
                row = QHBoxLayout()
                row.setSpacing(12)
                grid.addLayout(row)
            btn = QPushButton(THEME_LABELS.get(name, name))
            color = THEME_COLORS.get(name, "#888")
            is_light = name in ("ink", "silence", "vira")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {'#000' if is_light else '#fff'};
                    border-radius: 8px;
                    padding: 20px 0;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ opacity: 0.8; }}
            """)
            btn.setMinimumSize(140, 60)
            btn.clicked.connect(lambda checked, n=name: self._on_theme_click(n))
            row.addWidget(btn)

        layout.addLayout(grid)
        layout.addStretch()
        self.setWidget(view)
        self.setWidgetResizable(True)

    def _on_mode_changed(self):
        rb = self.sender()
        if rb == self.rb_light:
            setTheme(Theme.LIGHT)
            mode = "light"
        elif rb == self.rb_dark:
            setTheme(Theme.DARK)
            mode = "dark"
        else:
            setTheme(Theme.AUTO)
            mode = "auto"
        ui_cfg = global_config.setdefault("ui", {})
        ui_cfg["fluent_mode"] = mode
        save_config()

    def _on_theme_click(self, name: str):
        apply_theme(name)
        ui_cfg = global_config.setdefault("ui", {})
        ui_cfg["theme"] = name
        save_config()
