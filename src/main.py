"""程序入口"""
import datetime
import logging
import os
import sys
from collections.abc import Callable
from pathlib import Path

# onnxruntime DLL 加载需在 Qt 之前完成，否则可能因 DLL 搜索路径冲突失败
try:
    import onnxruntime  # noqa: F401
except ImportError:
    pass

# 高 DPI 缩放 — 仅启用基本感知，不强制自动缩放（避免与 Windows 系统缩放叠加）
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

from PyQt5.QtCore import Qt, QtMsgType, qInstallMessageHandler
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication

from app import TaskManager, utils
from gui_fluent.main_window import MainWindow


def qt_message_handler(msg_type, _, message):
    """统一 Qt 日志格式到 Python logging"""
    qt_level = {
        QtMsgType.QtDebugMsg: logging.INFO,
        QtMsgType.QtInfoMsg: logging.INFO,
        QtMsgType.QtWarningMsg: logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,
        QtMsgType.QtFatalMsg: logging.CRITICAL
    }.get(msg_type, logging.INFO)
    logging.log(qt_level, "[Qt] %s", message)

def setup_logging() -> None:
    """日志初始化"""
    timestamp: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path: Path = utils.writable_path(
        "data", "log", "py", f"python_{timestamp}.log"
    )

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    qInstallMessageHandler(qt_message_handler)
    logging.info("日志初始化成功(路径: %s)", log_path)

def ensure_files(
    path_dict: dict[str, list[str]],
    path_method: Callable[..., Path],
    task: Callable[[Path], None]
) -> None:
    """载入必要路径并确保所有路径存在"""
    path: list[str]
    for path in path_dict.values():
        task(path_method(*path))

if __name__ == "__main__":
    setup_logging()
    utils.init_config()

    ensure_files(
        utils.global_config.get("path_groups", {}).get("writable", {}),
        utils.writable_path,
        utils.ensure_file
    )
    ensure_files(
        utils.global_config.get("path_groups", {}).get("static", {}),
        utils.static_path,
        utils.check_file
    )

    application = QApplication(sys.argv)
    application.setWindowIcon(QIcon(
        str(utils.static_path("src", "resources", "ico", "the_icon.ico"))
    ))

    font = QFont("Microsoft YaHei", 9)
    application.setFont(font)

    application.setStyleSheet("""
        QWidget, QLabel, QLineEdit, QSpinBox, QComboBox, QPushButton {
            font-family: "Microsoft YaHei", "Microsoft YaHei UI", "SimHei", "Noto Sans CJK SC", sans-serif;
        }
    """)

    backend = TaskManager()
    window = MainWindow(backend)
    window.show()

    application.aboutToQuit.connect(backend.close)
    sys.exit(application.exec_())
