# 贡献指南 / 提交说明

感谢参与本项目。请遵循以下约定，保持提交历史清晰、可追溯。

---

## 分支约定

- 主分支为 `main`，始终保持可运行、可发布状态。
- 功能 / 修复请使用独立分支，命名示例：
  - `feat/一次性审批`
  - `fix/终端匹配`
  - `docs/更新说明`

---

## 提交信息规范

- 使用**中文**描述，简洁说明「做了什么」。
- 采用 Conventional Commits 前缀（与历史提交保持一致）：

| 前缀 | 含义 |
| --- | --- |
| `feat:` | 新增功能 |
| `fix:` | 修复缺陷 |
| `docs:` | 文档变更 |
| `chore:` | 构建 / 依赖 / 杂项 |
| `refactor:` | 重构（不改变外部行为） |
| `test:` | 测试相关 |

- **版本发布提交**使用 `vX.Y.Z: 概述` 的格式，正文以要点列表列出主要内容。
- 首个提交使用 `Initial commit`。

示例：

```
feat: 新增按行/一次性审批模式切换

- 逐条确认前询问是否按行审批，默认 y
- n 时一次性列出全部去重信息，仅审批一次
- 未找到的文件统一归入“需手动确认”，不生成删除命令
```

```
v1.0.0: 360 杀毒报表染毒文件清理工具

- 报表转 CSV、按终端筛选、路径去重
- 人工确认后生成并执行逐条 rm 命令
- 零依赖运行与全过程日志
```

---

## 代码规范

- 遵循现有代码风格，优先复用现有模块与工具函数。
- 新增逻辑需配套单元测试（`tests/`，pytest）。
- 不要提交运行时产物：`_lib/`、`*.csv`、`delete_commands_*.txt`、`interaction_*.log`、`*.xlsx`、`*.xls`（已在 `.gitignore` 中忽略）。

---

## 本地验证

提交前请确保测试全部通过：

```bash
python -m pytest tests -q
```

---

## 发布流程

发布由 GitHub Actions 负责（`.github/workflows/release.yml`），产物为
`linux-360-virus-cleaner-vX.Y.Z.zip`（含 `run.py`、`wheels/`、`virus_cleaner/`、
`LICENSE`、`README.md`，不含 `tests/`）。

### 方式一：推送标签自动发布（推荐）

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

### 方式二：手动触发

在仓库 **Actions → Release → Run workflow**，填写版本号（如 `1.0.0`）后运行。

两种方式都会创建标签 `vX.Y.Z` 对应的 Release，并自动生成 release notes。
