#!/usr/bin/env python3
"""Generate the ACKE.in logo, slide backgrounds and icons into assets/.

Usage: python generate_assets.py [--force]
Deterministic: same output on every run. Skips files that already exist unless --force.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import theme
from PIL import Image, ImageDraw, ImageFont

SS = 4  # supersampling factor for smooth edges

# Logo geometry in a 100x100 box: hexagon with an "A" cut-out and a red signal dot.
HEX = [(50, 2), (91.57, 26), (91.57, 74), (50, 98), (8.43, 74), (8.43, 26)]
A_LEGS = [(50, 20), (74, 78), (62, 78), (50, 48), (38, 78), (26, 78)]
A_BAR = [(42, 63), (58, 63), (58, 69), (42, 69)]
DOT = (73.0, 34.0, 5.5)  # cx, cy, r

MARK_PX = 120  # mark height in logo units
TEXT_X = 146
TEXT_BASELINE = 86
TEXT_SIZE = 78

FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
)


def _rgb(name: str, alpha: int = 255) -> tuple[int, int, int, int]:
    h = theme.PALETTE[name]
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def _pts(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:g},{y:g}" for x, y in points)


# ---------------------------------------------------------------- logo ---------------------------


def _mark_svg(fill: str, dot: str, mask_id: str, transform: str) -> str:
    return (
        f'<g transform="{transform}">'
        f'<mask id="{mask_id}"><rect width="100" height="100" fill="black"/>'
        f'<polygon points="{_pts(HEX)}" fill="white"/>'
        f'<polygon points="{_pts(A_LEGS)}" fill="black"/>'
        f'<polygon points="{_pts(A_BAR)}" fill="black"/></mask>'
        f'<rect width="100" height="100" fill="#{fill}" mask="url(#{mask_id})"/>'
        f'<circle cx="{DOT[0]:g}" cy="{DOT[1]:g}" r="{DOT[2]:g}" fill="#{dot}"/></g>'
    )


def _text_widths() -> tuple[float, float]:
    font = _font(TEXT_SIZE)
    return font.getlength("ACKE"), font.getlength(".in")


def _logo_svg(variant: str) -> str:
    colors = _variant_colors(variant)
    wa, wb = _text_widths()
    width = TEXT_X + wa + wb + 6
    scale = MARK_PX / 100
    mark = _mark_svg(colors["mark"], colors["dot"], f"a-{variant}", f"scale({scale:g})")
    texts = (
        f'<text x="{TEXT_X}" y="{TEXT_BASELINE}" font-family="Arial, Helvetica, sans-serif" '
        f'font-weight="700" font-size="{TEXT_SIZE}" textLength="{wa:.1f}" '
        f'lengthAdjust="spacingAndGlyphs" fill="#{colors["text"]}">ACKE</text>'
        f'<text x="{TEXT_X + wa:.1f}" y="{TEXT_BASELINE}" font-family="Arial, Helvetica, '
        f'sans-serif" font-weight="700" font-size="{TEXT_SIZE}" textLength="{wb:.1f}" '
        f'lengthAdjust="spacingAndGlyphs" fill="#{colors["accent"]}">.in</text>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {MARK_PX}" '
        f'width="{width:.0f}" height="{MARK_PX}" role="img" aria-label="ACKE.in">'
        f"{mark}{texts}</svg>\n"
    )


def _mark_only_svg() -> str:
    colors = _variant_colors("color")
    mark = _mark_svg(colors["mark"], colors["dot"], "a-mark", "")
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100" '
        f'role="img" aria-label="ACKE.in">{mark}</svg>\n'
    )


def _variant_colors(variant: str) -> dict[str, str]:
    p = theme.PALETTE
    if variant == "white":
        return {"mark": p["white"], "dot": p["red"], "text": p["white"], "accent": p["light_blue"]}
    return {"mark": p["blue"], "dot": p["red"], "text": p["blue"], "accent": p["red"]}


def _draw_mark(img: Image.Image, origin: tuple[float, float], size: float, variant: str) -> None:
    colors = _variant_colors(variant)
    k = size / 100

    def tx(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
        return [(origin[0] + x * k, origin[1] + y * k) for x, y in points]

    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    md.polygon(tx(HEX), fill=255)
    md.polygon(tx(A_LEGS), fill=0)
    md.polygon(tx(A_BAR), fill=0)
    fill = Image.new("RGBA", img.size, _hex(colors["mark"]))
    img.paste(fill, (0, 0), mask)
    cx, cy, r = DOT
    ImageDraw.Draw(img).ellipse(
        [origin[0] + (cx - r) * k, origin[1] + (cy - r) * k,
         origin[0] + (cx + r) * k, origin[1] + (cy + r) * k],
        fill=_hex(colors["dot"]),
    )


def _hex(h: str) -> tuple[int, int, int, int]:
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255


def _logo_png(variant: str) -> Image.Image:
    colors = _variant_colors(variant)
    wa, wb = _text_widths()
    width = int(TEXT_X + wa + wb + 6)
    img = Image.new("RGBA", (width * SS, MARK_PX * SS), (0, 0, 0, 0))
    _draw_mark(img, (0, 0), MARK_PX * SS, variant)
    font = _font(TEXT_SIZE * SS)
    d = ImageDraw.Draw(img)
    d.text((TEXT_X * SS, TEXT_BASELINE * SS), "ACKE", font=font, fill=_hex(colors["text"]),
           anchor="ls")
    d.text(((TEXT_X + wa) * SS, TEXT_BASELINE * SS), ".in", font=font,
           fill=_hex(colors["accent"]), anchor="ls")
    return img


def _mark_png() -> Image.Image:
    img = Image.new("RGBA", (100 * SS * 2, 100 * SS * 2), (0, 0, 0, 0))
    _draw_mark(img, (0, 0), 100 * SS * 2, "color")
    return img


# ---------------------------------------------------------- backgrounds --------------------------

W, H = 1920, 1080
BAR_COLORS = ("red", "light_blue", "teal", "green", "blue")


def _color_bar(draw: ImageDraw.ImageDraw, y: int, height: int) -> None:
    seg = W // len(BAR_COLORS)
    for i, name in enumerate(BAR_COLORS):
        x1 = W if i == len(BAR_COLORS) - 1 else (i + 1) * seg
        draw.rectangle([i * seg, y, x1, y + height], fill=_rgb(name))


def _bg_title() -> Image.Image:
    top, bottom = _rgb("navy"), _rgb("blue")
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)],
               fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom, strict=True)))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.polygon([(1420, 0), (1920, 0), (1920, 1080), (1140, 1080)], fill=_rgb("white", 12))
    for cx, cy, r, alpha in ((1550, 330, 420, 150), (1700, 760, 260, 180), (1280, 860, 150, 130)):
        pts = [(cx + r * _cos(60 * k - 90), cy + r * _sin(60 * k - 90)) for k in range(6)]
        od.polygon(pts, outline=_rgb("light_blue", alpha), width=5)
    img = Image.alpha_composite(img, overlay)
    _color_bar(ImageDraw.Draw(img), H - 20, 20)
    return img


def _bg_content() -> Image.Image:
    img = Image.new("RGBA", (W, H), _rgb("white"))
    d = ImageDraw.Draw(img)
    _color_bar(d, 0, 14)
    d.rectangle([0, 1008, W, H], fill=_rgb("gray"))  # footer strip starts at 7.0in
    return img


def _cos(deg: float) -> float:
    return math.cos(math.radians(deg))


def _sin(deg: float) -> float:
    return math.sin(math.radians(deg))


# --------------------------------------------------------------- icons --------------------------

ICON_PX = 256
CANVAS = 512


def _icon(name: str) -> Image.Image:
    colors = {"done": "green", "progress": "blue", "blocked": "red", "risk": "amber",
              "next": "light_blue", "velocity": "blue", "goal": "teal"}
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([8, 8, 504, 504], fill=_rgb(colors[name]))
    white, dark = _rgb("white"), _rgb("dark")
    if name == "done":
        d.line([(140, 270), (222, 350), (374, 180)], fill=white, width=44, joint="curve")
        for x, y in ((140, 270), (374, 180)):
            d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=white)
    elif name == "progress":
        d.polygon([(190, 140), (190, 372), (380, 256)], fill=white)
    elif name == "blocked":
        d.rounded_rectangle([120, 222, 392, 290], radius=30, fill=white)
    elif name == "risk":
        d.rounded_rectangle([232, 120, 280, 300], radius=20, fill=dark)
        d.ellipse([230, 330, 282, 382], fill=dark)
    elif name == "next":
        d.line([(130, 256), (320, 256)], fill=white, width=44)
        d.polygon([(290, 160), (410, 256), (290, 352)], fill=white)
    elif name == "velocity":
        for x0, top in ((130, 300), (222, 230), (314, 160)):
            d.rounded_rectangle([x0, top, x0 + 70, 380], radius=10, fill=white)
    elif name == "goal":
        d.ellipse([116, 116, 396, 396], outline=white, width=36)
        d.ellipse([216, 216, 296, 296], fill=white)
    return img.resize((ICON_PX, ICON_PX), Image.LANCZOS)


# ---------------------------------------------------------------- main --------------------------


def generate(force: bool = False) -> list[str]:
    """Write every asset that is missing (or all with force). Returns the files written."""
    theme.ICONS_DIR.mkdir(parents=True, exist_ok=True)
    jobs: dict[str, object] = {
        "acke-logo.svg": _logo_svg("color"),
        "acke-logo-white.svg": _logo_svg("white"),
        "acke-logo-mark.svg": _mark_only_svg(),
        "acke-logo.png": lambda: _logo_png("color"),
        "acke-logo-white.png": lambda: _logo_png("white"),
        "acke-logo-mark.png": _mark_png,
        "bg-title.png": _bg_title,
        "bg-content.png": _bg_content,
        **{f"icons/{n}.png": (lambda n=n: _icon(n)) for n in theme.ICON_NAMES},
    }
    written = []
    for name, job in jobs.items():
        path = theme.ASSETS_DIR / name
        if path.exists() and not force:
            continue
        if isinstance(job, str):
            path.write_text(job, encoding="utf-8")
        else:
            job().save(path)  # type: ignore[operator]
        written.append(name)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="regenerate existing files")
    args = parser.parse_args()
    written = generate(force=args.force)
    print(f"Wrote {len(written)} asset(s) to {theme.ASSETS_DIR}")
    for name in written:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
