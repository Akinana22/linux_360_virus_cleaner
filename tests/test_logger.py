"""测试会话日志原样记录"""

import os

from virus_cleaner.logger import SessionLogger, set_logger, get_logger, log, ask


def test_write_and_raw(tmp_path):
    path = os.path.join(tmp_path, "log.txt")
    logger = SessionLogger(path)
    logger.write("line1")
    logger.write_raw("prompt: ")
    logger.write("")
    logger.close()

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == "line1\nprompt: \n"


def test_ask_records_prompt_and_answer(tmp_path, monkeypatch):
    path = os.path.join(tmp_path, "log.txt")
    logger = SessionLogger(path)
    monkeypatch.setattr("builtins.input", lambda: "y")
    answer = logger.ask("是否删除? [Y/n]: ")
    logger.close()

    assert answer == "y"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == "是否删除? [Y/n]: y\n"


def test_module_level_logger(tmp_path, monkeypatch):
    path = os.path.join(tmp_path, "log.txt")
    set_logger(SessionLogger(path))
    monkeypatch.setattr("builtins.input", lambda: "x")
    try:
        assert get_logger() is not None
        log("hello")
        answer = ask("ask: ")
        assert answer == "x"
    finally:
        get_logger().close()
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == "hello\nask: x\n"
