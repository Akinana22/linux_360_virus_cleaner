"""文件浏览器：支持子目录浏览的交互式表格文件选择器（不刷新界面）。"""

import os

from .logger import log, ask
from .menu_utils import print_header, BACK, TO_MAIN

TABLE_EXTENSIONS = {".xlsx", ".xls", ".csv"}


def _is_table_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in TABLE_EXTENSIONS


def _go_parent(path):
    parent = os.path.dirname(path)
    if parent == path:
        return path
    return parent


def browse_files(start_dir):
    """交互式文件浏览器。

    Returns:
        选中的文件完整路径 / BACK / TO_MAIN
    """
    current_dir = os.path.abspath(start_dir)

    while True:
        print_header("文件浏览器")
        log(f"  当前目录: {current_dir}")
        log()

        try:
            entries = sorted(os.listdir(current_dir))
        except PermissionError:
            log("  [错误] 无权限访问该目录")
            ask("  按回车返回上级...")
            return BACK

        dirs = []
        files = []
        for entry in entries:
            full = os.path.join(current_dir, entry)
            if os.path.isdir(full):
                dirs.append(entry)
            elif os.path.isfile(full) and _is_table_file(entry):
                files.append(entry)

        idx = 1
        mapping = {}

        if _go_parent(current_dir) != current_dir:
            log(f"  [{idx}] [目录] .. (上级目录)")
            mapping[idx] = ".."
            idx += 1

        for d in dirs:
            log(f"  [{idx}] [目录] {d}/")
            mapping[idx] = d
            idx += 1

        for f in files:
            log(f"  [{idx}] [文件] {f}")
            mapping[idx] = f
            idx += 1

        log("  [0] 返回上级")
        log("  [q] 退出程序")

        if idx == 1:
            log("\n  (该目录下没有表格文件)")

        raw = ask("\n  请选择 (输入编号): ").strip()
        if raw.lower() == "q":
            return TO_MAIN
        if raw == "0":
            return BACK
        if not raw.isdigit():
            log("  请输入有效编号")
            ask("  按回车继续...")
            continue

        num = int(raw)
        if num not in mapping:
            log("  请输入有效编号")
            ask("  按回车继续...")
            continue

        selected = mapping[num]
        if selected == "..":
            current_dir = _go_parent(current_dir)
            continue

        target_path = os.path.join(current_dir, selected)
        if os.path.isdir(target_path):
            current_dir = target_path
            continue

        confirmed = ask(
            f"\n  已选择: {target_path}\n  确认? (y/n, [0]返回, [q]退出): "
        ).strip().lower()
        if confirmed == "q":
            return TO_MAIN
        if confirmed == "0":
            continue
        if confirmed in ("y", "yes", ""):
            return target_path
