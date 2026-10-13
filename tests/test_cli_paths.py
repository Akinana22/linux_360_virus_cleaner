"""测试每次运行的输出目录创建"""

import os

import virus_cleaner.cli as cli


def test_make_run_dir_creates_tmp_timestamp(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "PROJECT_ROOT", str(tmp_path))
    run_dir = cli._make_run_dir("20261013_141525")
    assert run_dir == os.path.join(str(tmp_path), "tmp", "20261013_141525")
    assert os.path.isdir(run_dir)


def test_make_run_dir_distinct_per_timestamp(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "PROJECT_ROOT", str(tmp_path))
    d1 = cli._make_run_dir("20261013_141525")
    d2 = cli._make_run_dir("20261013_150000")
    assert d1 != d2
    assert os.path.isdir(d1) and os.path.isdir(d2)
