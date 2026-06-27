from __future__ import annotations
import argparse
import sys
from .classifier import classify_worklog
from .formatter import format_output
from .parser import parse_file, parse_worklog
from .writer import generate_filename, write_output


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="status-brew",
        description="Convert a work log file into a formatted status-update email.",
    )
    p.add_argument(
        "--file", "-f",
        required=True,
        help="Path to the work log file (.md or .txt)",
    )
    p.add_argument(
        "--format",
        choices=["text", "markdown", "html"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print output to stdout instead of saving to a file",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()
    try:
        text = parse_file(args.file)
        worklog = parse_worklog(text)
        classify_worklog(worklog)
        output = format_output(worklog, args.format)
        if args.dry_run:
            print(output)
        else:
            filename = generate_filename(worklog.date_range, args.format)
            path = write_output(output, filename)
            print(f"Saved to {path}")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
