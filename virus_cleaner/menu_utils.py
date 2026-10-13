"""通用菜单工具：输入获取、标题打印、导航处理。

注意：本工具全流程不刷新终端界面（不调用 clear_screen），
以便用户通过滚动条上翻回顾全部交互信息。
"""

from .logger import log, ask

BACK = "0"       # 返回上一级 / 取消
TO_MAIN = "q"    # 退出程序
VIEW = "s"       # 查看


def print_header(title, width=60):
    log()
    log("=" * width)
    log(f"  {title}")
    log("=" * width)
    log()


def print_step(step):
    log(f"\n>> {step}")


def get_input(prompt, allow_back=True, allow_main=True, allow_view=False):
    """获取非空用户输入。

    Returns:
        用户输入字符串（已 strip）/ BACK / TO_MAIN / VIEW
    """
    hints = []
    if allow_back:
        hints.append("[0]取消")
    if allow_main:
        hints.append("[q]退出")
    if allow_view:
        hints.append("[s]查看")
    display = f"{prompt} ({' '.join(hints)}): " if hints else f"{prompt}: "

    while True:
        value = ask(display).strip()
        if allow_main and value.lower() == "q":
            return TO_MAIN
        if allow_back and value == "0":
            return BACK
        if allow_view and value.lower() == "s":
            return VIEW
        if value == "":
            log("  输入不能为空，请重新输入")
            continue
        return value


def get_input_allow_empty(prompt, allow_back=True, allow_main=True, allow_view=False):
    """获取允许空的用户输入。

    Returns:
        用户输入字符串（已 strip，可为空）/ BACK / TO_MAIN / VIEW
    """
    hints = []
    if allow_back:
        hints.append("[0]取消")
    if allow_main:
        hints.append("[q]退出")
    if allow_view:
        hints.append("[s]查看")
    display = f"{prompt} ({' '.join(hints)}): " if hints else f"{prompt}: "

    while True:
        value = ask(display).strip()
        if allow_main and value.lower() == "q":
            return TO_MAIN
        if allow_back and value == "0":
            return BACK
        if allow_view and value.lower() == "s":
            return VIEW
        return value


def select_from_list(options, prompt="请选择", allow_back=True, allow_main=True,
                     allow_view=False):
    """展示编号列表让用户选择。

    Returns:
        选中项的索引(0-based) / BACK / TO_MAIN / VIEW
    """
    for idx, opt in enumerate(options, start=1):
        log(f"  [{idx}] {opt}")
    if allow_back:
        log("  [0] 取消")
    if allow_main:
        log("  [q] 退出")
    if allow_view:
        log("  [s] 查看")

    while True:
        raw = ask(f"\n{prompt} (输入编号): ").strip()
        if raw.lower() == "q" and allow_main:
            return TO_MAIN
        if raw == "0" and allow_back:
            return BACK
        if raw.lower() == "s" and allow_view:
            return VIEW
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw) - 1
        log("  请输入有效编号")
