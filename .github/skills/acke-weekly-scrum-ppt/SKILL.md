---
name: acke-weekly-scrum-ppt
description: "Use when creating a weekly scrum status report PowerPoint (.pptx) for ACKE.in: sprint progress, completed / in-progress / blocked items, risks, velocity, burndown, next-week plan, with the ACKE.in logo and a Bosch-colored (red/blue) theme. Triggers: weekly scrum report, scrum status ppt, sprint status deck, weekly status slides, status report for ACKE, regenerate the weekly deck."
argument-hint: "Path to status JSON, or paste this week's updates (team, sprint, done/in-progress/blocked items)"
---

# ACKE.in Weekly Scrum Status Deck

Builds a branded 9+ slide `.pptx` from one JSON file. All deterministic work (assets, validation, layout, checks) lives in `scripts/`; never hand-build slides or edit the generated logo.

## Inputs
Team, sprint, week dates, RAG, goal, and the item lists. Field rules: [status-data-schema.md](./references/status-data-schema.md). Ask the user for anything missing instead of inventing data; use `"TBD"` only when the user confirms it is unknown.

## Procedure
1. **Scaffold** (new week): `python scripts/new_status.py --team "<team>" --sprint <n> [--week-start YYYY-MM-DD]` creates `reports/<YYYY>-W<WW>/status.json`. Use `--sample` only to demo the pipeline.
2. **Fill data**: normalize the user's notes into that JSON. Keep titles <= 70 chars; put extra text in each item's `detail` (becomes speaker notes).
3. **Run the pipeline**: `python scripts/make_report.py --data reports/<YYYY>-W<WW>/status.json --preview`
   - validates data -> generates missing assets -> builds deck -> validates deck -> renders PNG previews.
   - Exits non-zero at the first failing step; fix the reported field/slide and rerun.
4. **Review previews** in `reports/<YYYY>-W<WW>/preview/` (open the PNGs, check the Executive Summary, Blockers and any paginated tables).
5. **Report** the `.pptx` path, a slide-by-slide summary, and any `TBD` warnings.

Individual steps if needed: `validate_status.py`, `generate_assets.py [--force]`, `build_deck.py`, `validate_deck.py`, `render_preview.py`. Install deps once: `pip install -r scripts/requirements.txt` (preview also needs LibreOffice and `pdftoppm`).

## Rules
- Slide order, layout and per-slide limits: [slide-structure.md](./references/slide-structure.md).
- Colors, fonts, logo usage: [brand-theme.md](./references/brand-theme.md). Colors come only from the palette in `scripts/theme.py`.
- Empty sections show "None this week."; every blocker has an owner and an ask.
- RAG always shows a text label, never color alone.
- To change visuals, edit `scripts/build_deck.py` or `scripts/generate_assets.py` and rerun; do not patch the `.pptx` by hand.
- Use the Bosch palette only; do not use the Bosch logo or trademarks.

## Done when
`make_report.py` prints `OK` with no errors, previews have been viewed, and the user has the output path.

## Assets (`assets/`)
`acke-logo.{svg,png}`, `acke-logo-white.{svg,png}`, `acke-logo-mark.{svg,png}`, `bg-title.png`, `bg-content.png`, `icons/*.png` (generated, deterministic), and `sample-status.json`.
