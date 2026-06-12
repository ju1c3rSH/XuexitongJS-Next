"""浏览器驱动模块"""
import asyncio
import dataclasses
import json
import logging
import secrets
import threading
import time
from pathlib import Path

import aiofiles
import websockets
from selenium import webdriver
from selenium.common.exceptions import NoSuchDriverException, WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from .auto_answer import answer_questions
from .utils import get_path_config, global_config, save_config


@dataclasses.dataclass
class CourseSettings:
    """刷课相关设置"""
    browser: str
    url: dict[str, str]
    user_cookies: str
    restore_cookies: bool
    force_speed: bool
    speed: float

def load_settings() -> CourseSettings:
    """从 global_config 加载刷课相关设置"""
    ac_cfg: dict = global_config.get("auto_course", {})
    return CourseSettings(
        browser=ac_cfg.get("browser", ""),
        url={
            key: ac_cfg.get(f"{key}_url", "")
            for key in ["home", "login", "history"]
        },
        user_cookies=ac_cfg.get("user_cookies", ""),
        restore_cookies=ac_cfg.get("restore_cookies", True),
        force_speed=ac_cfg.get("force_speed", False),
        speed=ac_cfg.get("speed", 2.0),
    )

class CourseHandler:
    """网课处理类, 包含selenium浏览器驱动启动和 AI 答题所需的JS/PY 双向 WebSocket 服务"""
    def __init__(self):
        self._driver: webdriver.Firefox | webdriver.Edge | webdriver.Chrome | None = None
        self._ws_thread: threading.Thread | None = None
        self._mouse_thread: threading.Thread | None = None
        self._monitor_thread: threading.Thread | None = None
        self._ws_client_count: int = 0
        self._settings = load_settings()
        self._script_code: str = ""
        self._monitor_active: bool = False

    async def _messenger(self, websocket: websockets.ServerConnection) -> None:
        """WebSocket 消息处理器"""
        self._ws_client_count += 1
        que_path: Path = get_path_config(False, "original_questions")
        ans_path: Path = get_path_config(False, "answers")
        try:
            async for msg in websocket:
                data: dict = json.loads(msg)
                if data.get("type") == "testDocHtml":
                    html_str: str = data.get("html", "")
                    logging.info("收到问题HTML, 长度: %d", len(html_str))
                    async with aiofiles.open(que_path, "w", encoding="utf-8") as f:
                        await f.write(html_str)
                    logging.info("HTML已保存到 %s", que_path)
                    await answer_questions()
                    async with aiofiles.open(ans_path, encoding="utf-8") as f:
                        ans_json = await f.read()
                    await websocket.send(ans_json)

                elif data.get("type") == "quizData":
                    font_base64: str = data.get("fontBase64", "")
                    ttf = get_path_config(False, "obf_font")
                    ttf.write_bytes(base64.b64decode(font_base64))

                    quiz_data: dict = {
                        "fontBase64": font_base64,
                        "questions": data.get("questions", []),
                        "images": data.get("images", []),
                    }
                    async with aiofiles.open(que_path, "w", encoding="utf-8") as f:
                        await f.write(json.dumps(quiz_data, ensure_ascii=False))
                    logging.info("quizData已保存, %d 题, %d 图片",
                                 len(quiz_data["questions"]), len(quiz_data["images"]))

                    await answer_questions()

                    async with aiofiles.open(ans_path, encoding="utf-8") as f:
                        ans_json = await f.read()
                    await websocket.send(ans_json)

                elif data.get("type") == "configSync":
                    payload: dict = data.get("payload", {})
                    ac: dict = global_config.setdefault("auto_course", {})
                    if payload.get("historyUrl"):
                        ac["history_url"] = payload["historyUrl"]
                    if payload.get("currentUrl"):
                        ac["current_url"] = payload["currentUrl"]
                    save_config()
                    logging.info("\u914d\u7f6e\u5df2\u81ea\u52a8\u66f4\u65b0: %s", payload)
                else:
                    logging.info("收到\u975eHTML\u6d88\u606f: %s", data)
        finally:
            self._ws_client_count -= 1

    def _launch_websocket(self):
        """启动 WebSocket 服务器"""
        async def run(port: int = 8765):
            async with websockets.serve(self._messenger, "localhost", port):
                logging.info("WebSocket服务器已启动 ws://localhost:%d", port)
                await asyncio.Future()
        asyncio.run(run())

    def _init_driver(
        self,
        headless: bool = True,
        browser: str = "Firefox"
    ) -> webdriver.Firefox | webdriver.Edge | webdriver.Chrome:
        """初始化浏览器驱动"""
        driver_map: dict = {
            "Chrome": (webdriver.Chrome, ChromeOptions),
            "Firefox": (webdriver.Firefox, FirefoxOptions),
            "Edge": (webdriver.Edge, EdgeOptions),
        }

        driver_cls, options_cls = driver_map.get(browser, driver_map["Firefox"])
        options: FirefoxOptions | EdgeOptions | ChromeOptions = options_cls()

        if isinstance(options, FirefoxOptions):
            options.set_preference("intl.accept_languages", "zh-CN")
        else:
            options.add_argument("--lang=zh-CN")
        if headless:
            options.add_argument("--headless")

        logging.info("正在通过 Selenium Manager 查找 %s 驱动并启动浏览器...", browser)
        t0: float = time.time()
        driver = driver_cls(options=options)
        logging.info("%s 驱动初始化完成（耗时 %.1f 秒）", browser, time.time() - t0)
        return driver

    def _parse_cookies(self, cookie_str: str) -> list:
        """将标准 cookie 字符串解析为 selenium cookies 列表"""
        cookies = []
        for item in cookie_str.split(';'):
            if '=' in item:
                name, value = item.strip().split('=', 1)
                cookies.append({'name': name, 'value': value})
        return cookies

    def _inject_cookies(self) -> None:
        """注入用户 Cookie"""
        if self._settings.user_cookies.strip() == "":
            logging.info("用户 Cookie 为空, 跳过注入")
            return

        cookies = self._parse_cookies(self._settings.user_cookies)
        for cookie in cookies:
            self._driver.add_cookie(cookie)
        logging.info("已成功设置 %d 个 Cookie", len(cookies))

    def _init_script(self) -> str:
        """初始化 JS 脚本"""
        script_path: Path = get_path_config(True, "js_script")
        logging.info("正在加载脚本: %s", script_path)
        with Path(script_path).open(encoding="utf-8") as f:
            main_script: str = f.read()

        logging.info("脚本已加载, 长度: %d", len(main_script))
        options: str = f"""
            globalThis.LAUNCH_OPTION = 1;
            globalThis.FORCE_SPEED = {str(self._settings.force_speed).lower()};
            globalThis.SPEED = {self._settings.speed};
        """
        return "\n".join([options, main_script])

    def _start_script_monitor(self) -> None:
        """启动 JS 存活监控线程（双速检测）"""
        if self._monitor_active:
            return
        self._monitor_active = True

        def monitor_loop():
            fast_mode = True
            fast_count = 0
            while self._monitor_active:
                if self._ws_client_count > 0:
                    fast_mode = False
                    fast_count = 0
                else:
                    if not fast_mode:
                        fast_mode = True
                    fast_count += 1

                if fast_mode and fast_count >= 3:
                    try:
                        alive = self._driver.execute_script(
                            "return !!window._uxAlive"
                        )
                        if alive:
                            fast_count = 0
                        else:
                            logging.warning("[uX] JS 存活检测失败，重新注入...")
                            self._inject_script()
                            fast_count = 0
                    except Exception:
                        fast_count = 0

                interval = 3 if fast_mode else 30
                time.sleep(interval)

            self._monitor_active = False

        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        logging.info("[uX] 存活监控已启动")

    def _inject_script(self) -> None:
        """重新注入 JS 脚本"""
        try:
            self._script_code = self._init_script()
            handles = self._driver.window_handles
            self._driver.switch_to.window(handles[-1])
            self._driver.execute_script(self._script_code)
            logging.info("[uX] JS 脚本重新注入成功")
        except Exception as e:
            logging.error("[uX] JS 脚本重新注入失败: %s", e)

    def _launch_ws_server(self) -> None:
        """启动 WebSocket 服务器线程"""
        self._ws_thread = threading.Thread(target=self._launch_websocket, daemon=True)
        self._ws_thread.start()

    def _cookies_to_str(self, cookies: list) -> str:
        """将 selenium cookies 列表转为标准 cookie 字符串"""
        return "; ".join([f"{c['name']}={c['value']}" for c in cookies])

    def _verify_browser(self, browser: str) -> None:
        """测试浏览器是否正常工作"""
        t_start: float = time.time()
        self._driver = self._init_driver(headless=False, browser=browser)
        t_driver: float = time.time()
        logging.info("%s 进程已启动（%.1f 秒），正在验证...", browser, t_driver - t_start)

        self._driver.get("about:blank")
        logging.info("%s about:blank 加载完成（%.1f 秒）", browser, time.time() - t_driver)

        self._settings.browser = browser
        global_config["auto_course"]["browser"] = browser
        save_config()

    def _open_website(self) -> None:
        try:
            self._driver.get(self._settings.url["home"])
            logging.info("已打开主页面: %s", self._settings.url["home"])
            if self._settings.restore_cookies and self._settings.user_cookies.strip() != "":
                self._inject_cookies()
                time.sleep(0.5)
                if len(self._settings.url["history"]) > 0:
                    self._driver.get(self._settings.url["history"])
                    logging.info("已打开历史页面: %s", self._settings.url["history"])
                else:
                    logging.warning("历史页面 URL 为空, 无法打开历史页面")
            else:
                logging.info("历史为空或记忆功能未开启, 进入默认登录界面")
                self._driver.get(self._settings.url["login"])
        except WebDriverException as e:
            logging.error("访问页面失败: %s, 请检查网络连接并重启应用", e)

    def refresh_settings(self) -> None:
        """刷新配置"""
        self._settings = load_settings()

    def launch_driver(self) -> None:
        """初始化浏览器驱动"""
        if self._settings.browser == "":
            logging.info("未指定浏览器内核, 尝试依次启动 Firefox、Edge、Chrome")
        else:
            logging.info("尝试启动指定的 %s 浏览器", self._settings.browser)

        for browser in (
            ["Firefox", "Edge", "Chrome"] if self._settings.browser == ""
            else [self._settings.browser]
        ):
            t_attempt: float = time.time()
            try:
                self._verify_browser(browser)
                logging.info("%s 启动成功（总计 %.1f 秒）", browser, time.time() - t_attempt)
                break
            except (NoSuchDriverException, WebDriverException) as e:
                logging.warning("%s 启动失败（%.1f 秒）: %s", browser, time.time() - t_attempt, e)

        if self._driver is None:
            logging.error("所有浏览器内核均启动失败, 请检查浏览器是否已安装")
            return
        self._open_website()

    def launch_script(self) -> None:
        """启动并注入js脚本"""
        self._script_code = self._init_script()
        self._launch_ws_server()

        handles = self._driver.window_handles
        self._driver.switch_to.window(handles[-1])
        time.sleep(2)
        self._driver.execute_script(self._script_code)
        logging.info("js脚本注入成功")

        self._start_script_monitor()

    def pretend_active(self) -> None:
        """模拟鼠标活动, 防止被检测为挂机"""
        def mouse_action():
            while True:
                handles = self._driver.window_handles
                self._driver.switch_to.window(handles[-1])

                # 模拟鼠标滚轮轻微滚动(向下/向上)
                scroll_value = secrets.randbelow(101) - 50  # -50 to 50
                self._driver.execute_script(
                    "window.scrollBy(0, arguments[0]);",
                    scroll_value
                )
                time.sleep(secrets.randbelow(31) + 30)  # 30 to 60
        self._mouse_thread = threading.Thread(target=mouse_action, daemon=True)
        self._mouse_thread.start()

    def driver_quit(self) -> None:
        """关闭浏览器驱动"""
        if self._driver is not None:
            try:
                handles = self._driver.window_handles
                self._driver.switch_to.window(handles[-1])
                if self._settings.restore_cookies:
                    global_config["auto_course"]["user_cookies"] = self._cookies_to_str(
                        self._driver.get_cookies()
                    )
                    global_config["auto_course"]["history_url"] = self._driver.current_url
                    logging.info("已保存最新的 cookies 和 history_url 至配置文件")
                    save_config()

            except WebDriverException:
                logging.error("驱动被人为关闭, 保存 cookies 和 history_url 失败")
            finally:
                self._driver.quit()
                logging.info("浏览器驱动已关闭")
        else:
            logging.info("浏览器驱动未启动")
