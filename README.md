# linux_360_virus_cleaner

将 **360 杀毒导出的问题文件报表（Excel）** 转换为 CSV，自动识别当前电脑对应的
终端，筛选出属于本机的染毒文件，并**逐条人工确认后**生成并执行删除命令。

面向 Linux（国产桌面 / 信创环境）设计，**零依赖**运行：无需 pip、venv、apt 或联网。

---

## 功能特性

- **报表转 CSV**：支持 `.xlsx` / `.xls` / `.csv` 输入，自动输出为同名 CSV（重名自动追加序号）。
- **当前终端识别**：依据报表「终端名称」列，用 `socket.gethostname()` 精确匹配当前主机；
  匹配不到或存在歧义时可从终端列表中手动选择。
- **按终端筛选**：只处理属于本机的记录，不误删其他电脑的文件。
- **路径去重**：依据「染毒文件」路径去重，同一路径仅处理一次。
- **两种审批模式**：
  - **按行审批（默认 y）**：逐个文件询问，存在文件回车即删除，不存在的文件回车知悉；
    支持 `a` 全部删除、`q` 退出确认。
  - **一次性审批（n）**：一次列出全部去重信息，仅审批一次即可进入命令环节（默认不删除，需显式 `y`）。
- **命令预览与二次确认**：为每条被确认的路径单独生成 `rm -- '<路径>'` 命令文本，
  展示并保存为文件，用户再次确认后才逐条执行。
- **安全兜底**：拒绝空路径、相对路径、根目录 `/` 等危险目标；不存在的文件只提示、不生成删除命令。
- **全过程日志**：界面不刷新、可上滚回顾；所有输出与输入原样写入 `interaction_<主机>_<时间戳>.log`。

---

## 环境要求

- 操作系统：Linux（在任意支持 Python 3 的平台亦可运行逻辑，但按 POSIX 路径处理）
- Python：**3.6+**（仅需标准库 `zipfile` 即可完成依赖解压）
- 依赖：`openpyxl`、`et_xmlfile`、`xlrd`（已随 `wheels/` 打包，首次运行自动解压到 `_lib/`，无需安装）

---

## 快速开始

```bash
# 首次运行会自动解压依赖（仅此一次）
python3 run.py
```

之后每次直接运行 `python3 run.py` 即可进入交互流程。

---

## 使用流程

```
步骤 1/6  选择 360 杀毒导出的报表文件（内置文件浏览器）
步骤 2/6  转换报表为 CSV
步骤 3/6  识别当前电脑所属终端（hostname 自动匹配 / 手动选择）
步骤 4/6  按终端筛选并按路径去重
步骤 5/6  人工确认删除
           - 是否按行审批? [Y/n]
             y（默认）= 逐条确认
             n        = 一次性列出全部去重信息，仅审批一次
步骤 6/6  生成删除命令文本 → 展示 → 二次确认 → 逐条执行
```

- 存在文件：`是否删除? [Y/n]`，**回车默认删除**；`n` 跳过；`a` 全部删除；`q` 退出确认。
- 不存在文件：提示 `报表记录的 <路径> 未找到，请稍后手动确认`，回车知悉，不进入删除命令。
- 执行前会把每条命令写入 `delete_commands_<主机>_<时间戳>.txt`，便于留档与复核。

---

## 项目结构

```
run.py                        # 零依赖启动引导（解压 wheels/ → _lib/，启动 CLI）
wheels/                       # 内置依赖（openpyxl / et_xmlfile / xlrd）
virus_cleaner/
  cli.py                      # 专用单流程编排
  report_io.py                # 报表转 CSV、读取、列定位
  terminal_filter.py          # hostname 检测、终端匹配、筛选、去重
  command_builder.py          # 逐条 rm 命令生成、命令文件写入、安全校验
  executor.py                 # 逐条执行命令并收集结果
  logger.py                   # 会话日志（原样记录）
  menu_utils.py               # 菜单/输入/导航工具
  file_browser.py             # 交互式文件浏览器
tests/                        # pytest 测试
```

---

## 测试

```bash
python -m pytest tests -q
```

测试通过 `tests/conftest.py` 将 `wheels/` 中的依赖直接以 zip 形式加入 `sys.path`，
无需预先安装 `openpyxl`；仅需本机已安装 `pytest`。

---

## 发布

发布流程通过 GitHub Actions 完成（`.github/workflows/release.yml`）：

- **打标签自动发布**：推送形如 `v1.0.0` 的标签后自动打包并创建 Release。
- **手动触发**：在 Actions 页面手动运行 `Release` 工作流并填写版本号。

发布产物为 `linux-360-virus-cleaner-vX.Y.Z.zip`，包含 `run.py`、`wheels/`、
`virus_cleaner/`、`LICENSE`、`README.md`（不含 `tests/`）。

```bash
git tag v1.0.0
git push origin v1.0.0
```

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 许可证

本项目采用 **GNU General Public License v3.0**，详见 [LICENSE](LICENSE)。
