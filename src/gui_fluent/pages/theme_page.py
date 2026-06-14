from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QButtonGroup, QCheckBox, QSizePolicy
from qfluentwidgets import (
    ScrollArea, setTheme, setThemeColor, Theme, RadioButton,
    ElevatedCardWidget, PrimaryPushButton, SwitchButton,
    Slider, ProgressBar,
)
from app.utils import global_config, save_config
from ..i18n import tr


THEME_NAMES = ["aoguchi", "gummy", "prussian", "regal", "rosmarinus", "vandyke", "vira"]
THEME_LABELS = {
    "aoguchi": "Aoguchi", "gummy": "Gummy", "prussian": "Prussian",
    "regal": "Regal", "rosmarinus": "Rosmarinus",
    "vandyke": "Vandyke", "vira": "Vira",
}
THEME_COLORS = {
    "aoguchi": "#6bb3b7", "gummy": "#fc6076", "prussian": "#003153",
    "regal": "#60efdb", "rosmarinus": "#7c5ca8",
    "vandyke": "#8d5742", "vira": "#89ddff",
}


def apply_theme(name: str):
    color = THEME_COLORS.get(name, "#6bb3b7")
    setThemeColor(color)


class _ThemeCard(ElevatedCardWidget):
    def __init__(self, name: str, is_selected: bool, parent=None):
        super().__init__(parent)
        self._name = name
        self._label_text = name

        self.setFixedSize(160, 90)

        self._color_bar = QWidget()
        self._color_bar.setFixedHeight(16)
        self._color_bar.setStyleSheet(f"background-color: {THEME_COLORS[name]};border-radius:0;")

        self._check = QLabel("✓" if is_selected else "")
        self._check.setAlignment(Qt.AlignCenter)
        self._check.setStyleSheet("font-size: 18px; font-weight: bold; color: " + THEME_COLORS[name] + ";")

        self._lbl = QLabel(tr(THEME_LABELS[name]))
        self._lbl.setAlignment(Qt.AlignCenter)
        self._lbl.setStyleSheet("font-size: 13px; font-weight: bold;")

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        v.addWidget(self._color_bar)
        v.addStretch()
        v.addWidget(self._lbl)
        v.addWidget(self._check)
        v.addStretch()

    def set_selected(self, selected: bool):
        self._check.setText("✓" if selected else "")

    def set_label_text(self, text: str):
        self._lbl.setText(text)


class ThemePage(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._theme_cards: dict[str, _ThemeCard] = {}
        self._setup_ui()

    def _setup_ui(self):
        cfg = global_config.get("ui", {})
        self._current_theme = cfg.get("theme", "aoguchi")
        self._fluent_mode = cfg.get("fluent_mode", "auto")

        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(16)

        # --- Title ---
        self.title = QLabel(tr("Theme"))
        self.title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(self.title)

        # --- Fluent Mode ---
        self.lbl_mode = QLabel(tr("Fluent Mode"))
        self.lbl_mode.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_mode)

        self.rb_light = RadioButton(tr("Light"))
        self.rb_dark = RadioButton(tr("Dark"))
        self.rb_auto = RadioButton(tr("System"))
        self._mode_group = QButtonGroup(self)
        self._mode_group.addButton(self.rb_light)
        self._mode_group.addButton(self.rb_dark)
        self._mode_group.addButton(self.rb_auto)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(24)
        mode_row.addWidget(self.rb_light)
        mode_row.addWidget(self.rb_dark)
        mode_row.addWidget(self.rb_auto)
        layout.addLayout(mode_row)

        if self._fluent_mode == "light":
            self.rb_light.setChecked(True)
        elif self._fluent_mode == "dark":
            self.rb_dark.setChecked(True)
        else:
            self.rb_auto.setChecked(True)

        self._mode_group.buttonClicked.connect(self._on_mode_changed)

        # --- Accent Color Grid ---
        self.lbl_accent = QLabel(tr("Custom Accent"))
        self.lbl_accent.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 12px;")
        layout.addWidget(self.lbl_accent)

        grid = QVBoxLayout()
        grid.setSpacing(12)
        for i, name in enumerate(THEME_NAMES):
            if i % 3 == 0:
                row = QHBoxLayout()
                row.setSpacing(12)
                grid.addLayout(row)
            card = _ThemeCard(name, name == self._current_theme)
            card.clicked.connect(lambda checked=False, n=name: self._on_theme_click(n))
            self._theme_cards[name] = card
            row.addWidget(card)

        layout.addLayout(grid)

        # --- Live Preview ---
        self.lbl_preview = QLabel(tr("Preview"))
        self.lbl_preview.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 12px;")
        layout.addWidget(self.lbl_preview)

        self._preview_card = ElevatedCardWidget()
        self._build_preview_content()
        layout.addWidget(self._preview_card)

        layout.addStretch()
        self.setWidget(view)
        self.setWidgetResizable(True)

    def _build_preview_content(self):
        layout = QVBoxLayout(self._preview_card)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)

        # Row 1: Button + Slider + Switch
        row1 = QHBoxLayout()
        row1.setSpacing(16)
        self._pv_btn = PrimaryPushButton(tr("Button"))
        self._pv_btn.setMinimumWidth(120)
        row1.addWidget(self._pv_btn)

        self._pv_slider = Slider()
        self._pv_slider.setRange(0, 100)
        self._pv_slider.setValue(60)
        row1.addWidget(self._pv_slider, 1)

        self._pv_switch = SwitchButton(tr("Toggle"))
        row1.addWidget(self._pv_switch)
        layout.addLayout(row1)

        # Row 2: ProgressBar + CheckBox
        row2 = QHBoxLayout()
        row2.setSpacing(16)
        self._pv_progress = ProgressBar()
        self._pv_progress.setValue(60)
        row2.addWidget(self._pv_progress, 1)

        self._pv_cb = QCheckBox(tr("Checkbox"))
        row2.addWidget(self._pv_cb)
        self._pv_cb.setChecked(True)
        layout.addLayout(row2)

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
        self._current_theme = name
        apply_theme(name)
        ui_cfg = global_config.setdefault("ui", {})
        ui_cfg["theme"] = name
        save_config()
        # Update check marks
        for n, card in self._theme_cards.items():
            card.set_selected(n == name)

    def retranslate(self):
        self.title.setText(tr("Theme"))
        self.lbl_mode.setText(tr("Fluent Mode"))
        self.rb_light.setText(tr("Light"))
        self.rb_dark.setText(tr("Dark"))
        self.rb_auto.setText(tr("System"))
        self.lbl_accent.setText(tr("Custom Accent"))
        self.lbl_preview.setText(tr("Preview"))
        self._pv_btn.setText(tr("Button"))
        self._pv_switch.setText(tr("Toggle"))
        self._pv_cb.setText(tr("Checkbox"))
        for name, card in self._theme_cards.items():
            card.set_label_text(tr(THEME_LABELS[name]))
