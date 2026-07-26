#!/usr/bin/env python3
"""
make_ascii_svg.py — Convert source-prepped.png into a self-typing ASCII SVG.

Design principles:
  • Monochrome — one light-gray fill color; no per-character rainbow.
  • High contrast — bright background → space glyph, so only the subject prints.
  • SMIL animation — each row clips left→right with a small block cursor,
    staggered top-to-bottom.  Plays once and freezes.  No looping.
  • Self-contained — the SVG embeds everything; GitHub renders it via <img>.

Usage:
    python scripts/make_ascii_svg.py

Reads:   source-prepped.png  (produced by prep_photo.py)
Writes:  avi-ascii.svg
"""

import sys
from pathlib import Path
from xml.sax.saxutils import escape

try:
    from .config import get_output_paths
except ImportError:  # pragma: no cover - direct script execution
    from config import get_output_paths

try:
    from PIL import Image
    import numpy as np
except ImportError as e:
    print(f"[make_ascii_svg] Missing dependency: {e}")
    print("Run:  pip install pillow numpy")
    sys.exit(1)

# Configuration
ROOT = Path(__file__).parent.parent
OUTPUT_PATHS = get_output_paths(ROOT)
INPUT_PATH = ROOT / "source-prepped.png"
OUTPUT_PATH = OUTPUT_PATHS["ascii"]

# Character grid size
COLS = 100
ROWS = 53

# Bright-to-dark character ramp; whitespace preserves the brightest pixels
RAMP = " .`:-=+*cs#%@"

# Render settings
FONT_SIZE = 7
CHAR_W = FONT_SIZE * 0.60
CHAR_H = FONT_SIZE * 1.20
FILL_COLOR = "#c9d1d9"
BG_COLOR = "#0d1117"
CURSOR_W = CHAR_W

# Animation timing
ROW_DURATION = 0.06
ROW_STAGGER = 0.04


def brightness_to_char(value: float) -> str:
    """Map a 0-255 brightness value to a RAMP character."""
    idx = int(value / 255 * (len(RAMP) - 1))
    return RAMP[idx]


def load_grid(path: Path) -> list[list[str]]:
    """Downsample the prepped image to COLS×ROWS and map to chars."""
    img = Image.open(path).convert("L")
    # Correct for font aspect ratio: characters are taller than wide,
    # so we need fewer rows relative to cols.
    img = img.resize((COLS, ROWS), Image.LANCZOS)
    pixels = np.array(img)
    grid = []
    for row in pixels:
        grid.append([brightness_to_char(p) for p in row])
    return grid


def build_svg(grid: list[list[str]]) -> str:
    nrows = len(grid)
    ncols = max(len(r) for r in grid)

    svg_w = ncols * CHAR_W + 4
    svg_h = nrows * CHAR_H + 4

    lines = []
    # ── Header ────────────────────────────────────────────────────────────────
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg"')
    lines.append(f'     xmlns:xlink="http://www.w3.org/1999/xlink"')
    lines.append(f'     width="{svg_w:.0f}" height="{svg_h:.0f}"')
    lines.append(f'     viewBox="0 0 {svg_w:.0f} {svg_h:.0f}">')
    lines.append(f'  <rect width="100%" height="100%" fill="{BG_COLOR}"/>')
    lines.append(f'  <style>')
    lines.append(f'    text {{ font-family: "Courier New", Courier, monospace;')
    lines.append(f'           font-size: {FONT_SIZE}px; fill: {FILL_COLOR}; }}')
    lines.append(f'  </style>')

    # ── Clip paths (one per row) + animated text rows ─────────────────────────
    lines.append("  <defs>")
    for r_idx in range(nrows):
        row_y = r_idx * CHAR_H + CHAR_H   # baseline y
        clip_h = CHAR_H + 2
        clip_y = r_idx * CHAR_H

        # Each row has a clipPath whose width animates 0 → full
        lines.append(
            f'    <clipPath id="clip{r_idx}">'
            f'      <rect id="cr{r_idx}" x="0" y="{clip_y:.1f}" '
            f'width="0" height="{clip_h:.1f}"/>'
            f'    </clipPath>'
        )
    lines.append("  </defs>")

    # ── Rows ──────────────────────────────────────────────────────────────────
    for r_idx, row in enumerate(grid):
        row_y = r_idx * CHAR_H + CHAR_H   # text baseline
        row_w = ncols * CHAR_W
        start = r_idx * (ROW_DURATION + ROW_STAGGER)
        end   = start + ROW_DURATION

        # Build the row text (join chars; SVG will render monospace)
        row_text = escape("".join(row))

        # Clip-rect animation: width 0 → row_w
        lines.append(
            f'  <animate xlink:href="#cr{r_idx}" attributeName="width" '
            f'from="0" to="{row_w:.1f}" '
            f'begin="{start:.3f}s" dur="{ROW_DURATION:.3f}s" '
            f'fill="freeze"/>'
        )

        # Text element (clipped to its row)
        lines.append(
            f'  <text x="2" y="{row_y:.1f}" clip-path="url(#clip{r_idx})"'
            f' xml:space="preserve">{row_text}</text>'
        )

        # Block cursor: rides the right edge of the wipe, then vanishes
        cur_x_start = 0
        cur_x_end   = row_w
        lines.append(
            f'  <rect x="{cur_x_start:.1f}" y="{r_idx * CHAR_H:.1f}" '
            f'width="{CURSOR_W:.1f}" height="{CHAR_H:.1f}" fill="{FILL_COLOR}" opacity="0.8">'
            # move cursor along the row
            f'    <animate attributeName="x" '
            f'from="{cur_x_start:.1f}" to="{cur_x_end:.1f}" '
            f'begin="{start:.3f}s" dur="{ROW_DURATION:.3f}s" fill="freeze"/>'
            # hide cursor once the row is done
            f'    <animate attributeName="opacity" '
            f'from="0.8" to="0" '
            f'begin="{end:.3f}s" dur="0.05s" fill="freeze"/>'
            f'  </rect>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


def main() -> None:
    if not INPUT_PATH.exists():
        print(f"[make_ascii_svg] ERROR: {INPUT_PATH} not found.")
        print("  Run prep_photo.py first:  python scripts/prep_photo.py <photo.jpg>")
        sys.exit(1)

    print(f"[make_ascii_svg] Loading {INPUT_PATH} …")
    grid = load_grid(INPUT_PATH)
    print(f"[make_ascii_svg] Grid: {len(grid[0])}×{len(grid)} chars")

    svg = build_svg(grid)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(svg, encoding="utf-8")
    total_time = len(grid) * (ROW_DURATION + ROW_STAGGER)
    print(f"[make_ascii_svg] ✓ Saved → {OUTPUT_PATH}  (animation: ~{total_time:.1f}s)")


if __name__ == "__main__":
    main()
