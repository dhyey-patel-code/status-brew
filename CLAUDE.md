# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**status-brew** is a Python tool that converts raw work log entries into polished status-update emails. It reads pasted rich text (with bullet points, bold/italic formatting) and produces formatted email output organized by workstream.

## Project Status

This project is in early scaffolding — `src/` and `tests/` directories exist but are empty. The `requirements.txt` file currently holds planning notes (not package dependencies); it should be replaced with actual pip dependencies once implementation begins.

## Key Domain Context

**Workstreams** the tool must recognize and group work under:
- LCO (Legal and Contract Operations)
- GDD (Global Due Diligence)
- ROPA
- MCD (Material Contract Detector)
- TSI (Trademark Search Intake)
- Workspace
- Vendor Portal
- Dr. Sunshine Act Correction

**Input:** Pasted rich text including bullet points, bold, and italic formatting.

**Output format** (email structure):
1. Greeting
2. One-liner context
3. PTO dates (if any)
4. Work updates divided by workstream sections
5. Sign-off: `Thanks, Dhyey Patel`

Recipients vary per project; all recipients within a project receive the same level of detail.

## Environment

Copy `.env.example` to `.env` before running. API keys or config values needed by the tool should be documented in `.env.example`.

## Development Commands

Once dependencies are added to `requirements.txt`, set up the environment with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run tests:
```bash
pytest
pytest tests/test_specific.py::test_name   # single test
```
