"""360 杀毒报表染毒文件清理工具 - 专用单流程。

流程：选报表 → 转 CSV → 检测当前终端 → 按终端筛选去重
      → （按行 / 一次性）人工确认删除 → 生成 rm 命令文本 → 二次确认 → 逐条执行。

说明：全流程不刷新终端界面，所有信息顺序打印，可上滚回顾；
     每一行输出与用户输入都原样写入日志文件。
"""

import os
import sys
from datetime import datetime

from .logger import SessionLogger, set_logger, log, ask
from .menu_utils import BACK, TO_MAIN, print_header, print_step, select_from_list
from .file_browser import browse_files
from .report_io import (
    convert_report_to_csv, read_csv_rows, find_column,
)
from .terminal_filter import (
    get_current_hostname, list_terminals, match_terminal,
    filter_by_terminal, dedup_entries,
)
from .command_builder import build_delete_commands, write_command_file
from .executor import execute_commands

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TERMINAL_COLUMNS = ["终端名称", "终端", "主机名", "hostname", "计算机名"]
FILE_COLUMNS = ["染毒文件", "文件路径", "文件", "路径"]
VIRUS_COLUMNS = ["病毒名", "病毒名称", "威胁名称"]
TYPE_COLUMNS = ["病毒类型", "威胁类型", "类型"]


def _select_column(headers, what):
    """列名不存在时，让用户从表头中手动选择。返回列名 / BACK / TO_MAIN。"""
    log(f"\n  无法自动识别「{what}」列，请手动选择：")
    result = select_from_list(headers, f"请选择「{what}」对应的列")
    if result in (BACK, TO_MAIN):
        return result
    return headers[result]


def _confirm_entries(entries):
    """先询问审批方式，再进入对应确认流程。

    - 按行审批（y，默认）：逐个文件确认；
    - 一次性审批（n）：一次列出全部去重信息，仅审批一次。

    Returns:
        (confirmed_paths, not_found_entries)
    """
    while True:
        ans = ask("是否按行审批? [Y/n]: ").strip().lower()
        if ans in ("", "y", "yes"):
            return _confirm_entries_by_row(entries)
        if ans in ("n", "no"):
            return _confirm_entries_bulk(entries)
        if ans == "q":
            log("  已取消确认流程。")
            return [], []
        log("  请输入 y 或 n。")


def _confirm_entries_by_row(entries):
    """逐条人工确认（按行审批）。

    Returns:
        (confirmed_paths, not_found_entries)
    """
    confirmed = []
    not_found = []
    total = len(entries)

    log()
    log("=" * 60)
    log("  逐条确认（存在的文件默认回车=删除；不存在的文件回车=知悉）")
    log("=" * 60)

    for i, e in enumerate(entries, 1):
        log(f"\n[{i}/{total}] [{e['virus']}] [{e['type']}] {e['file']}")

        if not os.path.isfile(e["file"]):
            log(f"  报表记录的 {e['file']} 未找到，请稍后手动确认")
            ask("  按回车继续...")
            not_found.append(e)
            continue

        ans = ask("  是否删除? [Y/n]（q=退出确认）: ").strip().lower()
        if ans == "q":
            log("  已退出确认流程，保留此前的确认结果。")
            break
        if ans in ("", "y", "yes"):
            confirmed.append(e["file"])
            log("  → 确认删除")
        else:
            log("  → 已跳过")

    return confirmed, not_found


def _confirm_entries_bulk(entries):
    """一次性审批：列出全部去重信息，仅审批一次。

    本机不存在的文件直接归入“需手动确认”，不再逐条回车。
    默认回车=不删除，需显式输入 y 才删除全部存在的文件。

    Returns:
        (confirmed_paths, not_found_entries)
    """
    total = len(entries)

    log()
    log("=" * 60)
    log("  一次性确认（默认回车=不删除；需显式输入 y 才删除全部存在的文件）")
    log("=" * 60)

    existing = []
    not_found = []
    for i, e in enumerate(entries, 1):
        exists = os.path.isfile(e["file"])
        suffix = "" if exists else "（未找到）"
        log(f"[{i}/{total}] [{e['virus']}] [{e['type']}] {e['file']}{suffix}")
        if exists:
            existing.append(e)
        else:
            not_found.append(e)

    log(f"\n  本机存在的文件: {len(existing)} 个；未找到（需手动确认）: {len(not_found)} 个")

    if not existing:
        log("  没有本机存在的文件，全部归入“需手动确认”，不生成删除命令。")
        return [], not_found

    ans = ask(f"  确认删除以上存在的 {len(existing)} 个文件? [N/y]: ").strip().lower()
    if ans in ("y", "yes"):
        confirmed = [e["file"] for e in existing]
        log(f"  → 已确认删除 {len(confirmed)} 个文件")
    else:
        confirmed = []
        log("  → 未删除任何文件")

    return confirmed, not_found


def _run(run_dir, host):
    print_header("360 杀毒报表 - 染毒文件清理工具")
    log(f"  本次输出目录: {run_dir}")
    log("  （本流程不刷新界面，可上滚查看历史信息）")

    print_step("步骤 1/6: 选择 360 杀毒导出的报表文件")
    report_path = browse_files(PROJECT_ROOT)
    if report_path in (BACK, TO_MAIN):
        log("\n  已取消，程序退出。")
        return

    print_step("步骤 2/6: 转换报表为 CSV")
    base = os.path.splitext(os.path.basename(report_path))[0]
    csv_path = convert_report_to_csv(report_path, os.path.join(run_dir, base + ".csv"))
    log(f"  已生成 CSV: {csv_path}")

    headers, rows = read_csv_rows(csv_path)
    if not headers:
        log("  [错误] 报表为空，无法继续。")
        return

    terminal_col = find_column(headers, TERMINAL_COLUMNS)
    if terminal_col is None:
        terminal_col = _select_column(headers, "终端名称")
        if terminal_col in (BACK, TO_MAIN):
            log("\n  已取消，程序退出。")
            return

    file_col = find_column(headers, FILE_COLUMNS)
    if file_col is None:
        file_col = _select_column(headers, "染毒文件")
        if file_col in (BACK, TO_MAIN):
            log("\n  已取消，程序退出。")
            return

    virus_col = find_column(headers, VIRUS_COLUMNS)
    type_col = find_column(headers, TYPE_COLUMNS)

    print_step("步骤 3/6: 识别当前电脑所属终端")
    log(f"  当前主机名 (hostname): {host}")

    terminals = list_terminals(headers, rows, terminal_col)
    if not terminals:
        log("  [错误] 报表中没有可用的终端名称。")
        return

    terminal = match_terminal(host, terminals)
    if terminal is None:
        log("  未能自动匹配到唯一终端，请手动选择：")
        result = select_from_list(terminals, "请选择当前电脑对应的终端")
        if result in (BACK, TO_MAIN):
            log("\n  已取消，程序退出。")
            return
        terminal = terminals[result]

    log(f"  → 当前终端: {terminal}")

    print_step("步骤 4/6: 按终端筛选并去重")
    matched = filter_by_terminal(headers, rows, terminal, terminal_col)
    entries = dedup_entries(headers, matched, file_col, virus_col, type_col)
    log(f"  匹配记录: {len(matched)} 条，按路径去重后: {len(entries)} 条")
    if not entries:
        log("  没有属于当前终端的染毒文件记录，程序结束。")
        return

    print_step("步骤 5/6: 人工确认删除（按行 / 一次性）")
    confirmed, not_found = _confirm_entries(entries)
    log(f"\n  已确认删除: {len(confirmed)} 条；未找到（需手动确认）: {len(not_found)} 条")

    print_step("步骤 6/6: 生成删除命令并二次确认")
    commands, rejected = build_delete_commands(confirmed)
    for path in rejected:
        log(f"  [跳过] 不安全的路径，已忽略: {path!r}")

    if not commands:
        log("  没有需要执行的删除命令，程序结束。")
    else:
        cmd_file = write_command_file(commands, run_dir, host)
        log(f"\n  生成的删除命令（共 {len(commands)} 条）:")
        for cmd in commands:
            log(f"    {cmd}")
        log(f"\n  命令已保存到: {cmd_file}")

        ans = ask(
            f"\n  确认执行以上 {len(commands)} 条删除命令? [N/y]: "
        ).strip().lower()
        if ans in ("y", "yes"):
            log("\n  开始执行删除...")
            results = execute_commands(commands)
            success = 0
            for r in results:
                if r["returncode"] == 0:
                    success += 1
                    log(f"  [成功] {r['command']}")
                else:
                    log(f"  [失败] {r['command']} (退出码 {r['returncode']})")
                    if r["stderr"].strip():
                        log(f"         {r['stderr'].strip()}")
            log(f"\n  执行完成：成功 {success} / {len(results)}")
        else:
            log("\n  已取消执行。命令已保存到文件，可稍后手动核对执行。")

    if not_found:
        log("\n以下文件在报表中记录，但本机未找到，请稍后手动确认：")
        for e in not_found:
            log(f"  [{e['virus']}] [{e['type']}] {e['file']}")

    log("\n流程结束。")


def _make_run_dir(timestamp):
    """创建本次运行的独立输出目录 <项目根>/tmp/<timestamp>，返回其路径。"""
    run_dir = os.path.join(PROJECT_ROOT, "tmp", timestamp)
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def main():
    host = get_current_hostname()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = _make_run_dir(timestamp)
    log_path = os.path.join(run_dir, f"interaction_{host}_{timestamp}.log")

    logger = SessionLogger(log_path)
    set_logger(logger)
    try:
        logger.write(f"# 会话开始: {timestamp}  主机: {host}")
        _run(run_dir, host)
    except KeyboardInterrupt:
        logger.write("\n# 用户中断，程序退出。")
    finally:
        logger.close()
    sys.exit(0)


if __name__ == "__main__":
    main()
