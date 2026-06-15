from qfluentwidgets import FluentWindow, NavigationItemPosition
from qfluentwidgets import FluentIcon as FIF

from app import TaskManager
from .i18n import _manager as lang_mgr, tr


class MainWindow(FluentWindow):
    def __init__(self, backend: TaskManager):
        super().__init__()
        self.backend = backend
        self.setWindowTitle("uXueXiTongX")
        self.setMinimumSize(860, 560)
        self.resize(1024, 680)
        self._page_map = {}
        self._nav_items = []
        self._setup_navigation()
        lang_mgr.languageChanged.connect(self._on_language_changed)

    def _setup_navigation(self):
        from .pages.script_page import ScriptPage
        from .pages.api_page import ApiPage
        from .pages.settings_page import SettingsPage
        from .pages.advanced_page import AdvancedPage
        from .pages.theme_page import ThemePage
        from .pages.about_page import AboutPage

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

        self.about_page = AboutPage(parent=self)
        self.about_page.setObjectName("aboutPage")

        self._page_map = {
            "scriptPage": (self.script_page, FIF.COMMAND_PROMPT, "Script", None),
            "apiPage": (self.api_page, FIF.CLOUD, "API", None),
            "settingsPage": (self.settings_page, FIF.SETTING, "Settings", None),
            "advancedPage": (self.advanced_page, FIF.DEVELOPER_TOOLS, "Advanced", None),
            "themePage": (self.theme_page, FIF.PALETTE, "Theme", NavigationItemPosition.BOTTOM),
            "aboutPage": (self.about_page, FIF.GITHUB, "About", NavigationItemPosition.BOTTOM),
        }

        self._rebuild_navigation()

    def _rebuild_navigation(self):
        for key, (page, icon, label, pos) in self._page_map.items():
            nav_kwargs = {}
            if pos is not None:
                nav_kwargs["position"] = pos
            self.addSubInterface(page, icon, tr(label), **nav_kwargs)

    def _on_language_changed(self, lang):
        self.setWindowTitle("uXueXiTongX")
        # Remove existing navigation items and re-add with translated labels
        for key in list(self._page_map.keys()):
            self.navigationInterface.removeWidget(key)
        self._rebuild_navigation()
        # Retranslate all sub-pages
        self.script_page.retranslate()
        self.api_page.retranslate()
        self.settings_page.retranslate()
        self.advanced_page.retranslate()
        self.theme_page.retranslate()
        self.about_page.retranslate()
