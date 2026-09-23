#!/usr/bin/env python3
"""
Open (or update) a GitHub Issue when new Thrasher cover image(s) land.

Meant for GitHub Actions — uses GITHUB_TOKEN + GITHUB_REPOSITORY.
No Resend/ntfy secrets required; watching the repo (or enabling Issues
emails) is enough to get notified.

Skips quietly when HEAD did not add any cover JPGs under
images/original/ or images/optimized_final_with_text/.
"""

from __future__ import annotations

import json
import os
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

LABEL_NAME = "new-cover"


def git_changed_files() -> list[str]:
    out = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def parse_cover_filename(name: str) -> str | None:
    base = name.split("/")[-1]
    m = re.match(r"^(?P<y>\d{4})_(?P<mm>\d{2})\.jpg$", base, re.I)
    if m:
        y, mm = m.group("y"), m.group("mm")
        mi = int(mm)
        if 1 <= mi <= 12:
            return f"{MONTHS[mi - 1]} {y}"
    m2 = re.match(r"^(?P<y>\d{4})_(?P<sp>Summer|PhotoIssue)\.jpg$", base, re.I)
    if m2:
        y, sp = m2.group("y"), m2.group("sp")
        if sp.lower() == "summer":
            return f"Summer {y}"
        return f"Photo Issue {y}"
    return None


def new_cover_labels(changed: list[str]) -> list[tuple[str, str]]:
    """Return unique (filename, display label) for new cover JPGs in this commit."""
    seen: set[str] = set()
    covers: list[tuple[str, str]] = []
    for path in changed:
        if not (
            path.startswith("images/original/")
            or path.startswith("images/optimized_final_with_text/")
        ):
            continue
        if not path.lower().endswith(".jpg"):
            continue
        base = path.split("/")[-1]
        if base in seen:
            continue
        label = parse_cover_filename(base)
        if not label:
            continue
        seen.add(base)
        covers.append((base, label))
    covers.sort(key=lambda x: x[0])
    return covers


def metadata_line(filename: str, data: dict) -> str:
    for img in data.get("images", []):
        if img.get("filename") != filename:
            continue
        meta = img.get("metadata") or {}
        bits: list[str] = []
        for key, prefix in (("skater", ""), ("trick", ""), ("location", "📍 ")):
            val = (meta.get(key) or "").strip()
            if val:
                bits.append(f"{prefix}{val}" if prefix else val)
        if bits:
            return " · ".join(bits)
    return ""


def api_request(method: str, url: str, token: str, payload: dict | None = None) -> dict | list:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "thrasher-lockscreen-notify",
            **({"Content-Type": "application/json"} if payload is not None else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        if not body:
            return {}
        return json.loads(body)


def ensure_label(repo: str, token: str) -> None:
    url = f"https://api.github.com/repos/{repo}/labels/{LABEL_NAME}"
    try:
        api_request("GET", url, token)
        return
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    api_request(
        "POST",
        f"https://api.github.com/repos/{repo}/labels",
        token,
        {
            "name": LABEL_NAME,
            "color": "111111",
            "description": "Automation found a new Thrasher cover in the JSON/image database",
        },
    )


def create_issue(repo: str, token: str, title: str, body: str) -> dict:
    return api_request(  # type: ignore[return-value]
        "POST",
        f"https://api.github.com/repos/{repo}/issues",
        token,
        {"title": title, "body": body, "labels": [LABEL_NAME]},
    )


def main() -> int:
    token = (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "").strip()
    repo = (os.environ.get("GITHUB_REPOSITORY") or "").strip()
    if not token or not repo:
        print("Skipping issue: need GITHUB_TOKEN and GITHUB_REPOSITORY.", file=sys.stderr)
        return 0

    try:
        changed = git_changed_files()
    except subprocess.CalledProcessError as e:
        print("git diff-tree failed:", e, file=sys.stderr)
        return 1

    covers = new_cover_labels(changed)
    if not covers:
        print("No new cover JPGs in HEAD — skipping GitHub Issue.")
        return 0

    data: dict = {}
    json_path = "shortcuts_text_overlay_covers.json"
    if os.path.isfile(json_path):
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

    sha = (
        subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
        .stdout.strip()
        or "HEAD"
    )
    labels = [label for _fn, label in covers]
    if len(covers) == 1:
        title = f"🛹 New Thrasher cover: {labels[0]}"
    else:
        title = f"🛹 {len(covers)} new Thrasher covers: {', '.join(labels)}"

    lines = [
        "The monthly cover automation added new cover art to the JSON database.",
        "",
        f"**Commit:** `{sha}`",
        f"**Total covers now:** {data.get('total_images', len(data.get('images', [])))}",
        "",
        "### Just added",
        "",
    ]
    for filename, label in covers:
        meta = metadata_line(filename, data)
        bullet = f"- **{label}** (`{filename}`)"
        if meta:
            bullet += f" — {meta}"
        lines.append(bullet)
    lines.extend(
        [
            "",
            "Shortcut feed: `shortcuts_text_overlay_covers.json`",
            "",
            "_Auto-opened by `.github/workflows/monthly-cover.yml` so you get notified without Resend/ntfy secrets._",
        ]
    )
    body = "\n".join(lines)

    try:
        ensure_label(repo, token)
        issue = create_issue(repo, token, title, body)
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        print(f"GitHub API error: {e.code} {err}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Issue notify error: {e}", file=sys.stderr)
        return 1

    html_url = issue.get("html_url") if isinstance(issue, dict) else None
    number = issue.get("number") if isinstance(issue, dict) else None
    print(f"Opened issue #{number}: {html_url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
