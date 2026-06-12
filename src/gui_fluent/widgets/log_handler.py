from PyQt5.QtCore import QObject, pyqtSignal
import logging


class LogSignal(QObject):
    message = pyqtSignal(str)


class LogHandler(logging.Handler):
    def __init__(self, signal: LogSignal):
        super().__init__()
        self.signal = signal

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        self.signal.message.emit(msg)
