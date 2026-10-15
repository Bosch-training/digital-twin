#!/usr/bin/env python3
"""Scaffold reports/<YYYY>-W<WW>/status.json for a week.

Usage:
  python new_status.py --team "Platform Engineering" --sprint 12 [--week-start 2026-10-12]
                       [--reports-dir reports] [--sample]
Without --week-start the Monday of the current ISO week is used (Mon-Fri range).
--sample copies assets/sample-status.json with the dates replaced, for trying the pipeline.
"""
from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import theme


def monday_of(day: date) -> date:
    return day - timedelta(days=day.weekday())


def skeleton(team: str, sprint: str, start: date, days: int) -> dict[str, Any]:
    return {
        "team": team,
        "sprint": sprint,
        "week_start": start.isoformat(),
        "week_end": (start + timedelta(days=4)).isoformat(),
        "rag": "green",
        "rag_reason": "TBD",
        "committed_points": 0,
        "goal": "TBD",
        "prepared_by": "",
        "contact": "",
        "summary": ["TBD"],
        "burndown": {"labels": [f"D{i}" for i in range(1, days + 1)], "remaining": [0]},
        "completed": [],
        "in_progress": [],
        "blocked": [],
        "risks": [],
        "velocity": [{"sprint": "S0", "committed": 0, "completed": 0}],
        "next_week": [],
    }


def scaffold(team: str, sprint: str, start: date, reports_dir: Path, sample: bool,
             days: int = 10) -> Path:
    iso = start.isocalendar()
    out = reports_dir / f"{iso.year}-W{iso.week:02d}" / "status.json"
    if out.exists():
        raise FileExistsError(f"{out} already exists; refusing to overwrite")
    if sample:
        data = json.loads((theme.ASSETS_DIR / "sample-status.json").read_text(encoding="utf-8"))
        data["week_start"] = start.isoformat()
        data["week_end"] = (start + timedelta(days=4)).isoformat()
    else:
        data = skeleton(team, sprint, start, days)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--team", default="TBD")
    parser.add_argument("--sprint", default="TBD")
    parser.add_argument("--week-start", type=date.fromisoformat, default=None)
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()
    start = monday_of(args.week_start or date.today())
    print(scaffold(args.team, args.sprint, start, args.reports_dir, args.sample))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
