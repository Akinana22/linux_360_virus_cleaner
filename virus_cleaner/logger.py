"""会话日志：将终端输出与用户输入原样记录到日志文件。

全流程不刷新界面，所有信息顺序打印，可上滚回顾；
同时每一行输出（含提示符）与用户输入都原样写入日志文件。
"""

import sys


class SessionLogger:
    """把 print 输出和 input 输入原样 tee 到日志文件。"""

    def __init__(self, log_path):
        self.log_path = log_path
        self._fh = open(log_path, "w", encoding="utf-8")

    def write(self, text=""):
        """输出一行文本（终端 + 日志），日志追加换行。"""
        print(text)
        self._fh.write(str(text) + "\n")
        self._fh.flush()

    def write_raw(self, text):
        """输出不带换行的文本（终端 + 日志）。"""
        print(text, end="")
        self._fh.write(str(text))
        self._fh.flush()

    def ask(self, prompt=""):
        """显示提示符并读取用户输入，提示与输入原样写入日志。

        Returns:
            用户输入的原始字符串（未 strip）。
        """
        self.write_raw(prompt)
        try:
            answer = input()
        except (EOFError, KeyboardInterrupt):
            self.write("")
            self.close()
            sys.exit(0)
        self._fh.write(answer + "\n")
        self._fh.flush()
        return answer

    def close(self):
        try:
            self._fh.close()
        except Exception:
            pass


_LOGGER = None


def set_logger(logger):
    global _LOGGER
    _LOGGER = logger


def get_logger():
    return _LOGGER


def log(text=""):
    if _LOGGER is not None:
        _LOGGER.write(text)
    else:
        print(text)


def ask(prompt=""):
    if _LOGGER is not None:
        return _LOGGER.ask(prompt)
    return input(prompt)
