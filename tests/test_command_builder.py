"""测试删除命令生成与命令文件写入"""

import os
import shlex

from virus_cleaner.command_builder import (
    is_safe_delete_path, build_delete_commands, write_command_file,
)


class TestSafePath:
    def test_valid_absolute(self):
        assert is_safe_delete_path("/home/a.exe") is True

    def test_reject_empty(self):
        assert is_safe_delete_path("") is False
        assert is_safe_delete_path("   ") is False

    def test_reject_relative(self):
        assert is_safe_delete_path("home/a.exe") is False

    def test_reject_root(self):
        assert is_safe_delete_path("/") is False
        assert is_safe_delete_path("/../") is False


class TestBuildDeleteCommands:
    def test_one_command_per_path(self):
        paths = ["/home/a.exe", "/home/b.exe"]
        commands, rejected = build_delete_commands(paths)
        assert commands == ["rm -- /home/a.exe", "rm -- /home/b.exe"]
        assert rejected == []

    def test_quotes_paths_with_spaces_and_quotes(self):
        paths = ["/home/a b.exe", "/home/it's.dll"]
        commands, rejected = build_delete_commands(paths)
        assert rejected == []
        assert commands[0] == "rm -- " + shlex.quote("/home/a b.exe")
        assert commands[1] == "rm -- " + shlex.quote("/home/it's.dll")
        assert "'" in commands[1]

    def test_rejects_unsafe(self):
        commands, rejected = build_delete_commands(["/home/a.exe", "/", "rel.exe"])
        assert commands == ["rm -- /home/a.exe"]
        assert rejected == ["/", "rel.exe"]


class TestWriteCommandFile:
    def test_write_file(self, tmp_path):
        commands = ["rm -- /home/a.exe", "rm -- /home/b.exe"]
        path = write_command_file(commands, str(tmp_path), "myhost",
                                  timestamp="20260101_000000")
        assert os.path.basename(path) == "delete_commands_myhost_20260101_000000.txt"
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        assert "rm -- /home/a.exe" in lines
        assert "rm -- /home/b.exe" in lines
        assert any(line.startswith("#") for line in lines)

    def test_write_file_no_overwrite(self, tmp_path):
        commands = ["rm -- /home/a.exe"]
        p1 = write_command_file(commands, str(tmp_path), "h", timestamp="t")
        p2 = write_command_file(commands, str(tmp_path), "h", timestamp="t")
        assert p1 != p2
