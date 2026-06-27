from __future__ import annotations
import calendar
import os
from typing import Optional
from .models import DateRange


def _month_abbr(month_num: int) -> str:
    return calendar.month_abbr[month_num]


def _format_to_extension(fmt: str) -> str:
    return {"text": ".txt", "markdown": ".md", "html": ".html"}.get(fmt, ".txt")


def generate_filename(date_range: Optional[DateRange], fmt: str) -> str:
    ext = _format_to_extension(fmt)
    if date_range is None:
        return f"status_update{ext}"
    sd = f"{date_range.start_day:02d}{_month_abbr(date_range.start_month)}"
    ed = f"{date_range.end_day:02d}{_month_abbr(date_range.end_month)}"
    return f"status_{sd}_{ed}_{date_range.year}{ext}"


def write_output(content: str, filename: str, output_dir: str = ".") -> str:
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
