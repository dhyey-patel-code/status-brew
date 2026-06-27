from __future__ import annotations
import calendar
from typing import Optional
from .models import DateRange, PtoEntry, WorkLog


def _month_abbr(month_num: int) -> str:
    return calendar.month_abbr[month_num]


def _format_date_range_human(dr: Optional[DateRange]) -> str:
    if dr is None:
        return "Unknown Dates"
    start = f"{dr.start_day} {_month_abbr(dr.start_month)}"
    end = f"{dr.end_day} {_month_abbr(dr.end_month)} {dr.year}"
    return f"{start} – {end}"


def _build_subject(dr: Optional[DateRange]) -> str:
    return f"Status Update: {_format_date_range_human(dr)}"


def _collect_all_blockers(worklog: WorkLog) -> list[str]:
    combined = list(worklog.explicit_blockers)
    for section in worklog.sections:
        for item in section.items:
            if item.is_blocker:
                combined.append(item.text)
    return list(dict.fromkeys(combined))


def _format_pto_text(pto_entries: list[PtoEntry]) -> str:
    all_dates: list[str] = []
    for entry in pto_entries:
        all_dates.extend(entry.dates)
    return ", ".join(all_dates)


def _html_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_text(worklog: WorkLog) -> str:
    lines: list[str] = []
    lines.append(f"Subject: {_build_subject(worklog.date_range)}")
    lines.append("")

    pto_text = _format_pto_text(worklog.pto_entries)
    if pto_text:
        lines.append(f"PTO: {pto_text}")
        lines.append("")

    for section in worklog.sections:
        if not section.items:
            continue
        lines.append(f"--- {section.canonical_name} ---")
        for item in section.items:
            lines.append(f"  - {item.text}")
        lines.append("")

    blockers = _collect_all_blockers(worklog)
    if blockers:
        lines.append("--- Blockers / Risks ---")
        for b in blockers:
            lines.append(f"  - {b}")
        lines.append("")

    lines.append("Thanks,")
    lines.append("Dhyey Patel")

    return "\n".join(lines)


def format_markdown(worklog: WorkLog) -> str:
    lines: list[str] = []
    lines.append(f"**Subject:** {_build_subject(worklog.date_range)}")
    lines.append("")

    pto_text = _format_pto_text(worklog.pto_entries)
    if pto_text:
        lines.append("## PTO")
        lines.append(f"- {pto_text}")
        lines.append("")

    for section in worklog.sections:
        if not section.items:
            continue
        lines.append(f"## {section.canonical_name}")
        for item in section.items:
            lines.append(f"- {item.text}")
        lines.append("")

    blockers = _collect_all_blockers(worklog)
    if blockers:
        lines.append("## Blockers / Risks")
        for b in blockers:
            lines.append(f"- {b}")
        lines.append("")

    lines.append("Thanks,  ")
    lines.append("Dhyey Patel")

    return "\n".join(lines)


def format_html(worklog: WorkLog) -> str:
    subject = _html_escape(_build_subject(worklog.date_range))
    parts: list[str] = [
        "<!DOCTYPE html>",
        "<html>",
        f'<head><meta charset="utf-8"><title>{subject}</title></head>',
        "<body>",
        f"<p><strong>Subject:</strong> {subject}</p>",
    ]

    pto_text = _format_pto_text(worklog.pto_entries)
    if pto_text:
        parts.append("<h2>PTO</h2>")
        parts.append(f"<p>{_html_escape(pto_text)}</p>")

    for section in worklog.sections:
        if not section.items:
            continue
        parts.append(f"<h2>{_html_escape(section.canonical_name)}</h2>")
        parts.append("<ul>")
        for item in section.items:
            parts.append(f"  <li>{_html_escape(item.text)}</li>")
        parts.append("</ul>")

    blockers = _collect_all_blockers(worklog)
    if blockers:
        parts.append("<h2>Blockers / Risks</h2>")
        parts.append("<ul>")
        for b in blockers:
            parts.append(f"  <li>{_html_escape(b)}</li>")
        parts.append("</ul>")

    parts.append("<p>Thanks,<br>Dhyey Patel</p>")
    parts.append("</body>")
    parts.append("</html>")

    return "\n".join(parts)


def format_output(worklog: WorkLog, fmt: str) -> str:
    if fmt == "text":
        return format_text(worklog)
    if fmt == "markdown":
        return format_markdown(worklog)
    if fmt == "html":
        return format_html(worklog)
    raise ValueError(f"Unsupported format: {fmt!r}. Choose text, markdown, or html.")
