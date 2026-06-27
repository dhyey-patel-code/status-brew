from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DateRange:
    raw: str
    start_day: int
    start_month: int
    end_day: int
    end_month: int
    year: int


@dataclass
class WorkItem:
    text: str
    is_blocker: bool = False


@dataclass
class WorkSection:
    raw_name: str
    canonical_name: str
    items: list[WorkItem] = field(default_factory=list)


@dataclass
class PtoEntry:
    dates: list[str]
    note: str = ""


@dataclass
class WorkLog:
    date_range: Optional[DateRange]
    sections: list[WorkSection]
    pto_entries: list[PtoEntry]
    explicit_blockers: list[str]
