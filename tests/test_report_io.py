"""测试报表转换与读取"""

import csv
import os

import openpyxl

from virus_cleaner.report_io import (
    convert_report_to_csv, read_csv_rows, find_column, cell, unique_path,
)


def _make_xlsx(rows, path):
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet()
    for row in rows:
        ws.append(row)
    wb.save(path)
    wb.close()


HEADERS = ["时间", "终端名称", "病毒名", "病毒类型", "染毒文件"]
ROWS = [
    ["2026-09-28 14:47:13", "gusubin.njqj.local", "V1", "其它", "/home/a.exe"],
    ["2026-09-28 14:47:13", "xumin.njqj.local", "V2", "木马", "/home/b.exe"],
]


class TestConvertReportToCsv:
    def test_xlsx_to_csv(self, tmp_path):
        src = os.path.join(tmp_path, "report.xlsx")
        _make_xlsx([HEADERS] + ROWS, src)
        out = convert_report_to_csv(src)
        assert out.endswith(".csv")
        assert os.path.exists(out)
        headers, rows = read_csv_rows(out)
        assert headers == HEADERS
        assert len(rows) == 2
        assert rows[0][-1] == "/home/a.exe"

    def test_no_overwrite_with_unique_path(self, tmp_path):
        src = os.path.join(tmp_path, "report.xlsx")
        _make_xlsx([HEADERS] + ROWS, src)
        first = convert_report_to_csv(src)
        second = convert_report_to_csv(src)
        assert first != second
        assert os.path.exists(second)

    def test_csv_to_csv(self, tmp_path):
        src = os.path.join(tmp_path, "in.csv")
        with open(src, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(HEADERS)
            w.writerows(ROWS)
        out = os.path.join(tmp_path, "out.csv")
        convert_report_to_csv(src, out)
        _, rows = read_csv_rows(out)
        assert len(rows) == 2


class TestHelpers:
    def test_find_column(self):
        assert find_column(HEADERS, ["终端名称"]) == "终端名称"
        assert find_column(HEADERS, ["不存在", "染毒文件"]) == "染毒文件"
        assert find_column(HEADERS, ["没有"]) is None

    def test_cell_out_of_range(self):
        assert cell(["a"], ["x", "y"], "y") == ""
        assert cell(["a", "b"], ["x", "y"], "y") == "b"
        assert cell(["a", "b"], ["x", "y"], "z") == ""

    def test_unique_path(self, tmp_path):
        p = os.path.join(tmp_path, "file.csv")
        with open(p, "w", encoding="utf-8") as f:
            f.write("x")
        assert unique_path(p) == os.path.join(tmp_path, "file(1).csv")
