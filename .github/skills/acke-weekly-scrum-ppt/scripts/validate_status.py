#!/usr/bin/env python3
"""Validate a weekly status JSON file against the schema in references/status-data-schema.md.

Usage: python validate_status.py status.json
Exit code 1 when there are errors; warnings never fail the run.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

RAG = ("green", "amber", "red")
SEVERITY = ("low", "medium", "high")
MAX_SUMMARY = 6
MAX_WORDS = 12
MAX_TITLE_CHARS = 70


def _num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _text(obj: dict[str, Any], key: str, path: str, errors: list[str], *, required: bool = True,
          max_chars: int | None = None) -> None:
    v = obj.get(key)
    if v is None or v == "":
        if required:
            errors.append(f"{path}.{key}: required non-empty string")
        return
    if not isinstance(v, str):
        errors.append(f"{path}.{key}: must be a string")
    elif max_chars and len(v) > max_chars:
        errors.append(f"{path}.{key}: {len(v)} chars exceeds {max_chars}; shorten or use 'detail'")


def _list(data: dict[str, Any], key: str, errors: list[str]) -> list[dict[str, Any]]:
    v = data.get(key)
    if not isinstance(v, list):
        errors.append(f"{key}: required list (use [] when empty)")
        return []
    out = []
    for i, item in enumerate(v):
        if isinstance(item, dict):
            out.append(item)
        else:
            errors.append(f"{key}[{i}]: must be an object")
    return out


def _date(data: dict[str, Any], key: str, errors: list[str]) -> date | None:
    try:
        return date.fromisoformat(str(data.get(key)))
    except ValueError:
        errors.append(f"{key}: required ISO date YYYY-MM-DD")
        return None


def validate_status(data: Any) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return ["root: must be a JSON object"], warnings

    _text(data, "team", "", errors)
    if data.get("sprint") in (None, ""):
        errors.append("sprint: required (number or string)")
    start, end = _date(data, "week_start", errors), _date(data, "week_end", errors)
    if start and end and end < start:
        errors.append("week_end: must not be before week_start")
    if data.get("rag") not in RAG:
        errors.append(f"rag: must be one of {RAG}")
    _text(data, "rag_reason", "", errors)
    _text(data, "goal", "", errors, max_chars=160)
    _text(data, "prepared_by", "", errors, required=False)
    _text(data, "contact", "", errors, required=False)
    cp = data.get("committed_points")
    if cp is not None and (not _num(cp) or cp < 0):
        errors.append("committed_points: must be a number >= 0")

    summary = data.get("summary")
    if not isinstance(summary, list) or not summary or not all(isinstance(s, str) for s in summary):
        errors.append("summary: required list of 1-6 strings")
    else:
        if len(summary) > MAX_SUMMARY:
            errors.append(f"summary: {len(summary)} bullets exceeds {MAX_SUMMARY}")
        for i, s in enumerate(summary):
            if len(s.split()) > MAX_WORDS:
                warnings.append(f"summary[{i}]: over {MAX_WORDS} words")

    for key in ("completed", "in_progress"):
        for i, item in enumerate(_list(data, key, errors)):
            p = f"{key}[{i}]"
            _text(item, "id", p, errors)
            _text(item, "title", p, errors, max_chars=MAX_TITLE_CHARS)
            _text(item, "owner", p, errors)
            _text(item, "detail", p, errors, required=False)
            if not _num(item.get("points")) or item["points"] < 0:
                errors.append(f"{p}.points: required number >= 0")
            if key == "in_progress":
                pct = item.get("percent")
                if not _num(pct) or not 0 <= pct <= 100:
                    errors.append(f"{p}.percent: required number 0-100")

    for i, item in enumerate(_list(data, "blocked", errors)):
        p = f"blocked[{i}]"
        _text(item, "id", p, errors)
        _text(item, "title", p, errors, max_chars=MAX_TITLE_CHARS)
        _text(item, "owner", p, errors)
        _text(item, "ask", p, errors, max_chars=110)  # every blocker needs an owner and an ask
        _text(item, "detail", p, errors, required=False)

    for i, item in enumerate(_list(data, "risks", errors)):
        p = f"risks[{i}]"
        _text(item, "risk", p, errors, max_chars=MAX_TITLE_CHARS)
        _text(item, "mitigation", p, errors, max_chars=110)
        _text(item, "owner", p, errors, required=False)
        if item.get("severity") not in SEVERITY:
            errors.append(f"{p}.severity: must be one of {SEVERITY}")

    for i, item in enumerate(_list(data, "next_week", errors)):
        p = f"next_week[{i}]"
        _text(item, "title", p, errors, max_chars=MAX_TITLE_CHARS)
        _text(item, "owner", p, errors)

    vel = _list(data, "velocity", errors)
    if not vel:
        errors.append("velocity: at least one sprint required")
    for i, item in enumerate(vel):
        p = f"velocity[{i}]"
        _text(item, "sprint", p, errors)
        for k in ("committed", "completed"):
            if not _num(item.get(k)) or item[k] < 0:
                errors.append(f"{p}.{k}: required number >= 0")

    bd = data.get("burndown")
    if not isinstance(bd, dict):
        errors.append("burndown: required object {labels, remaining}")
    else:
        labels, rem = bd.get("labels"), bd.get("remaining")
        if not isinstance(labels, list) or len(labels) < 2:
            errors.append("burndown.labels: required list with at least 2 entries")
        if not isinstance(rem, list) or not rem or not all(_num(x) for x in rem):
            errors.append("burndown.remaining: required list of numbers")
        elif isinstance(labels, list) and len(rem) > len(labels):
            errors.append("burndown.remaining: longer than burndown.labels")

    for key, limit in (("blocked", 3), ("risks", 3)):
        if isinstance(data.get(key), list) and len(data[key]) > limit:
            warnings.append(f"{key}: only the first {limit} fit on the slide; rest go to notes")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.data.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR cannot read {args.data}: {exc}", file=sys.stderr)
        return 1
    errors, warnings = validate_status(data)
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
