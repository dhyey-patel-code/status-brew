# status-brew

Converts bullet-point work logs into polished status-update emails. Paste your weekly notes in a structured markdown file and get back a formatted email body — grouped by workstream, with blockers called out and PTO noted.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Requires Python 3.9+. No third-party dependencies.

## Usage

```bash
status-brew --file worklog.md
```

This writes the formatted output to a file in the current directory (e.g. `status_22Jun_26Jun_2026.txt`).

### Options

| Flag | Description |
|---|---|
| `--file`, `-f` | Path to the work log file (required) |
| `--format` | Output format: `text` (default), `markdown`, or `html` |
| `--dry-run` | Print to stdout instead of saving a file |
| `--verbose`, `-v` | Enable debug logging to stderr |

### Examples

```bash
# Preview output without saving
status-brew --file worklog.md --dry-run

# Save as HTML
status-brew --file worklog.md --format html

# Debug a parsing issue
status-brew --file worklog.md --dry-run --verbose
```

## Input format

Work logs use a two-level bullet structure. The top-level bullet is the workstream name; indented bullets are the individual work items.

```
Dates: 22/6-26/6

- GDD
    - Created GDD Dashboard
    - Updated due diligence indicators
- LCO
    - Reviewed contract templates
- Blockers
    - Waiting on API credentials from vendor
- PTO - 25/6
```

**Date range** (`Dates: DD/MM-DD/MM`) — optional, used in the email subject and output filename.

**Workstreams** — any top-level bullet not named `Blockers` or `PTO` is treated as a workstream section. Aliases are resolved to canonical names automatically (e.g. `Global Due Diligence` → `GDD`).

**Blockers** — a top-level `Blockers` section collects explicit blockers. Items within workstream sections that contain keywords like `blocked`, `waiting on`, `pending`, `delayed`, or `at risk` are also surfaced in the blockers block of the output.

**PTO** — inline format: `- PTO - DD/MM` or `- PTO - DD/MM, DD/MM` for multiple dates.

### Supported workstream names and aliases

| Canonical | Recognized aliases |
|---|---|
| GDD | `global due diligence`, `global dd` |
| LCO | `legal and contract operations`, `legal operations`, `legal op` |
| ROPA | `ropa` |
| MCD | `material contract detector`, `material contract` |
| TSI | `trademark search intake`, `trademark search` |
| Workspace | `workspace` |
| Vendor Portal | `vendor portal` |
| Dr. Sunshine Act Correction | `sunshine act`, `dr. sunshine`, `dr sunshine` |

Unrecognized section names pass through as-is.

## Output example

Given the input above, `--format text` produces:

```
Subject: Status Update: 22 Jun – 26 Jun 2026

PTO: 25/6

--- GDD ---
  - Created GDD Dashboard
  - Updated due diligence indicators

--- LCO ---
  - Reviewed contract templates

--- Blockers / Risks ---
  - Waiting on API credentials from vendor

Thanks,
Dhyey Patel
```

## Development

```bash
# Run tests
pytest

# Run a single test
pytest tests/test_parser.py::test_parse_date_range_basic
```

The test suite covers the parser, classifier, formatter, writer, and CLI end-to-end (80 tests, no external dependencies).
