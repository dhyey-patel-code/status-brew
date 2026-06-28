from __future__ import annotations
import argparse
import logging
import sys
from .classifier import classify_worklog
from .formatter import format_output, format_template
from .parser import parse_file, parse_worklog
from .writer import generate_filename, write_output

logger = logging.getLogger(__name__)


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
    p.add_argument(
        "--template", "-t",
        metavar="FILE",
        help="Jinja2 template file (.j2) for custom output format",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging",
    )
    return p


def _configure_logging(verbose: bool) -> None:
    logger.handlers.clear()
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if verbose else logging.WARNING)
    logger.propagate = False


def main() -> None:
    args = build_parser().parse_args()
    _configure_logging(args.verbose)
    try:
        logger.debug("Reading file: %s", args.file)
        text = parse_file(args.file)
        worklog = parse_worklog(text)
        logger.debug(
            "Parsed %d section(s), %d PTO entry(ies), %d explicit blocker(s)",
            len(worklog.sections),
            len(worklog.pto_entries),
            len(worklog.explicit_blockers),
        )

        classify_worklog(worklog)
        logger.debug("Classification complete")

        for section in worklog.sections:
            if not section.items:
                logger.warning("No entries found for workstream: %s", section.canonical_name)

        if not worklog.sections and not worklog.explicit_blockers and not worklog.pto_entries:
            logger.warning("No work entries found in the input file")

        if args.template:
            import os
            if not os.path.isfile(args.template):
                print(f"Error: Template file not found: {args.template}", file=sys.stderr)
                sys.exit(1)
            logger.debug("Rendering with template: %s", args.template)
            output = format_template(worklog, args.template)
        else:
            logger.debug("Formatting output as %s", args.format)
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
