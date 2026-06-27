from __future__ import annotations
import datetime
import re
from typing import Optional
from .models import DateRange, PtoEntry, WorkItem, WorkLog, WorkSection

_DATE_RANGE_RE = re.compile(
    r"Dates:\s*(\d{1,2})/(\d{1,2})\s*-\s*(\d{1,2})/(\d{1,2})",
    re.IGNORECASE,
)
_PTO_RE = re.compile(r"^PTO\s*[-–]\s*(.+)$", re.IGNORECASE)
_DATE_TOKEN_RE = re.compile(r"^\d{1,2}/\d{1,2}$")
_BULLET_RE = re.compile(r"^[-*•]\s*")


def parse_file(filepath: str) -> str:
    try:
        with open(filepath, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {filepath}")


def parse_worklog(text: str) -> WorkLog:
    if not text.strip():
        raise ValueError("Input file is empty or contains no readable content")
    lines = text.splitlines()
    date_range = _parse_date_range(lines)
    blocks = _split_into_blocks(lines)
    sections, explicit_blockers, pto_entries = _parse_sections(blocks)
    return WorkLog(
        date_range=date_range,
        sections=sections,
        pto_entries=pto_entries,
        explicit_blockers=explicit_blockers,
    )


def _parse_date_range(lines: list[str]) -> Optional[DateRange]:
    for line in lines:
        m = _DATE_RANGE_RE.search(line)
        if m:
            sd, sm, ed, em = (
                int(m.group(1)),
                int(m.group(2)),
                int(m.group(3)),
                int(m.group(4)),
            )
            return DateRange(
                raw=m.group(0),
                start_day=sd,
                start_month=sm,
                end_day=ed,
                end_month=em,
                year=datetime.date.today().year,
            )
    return None


def _detect_indent_level(line: str) -> int:
    expanded = line.replace("\t", "    ")
    spaces = len(expanded) - len(expanded.lstrip())
    return 0 if spaces == 0 else 1


def _strip_bullet(text: str) -> str:
    return _BULLET_RE.sub("", text.strip())


def _is_special_section(name: str) -> Optional[str]:
    lower = name.lower().strip()
    if lower in ("blockers", "blocker", "risks", "risk") or lower.startswith("blockers") or lower.startswith("blocker"):
        return "blockers"
    if lower == "pto" or lower.startswith("pto ") or lower.startswith("pto-") or lower.startswith("pto–"):
        return "pto"
    return None


def _parse_pto_line(text: str) -> PtoEntry:
    m = _PTO_RE.match(text.strip())
    if not m:
        return PtoEntry(dates=[], note=text.strip())
    remainder = m.group(1).strip()
    parts = [p.strip() for p in remainder.split(",")]
    dates: list[str] = []
    note_parts: list[str] = []
    for part in parts:
        if _DATE_TOKEN_RE.match(part):
            dates.append(part)
        else:
            note_parts.append(part)
    return PtoEntry(dates=dates, note=", ".join(note_parts))


def _split_into_blocks(lines: list[str]) -> list[tuple[str, list[str]]]:
    blocks: list[tuple[str, list[str]]] = []
    current_header: Optional[str] = None
    current_items: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if not _BULLET_RE.match(stripped):
            continue

        level = _detect_indent_level(line)
        text = _strip_bullet(stripped)

        if level == 0:
            if current_header is not None:
                blocks.append((current_header, current_items))
            current_header = text
            current_items = []
        else:
            if current_header is not None:
                current_items.append(text)

    if current_header is not None:
        blocks.append((current_header, current_items))

    return blocks


def _parse_sections(
    blocks: list[tuple[str, list[str]]],
) -> tuple[list[WorkSection], list[str], list[PtoEntry]]:
    sections: list[WorkSection] = []
    explicit_blockers: list[str] = []
    pto_entries: list[PtoEntry] = []

    for header, items in blocks:
        special = _is_special_section(header)
        if special == "blockers":
            explicit_blockers.extend(items)
        elif special == "pto":
            pto_entries.append(_parse_pto_line(header))
        else:
            work_items = [WorkItem(text=item) for item in items]
            sections.append(
                WorkSection(raw_name=header, canonical_name=header, items=work_items)
            )

    return sections, explicit_blockers, pto_entries
