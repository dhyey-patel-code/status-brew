from __future__ import annotations
import os
import sys
import pytest
from status_brew.cli import build_parser, main
from status_brew.writer import generate_filename
from status_brew.models import DateRange

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def fixture(name: str) -> str:
    return os.path.join(FIXTURES, name)


# --- generate_filename ---

def test_generate_filename_text():
    dr = DateRange("", 22, 6, 26, 6, 2026)
    assert generate_filename(dr, "text") == "status_22Jun_26Jun_2026.txt"


def test_generate_filename_markdown():
    dr = DateRange("", 22, 6, 26, 6, 2026)
    assert generate_filename(dr, "markdown") == "status_22Jun_26Jun_2026.md"


def test_generate_filename_html():
    dr = DateRange("", 22, 6, 26, 6, 2026)
    assert generate_filename(dr, "html") == "status_22Jun_26Jun_2026.html"


def test_generate_filename_no_date():
    assert generate_filename(None, "text") == "status_update.txt"


# --- build_parser ---

def test_missing_file_arg_exits():
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args([])
    assert exc.value.code == 2


# --- main() integration via monkeypatch ---

def test_dry_run_prints_to_stdout(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["status-brew", "--file", fixture("basic_worklog.md"), "--dry-run"])
    main()
    captured = capsys.readouterr()
    assert "Subject:" in captured.out
    assert captured.err == ""


def test_dry_run_no_file_created(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv", ["status-brew", "--file", fixture("basic_worklog.md"), "--dry-run"])
    monkeypatch.chdir(tmp_path)
    main()
    assert list(tmp_path.iterdir()) == []


def test_saves_file_without_dry_run(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(sys, "argv", ["status-brew", "--file", fixture("basic_worklog.md")])
    monkeypatch.chdir(tmp_path)
    main()
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    assert files[0].suffix == ".txt"
    captured = capsys.readouterr()
    assert "Saved to" in captured.out


def test_saves_html_file(monkeypatch, tmp_path):
    monkeypatch.setattr(
        sys, "argv",
        ["status-brew", "--file", fixture("basic_worklog.md"), "--format", "html"]
    )
    monkeypatch.chdir(tmp_path)
    main()
    files = list(tmp_path.iterdir())
    assert files[0].suffix == ".html"


def test_nonexistent_file_exits(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["status-brew", "--file", "/does/not/exist.md"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1


def test_dry_run_markdown_format(monkeypatch, capsys):
    monkeypatch.setattr(
        sys, "argv",
        ["status-brew", "--file", fixture("basic_worklog.md"), "--format", "markdown", "--dry-run"]
    )
    main()
    captured = capsys.readouterr()
    assert "**Subject:**" in captured.out


def test_dry_run_with_blockers(monkeypatch, capsys):
    monkeypatch.setattr(
        sys, "argv",
        ["status-brew", "--file", fixture("with_blockers.md"), "--dry-run"]
    )
    main()
    captured = capsys.readouterr()
    assert "Blockers / Risks" in captured.out


def test_dry_run_with_pto_multi(monkeypatch, capsys):
    monkeypatch.setattr(
        sys, "argv",
        ["status-brew", "--file", fixture("with_pto_multi.md"), "--dry-run"]
    )
    main()
    captured = capsys.readouterr()
    assert "22/6" in captured.out
    assert "23/6" in captured.out
