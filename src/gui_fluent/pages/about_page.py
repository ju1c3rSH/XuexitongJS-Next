from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from qfluentwidgets import ScrollArea

from ..i18n import tr
from version import __version__


FEATURES = [
    ("JS Automation", "iframe traversal, lock/cooldown coordination, auto-reconnect on page refresh."),
    ("AI Answering", "Font deobfuscation, OpenAI-compatible API, auto-retry, web search context."),
    ("Question Fetching", "Structured JSON extraction, image OCR, patch mode with history memory."),
    ("Stability", "Multi-threaded, WebSocket auto-reconnect, cookie persistence."),
    ("Graphical Interface", "PyQt5 + qfluentwidgets, log panel, config management, theme switching."),
]

CREDITS = [
    ("@chaolucky18", "xuexitongScript", "https://github.com/chaolucky18/xuexitongScript"),
    ("@unraous", "uXuexitongJS", "https://github.com/unraous/uXuexitongJS"),
    ("@ju1c3rSH", "uXueXiTongX", "https://github.com/ju1c3rSH/uXueXiTongX"),
]


def _separator():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    line.setStyleSheet("color: #ddd;")
    return line


class AboutPage(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(12)

        self.title = QLabel("uXueXiTongX")
        self.title.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(self.title)

        self.version_lbl = QLabel(f"{tr('Version')} {__version__}")
        self.version_lbl.setStyleSheet("color: #888; font-size: 13px;")
        layout.addWidget(self.version_lbl)

        self.tagline = QLabel(tr("More stable video, more accurate answering, effortless to use."))
        self.tagline.setStyleSheet("font-size: 14px; color: #666; margin-bottom: 4px;")
        layout.addWidget(self.tagline)

        layout.addWidget(_separator())

        self.lbl_desc_title = QLabel(tr("Description"))
        self.lbl_desc_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_desc_title)

        self.desc = QLabel(
            tr("Auto-learning tool for Chaoxing Xuexitong. Supports auto video playback, PDF auto-scrolling, AI-powered answering, based on Selenium and WebSocket for browser automation.")
        )
        self.desc.setWordWrap(True)
        self.desc.setStyleSheet("font-size: 13px; line-height: 1.6;")
        layout.addWidget(self.desc)

        layout.addWidget(_separator())

        self.lbl_credits_title = QLabel(tr("Credits"))
        self.lbl_credits_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_credits_title)

        self.credits_intro = QLabel(tr("This project originated from the following open-source projects:"))
        self.credits_intro.setWordWrap(True)
        self.credits_intro.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.credits_intro)

        self._credit_labels = []
        for author, project, url in CREDITS:
            lbl = QLabel(f'<a href="{url}" style="text-decoration:none;">{author}</a> — {project}')
            lbl.setOpenExternalLinks(True)
            lbl.setStyleSheet("font-size: 13px; padding-left: 16px;")
            self._credit_labels.append(lbl)
            layout.addWidget(lbl)

        layout.addWidget(_separator())

        self.lbl_features_title = QLabel(tr("Features"))
        self.lbl_features_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_features_title)

        self._feature_widgets = []
        for title_key, desc_key in FEATURES:
            row = QHBoxLayout()
            row.setSpacing(10)
            bullet = QLabel("◆")
            bullet.setStyleSheet("font-size: 12px; color: #888; margin-top: 2px;")
            bullet.setFixedWidth(16)
            row.addWidget(bullet)

            col = QVBoxLayout()
            col.setSpacing(2)
            ftitle = QLabel(f"<b>{tr(title_key)}</b>")
            ftitle.setStyleSheet("font-size: 13px;")
            col.addWidget(ftitle)
            fdesc = QLabel(tr(desc_key))
            fdesc.setWordWrap(True)
            fdesc.setStyleSheet("font-size: 12px; color: #888;")
            col.addWidget(fdesc)
            self._feature_widgets.append((ftitle, fdesc))

            row.addLayout(col, 1)
            layout.addLayout(row)

        layout.addWidget(_separator())

        self.lbl_stack_title = QLabel(tr("Tech Stack"))
        self.lbl_stack_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_stack_title)

        self.stack_lbl = QLabel("Python  ·  PyQt5  ·  qfluentwidgets  ·  Selenium  ·  WebSocket  ·  OpenAI API")
        self.stack_lbl.setStyleSheet("font-size: 13px; color: #555;")
        layout.addWidget(self.stack_lbl)

        layout.addWidget(_separator())

        self.lbl_license_title = QLabel(tr("License"))
        self.lbl_license_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_license_title)

        self.license_lbl = QLabel(
            '<a href="https://creativecommons.org/licenses/by-nc/4.0/" style="text-decoration:none;">CC BY-NC 4.0</a>'
            " — Attribution-NonCommercial 4.0 International"
        )
        self.license_lbl.setOpenExternalLinks(True)
        self.license_lbl.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.license_lbl)

        self.github_lbl = QLabel(
            '<a href="https://github.com/ju1c3rSH/uXueXiTongX" style="text-decoration:none;font-size:13px;">'
            f"  GitHub: {tr('GitHub Repository')}</a>"
        )
        self.github_lbl.setOpenExternalLinks(True)
        self.github_lbl.setStyleSheet("margin-top: 8px;")
        layout.addWidget(self.github_lbl)

        layout.addStretch()
        self.setWidget(view)
        self.setWidgetResizable(True)

    def retranslate(self):
        self.version_lbl.setText(f"{tr('Version')} {__version__}")
        self.tagline.setText(tr("More stable video, more accurate answering, effortless to use."))
        self.lbl_desc_title.setText(tr("Description"))
        self.desc.setText(
            tr("Auto-learning tool for Chaoxing Xuexitong. Supports auto video playback, PDF auto-scrolling, AI-powered answering, based on Selenium and WebSocket for browser automation.")
        )
        self.lbl_credits_title.setText(tr("Credits"))
        self.credits_intro.setText(tr("This project originated from the following open-source projects:"))
        self.lbl_features_title.setText(tr("Features"))
        for (title_key, desc_key), (ftitle, fdesc) in zip(FEATURES, self._feature_widgets):
            ftitle.setText(f"<b>{tr(title_key)}</b>")
            fdesc.setText(tr(desc_key))
        self.lbl_stack_title.setText(tr("Tech Stack"))
        self.lbl_license_title.setText(tr("License"))
        self.github_lbl.setText(
            '<a href="https://github.com/ju1c3rSH/uXueXiTongX" style="text-decoration:none;font-size:13px;">'
            f"  GitHub: {tr('GitHub Repository')}</a>"
        )
