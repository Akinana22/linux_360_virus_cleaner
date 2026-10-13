"""终端识别与筛选：检测当前主机、匹配报表终端、按终端筛选并去重。

报表中「终端名称」由 360 杀毒客户端从 Linux hostname 拉取，通常为完整名
（如 gusubin.njqj.local），与 socket.gethostname() 一致，因此优先精确匹配。
"""

import socket

from .report_io import cell


def get_current_hostname():
    """返回当前主机名（原样，未做大小写转换）。"""
    return socket.gethostname().strip()


def list_terminals(headers, rows, column):
    """按出现顺序列出报表中所有非空终端名称（去重）。"""
    seen = []
    seen_set = set()
    for row in rows:
        name = cell(row, headers, column).strip()
        if name and name not in seen_set:
            seen_set.add(name)
            seen.append(name)
    return seen


def match_terminal(hostname, terminals):
    """根据当前 hostname 在终端列表中匹配唯一终端。

    匹配顺序：
      1. 忽略大小写的精确匹配；
      2. 宽松匹配（短名相同，或一方是另一方的点分前缀）；
    只有唯一结果才返回该终端名，否则返回 None（交由调用方手动选择）。
    """
    if not hostname:
        return None

    host = hostname.strip().lower()

    for term in terminals:
        if term.strip().lower() == host:
            return term

    short = host.split(".")[0]
    candidates = []
    for term in terminals:
        tl = term.strip().lower()
        tshort = tl.split(".")[0]
        if (tshort == short
                or tl.startswith(host + ".")
                or host.startswith(tl + ".")):
            candidates.append(term)

    if len(candidates) == 1:
        return candidates[0]
    return None


def filter_by_terminal(headers, rows, terminal, column):
    """筛选出「终端名称」等于指定终端的行。"""
    key = terminal.strip().lower()
    matched = []
    for row in rows:
        if cell(row, headers, column).strip().lower() == key:
            matched.append(row)
    return matched


def dedup_entries(headers, rows, file_column, virus_column=None, type_column=None):
    """按「染毒文件」路径去重，保留首次出现的病毒名/病毒类型。

    Args:
        headers: 表头列表
        rows: 数据行列表
        file_column: 染毒文件列名
        virus_column: 病毒名列名（可选）
        type_column: 病毒类型列名（可选）

    Returns:
        列表，元素为 dict: {"file", "virus", "type"}
    """
    entries = []
    seen = set()
    for row in rows:
        path = cell(row, headers, file_column).strip()
        if not path or path in seen:
            continue
        seen.add(path)
        entries.append({
            "file": path,
            "virus": cell(row, headers, virus_column) if virus_column else "",
            "type": cell(row, headers, type_column) if type_column else "",
        })
    return entries
