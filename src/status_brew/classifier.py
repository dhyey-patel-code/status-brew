from __future__ import annotations
from typing import Optional
from .models import WorkLog

WORKSTREAM_ALIASES: dict[str, list[str]] = {
    "GDD": ["gdd", "global due diligence", "global dd"],
    "LCO": ["lco", "legal and contract operations", "legal operations", "legal op"],
    "ROPA": ["ropa"],
    "MCD": ["mcd", "material contract detector", "material contract"],
    "TSI": ["tsi", "trademark search intake", "trademark search"],
    "Workspace": ["workspace"],
    "Vendor Portal": ["vendor portal"],
    "Dr. Sunshine Act Correction": [
        "dr. sunshine act correction",
        "sunshine act",
        "dr. sunshine",
        "dr sunshine act correction",
        "dr sunshine",
    ],
}

BLOCKER_KEYWORDS: list[str] = [
    "blocked",
    "blocking",
    "unable",
    "pending",
    "waiting on",
    "at risk",
    "risk",
    "delayed",
    "stalled",
]

_ALIAS_TO_CANONICAL: dict[str, str] = {
    alias: canonical
    for canonical, aliases in WORKSTREAM_ALIASES.items()
    for alias in aliases
}


def normalize_workstream(name: str) -> Optional[str]:
    return _ALIAS_TO_CANONICAL.get(name.strip().lower())


def is_blocker_text(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in BLOCKER_KEYWORDS)


def classify_worklog(worklog: WorkLog) -> WorkLog:
    for section in worklog.sections:
        canonical = normalize_workstream(section.raw_name)
        section.canonical_name = canonical if canonical is not None else section.raw_name
        for item in section.items:
            item.is_blocker = is_blocker_text(item.text)
    return worklog
