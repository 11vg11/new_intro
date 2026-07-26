#!/usr/bin/env python3
"""
render_heatmap_svg.py — Render data/contributions.json as an animated heatmap SVG.

Features:
  • Classic 53-week × 7-day contribution grid of rounded boxes.
  • GitHub-ish green palette with a neon top tier.
  • One-shot diagonal reveal (column-by-column, CSS keyframes, no looping glow).
  • Less→More legend + stats footer.

Usage:
    python scripts/render_heatmap_svg.py

Reads:   data/contributions.json  (produced by fetch_contributions.py)
Writes:  contrib-heatmap.svg
"""

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

try:
    from .config import get_output_paths
except ImportError:  # pragma: no cover - direct script execution
    from config import get_output_paths

# ── Config ────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).parent.parent
OUTPUT_PATHS = get_output_paths(ROOT)
IN_PATH   = OUTPUT_PATHS["contributions"]
OUT_PATH  = OUTPUT_PATHS["heatmap"]

# Colour ramp: none → level 1 → … → level 5 (neon top)
PALETTE = [
    "#161b22",   # 0 – no contribution
    "#0e4429",   # 1 – very low
    "#006d32",   # 2 – low
    "#26a641",   # 3 – medium
    "#39d353",   # 4 – high
    "#69f0a0",   # 5 – maximum (neon)
]

BG      = "#0d1117"
BORDER  = "#21262d"
TEXT_DIM   = "#8b949e"
TEXT_WHITE = "#e6edf3"
ACCENT     = "#58a6ff"

# Grid geometry
BOX       = 12     # px — cell size
GAP       = 3      # px — gap between cells
RADIUS    = 2      # px — cell corner radius
PAD_LEFT  = 36    # space for day-of-week labels
PAD_TOP   = 24    # space for month labels
PAD_BOT   = 54    # space for legend + stats
PAD_RIGHT = 14

WEEKS     = 53
DAYS      = 7     # rows (Mon–Sun)

GRID_W = WEEKS * (BOX + GAP) - GAP
GRID_H = DAYS  * (BOX + GAP) - GAP
SVG_W  = PAD_LEFT + GRID_W + PAD_RIGHT
SVG_H  = PAD_TOP  + GRID_H + PAD_BOT

# Animation
COL_STAGGER = 0.025   # seconds between each week column appearing
SLIDE_PX    = 10      # pixels each column slides in from below

# Day-of-week labels (GitHub uses Mon, Wed, Fri)
DOW_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}

# ── Helpers ───────────────────────────────────────────────────────────────────

def count_to_level(count: int) -> int:
    if count == 0:   return 0
    if count <= 2:   return 1
    if count <= 5:   return 2
    if count <= 9:   return 3
    if count <= 15:  return 4
    return 5


def build_week_grid(days_data: dict[str, int]) -> list[list[tuple[str, int]]]:
    """
    Return a list of WEEKS columns, each column a list of DAYS (date_str, count).
    The grid starts on the Sunday of the week that is exactly 52 weeks before
    the current week (GitHub's convention).
    """
    today    = date.today()
    # Start from Sunday, 52 full weeks ago
    start    = today - timedelta(weeks=52, days=today.weekday() + 1)
    # Rewind to the previous Sunday
    while start.weekday() != 6:
        start -= timedelta(days=1)

    grid = []
    cur  = start
    for _ in range(WEEKS):
        col = []
        for _ in range(DAYS):
            ds    = cur.isoformat()
            count = days_data.get(ds, 0)
            col.append((ds, count))
            cur += timedelta(days=1)
        grid.append(col)
    return grid


def month_labels(grid: list[list[tuple[str, int]]]) -> list[tuple[int, str]]:
    """Return [(week_idx, 'Jan'), ...] for the first week of each month."""
    seen   = set()
    result = []
    for w_idx, col in enumerate(grid):
        ds    = col[0][0]              # first day of the week
        month = datetime.strptime(ds, "%Y-%m-%d").strftime("%b")
        if month not in seen:
            seen.add(month)
            result.append((w_idx, month))
    return result


# ── CSS keyframe animation ────────────────────────────────────────────────────

def css_keyframes(n_weeks: int) -> str:
    """Generate one keyframe per week column."""
    frames = []
    for i in range(n_weeks):
        begin_s = i * COL_STAGGER
        # We use a CSS class per column; each class references a named animation.
        # Because GitHub renders SVG-in-img, CSS animations inside the SVG play.
        anim_name = f"col{i}"
        frames.append(
            f"  @keyframes {anim_name} {{\n"
            f"    0%   {{ opacity: 0; transform: translateY({SLIDE_PX}px); }}\n"
            f"    100% {{ opacity: 1; transform: translateY(0); }}\n"
            f"  }}\n"
            f"  .c{i} {{\n"
            f"    animation: {anim_name} 0.3s ease forwards;\n"
            f"    animation-delay: {begin_s:.3f}s;\n"
            f"    opacity: 0;\n"
            f"  }}\n"
        )
    return "".join(frames)


# ── SVG builder ───────────────────────────────────────────────────────────────

def build_svg(data: dict) -> str:
    days_data = data.get("days", {})
    stats     = data.get("stats", {})
    username  = data.get("username", "")

    grid      = build_week_grid(days_data)
    m_labels  = month_labels(grid)

    parts: list[str] = []

    # Header
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_W}" height="{SVG_H}" '
        f'viewBox="0 0 {SVG_W} {SVG_H}">'
    )

    # Background
    parts.append(f'  <rect width="100%" height="100%" rx="10" fill="{BG}"/>')
    parts.append(f'  <rect width="100%" height="100%" rx="10" fill="none" '
                 f'stroke="{BORDER}" stroke-width="1"/>')

    # CSS animations
    parts.append(f'  <style>\n{css_keyframes(WEEKS)}\n  </style>')

    # ── Month labels ──────────────────────────────────────────────────────────
    for w_idx, month_name in m_labels:
        x = PAD_LEFT + w_idx * (BOX + GAP)
        parts.append(
            f'  <text x="{x}" y="{PAD_TOP - 6}" '
            f'font-family="\'Segoe UI\', Ubuntu, sans-serif" '
            f'font-size="10" fill="{TEXT_DIM}">{month_name}</text>'
        )

    # ── Day-of-week labels ────────────────────────────────────────────────────
    for dow, label in DOW_LABELS.items():
        y = PAD_TOP + dow * (BOX + GAP) + BOX - 2
        parts.append(
            f'  <text x="{PAD_LEFT - 6}" y="{y}" text-anchor="end" '
            f'font-family="\'Segoe UI\', Ubuntu, sans-serif" '
            f'font-size="10" fill="{TEXT_DIM}">{label}</text>'
        )

    # ── Grid cells ────────────────────────────────────────────────────────────
    for w_idx, col in enumerate(grid):
        gx = PAD_LEFT + w_idx * (BOX + GAP)
        parts.append(f'  <g class="c{w_idx}">')
        for d_idx, (ds, count) in enumerate(col):
            gy    = PAD_TOP + d_idx * (BOX + GAP)
            level = count_to_level(count)
            color = PALETTE[level]
            tip   = f"{count} contribution{'s' if count != 1 else ''} on {ds}"
            parts.append(
                f'    <rect x="{gx}" y="{gy}" width="{BOX}" height="{BOX}" '
                f'rx="{RADIUS}" fill="{color}">'
                f'<title>{escape(tip)}</title></rect>'
            )
        parts.append("  </g>")

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_y  = PAD_TOP + GRID_H + 18
    legend_x0 = PAD_LEFT
    parts.append(
        f'  <text x="{legend_x0}" y="{legend_y + BOX - 1}" '
        f'font-family="\'Segoe UI\', Ubuntu, sans-serif" '
        f'font-size="10" fill="{TEXT_DIM}">Less</text>'
    )
    for i, color in enumerate(PALETTE):
        bx = legend_x0 + 30 + i * (BOX + 3)
        parts.append(
            f'  <rect x="{bx}" y="{legend_y}" width="{BOX}" height="{BOX}" '
            f'rx="{RADIUS}" fill="{color}"/>'
        )
    more_x = legend_x0 + 30 + len(PALETTE) * (BOX + 3) + 4
    parts.append(
        f'  <text x="{more_x}" y="{legend_y + BOX - 1}" '
        f'font-family="\'Segoe UI\', Ubuntu, sans-serif" '
        f'font-size="10" fill="{TEXT_DIM}">More</text>'
    )

    # ── Stats footer ──────────────────────────────────────────────────────────
    footer_y = legend_y + BOX + 18
    total    = stats.get("total", 0)
    streak   = stats.get("current_streak", 0)
    longest  = stats.get("longest_streak", 0)
    best     = stats.get("best_day", {})
    best_str = f"{best.get('count', 0)} on {best.get('date', '')}" if best else ""

    stat_items = [
        f"{total:,} contributions in the last year",
        f"🔥 {streak}-day current streak",
        f"⚡ {longest}-day best streak",
        f"🏆 Best: {best_str}",
    ]
    # Display stats as a single wrapped row
    footer_parts = []
    for i, item in enumerate(stat_items):
        x = PAD_LEFT + i * (SVG_W - PAD_LEFT - PAD_RIGHT) // len(stat_items)
        parts.append(
            f'  <text x="{x}" y="{footer_y}" '
            f'font-family="\'Segoe UI\', Ubuntu, sans-serif" '
            f'font-size="10" fill="{TEXT_DIM}">{escape(item)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    if not IN_PATH.exists():
        print(f"[render_heatmap_svg] ERROR: {IN_PATH} not found.")
        print("  Run fetch_contributions.py first.")
        sys.exit(1)

    data = json.loads(IN_PATH.read_text(encoding="utf-8"))
    svg  = build_svg(data)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(svg, encoding="utf-8")

    days  = len(data.get("days", {}))
    total = data.get("stats", {}).get("total", "?")
    print(f"[render_heatmap_svg] ✓ {days} days · {total} contributions → {OUT_PATH}")


if __name__ == "__main__":
    main()
