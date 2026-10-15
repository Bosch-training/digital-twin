#!/usr/bin/env python3
"""Render a .pptx to PDF and per-slide PNGs for visual review (needs LibreOffice).

Usage: python render_preview.py deck.pptx [--dpi 60]
Writes <deck dir>/preview/<deck>.pdf and slide-N.png (PNGs need `pdftoppm`).
Exits 0 with a notice when the tools are unavailable, since the preview is optional.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def render(deck: Path, dpi: int = 60) -> list[Path]:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print("SKIP preview: LibreOffice (soffice) not found")
        return []
    out_dir = deck.parent / "preview"
    out_dir.mkdir(exist_ok=True)
    subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(out_dir),
                    str(deck)], check=True, capture_output=True, timeout=180)
    pdf = out_dir / f"{deck.stem}.pdf"
    if not shutil.which("pdftoppm"):
        print(f"PDF written to {pdf}; install poppler-utils for PNG previews")
        return [pdf]
    subprocess.run(["pdftoppm", "-png", "-r", str(dpi), str(pdf), str(out_dir / "slide")],
                   check=True, capture_output=True, timeout=180)
    return sorted(out_dir.glob("slide-*.png"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", type=Path)
    parser.add_argument("--dpi", type=int, default=60)
    args = parser.parse_args()
    for path in render(args.deck, args.dpi):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
