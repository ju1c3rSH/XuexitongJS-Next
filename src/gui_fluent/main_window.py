from qfluentwidgets import FluentWindow, NavigationItemPosition
from qfluentwidgets import FluentIcon as FIF

from app import TaskManager


class MainWindow(FluentWindow):
    def __init__(self, backend: TaskManager):
        super().__init__()
        self.backend = backend
        self.setWindowTitle("uXuexitong")
        self.setMinimumSize(860, 560)
        self.resize(1024, 680)
        self._setup_navigation()

    def _setup_navigation(self):
        from .pages.script_page import ScriptPage
        from .pages.api_page import ApiPage
        from .pages.settings_page import SettingsPage
        from .pages.advanced_page import AdvancedPage
        from .pages.theme_page import ThemePage

        self.script_page = ScriptPage(self.backend, parent=self)
        self.script_page.setObjectName("scriptPage")

        self.api_page = ApiPage(self.backend, parent=self)
        self.api_page.setObjectName("apiPage")

        self.settings_page = SettingsPage(self.backend, parent=self)
        self.settings_page.setObjectName("settingsPage")

        self.advanced_page = AdvancedPage(self.backend, parent=self)
        self.advanced_page.setObjectName("advancedPage")

        self.theme_page = ThemePage(parent=self)
        self.theme_page.setObjectName("themePage")

        self.addSubInterface(self.script_page, FIF.VIDEO, "脚本")
        self.addSubInterface(self.api_page, FIF.SETTING, "API")
        self.addSubInterface(self.settings_page, FIF.SYNC, "设置")
        self.addSubInterface(self.advanced_page, FIF.DEVELOPER_TOOLS, "高级")
        self.addSubInterface(
            self.theme_page, FIF.PALETTE, "主题",
            position=NavigationItemPosition.BOTTOM
        )
