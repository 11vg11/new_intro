#!/usr/bin/env python3
"""
fetch_contributions.py — Scrape GitHub contribution data without a token.

GitHub serves your public contribution calendar as HTML at:
  https://github.com/users/<username>/contributions

This script:
  1. Fetches that page with requests.
  2. Parses each <td data-date="..."> cell with BeautifulSoup.
  3. Derives stats: current streak, longest streak, best day, monthly totals.
  4. Writes data/contributions.json consumed by render_heatmap_svg.py.

Usage:
    python scripts/fetch_contributions.py

Env:
    GITHUB_USER  — GitHub username (default: avivashishta)
"""

import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

# ── Config ────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).parent.parent
OUT_PATH  = ROOT / "data" / "contributions.json"
USERNAME  = os.environ.get("GITHUB_USER", "avivashishta")
URL       = f"https://github.com/users/{USERNAME}/contributions"
HEADERS   = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}
TIMEOUT   = 20   # seconds


class ContributionHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days: dict[str, int] = {}

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "td":
            return
        attr_dict = dict(attrs)
        date_str = attr_dict.get("data-date")
        if not date_str:
            return

        tooltip = attr_dict.get("aria-label", "")
        count = None
        if tooltip:
            try:
                count = int(tooltip.split(" contribution")[0].split()[-1])
            except (ValueError, IndexError):
                count = None

        if count is None:
            level = int(attr_dict.get("data-level", "0") or "0")
            count = [0, 1, 3, 6, 10][level]

        self.days[date_str] = count


# ── Helpers ───────────────────────────────────────────────────────────────────

def fetch_html() -> str:
    print(f"[fetch_contributions] Fetching {URL} …")
    if requests is not None:
        resp = requests.get(URL, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.text

    req = urllib.request.Request(URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        charset = resp.headers.get_content_charset("utf-8")
        return resp.read().decode(charset, "replace")


def parse_days(html: str) -> dict[str, int]:
    """Return {date_str: count} for every <td> with a data-date attribute."""
    if BeautifulSoup is not None:
        soup = BeautifulSoup(html, "html.parser")
        days: dict[str, int] = {}

        for td in soup.find_all("td", attrs={"data-date": True}):
            date_str = td["data-date"]
            tooltip = td.get("aria-label", "")
            try:
                count = int(tooltip.split(" contribution")[0].split()[-1])
            except (ValueError, IndexError):
                level = int(td.get("data-level", 0))
                count = [0, 1, 3, 6, 10][level]
            days[date_str] = count

        return days

    parser = ContributionHTMLParser()
    parser.feed(html)
    return parser.days


def compute_stats(days: dict[str, int]) -> dict:
    if not days:
        return {}

    sorted_dates = sorted(days.keys())
    total        = sum(days.values())
    best_day     = max(days, key=days.__getitem__)

    # ── Streaks ───────────────────────────────────────────────────────────────
    current_streak = longest_streak = streak = 0
    today_str = date.today().isoformat()

    # Walk backwards from today for current streak
    check = date.today()
    while True:
        s = check.isoformat()
        if days.get(s, 0) > 0:
            current_streak += 1
            check -= timedelta(days=1)
        else:
            break

    # Walk all dates for longest streak
    for ds in sorted_dates:
        if days[ds] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0

    # ── Monthly totals ────────────────────────────────────────────────────────
    monthly: dict[str, int] = {}
    for ds, cnt in days.items():
        month_key = ds[:7]   # "YYYY-MM"
        monthly[month_key] = monthly.get(month_key, 0) + cnt

    return {
        "total": total,
        "best_day": {"date": best_day, "count": days[best_day]},
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "monthly": monthly,
    }


def main() -> None:
    html = fetch_html()
    days = parse_days(html)

    if not days:
        print("[fetch_contributions] WARNING: no day cells found — "
              "GitHub may have changed their markup.")

    stats = compute_stats(days)
    out = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "username": USERNAME,
        "days": days,
        "stats": stats,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(
        f"[fetch_contributions] ✓ {len(days)} days · "
        f"total={stats.get('total', '?')} · "
        f"streak={stats.get('current_streak', '?')} · "
        f"best={stats.get('best_day', {}).get('date', '?')}"
        f"({stats.get('best_day', {}).get('count', '?')})"
    )
    print(f"[fetch_contributions] → {OUT_PATH}")


if __name__ == "__main__":
    main()
