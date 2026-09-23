#!/usr/bin/env python3
"""
Keep README.md in sync with shortcuts_text_overlay_covers.json.

Updates:
  - Hero image (latest cover under images/original/)
  - Cover counts
  - Year range (e.g. 1981-2026)
  - Span in years

Run after the monthly scraper / cover processing so the next commit
includes an accurate README. Safe to run anytime (idempotent).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "shortcuts_text_overlay_covers.json"
README_PATH = ROOT / "README.md"
ORIGINAL_DIR = ROOT / "images" / "original"

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

REPO_RAW = (
    "https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/"
    "images/original/"
)


def cover_sort_key(filename: str) -> tuple[int, int, int]:
    base = filename.split("/")[-1]
    m = re.match(r"^(?P<y>\d{4})_(?P<mm>\d{2})\.jpg$", base, re.I)
    if m:
        return (int(m.group("y")), int(m.group("mm")), 0)
    m2 = re.match(r"^(?P<y>\d{4})_(?P<sp>Summer|PhotoIssue)\.jpg$", base, re.I)
    if m2:
        y = int(m2.group("y"))
        sp = m2.group("sp").lower()
        return (y, 13 if sp == "summer" else 14, 0)
    return (0, 0, 0)


def display_label(filename: str) -> str:
    base = filename.split("/")[-1]
    m = re.match(r"^(?P<y>\d{4})_(?P<mm>\d{2})\.jpg$", base, re.I)
    if m:
        y, mm = m.group("y"), int(m.group("mm"))
        if 1 <= mm <= 12:
            return f"{MONTHS[mm - 1]} {y}"
    m2 = re.match(r"^(?P<y>\d{4})_(?P<sp>Summer|PhotoIssue)\.jpg$", base, re.I)
    if m2:
        y, sp = m2.group("y"), m2.group("sp")
        if sp.lower() == "summer":
            return f"Summer {y}"
        return f"Photo Issue {y}"
    return base


def year_from_filename(filename: str) -> int | None:
    m = re.match(r"^(\d{4})_", filename.split("/")[-1])
    return int(m.group(1)) if m else None


def load_stats() -> dict:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    images = data.get("images") or []
    filenames = [img.get("filename") or "" for img in images if img.get("filename")]
    if not filenames:
        raise SystemExit("No cover filenames in JSON")

    filenames_sorted = sorted(filenames, key=cover_sort_key)
    count = int(data.get("total_images") or len(filenames_sorted))
    if count != len(filenames_sorted):
        count = len(filenames_sorted)

    years = sorted({y for y in (year_from_filename(f) for f in filenames_sorted) if y})
    first_year, last_year = years[0], years[-1]
    latest = filenames_sorted[-1]
    label = display_label(latest)
    span = last_year - first_year + 1

    original = ORIGINAL_DIR / latest
    if not original.is_file():
        print(f"Warning: {original} missing; README will still point at it.", file=sys.stderr)

    return {
        "count": count,
        "first_year": first_year,
        "last_year": last_year,
        "span": span,
        "latest_filename": latest,
        "latest_label": label,
        "hero_url": f"{REPO_RAW}{latest}",
    }


def update_readme(text: str, stats: dict) -> str:
    count = stats["count"]
    first = stats["first_year"]
    last = stats["last_year"]
    span = stats["span"]
    label = stats["latest_label"]
    hero = stats["hero_url"]
    year_range = f"{first}-{last}"

    # Hero: ![Month Year Cover](…/YYYY_MM.jpg)
    text, n = re.subn(
        r"!\[.*?Cover\]\(https://raw\.githubusercontent\.com/kyleplathe/"
        r"thrasher-lockscreen/main/images/original/[^)]+\)",
        f"![{label} Cover]({hero})",
        text,
        count=1,
    )
    if n != 1:
        raise SystemExit("Could not find README hero image markdown to update")

    # "provides **N Thrasher Magazine covers** from YYYY-YYYY"
    text, n = re.subn(
        r"provides \*\*\d+ Thrasher Magazine covers\*\* from \d{4}-\d{4}",
        f"provides **{count} Thrasher Magazine covers** from {year_range}",
        text,
        count=1,
    )
    if n != 1:
        raise SystemExit("Could not find README intro cover-count sentence")

    # "complete collection of N covers"
    text, n = re.subn(
        r"complete collection of \d+ covers",
        f"complete collection of {count} covers",
        text,
        count=1,
        flags=re.I,
    )
    if n != 1:
        raise SystemExit("Could not find README data-sources cover-count phrase")

    # "**N covers** spanning N years (YYYY-YYYY)"
    text, n = re.subn(
        r"\*\*\d+ covers\*\* spanning \d+ years \(\d{4}-\d{4}\)",
        f"**{count} covers** spanning {span} years ({year_range})",
        text,
        count=1,
    )
    if n != 1:
        raise SystemExit("Could not find README 'What You Get' cover-count bullet")

    # "picks from N options"
    text, n = re.subn(
        r"picks from \d+ options",
        f"picks from {count} options",
        text,
        count=1,
    )
    if n != 1:
        raise SystemExit("Could not find README troubleshooting cover-count phrase")

    return text


def main() -> int:
    if not JSON_PATH.is_file():
        print(f"Missing {JSON_PATH}", file=sys.stderr)
        return 1
    if not README_PATH.is_file():
        print(f"Missing {README_PATH}", file=sys.stderr)
        return 1

    stats = load_stats()
    before = README_PATH.read_text(encoding="utf-8")
    after = update_readme(before, stats)
    if after == before:
        print(
            f"README already up to date: {stats['count']} covers, "
            f"{stats['first_year']}-{stats['last_year']}, hero {stats['latest_filename']}"
        )
        return 0

    README_PATH.write_text(after, encoding="utf-8")
    print(
        f"Updated README: {stats['count']} covers, "
        f"{stats['first_year']}-{stats['last_year']} ({stats['span']} years), "
        f"hero {stats['latest_label']} ({stats['latest_filename']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
