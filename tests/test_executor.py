"""测试命令执行（注入假 runner，不真实删除）"""

from virus_cleaner.executor import execute_commands


def test_execute_collects_results():
    calls = []

    def fake_runner(command):
        calls.append(command)
        if "b" in command:
            return 1, "", "rm: cannot remove"
        return 0, "", ""

    commands = ["rm -- /home/a.exe", "rm -- /home/b.exe"]
    results = execute_commands(commands, runner=fake_runner)

    assert calls == commands
    assert len(results) == 2
    assert results[0]["returncode"] == 0
    assert results[1]["returncode"] == 1
    assert "cannot remove" in results[1]["stderr"]
    assert results[1]["command"] == "rm -- /home/b.exe"


def test_execute_empty():
    assert execute_commands([], runner=lambda c: (0, "", "")) == []
