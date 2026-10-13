"""报表读写：将 360 杀毒导出的报表转换为 CSV，并读取报表内容。

转换实现参照 python_excel_tools 项目：openpyxl 只读迭代写出 utf-8-sig CSV。
"""

import csv
import os


def unique_path(path):
    """若路径已存在，累加 (1)(2)... 直到不重名。"""
    if not os.path.exists(path):
        return path
    dir_name = os.path.dirname(path)
    base = os.path.splitext(os.path.basename(path))[0]
    ext = os.path.splitext(os.path.basename(path))[1]
    i = 1
    while True:
        candidate = os.path.join(dir_name, f"{base}({i}){ext}")
        if not os.path.exists(candidate):
            return candidate
        i += 1


def convert_report_to_csv(file_path, output_path=None, encoding="utf-8-sig"):
    """将报表（xlsx/xls/csv）转换为 CSV。

    Args:
        file_path: 源文件路径
        output_path: 输出 CSV 路径，None 则生成同名 .csv（自动避免覆盖）
        encoding: 输出编码

    Returns:
        生成的 CSV 文件路径
    """
    ext = os.path.splitext(file_path)[1].lower()

    if output_path is None:
        dir_name = os.path.dirname(os.path.abspath(file_path))
        base = os.path.splitext(os.path.basename(file_path))[0]
        output_path = unique_path(os.path.join(dir_name, f"{base}.csv"))

    if ext == ".csv":
        with open(file_path, "r", encoding="utf-8-sig", newline="") as f_in:
            rows = list(csv.reader(f_in))
        with open(output_path, "w", encoding=encoding, newline="") as f_out:
            csv.writer(f_out).writerows(rows)
        return output_path

    if ext == ".xls":
        import xlrd
        wb = xlrd.open_workbook(file_path)
        ws = wb.sheet_by_index(0)
        with open(output_path, "w", encoding=encoding, newline="") as f_out:
            writer = csv.writer(f_out)
            for r in range(ws.nrows):
                writer.writerow([ws.cell_value(r, c) for c in range(ws.ncols)])
        return output_path

    import openpyxl
    # 注意：部分 360 导出的 xlsx 工作表 dimension 元数据残缺，
    # read_only 模式会据此截断数据，故这里使用普通模式加载。
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb.active
    with open(output_path, "w", encoding=encoding, newline="") as f_out:
        writer = csv.writer(f_out)
        for row in ws.iter_rows(values_only=True):
            writer.writerow(row)
    wb.close()
    return output_path


def read_csv_rows(csv_path):
    """读取 CSV，返回 (表头列表, 数据行列表)。"""
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        return [], []
    headers = rows[0]
    data = [r for r in rows[1:]]
    return headers, data


def find_column(headers, candidates):
    """在表头中按候选名称查找列，返回列名或 None。"""
    for name in candidates:
        if name in headers:
            return name
    return None


def cell(row, headers, column):
    """按列名安全读取某行单元格，越界或列不存在返回空字符串。"""
    if column not in headers:
        return ""
    idx = headers.index(column)
    if idx >= len(row):
        return ""
    value = row[idx]
    return "" if value is None else str(value)
