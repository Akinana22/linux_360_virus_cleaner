"""命令执行：逐条执行 rm 命令并收集每条结果。"""

import subprocess


def _default_runner(command):
    """默认执行器：通过 shell 执行单条命令。

    Returns:
        (returncode, stdout, stderr)
    """
    proc = subprocess.run(
        command, shell=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return proc.returncode, proc.stdout, proc.stderr


def execute_commands(commands, runner=None):
    """逐条执行命令。

    Args:
        commands: 命令字符串列表
        runner: 可选，签名 runner(command) -> (returncode, stdout, stderr)，
                默认通过 shell 执行。注入假 runner 便于测试。

    Returns:
        结果列表，元素为 dict: {"command", "returncode", "stdout", "stderr"}
    """
    if runner is None:
        runner = _default_runner

    results = []
    for command in commands:
        returncode, stdout, stderr = runner(command)
        results.append({
            "command": command,
            "returncode": returncode,
            "stdout": stdout or "",
            "stderr": stderr or "",
        })
    return results
