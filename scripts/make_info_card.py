#!/usr/bin/env python3
"""
make_info_card.py — Generate a neofetch-style info card SVG.

The card mimics the classic `neofetch` terminal output:
  • A "title bar" with your handle and a separator line.
  • Colored key/value rows: Now, Prev, Stack, Highlights.
  • Each line fades in + slides up on a short stagger.
  • A STATIC=1 env var skips animation for local preview.

Usage:
    python scripts/make_info_card.py

Writes: info-card.svg
"""

import os
from pathlib import Path
from xml.sax.saxutils import escape

try:
    from .config import get_info_card_rows, get_output_paths
except ImportError:  # pragma: no cover - direct script execution
    from config import get_info_card_rows, get_output_paths

# ── Config ────────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).parent.parent
OUTPUT_PATHS = get_output_paths(ROOT)
OUTPUT_PATH = OUTPUT_PATHS["info_card"]
STATIC      = os.environ.get("STATIC", "") == "1"

CARD_W = 490
FONT_MONO = '"Courier New", Courier, monospace'
FONT_SANS = '"Segoe UI", Ubuntu, Sans-Serif'

BG        = "#0d1117"
BORDER    = "#30363d"
ACCENT    = "#58a6ff"    # blue — username / keys
GREEN     = "#3fb950"    # green — separator / language bullets
DIM       = "#8b949e"    # gray — parenthetical text
WHITE     = "#e6edf3"    # bright white — values
ORANGE    = "#ffa657"    # orange — highlight items

# Edit these to personalise the card ─────────────────────────────────────────
HANDLE    = "avivashishta"         # shown as  avivashishta@github
SEPARATOR = "─" * 26              # matches the key width visually

ROWS = get_info_card_rows()

# Layout
PAD_X      = 18
PAD_Y      = 18
LINE_H     = 22      # px between rows
TITLE_H    = 44      # space for the title block
SEP_H      = 20      # space for the separator line
FONT_SIZE  = 13

# Animation
STAGGER    = 0.12    # seconds between each line appearing
FADE_DUR   = 0.25    # seconds to fade + slide each line
SLIDE_PX   = 8       # pixels the line slides up during fade-in


def anim(idx: int, elem_id: str) -> str:
    """Return SMIL animation attributes for a single line element."""
    if STATIC:
        return ""
    begin = idx * STAGGER
    return (
        f'  <animate xlink:href="#{elem_id}" attributeName="opacity" '
        f'from="0" to="1" begin="{begin:.2f}s" dur="{FADE_DUR:.2f}s" fill="freeze"/>\n'
        f'  <animate xlink:href="#{elem_id}" attributeName="transform" '
        f'from="translate(0,{SLIDE_PX})" to="translate(0,0)" '
        f'begin="{begin:.2f}s" dur="{FADE_DUR:.2f}s" fill="freeze"/>\n'
    )


def tspan(text: str, color: str, bold: bool = False) -> str:
    weight = ' font-weight="bold"' if bold else ""
    return f'<tspan fill="{color}"{weight}>{escape(text)}</tspan>'


def main() -> None:
    n_rows   = len(ROWS)
    card_h   = PAD_Y + TITLE_H + SEP_H + n_rows * LINE_H + PAD_Y + 6

    lines: list[str] = []
    anims: list[str] = []

    # ── SVG header ────────────────────────────────────────────────────────────
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg"')
    lines.append(f'     xmlns:xlink="http://www.w3.org/1999/xlink"')
    lines.append(f'     width="{CARD_W}" height="{card_h}"')
    lines.append(f'     viewBox="0 0 {CARD_W} {card_h}">')

    # Background + border
    lines.append(f'  <rect width="100%" height="100%" rx="8" fill="{BG}"/>')
    lines.append(f'  <rect width="100%" height="100%" rx="8" fill="none"'
                 f' stroke="{BORDER}" stroke-width="1"/>')

    # ── Title block ───────────────────────────────────────────────────────────
    title_y = PAD_Y + 14
    elem_id = "title"
    init_opacity = "0" if not STATIC else "1"
    lines.append(
        f'  <text id="{elem_id}" x="{PAD_X}" y="{title_y}" '
        f'font-family={FONT_MONO} font-size="15" opacity="{init_opacity}">'
        f'{tspan(HANDLE, ACCENT, bold=True)}'
        f'{tspan("@", DIM)}'
        f'{tspan("github", WHITE)}'
        f'</text>'
    )
    anims.append(anim(0, elem_id))

    # ── Separator line ────────────────────────────────────────────────────────
    sep_y = title_y + SEP_H
    elem_id = "sep"
    lines.append(
        f'  <text id="{elem_id}" x="{PAD_X}" y="{sep_y}" '
        f'font-family={FONT_MONO} font-size="{FONT_SIZE}" opacity="{init_opacity}">'
        f'{tspan(SEPARATOR, GREEN)}'
        f'</text>'
    )
    anims.append(anim(1, elem_id))

    # ── Data rows ─────────────────────────────────────────────────────────────
    base_y = sep_y + LINE_H + 4
    for i, (k_col, key, v_col, val) in enumerate(ROWS):
        row_y   = base_y + i * LINE_H
        elem_id = f"row{i}"
        key_str = f"{key:<10}"   # left-pad key to fixed width
        lines.append(
            f'  <text id="{elem_id}" x="{PAD_X}" y="{row_y}" '
            f'font-family={FONT_MONO} font-size="{FONT_SIZE}" opacity="{init_opacity}">'
            f'{tspan(key_str, k_col, bold=True)}'
            f'{tspan(": ", DIM)}'
            f'{tspan(val, v_col)}'
            f'</text>'
        )
        anims.append(anim(i + 2, elem_id))   # +2 for title + sep

    # ── Animations (appended after all geometry) ──────────────────────────────
    lines.extend(anims)
    lines.append("</svg>")

    svg = "\n".join(lines)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(svg, encoding="utf-8")
    print(f"[make_info_card] ✓ Saved → {OUTPUT_PATH}  (static={STATIC})")


if __name__ == "__main__":
    main()
