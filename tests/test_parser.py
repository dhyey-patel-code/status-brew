from __future__ import annotations
import pytest
from status_brew.parser import (
    _parse_date_range,
    _parse_pto_line,
    _strip_bullet,
    parse_worklog,
)
from status_brew.models import PtoEntry

FIXTURES = "tests/fixtures"


def _lines(text: str) -> list[str]:
    return text.splitlines()


# --- Date range ---

def test_parse_date_range_basic():
    dr = _parse_date_range(_lines("Dates: 22/6-26/6"))
    assert dr is not None
    assert dr.start_day == 22
    assert dr.start_month == 6
    assert dr.end_day == 26
    assert dr.end_month == 6


def test_parse_date_range_missing():
    wl = parse_worklog("- GDD\n    - Did something\n")
    assert wl.date_range is None


def test_parse_date_range_with_spaces():
    dr = _parse_date_range(_lines("Dates: 22/6 - 26/6"))
    assert dr is not None
    assert dr.start_day == 22
    assert dr.end_day == 26


def test_parse_date_range_case_insensitive():
    dr = _parse_date_range(_lines("dates: 1/1-31/12"))
    assert dr is not None
    assert dr.start_month == 1
    assert dr.end_month == 12


# --- Section separation ---

def test_parse_sections_separates_blockers():
    text = "- GDD\n    - Done task\n- Blockers\n    - Something blocked\n"
    wl = parse_worklog(text)
    names = [s.raw_name for s in wl.sections]
    assert "Blockers" not in names
    assert wl.explicit_blockers == ["Something blocked"]


def test_parse_sections_separates_pto():
    text = "- GDD\n    - Done task\n- PTO - 25/6\n"
    wl = parse_worklog(text)
    names = [s.raw_name for s in wl.sections]
    assert not any("PTO" in n for n in names)
    assert len(wl.pto_entries) == 1


def test_parse_sections_basic_structure():
    text = "Dates: 22/6-26/6\n\n- GDD\n    - Item A\n    - Item B\n- TSI\n    - Item C\n"
    wl = parse_worklog(text)
    assert len(wl.sections) == 2
    assert wl.sections[0].raw_name == "GDD"
    assert len(wl.sections[0].items) == 2
    assert wl.sections[1].raw_name == "TSI"
    assert wl.sections[1].items[0].text == "Item C"


# --- PTO parsing ---

def test_parse_pto_single_date():
    entry = _parse_pto_line("PTO - 25/6")
    assert entry.dates == ["25/6"]
    assert entry.note == ""


def test_parse_pto_multi_date():
    entry = _parse_pto_line("PTO - 22/6, 23/6")
    assert entry.dates == ["22/6", "23/6"]
    assert entry.note == ""


def test_parse_pto_three_dates():
    entry = _parse_pto_line("PTO - 22/6, 23/6, 24/6")
    assert entry.dates == ["22/6", "23/6", "24/6"]


def test_parse_pto_no_match_fallback():
    entry = _parse_pto_line("PTO")
    assert entry.dates == []


# --- Bullet stripping ---

def test_strip_bullet_dash():
    assert _strip_bullet("- hello") == "hello"


def test_strip_bullet_star():
    assert _strip_bullet("* hello") == "hello"


def test_strip_bullet_indented():
    assert _strip_bullet("    - hello") == "hello"


# --- Explicit blockers ---

def test_parse_explicit_blockers():
    text = "- Blockers\n    - Issue one\n    - Issue two\n"
    wl = parse_worklog(text)
    assert wl.explicit_blockers == ["Issue one", "Issue two"]


# --- Mixed bullet chars ---

def test_parse_mixed_bullet_chars():
    text = "* GDD\n    * Created dashboard\n"
    wl = parse_worklog(text)
    assert len(wl.sections) == 1
    assert wl.sections[0].items[0].text == "Created dashboard"


# --- Tab indentation ---

def test_parse_tab_indented_items():
    text = "- GDD\n\t- Tab indented item\n"
    wl = parse_worklog(text)
    assert len(wl.sections[0].items) == 1
    assert wl.sections[0].items[0].text == "Tab indented item"


# --- Empty / whitespace input ---

def test_parse_worklog_empty_string_raises():
    with pytest.raises(ValueError, match="empty"):
        parse_worklog("")


def test_parse_worklog_whitespace_only_raises():
    with pytest.raises(ValueError, match="empty"):
        parse_worklog("   \n\n\t\n")
