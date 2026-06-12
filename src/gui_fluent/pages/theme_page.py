from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QButtonGroup
from qfluentwidgets import ScrollArea, setTheme, setThemeColor, Theme, RadioButton
from qfluentwidgets import FluentIcon as FIF

from app.utils import global_config, save_config


THEME_NAMES = [
    "aoguchi", "ink", "gummy", "prussian", "regal",
    "rosmarinus", "silence", "vandyke", "vira",
]

THEME_LABELS = {
    "aoguchi": "Aoguchi", "ink": "Ink", "gummy": "Gummy",
    "prussian": "Prussian", "regal": "Regal", "rosmarinus": "Rosmarinus",
    "silence": "Silence", "vandyke": "Vandyke", "vira": "Vira",
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
        layout.setContentsMargins(36, 20, 36, 20)
        layout.setSpacing(16)

        # Fluent mode selector
        lbl = QLabel("Fluent Theme Mode")
        lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl)

        from PyQt5.QtWidgets import QButtonGroup
        self.rb_light = RadioButton("Light")
        self.rb_dark = RadioButton("Dark")
        self.rb_auto = RadioButton("System Auto")
        self._mode_group = QButtonGroup(self)
        self._mode_group.addButton(self.rb_light)
        self._mode_group.addButton(self.rb_dark)
        self._mode_group.addButton(self.rb_auto)

        mode_row = QHBoxLayout()
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

        self._mode_group.buttonClicked.connect(self._on_mode_changed)

        # Custom themes
        lbl2 = QLabel("Custom Color Themes")
        lbl2.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(lbl2)

        grid_layout = QVBoxLayout()
        row = None
        for i, name in enumerate(THEME_NAMES):
            if i % 3 == 0:
                row = QHBoxLayout()
                grid_layout.addLayout(row)

            btn = QPushButton(THEME_LABELS.get(name, name))
            color = THEME_COLORS.get(name, "#888")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {'#fff' if name not in ['ink', 'silence', 'vira'] else '#000'};
                    border-radius: 8px;
                    padding: 20px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            btn.setMinimumSize(140, 60)
            btn.clicked.connect(lambda checked, n=name: self._on_theme_click(n))
            if current == name:
                btn.setProperty("selected", True)
                btn.setStyleSheet(btn.styleSheet() + "border: 3px solid white;")
            row.addWidget(btn)

        layout.addLayout(grid_layout)

        layout.addStretch()
        self.setWidget(view)
        self.setWidgetResizable(True)

    def _on_mode_changed(self):
        rb = self._mode_group.checkedButton()
        mode = "auto"
        if rb == self.rb_light:
            mode = "light"
            setTheme(Theme.LIGHT)
        elif rb == self.rb_dark:
            mode = "dark"
            setTheme(Theme.DARK)
        else:
            mode = "auto"
            setTheme(Theme.AUTO)
        ui_cfg = global_config.setdefault("ui", {})
        ui_cfg["fluent_mode"] = mode
        save_config()

    def _on_theme_click(self, name: str):
        apply_theme(name)
        ui_cfg = global_config.setdefault("ui", {})
        ui_cfg["theme"] = name
        save_config()
