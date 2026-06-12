from qfluentwidgets import FluentWindow, NavigationItemPosition
from qfluentwidgets import FluentIcon as FIF

from app import TaskManager


class MainWindow(FluentWindow):
    def __init__(self, backend: TaskManager):
        super().__init__()
        self.backend = backend
        self.setWindowTitle("uXuexitong")
        self.setMinimumSize(960, 640)
        self.resize(1200, 760)

        self._setup_navigation()

    def _setup_navigation(self):
        from .pages.script_page import ScriptPage
        from .pages.api_page import ApiPage
        from .pages.settings_page import SettingsPage
        from .pages.theme_page import ThemePage

        self.script_page = ScriptPage(self.backend, parent=self)
        self.script_page.setObjectName("scriptPage")

        self.api_page = ApiPage(self.backend, parent=self)
        self.api_page.setObjectName("apiPage")

        self.settings_page = SettingsPage(self.backend, parent=self)
        self.settings_page.setObjectName("settingsPage")

        self.theme_page = ThemePage(parent=self)
        self.theme_page.setObjectName("themePage")

        self.addSubInterface(self.script_page, FIF.VIDEO, "Script")
        self.addSubInterface(self.api_page, FIF.SETTING, "API")
        self.addSubInterface(self.settings_page, FIF.SYNC, "Settings")
        self.addSubInterface(
            self.theme_page, FIF.PALETTE, "Theme",
            position=NavigationItemPosition.BOTTOM
        )
