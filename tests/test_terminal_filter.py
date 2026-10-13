"""测试终端匹配、筛选与去重"""

from virus_cleaner.terminal_filter import (
    get_current_hostname, list_terminals, match_terminal,
    filter_by_terminal, dedup_entries,
)

HEADERS = ["终端名称", "病毒名", "病毒类型", "染毒文件"]
ROWS = [
    ["gusubin.njqj.local", "V1", "其它", "/home/a.exe"],
    ["gusubin.njqj.local", "V1", "其它", "/home/a.exe"],
    ["gusubin.njqj.local", "V2", "木马", "/home/b.exe"],
    ["xumin.njqj.local", "V3", "其它", "/opt/c.exe"],
]


class TestMatchTerminal:
    def test_exact_match(self):
        terms = ["gusubin.njqj.local", "xumin.njqj.local"]
        assert match_terminal("gusubin.njqj.local", terms) == "gusubin.njqj.local"

    def test_case_insensitive(self):
        terms = ["GuSubin.NJQJ.local"]
        assert match_terminal("gusubin.njqj.local", terms) == "GuSubin.NJQJ.local"

    def test_short_name_fallback(self):
        terms = ["gusubin.njqj.local"]
        assert match_terminal("gusubin", terms) == "gusubin.njqj.local"

    def test_ambiguous_returns_none(self):
        terms = ["gusubin.a.local", "gusubin.b.local"]
        assert match_terminal("gusubin", terms) is None

    def test_no_match_returns_none(self):
        terms = ["other.njqj.local"]
        assert match_terminal("nobody", terms) is None


class TestFilterAndDedup:
    def test_list_terminals(self):
        assert list_terminals(HEADERS, ROWS, "终端名称") == [
            "gusubin.njqj.local", "xumin.njqj.local",
        ]

    def test_filter_by_terminal(self):
        matched = filter_by_terminal(HEADERS, ROWS, "gusubin.njqj.local", "终端名称")
        assert len(matched) == 3

    def test_dedup_by_path_keeps_first(self):
        matched = filter_by_terminal(HEADERS, ROWS, "gusubin.njqj.local", "终端名称")
        entries = dedup_entries(HEADERS, matched, "染毒文件", "病毒名", "病毒类型")
        assert [e["file"] for e in entries] == ["/home/a.exe", "/home/b.exe"]
        assert entries[0]["virus"] == "V1"
        assert entries[1]["type"] == "木马"

    def test_get_current_hostname_nonempty(self):
        assert isinstance(get_current_hostname(), str)
        assert get_current_hostname() != ""
