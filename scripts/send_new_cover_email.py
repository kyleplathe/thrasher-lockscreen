#!/usr/bin/env python3
"""
Send a fun notification email when new cover(s) land (meant for GitHub Actions).

Requires secrets:
  RESEND_API_KEY  — from https://resend.com (free tier OK)
  NOTIFY_EMAIL    — recipient (e.g. your iCloud address)

Optional:
  EMAIL_FROM      — verified sender, e.g. "Thrasher Covers <news@yourdomain.com>"
                    If unset, uses Resend's test sender (only works for testing rules on Resend).

Skips quietly if RESEND_API_KEY is not set.

Optional:
  SHORTCUTS_URL   — override iCloud Shortcuts link (default is set in this file).
"""

from __future__ import annotations

import json
import os
import random
import re
import subprocess
import sys
import urllib.error
import urllib.request

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

SUBJECT_EMOJIS = [
    "🛹🔥📸",
    "🛹✨🗓️",
    "🔥📰🛹",
    "🛼💥📸",
    "🛹🖤✨",
    "📸🔥🛹",
]

# Thrasher Cover Shortcut (iOS) — share with anyone who gets this email.
# Override with SHORTCUTS_URL env / GitHub secret if the link ever changes.
DEFAULT_SHORTCUTS_URL = (
    "https://www.icloud.com/shortcuts/f7b91ae83200412b9c211e7b6b73f53a"
)


def git_changed_files() -> list[str]:
    out = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_cover_filename(name: str) -> tuple[str, str] | None:
    """Return (label, sort_key) for display, or None if not a cover we describe."""
    base = name.split("/")[-1]
    m = re.match(r"^(?P<y>\d{4})_(?P<mm>\d{2})\.jpg$", base, re.I)
    if m:
        y, mm = m.group("y"), m.group("mm")
        mi = int(mm)
        if 1 <= mi <= 12:
            label = f"{MONTHS[mi - 1]} {y}"
            return label, f"{y}-{mm}"
    m2 = re.match(r"^(?P<y>\d{4})_(?P<sp>Summer|PhotoIssue)\.jpg$", base, re.I)
    if m2:
        y, sp = m2.group("y"), m2.group("sp")
        if sp.lower() == "summer":
            return f"Summer {y}", f"{y}-summer"
        return f"Photo Issue {y}", f"{y}-photo"
    return None


def metadata_blurb(filename: str, data: dict) -> str:
    for img in data.get("images", []):
        if img.get("filename") != filename:
            continue
        meta = img.get("metadata") or {}
        bits: list[str] = []
        sk = (meta.get("skater") or "").strip()
        tr = (meta.get("trick") or "").strip()
        loc = (meta.get("location") or "").strip()
        if sk:
            bits.append(sk)
        if tr:
            bits.append(tr)
        if loc:
            bits.append(f"📍 {loc}")
        if bits:
            return " · ".join(bits[:4])
    return ""


def shortcuts_url() -> str:
    return (os.environ.get("SHORTCUTS_URL") or "").strip() or DEFAULT_SHORTCUTS_URL


def build_email(changed: list[str], data: dict) -> tuple[str, str]:
    covers: list[tuple[str, str, str]] = []
    for path in changed:
        if "optimized_final_with_text/" not in path and "images/optimized_final_with_text/" not in path:
            continue
        base = path.split("/")[-1]
        parsed = parse_cover_filename(base)
        if not parsed:
            continue
        label, _ = parsed
        blurb = metadata_blurb(base, data)
        covers.append((base, label, blurb))

    if not covers:
        # Fallback: any new jpg under images/
        for path in changed:
            if not path.lower().endswith(".jpg"):
                continue
            base = path.split("/")[-1]
            parsed = parse_cover_filename(base)
            if parsed:
                label, _ = parsed
                covers.append((base, label, metadata_blurb(base, data)))

    link = shortcuts_url()
    emoji = random.choice(SUBJECT_EMOJIS)
    if len(covers) == 1:
        _base, label, _blurb = covers[0]
        subject = f"{emoji} New cover live — {label} · Thrasher shortcut"
    else:
        subject = f"{emoji} {len(covers)} new covers · Thrasher Cover shortcut"

    lines = [
        "<div style='font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; max-width: 560px; color:#111;'>",
        "<p style='font-size:11px; letter-spacing:0.12em; text-transform:uppercase; color:#888; margin:0 0 8px;'>",
        "Thrasher cover · lock screen automation",
        "</p>",
        "<h1 style='font-size:22px; line-height:1.25; margin:0 0 14px; font-weight:800;'>",
        "Fresh ink just hit the repo 🔥",
        "</h1>",
        "<p style='font-size:16px; line-height:1.5; margin:0 0 18px; color:#333;'>",
        "Your <strong>Thrasher Cover Shortcut Automation</strong> pipeline pulled in a new magazine cover—optimized, "
        "text overlay and all—ready for your iPhone wallpaper rotation.",
        "</p>",
        "<p style='font-size:15px; line-height:1.5; margin:0 0 22px; color:#444;'>",
        "Tap through with the shortcut below: random cover, same layout you love, zero hunting on Instagram.",
        "</p>",
    ]
    for base, label, blurb in covers:
        lines.append(
            "<div style='border:1px solid #e5e5e5; border-radius:14px; padding:16px 18px; margin:14px 0; "
            "background:linear-gradient(180deg,#fafafa 0%,#fff 100%);'>"
        )
        lines.append(f"<p style='margin:0 0 4px; font-size:12px; color:#888;'>Just added</p>")
        lines.append(f"<p style='margin:0 0 8px; font-size:19px; font-weight:800;'>{label}</p>")
        lines.append(f"<p style='margin:0; color:#666; font-size:13px; font-family:ui-monospace,monospace;'>{base}</p>")
        if blurb:
            lines.append(f"<p style='margin:12px 0 0; font-size:15px; color:#222; line-height:1.45;'>{blurb}</p>")
        else:
            lines.append(
                "<p style='margin:12px 0 0; font-size:14px; color:#666; line-height:1.45;'>"
                "Full skater / trick metadata shows up in the feed when it’s in the JSON—either way, the cover art "
                "is ready to roll.</p>"
            )
        lines.append("</div>")

    lines.extend(
        [
            "<div style='margin:26px 0 18px; padding:20px 22px; border-radius:14px; background:#111; color:#fff;'>",
            "<p style='margin:0 0 10px; font-size:15px; font-weight:700;'>Get the Thrasher Cover shortcut</p>",
            "<p style='margin:0 0 16px; font-size:14px; line-height:1.5; opacity:0.92;'>",
            "One tap → pull from the live cover list → set your lock screen. Share it with friends who actually skate.",
            "</p>",
            f"<a href=\"{link}\" style=\"display:inline-block; background:#fff; color:#111; padding:12px 22px; "
            "border-radius:999px; text-decoration:none; font-weight:800; font-size:15px;\">",
            "Open in Shortcuts →",
            "</a>",
            "</div>",
            f"<p style='font-size:12px; color:#999; margin:0 0 6px; word-break:break-all;'>{link}</p>",
            "<p style='font-size:13px; color:#888; margin:18px 0 0; line-height:1.45;'>",
            "This email fires when GitHub Actions ships a real update—same automation that keeps your shortcut JSON "
            "and images in sync. Skate and destroy. 🛹",
            "</p>",
            "</div>",
        ]
    )
    html = "\n".join(lines)
    return subject, html


def send_resend(api_key: str, to_addr: str, from_addr: str, subject: str, html: str) -> None:
    payload = json.dumps(
        {
            "from": from_addr,
            "to": [to_addr],
            "subject": subject,
            "html": html,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        if resp.status not in (200, 201):
            raise RuntimeError(f"Resend HTTP {resp.status}: {body}")


def main() -> int:
    api_key = (os.environ.get("RESEND_API_KEY") or "").strip()
    to_addr = (os.environ.get("NOTIFY_EMAIL") or "").strip()
    if not api_key or not to_addr:
        print(
            "Skipping email: set RESEND_API_KEY and NOTIFY_EMAIL secrets "
            "(see scripts/AUTOMATION_SETUP.md)."
        )
        return 0

    from_addr = (os.environ.get("EMAIL_FROM") or "").strip()
    if not from_addr:
        from_addr = "Thrasher Lock Screen <onboarding@resend.dev>"

    try:
        changed = git_changed_files()
    except subprocess.CalledProcessError as e:
        print("git diff-tree failed:", e, file=sys.stderr)
        return 1

    json_path = "shortcuts_text_overlay_covers.json"
    if not os.path.isfile(json_path):
        print("No shortcuts_text_overlay_covers.json", file=sys.stderr)
        return 1

    data = load_json(json_path)
    subject, html = build_email(changed, data)

    try:
        send_resend(api_key, to_addr, from_addr, subject, html)
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        print(f"Resend HTTP error: {e.code} {err}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Resend error: {e}", file=sys.stderr)
        return 1

    print("Email sent OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
