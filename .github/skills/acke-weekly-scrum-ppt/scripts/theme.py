"""Shared constants for the ACKE.in weekly scrum deck scripts."""
from __future__ import annotations

from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"

# Bosch-inspired palette (hex, no '#'); any other color fails validate_deck.py.
PALETTE: dict[str, str] = {
    "red": "ED0007",
    "blue": "005691",
    "navy": "003B6A",
    "light_blue": "00A9E0",
    "teal": "18837E",
    "green": "3E9B2F",
    "amber": "FFC000",
    "dark": "263238",
    "gray": "EBEFF2",
    "mid_gray": "8A9BA8",
    "white": "FFFFFF",
}

FONT = "Arial"

SLIDE_W_IN = 13.333
SLIDE_H_IN = 7.5

ICON_NAMES = ("done", "progress", "blocked", "risk", "next", "velocity", "goal")

REQUIRED_ASSETS = (
    "acke-logo.png",
    "acke-logo-white.png",
    "acke-logo-mark.png",
    "bg-title.png",
    "bg-content.png",
    *(f"icons/{name}.png" for name in ICON_NAMES),
)


def missing_assets() -> list[str]:
    return [name for name in REQUIRED_ASSETS if not (ASSETS_DIR / name).exists()]
