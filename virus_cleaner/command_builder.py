"""删除命令生成：为每条被确认的文件路径生成单独的 rm 命令文本。"""

import os
import posixpath
import shlex
from datetime import datetime

from .report_io import unique_path


def is_safe_delete_path(path):
    """判断路径是否允许作为删除目标（防御性检查）。

    报表路径均为 Linux 绝对路径，故统一按 POSIX 规则规范化。
    """
    if not path or not path.strip():
        return False
    if not path.startswith("/"):
        return False
    if posixpath.normpath(path) == "/":
        return False
    return True


def build_delete_commands(paths, rm="rm"):
    """为每条路径生成单独的 rm 命令。

    Args:
        paths: 文件路径列表
        rm: 删除命令名（默认 rm）

    Returns:
        (commands, rejected)：命令字符串列表、被安全策略拒绝的路径列表。
        命令形如: rm -- '/path/with space/file'
    """
    commands = []
    rejected = []
    for path in paths:
        if not is_safe_delete_path(path):
            rejected.append(path)
            continue
        commands.append(f"{rm} -- {shlex.quote(path)}")
    return commands, rejected


def write_command_file(commands, out_dir, hostname, timestamp=None):
    """把命令写入文本文件，返回文件路径。

    文件名: delete_commands_<hostname>_<YYYYmmdd_HHMMSS>.txt
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_host = hostname.strip() or "unknown"
    name = f"delete_commands_{safe_host}_{timestamp}.txt"
    out_path = unique_path(os.path.join(out_dir, name))

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# 终端: {hostname}\n")
        f.write(f"# 生成时间: {timestamp}\n")
        f.write(f"# 共 {len(commands)} 条删除命令\n")
        for cmd in commands:
            f.write(cmd + "\n")
    return out_path
