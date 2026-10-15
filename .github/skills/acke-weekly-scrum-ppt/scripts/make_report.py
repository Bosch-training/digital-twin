#!/usr/bin/env python3
"""One-shot pipeline: validate data -> ensure assets -> build deck -> validate deck -> preview.

Usage: python make_report.py --data reports/2026-W42/status.json [--out deck.pptx] [--preview]
Default output: ACKE-Weekly-Scrum-<YYYY>-W<WW>.pptx next to the data file.
Stops at the first failing step and exits non-zero.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import build_deck
import generate_assets
import render_preview
import validate_deck
import validate_status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--preview", action="store_true", help="also render PDF/PNG previews")
    args = parser.parse_args()

    try:
        data = json.loads(args.data.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR cannot read {args.data}: {exc}", file=sys.stderr)
        return 1

    errors, warnings = validate_status.validate_status(data)
    for w in warnings:
        print(f"WARN  data: {w}")
    if errors:
        for e in errors:
            print(f"ERROR data: {e}")
        return 1

    written = generate_assets.generate(force=False)
    if written:
        print(f"Generated {len(written)} missing asset(s)")

    iso = date.fromisoformat(data["week_start"]).isocalendar()
    out = args.out or args.data.parent / f"ACKE-Weekly-Scrum-{iso.year}-W{iso.week:02d}.pptx"
    build_deck.build(data, out)
    print(f"Built {out}")

    deck_errors, deck_warnings = validate_deck.check(out)
    for w in deck_warnings:
        print(f"WARN  deck: {w}")
    if deck_errors:
        for e in deck_errors:
            print(f"ERROR deck: {e}")
        return 1

    if args.preview:
        for path in render_preview.render(out):
            print(f"Preview {path}")
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
