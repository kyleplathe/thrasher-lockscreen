#!/usr/bin/env python3
"""
Remove JPGs under images/optimized_final_with_text/ that are NOT listed in
shortcuts_text_overlay_covers.json — keeps the folder aligned with the Shortcut
feed and restores clean YYYY_MM sorting.

Usage:
  python3 scripts/prune_orphan_optimized_covers.py          # delete orphans
  python3 scripts/prune_orphan_optimized_covers.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys

JSON_FILE = "shortcuts_text_overlay_covers.json"
OPT_DIR = os.path.join("images", "optimized_final_with_text")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be deleted without deleting",
    )
    args = ap.parse_args()

    if not os.path.isfile(JSON_FILE):
        print(f"Missing {JSON_FILE}", file=sys.stderr)
        return 1
    if not os.path.isdir(OPT_DIR):
        print(f"Missing {OPT_DIR}", file=sys.stderr)
        return 1

    with open(JSON_FILE, encoding="utf-8") as f:
        data = json.load(f)
    required = {img["filename"] for img in data.get("images", []) if img.get("filename")}

    on_disk = {
        f
        for f in os.listdir(OPT_DIR)
        if f.lower().endswith(".jpg") and os.path.isfile(os.path.join(OPT_DIR, f))
    }

    orphans = sorted(on_disk - required)
    missing = sorted(required - on_disk)

    if missing:
        print("ERROR: JSON references files not on disk:", file=sys.stderr)
        for m in missing[:30]:
            print(f"  {m}", file=sys.stderr)
        if len(missing) > 30:
            print(f"  ... and {len(missing) - 30} more", file=sys.stderr)
        return 1

    print(f"Required (from JSON): {len(required)}")
    print(f"On disk: {len(on_disk)}")
    print(f"Orphans to remove: {len(orphans)}")

    for name in orphans:
        path = os.path.join(OPT_DIR, name)
        if args.dry_run:
            print(f"  would delete: {name}")
        else:
            os.remove(path)
            print(f"  deleted: {name}")

    if args.dry_run and orphans:
        print("\nRun without --dry-run to delete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
