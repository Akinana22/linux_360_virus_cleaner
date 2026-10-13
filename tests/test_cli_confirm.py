"""测试确认逻辑：按行审批 / 一次性审批

- 按行：默认回车删除、未找到仅需知悉、跳过与退出
- 一次性：一次列出全部信息，默认不删除，显式 y 才删除存在的文件
"""

import os

import virus_cleaner.cli as cli
from virus_cleaner.logger import SessionLogger, set_logger, get_logger


def _setup_logger(tmp_path):
    set_logger(SessionLogger(os.path.join(tmp_path, "log.txt")))


def _entries(*paths):
    return [{"file": p, "virus": "V", "type": "其它"} for p in paths]


def _answers(monkeypatch, *seq):
    it = iter(seq)
    monkeypatch.setattr("builtins.input", lambda: next(it))


def test_mode_row_default_y(tmp_path, monkeypatch):
    _setup_logger(tmp_path)
    monkeypatch.setattr(cli.os.path, "isfile", lambda p: p == "/exists/a.exe")
    # 首项空=默认按行审批；然后 存在文件回车删除、未找到回车知悉
    _answers(monkeypatch, "", "", "")

    confirmed, not_found = cli._confirm_entries(
        _entries("/exists/a.exe", "/missing/b.exe"))
    get_logger().close()

    assert confirmed == ["/exists/a.exe"]
    assert [e["file"] for e in not_found] == ["/missing/b.exe"]


def test_mode_row_explicit_y(tmp_path, monkeypatch):
    _setup_logger(tmp_path)
    monkeypatch.setattr(cli.os.path, "isfile", lambda p: True)
    _answers(monkeypatch, "y", "n")

    confirmed, not_found = cli._confirm_entries(_entries("/a.exe"))
    get_logger().close()

    assert confirmed == []
    assert not_found == []


def test_row_skip_with_n(tmp_path, monkeypatch):
    _setup_logger(tmp_path)
    monkeypatch.setattr(cli.os.path, "isfile", lambda p: True)
    _answers(monkeypatch, "", "n")

    confirmed, not_found = cli._confirm_entries(_entries("/a.exe"))
    get_logger().close()

    assert confirmed == []
    assert not_found == []


def test_row_quit_with_q(tmp_path, monkeypatch):
    _setup_logger(tmp_path)
    monkeypatch.setattr(cli.os.path, "isfile", lambda p: True)
    _answers(monkeypatch, "", "y", "q")

    confirmed, not_found = cli._confirm_entries(_entries("/a.exe", "/b.exe"))
    get_logger().close()

    assert confirmed == ["/a.exe"]
    assert not_found == []


def test_mode_bulk_approve(tmp_path, monkeypatch):
    _setup_logger(tmp_path)
    monkeypatch.setattr(cli.os.path, "isfile", lambda p: p == "/exists/a.exe")
    _answers(monkeypatch, "n", "y")

    confirmed, not_found = cli._confirm_entries(
        _entries("/exists/a.exe", "/missing/b.exe"))
    get_logger().close()

    assert confirmed == ["/exists/a.exe"]
    assert [e["file"] for e in not_found] == ["/missing/b.exe"]


def test_mode_bulk_default_no(tmp_path, monkeypatch):
    _setup_logger(tmp_path)
    monkeypatch.setattr(cli.os.path, "isfile", lambda p: True)
    _answers(monkeypatch, "n", "")

    confirmed, not_found = cli._confirm_entries(_entries("/a.exe"))
    get_logger().close()

    assert confirmed == []
    assert not_found == []


def test_mode_bulk_all_missing_no_prompt(tmp_path, monkeypatch):
    _setup_logger(tmp_path)
    monkeypatch.setattr(cli.os.path, "isfile", lambda p: False)
    # 只回答模式问题；全部未找到时不再询问审批
    _answers(monkeypatch, "n")

    confirmed, not_found = cli._confirm_entries(_entries("/a.exe", "/b.exe"))
    get_logger().close()

    assert confirmed == []
    assert [e["file"] for e in not_found] == ["/a.exe", "/b.exe"]


def test_mode_bulk_quit(tmp_path, monkeypatch):
    _setup_logger(tmp_path)
    monkeypatch.setattr(cli.os.path, "isfile", lambda p: True)
    _answers(monkeypatch, "n", "q")

    confirmed, not_found = cli._confirm_entries(_entries("/a.exe"))
    get_logger().close()

    assert confirmed == []
    assert not_found == []
