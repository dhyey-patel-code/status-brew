from __future__ import annotations
import pytest
from status_brew.classifier import (
    WORKSTREAM_ALIASES,
    classify_worklog,
    is_blocker_text,
    normalize_workstream,
)
from status_brew.models import WorkItem, WorkLog, WorkSection


def _make_worklog(sections: list[WorkSection]) -> WorkLog:
    return WorkLog(date_range=None, sections=sections, pto_entries=[], explicit_blockers=[])


def _make_section(name: str, items: list[str]) -> WorkSection:
    return WorkSection(
        raw_name=name,
        canonical_name=name,
        items=[WorkItem(text=t) for t in items],
    )


# --- normalize_workstream ---

def test_normalize_exact_canonical():
    assert normalize_workstream("GDD") == "GDD"


def test_normalize_alias_lowercase():
    assert normalize_workstream("global due diligence") == "GDD"


def test_normalize_case_insensitive():
    assert normalize_workstream("Global DD") == "GDD"


def test_normalize_unknown_returns_none():
    assert normalize_workstream("foobar") is None


def test_normalize_all_workstreams():
    for canonical, aliases in WORKSTREAM_ALIASES.items():
        for alias in aliases:
            assert normalize_workstream(alias) == canonical, f"alias {alias!r} failed"


# --- is_blocker_text ---

def test_is_blocker_keyword_waiting_on():
    assert is_blocker_text("waiting on approval from team") is True


def test_is_blocker_keyword_blocked():
    assert is_blocker_text("task is blocked by infra team") is True


def test_is_blocker_multi_keyword():
    assert is_blocker_text("task is stalled and delayed") is True


def test_is_blocker_no_match():
    assert is_blocker_text("completed GDD dashboard successfully") is False


def test_is_blocker_case_insensitive():
    assert is_blocker_text("Task is BLOCKED") is True


def test_is_blocker_pending():
    assert is_blocker_text("approval still pending") is True


# --- classify_worklog ---

def test_classify_sets_canonical_name():
    section = _make_section("Global Due Diligence", ["Did something"])
    wl = classify_worklog(_make_worklog([section]))
    assert wl.sections[0].canonical_name == "GDD"


def test_classify_unknown_passes_through_raw_name():
    section = _make_section("Foobar", ["Did something"])
    wl = classify_worklog(_make_worklog([section]))
    assert wl.sections[0].canonical_name == "Foobar"


def test_classify_marks_blocker_items():
    section = _make_section("GDD", ["waiting on approval", "normal task"])
    wl = classify_worklog(_make_worklog([section]))
    assert wl.sections[0].items[0].is_blocker is True
    assert wl.sections[0].items[1].is_blocker is False


def test_classify_non_blocker_items_unchanged():
    section = _make_section("TSI", ["Created record producer", "Updated config"])
    wl = classify_worklog(_make_worklog([section]))
    assert all(not item.is_blocker for item in wl.sections[0].items)


def test_classify_sunshine_act_alias():
    section = _make_section("Sunshine Act", ["Reviewed corrections"])
    wl = classify_worklog(_make_worklog([section]))
    assert wl.sections[0].canonical_name == "Dr. Sunshine Act Correction"
