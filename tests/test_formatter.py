from __future__ import annotations
import os
import pytest
from status_brew.formatter import (
    _build_subject,
    _collect_all_blockers,
    _html_escape,
    format_html,
    format_markdown,
    format_output,
    format_template,
    format_text,
)
from status_brew.models import DateRange, PtoEntry, WorkItem, WorkLog, WorkSection
import datetime


def _make_date_range() -> DateRange:
    return DateRange(
        raw="22/6-26/6",
        start_day=22,
        start_month=6,
        end_day=26,
        end_month=6,
        year=2026,
    )


def _make_worklog(
    dr=None,
    sections=None,
    pto_entries=None,
    explicit_blockers=None,
) -> WorkLog:
    return WorkLog(
        date_range=dr,
        sections=sections or [],
        pto_entries=pto_entries or [],
        explicit_blockers=explicit_blockers or [],
    )


def _section(name: str, items: list[str], blocker_flags: list[bool] | None = None) -> WorkSection:
    flags = blocker_flags or [False] * len(items)
    return WorkSection(
        raw_name=name,
        canonical_name=name,
        items=[WorkItem(text=t, is_blocker=f) for t, f in zip(items, flags)],
    )


# --- Subject line ---

def test_build_subject_with_date_range():
    dr = _make_date_range()
    assert _build_subject(dr) == "Status Update: 22 Jun – 26 Jun 2026"


def test_build_subject_without_date_range():
    assert _build_subject(None) == "Status Update: Unknown Dates"


# --- Blockers collection ---

def test_collect_all_blockers_explicit_only():
    wl = _make_worklog(explicit_blockers=["issue A"])
    assert _collect_all_blockers(wl) == ["issue A"]


def test_collect_all_blockers_keyword_only():
    s = _section("GDD", ["waiting on approval"], blocker_flags=[True])
    wl = _make_worklog(sections=[s])
    assert _collect_all_blockers(wl) == ["waiting on approval"]


def test_collect_all_blockers_deduplication():
    s = _section("GDD", ["duplicate issue"], blocker_flags=[True])
    wl = _make_worklog(sections=[s], explicit_blockers=["duplicate issue"])
    result = _collect_all_blockers(wl)
    assert result.count("duplicate issue") == 1


# --- HTML escape ---

def test_html_escape_entities():
    assert _html_escape("a & b < c > d") == "a &amp; b &lt; c &gt; d"


def test_html_escape_no_change():
    assert _html_escape("plain text") == "plain text"


# --- format_text ---

def test_format_text_contains_subject():
    wl = _make_worklog(dr=_make_date_range())
    out = format_text(wl)
    assert "Subject: Status Update:" in out


def test_format_text_contains_sign_off():
    wl = _make_worklog()
    out = format_text(wl)
    assert out.endswith("Thanks,\nDhyey Patel")


def test_format_text_no_pto_section_omitted():
    wl = _make_worklog()
    out = format_text(wl)
    assert "PTO" not in out


def test_format_text_with_pto():
    pto = PtoEntry(dates=["22/6", "23/6"])
    wl = _make_worklog(pto_entries=[pto])
    out = format_text(wl)
    assert "PTO: 22/6, 23/6" in out


def test_format_text_no_blockers_section_omitted():
    wl = _make_worklog()
    out = format_text(wl)
    assert "Blockers" not in out


def test_format_text_with_blockers():
    s = _section("GDD", ["waiting on approval"], blocker_flags=[True])
    wl = _make_worklog(sections=[s], explicit_blockers=["portal down"])
    out = format_text(wl)
    assert "Blockers / Risks" in out
    assert "waiting on approval" in out
    assert "portal down" in out


def test_format_text_empty_section_omitted():
    s = WorkSection(raw_name="Empty", canonical_name="Empty", items=[])
    wl = _make_worklog(sections=[s])
    out = format_text(wl)
    assert "Empty" not in out


def test_format_text_unrecognized_workstream_included():
    s = _section("Foobar", ["some task"])
    wl = _make_worklog(sections=[s])
    out = format_text(wl)
    assert "Foobar" in out


# --- format_markdown ---

def test_format_markdown_uses_headings():
    s = _section("GDD", ["task one"])
    wl = _make_worklog(sections=[s])
    out = format_markdown(wl)
    assert "## GDD" in out


def test_format_markdown_subject_bold():
    wl = _make_worklog(dr=_make_date_range())
    out = format_markdown(wl)
    assert out.startswith("**Subject:**")


# --- format_html ---

def test_format_html_valid_structure():
    wl = _make_worklog(dr=_make_date_range())
    out = format_html(wl)
    assert out.startswith("<!DOCTYPE html>")
    assert out.strip().endswith("</html>")


def test_format_html_escapes_special_chars():
    s = _section("GDD", ["item with <angle> & 'quotes'"])
    wl = _make_worklog(sections=[s])
    out = format_html(wl)
    assert "&lt;angle&gt;" in out
    assert "&amp;" in out


def test_format_html_contains_sign_off():
    wl = _make_worklog()
    out = format_html(wl)
    assert "Thanks,<br>Dhyey Patel" in out


# --- format_output dispatch ---

def test_format_output_dispatch_text():
    wl = _make_worklog()
    out = format_output(wl, "text")
    assert "Subject:" in out


def test_format_output_dispatch_markdown():
    wl = _make_worklog()
    out = format_output(wl, "markdown")
    assert "**Subject:**" in out


def test_format_output_dispatch_html():
    wl = _make_worklog()
    out = format_output(wl, "html")
    assert "<!DOCTYPE html>" in out


def test_format_output_invalid_raises():
    wl = _make_worklog()
    with pytest.raises(ValueError, match="Unsupported format"):
        format_output(wl, "pdf")


# --- format_template ---

def test_format_template_renders_subject(tmp_path):
    tmpl = tmp_path / "t.j2"
    tmpl.write_text("{{ subject }}")
    wl = _make_worklog(dr=_make_date_range())
    out = format_template(wl, str(tmpl))
    assert "Status Update:" in out


def test_format_template_renders_sections(tmp_path):
    tmpl = tmp_path / "t.j2"
    tmpl.write_text(
        "{% for section in sections %}{{ section.canonical_name }}: "
        "{% for item in section.items %}{{ item.text }}{% endfor %}{% endfor %}"
    )
    s = _section("GDD", ["review contract"])
    wl = _make_worklog(sections=[s])
    out = format_template(wl, str(tmpl))
    assert "GDD" in out
    assert "review contract" in out


def test_format_template_renders_pto(tmp_path):
    tmpl = tmp_path / "t.j2"
    tmpl.write_text("{{ pto_dates_str }}")
    pto = PtoEntry(dates=["22/6", "23/6"])
    wl = _make_worklog(pto_entries=[pto])
    out = format_template(wl, str(tmpl))
    assert "22/6" in out
    assert "23/6" in out


def test_format_template_renders_blockers(tmp_path):
    tmpl = tmp_path / "t.j2"
    tmpl.write_text("{% for b in blockers %}{{ b }}|{% endfor %}")
    s = _section("GDD", ["waiting on approval"], blocker_flags=[True])
    wl = _make_worklog(sections=[s], explicit_blockers=["portal down"])
    out = format_template(wl, str(tmpl))
    assert "waiting on approval" in out
    assert "portal down" in out


def test_format_template_missing_file_raises(tmp_path):
    with pytest.raises(Exception):
        format_template(_make_worklog(), str(tmp_path / "nonexistent.j2"))


def test_format_template_undefined_var_raises(tmp_path):
    from jinja2 import UndefinedError
    tmpl = tmp_path / "t.j2"
    tmpl.write_text("{{ nonexistent_variable }}")
    with pytest.raises(UndefinedError):
        format_template(_make_worklog(), str(tmpl))
