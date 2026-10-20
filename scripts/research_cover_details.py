#!/usr/bin/env python3
"""
Research Thrasher cover credits from Thrasher's own pages.

Sources:
  - Shop product blurbs (shop.thrashermagazine.com magazines collection)
  - Covers archive image filenames (thrashermagazine.com/covers/)
  - The current magazine-page cover alt text

Fills empty skater, trick, photographer, location, and spot fields.
Does not replace a credit that is already filled in, except to pull a
photographer surname back out of the skater or trick when the archive
filename marks that person as the photographer.

Writes an audit file to data/cover_research.json. Pass --apply to update
shortcuts_text_overlay_covers.json.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from html import unescape

SHOP_URL = (
    "https://shop.thrashermagazine.com/collections/magazines/products.json?limit=250"
)
ARCHIVE_URL = "https://www.thrashermagazine.com/covers/"
MAGAZINE_URL = "https://www.thrashermagazine.com/articles/magazine/"
JSON_PATH = "shortcuts_text_overlay_covers.json"
RESEARCH_PATH = "data/cover_research.json"

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}
PARTICLES = {"van", "der", "de", "da", "del", "la", "di"}
# Surnames Thrasher puts in archive filenames as the photographer, not the trick.
PHOTOGRAPHER_SURNAMES = {"burnett", "darwen", "heikkila", "aguilar", "acosta"}
PHOTOGRAPHER_PAIRS = {("marco", "hernandez")}
TRICK_WORDS = {
    "switch",
    "nollie",
    "fakie",
    "frontside",
    "backside",
    "kickflip",
    "heelflip",
    "ollie",
    "nosegrind",
    "darkslide",
    "disaster",
    "wallride",
    "back",
    "front",
    "fs",
    "bs",
    "sw",
}
# First word of a "Name Name" match that is not a skater.
SKIP_NAME_STARTS = {
    "thrasher",
    "magazine",
    "skater",
    "santa",
    "death",
    "golden",
    "north",
    "el",
    "hollywood",
    "puerto",
    "south",
    "czech",
    "basque",
    "mexico",
    "boca",
    "new",
    "los",
    "san",
    "king",
    "photo",
    "the",
    "our",
    "this",
    "inside",
    "cover",
    "issue",
    "shop",
    "red",
    "nike",
    "vans",
    "girl",
    "zero",
    "real",
    "anti",
    "pass",
}


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", "replace")


def clean_text(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def issue_from_title(title: str) -> tuple[int, int] | None:
    lowered = title.lower()
    month = next((MONTHS[name] for name in MONTHS if name in lowered), None)
    year_match = re.search(r"(20\d{2})", lowered)
    if not month or not year_match:
        return None
    return int(year_match.group(1)), month


def load_shop() -> dict[tuple[int, int], dict]:
    payload = json.loads(fetch(SHOP_URL))
    found: dict[tuple[int, int], dict] = {}
    for product in payload.get("products", []):
        title = (product.get("title") or "").strip()
        issue = issue_from_title(title)
        if not issue:
            continue
        # Prefer the plain "Thrasher Magazine <Month> <Year>" listing over reprints.
        if issue in found and "magazine" not in title.lower():
            continue
        found[issue] = {
            "title": title,
            "blurb": clean_text(product.get("body_html") or ""),
            "url": "https://shop.thrashermagazine.com/products/"
            + (product.get("handle") or ""),
        }
    return found


def load_archive() -> dict[tuple[int, int], str]:
    html = fetch(ARCHIVE_URL)
    found: dict[tuple[int, int], str] = {}
    for tag in re.findall(r"<img\b[^>]*>", html):
        src_match = re.search(r'src="([^"]+)"', tag)
        alt_match = re.search(r'alt="([^"]*)"', tag)
        if not src_match or not alt_match:
            continue
        alt = unescape(alt_match.group(1))
        dated = re.search(r"(20\d{2})-(\d{2})-\d{2} Cover", alt)
        if not dated:
            continue
        issue = (int(dated.group(1)), int(dated.group(2)))
        filename = unescape(src_match.group(1)).split("/")[-1]
        # The archive lists the primary cover first for months with extras.
        found.setdefault(issue, filename)
    return found


def load_current_alt() -> str:
    try:
        html = fetch(MAGAZINE_URL)
    except Exception:
        return ""
    match = re.search(r'alt="([^"]*Thrasher Magazine Cover[^"]*)"', html)
    return unescape(match.group(1)) if match else ""


RESOLUTIONS = {"610", "900", "950", "1080", "1200", "2000"}


def title_tokens(filename: str) -> list[str]:
    base = filename.split("/")[-1]
    base = re.sub(r"\.(jpg|jpeg|png)$", "", base, flags=re.I)
    base = re.sub(r"_\d+x$", "", base, flags=re.I)
    tokens = []
    for token in base.split("_"):
        if not token:
            continue
        lowered = token.lower()
        if lowered in RESOLUTIONS or lowered in {"sml", "1x"}:
            continue
        if lowered.startswith("cv1th"):
            continue
        # "Thrasher-Cover" is two noise words. Keep trick tokens like "50-50" intact.
        if "-" in token and not re.fullmatch(r"\d+-\d+", token):
            tokens.extend(part for part in token.split("-") if part)
            continue
        tokens.append(token)
    return tokens


def take_skater(tokens: list[str]) -> tuple[list[str], list[str]]:
    if not tokens:
        return [], tokens
    if tokens[0].lower() in TRICK_WORDS:
        return [], tokens
    name = [tokens.pop(0)]
    while tokens:
        nxt = tokens[0]
        if nxt.lower() in TRICK_WORDS or nxt.lower() in PHOTOGRAPHER_SURNAMES:
            break
        if re.fullmatch(r"\d.*", nxt) or nxt.lower() in {"ph", "photo", "soty", "fdr"}:
            break
        if name[-1].lower() in PARTICLES or nxt.lower() in PARTICLES:
            name.append(tokens.pop(0))
            continue
        if len(name) == 1:
            name.append(tokens.pop(0))
            continue
        break
    return name, tokens


def parse_filename(filename: str) -> dict[str, str]:
    """Pull skater, trick, photographer, and spot out of an archive filename."""
    raw = title_tokens(filename)
    # Drop leading date tokens (26_11, 2024_12, 09_25, 0825 is one token).
    tokens = list(raw)
    while tokens and re.fullmatch(r"\d{2,4}", tokens[0]):
        tokens.pop(0)
    for noise in ("thrasher", "magazine", "cover", "cv1th"):
        tokens = [token for token in tokens if token.lower() != noise]
    tokens = [token for token in tokens if not re.fullmatch(r"20\d{2}", token)]

    skater, rest = take_skater(tokens)
    photographer = ""
    spot = ""
    lowered = [token.lower() for token in rest]
    if "photo" in lowered:
        index = lowered.index("photo")
        photographer = " ".join(rest[index + 1 :])
        rest = rest[:index]
    elif "ph" in lowered:
        index = lowered.index("ph")
        photographer = " ".join(rest[index + 1 :])
        rest = rest[:index]
    elif len(rest) >= 2 and tuple(token.lower() for token in rest[-2:]) in PHOTOGRAPHER_PAIRS:
        photographer = " ".join(rest[-2:])
        rest = rest[:-2]
    elif rest and rest[-1].lower() in PHOTOGRAPHER_SURNAMES:
        photographer = rest[-1]
        rest = rest[:-1]
    else:
        for index, token in enumerate(rest):
            if token.lower() in PHOTOGRAPHER_SURNAMES and index + 1 < len(rest):
                photographer = token
                rest = rest[index + 1 :]
                break

    if any(token.lower() == "fdr" for token in rest):
        spot = "FDR"
        rest = [token for token in rest if token.lower() != "fdr"]
    rest = [token for token in rest if token.lower() != "soty"]

    if rest == ["50", "50"]:
        rest = ["50-50"]
    elif rest and all(re.fullmatch(r"\d+", token) for token in rest):
        rest = []
    photographer = " ".join(
        token for token in photographer.split() if token.lower() not in RESOLUTIONS and not token.isdigit()
    )
    trick = " ".join(rest)
    trick = trick.replace("50 50", "50-50").replace("5 0", "5-0")
    skater_name = " ".join(skater).lower()
    if skater_name.startswith("cv1") or re.fullmatch(r"[\d ]+", skater_name or "0"):
        skater_name = ""
    result = {
        "skater": skater_name,
        "trick": trick.lower().strip(),
        "photographer": photographer.lower().strip(),
        "spot": spot,
    }
    if result["skater"] == "andrew reynollds":
        result["skater"] = "andrew reynolds"
    return {key: value for key, value in result.items() if value}


def proper_names(text: str) -> list[str]:
    pattern = (
        r"\b([A-Z][a-z]+(?:\s+(?:Van|Der|De|Da|Del|La|Di|[A-Z][a-z]+)){1,3})\b"
    )
    names = []
    for match in re.finditer(pattern, text):
        name = match.group(1).strip()
        if name.split()[0].lower() in SKIP_NAME_STARTS:
            continue
        if name.lower() in {"van der", "el toro"}:
            continue
        names.append(name)
    return names


def cover_lede(blurb: str) -> str:
    """The cover credit is the opening, before the 'inside this issue' tour."""
    opening = re.split(
        r"\b(?:In this issue|In this mag|Inside this|Open up that|Break open|Dig into|Further in|"
        r"Also in this|Crack open|Pop that issue|This issue is|More for your)\b",
        blurb.strip(),
        maxsplit=1,
        flags=re.I,
    )[0]
    sentences = re.split(r"(?<=[.!?])\s+", opening)
    kept = [
        sentence
        for sentence in sentences[:3]
        if not re.search(r"\b(?:fun fact|invented in)\b", sentence, flags=re.I)
    ]
    return " ".join(kept).strip()


def parse_blurb(blurb: str) -> dict[str, str]:
    lede = cover_lede(blurb)
    if not lede:
        return {}
    found: dict[str, str] = {}
    names = proper_names(lede)
    if names:
        found["skater"] = names[0].lower()
    else:
        # A one-word cover skater, as in "Kader finally gives us an excuse..."
        starters = {
            "doing", "before", "count", "look", "starting", "upside", "nothin",
            "the", "handrail", "congrats", "off", "not", "there", "our", "no",
            "after", "once", "from", "this", "that",
        }
        lead = re.match(r"^([A-Z][a-z]{2,})\b", lede)
        if lead and lead.group(1).lower() not in starters:
            found["skater"] = lead.group(1).lower()

    photo = re.search(
        r"(?:shot|snapshot|photo|photographed)\s+by\s+(?:our\s+guy\s+)?"
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        lede,
        flags=re.I,
    )
    if photo:
        found["photographer"] = photo.group(1).lower()

    places = []
    for match in re.finditer(
        r"\b(?:in|at|onto)\s+([A-Z][A-Za-z.'’-]+(?:\s+[A-Z][A-Za-z.'’-]+){0,3}"
        r"(?:,\s*[A-Z][A-Za-z.'’-]+)?)",
        lede,
    ):
        place = match.group(1).strip(" .,")
        if "." in place or place.split()[0].lower() in {
            "this",
            "the",
            "our",
            "his",
            "her",
            "that",
            "an",
            "a",
        }:
            continue
        if place in {"SF", "LA", "NYC"}:
            place = {"SF": "San Francisco, CA", "LA": "Los Angeles, CA", "NYC": "New York, NY"}[place]
        places.append(place)
    if re.search(r"\bOahu\b", lede):
        places.insert(0, "Oahu, Hawaii")
    if re.search(r"\bGolden Gate Bridge\b", lede):
        places.insert(0, "San Francisco, CA")
    if re.search(r"\bHollywood High\b", lede):
        found["spot"] = "Hollywood High"
        places.insert(0, "Los Angeles, CA")
    if re.search(r"\bEl Toro\b", lede):
        found["spot"] = "El Toro"
    if re.search(r"\bBay Blocks\b", lede):
        found["spot"] = "Bay Blocks"
        places.insert(0, "San Francisco, CA")
    if re.search(r"\bBrooklyn Banks\b|\bthe Banks\b", lede):
        found["spot"] = "Brooklyn Banks"
        places.insert(0, "Brooklyn, NY")
    if re.search(r"\bChinatown\b", lede):
        found["spot"] = "Chinatown"
    if re.search(r"\bRincon\b", lede):
        found["spot"] = "Rincon"
    if re.search(r"\bFDR\b", lede):
        found["spot"] = "FDR"
    if re.search(r"\bLA table\b", lede):
        places.insert(0, "Los Angeles, CA")
    if re.search(r"\bin OZ\b", lede):
        places.insert(0, "Australia")
    if re.search(r"\bBasque Country\b", lede):
        places.insert(0, "Basque Country")
    if re.search(r"\bMexico City\b", lede):
        places.insert(0, "Mexico City, Mexico")
    if places:
        location = places[0]
        if location != found.get("spot"):
            found["location"] = location

    trick_match = re.search(
        r"\b((?:switch |nollie |fakie )?(?:frontside |backside |fs |bs )?"
        r"(?:kickflip|heelflip|ollie|nosegrind|darkslide|disaster|wallride|"
        r"fakie flip|front lip|5-0|50-50|tre flip|frontside flip|backside flip|eggplant|"
        r"half-cab[^.]{0,40}|one-footer|noseblunt[^.]{0,24}))",
        lede,
        flags=re.I,
    )
    if trick_match:
        trick = re.sub(r"\s+", " ", trick_match.group(1)).strip(" .,").lower()
        trick = re.split(r"\b(?:for|over|onto|down|at|in|from|on)\b|,", trick)[0].strip()
        if trick and trick not in {"the", "a"}:
            found["trick"] = trick
    if re.search(r"\bKF FS BLUNT\b", lede):
        found["trick"] = "kickflip fs blunt"
    return found


def parse_current_alt(alt: str, issue: tuple[int, int]) -> dict[str, str]:
    """Alt text like 'Tristan Funkhouser ... Cover November, 2026, 5-0 Fakie Brooklyn Banks'."""
    if not alt:
        return {}
    month_name = next(name for name, number in MONTHS.items() if number == issue[1])
    if month_name not in alt.lower() or str(issue[0]) not in alt:
        return {}
    tail = re.split(r"20\d{2},?\s*", alt, maxsplit=1)
    found: dict[str, str] = {}
    if len(tail) == 2:
        detail = tail[1].strip(" .")
        if "Brooklyn Banks" in detail:
            found["spot"] = "Brooklyn Banks"
            found["location"] = "Brooklyn, NY"
            detail = detail.replace("Brooklyn Banks", "").strip(" ,")
        if detail:
            found["trick"] = detail.lower()
    names = proper_names(alt.split("Thrasher")[0])
    if names:
        found["skater"] = names[0].lower()
    return found


def prefer_longer(current: str, new: str) -> str:
    if not current:
        return new
    if not new:
        return current
    if current in new or new in current:
        return new if len(new) > len(current) else current
    return current


def research_issue(
    issue: tuple[int, int], shop: dict, archive: dict, current_alt: str
) -> dict:
    year, month = issue
    filename_meta = parse_filename(archive.get(issue, ""))
    blurb_meta = parse_blurb((shop.get(issue) or {}).get("blurb", ""))
    alt_meta = parse_current_alt(current_alt, issue)
    merged: dict[str, str] = {}
    # Filename wins for skater and photographer. Blurb fills location and gaps.
    for source in (alt_meta, blurb_meta, filename_meta):
        for key, value in source.items():
            if not value:
                continue
            if key == "photographer":
                merged[key] = prefer_longer(merged.get(key, ""), value)
            elif key not in merged:
                merged[key] = value
    # A real name in the archive filename beats whoever is mentioned first in the blurb.
    if filename_meta.get("skater"):
        merged["skater"] = filename_meta["skater"]
    if filename_meta.get("trick"):
        merged["trick"] = filename_meta["trick"]
    if filename_meta.get("photographer"):
        merged["photographer"] = prefer_longer(
            filename_meta["photographer"], merged.get("photographer", "")
        )
    record = {
        "filename": f"{year}_{month:02d}.jpg",
        "year": year,
        "month": month,
        "archive_filename": archive.get(issue, ""),
        "shop_title": (shop.get(issue) or {}).get("title", ""),
        "shop_url": (shop.get(issue) or {}).get("url", ""),
        "blurb": (shop.get(issue) or {}).get("blurb", ""),
        "lede": cover_lede((shop.get(issue) or {}).get("blurb", "")),
        "credits": merged,
    }
    return record


def blank(value: object) -> bool:
    return not (value or "").strip() if isinstance(value, str) else value in (None, "")


def contains_name(text: str, name: str) -> bool:
    if not text or not name:
        return False
    return re.search(rf"\b{re.escape(name.lower())}\b", text.lower()) is not None


def strip_name(text: str, name: str) -> str:
    cleaned = re.sub(rf"\b{re.escape(name)}\b", "", text, flags=re.I)
    return re.sub(r"\s+", " ", cleaned).strip(" -")


def apply_credits(data: dict, records: list[dict]) -> list[str]:
    by_file = {record["filename"]: record for record in records}
    changes: list[str] = []
    for image in data.get("images", []):
        record = by_file.get(image.get("filename"))
        if not record or not record["credits"]:
            continue
        meta = image.setdefault("metadata", {})
        credits = record["credits"]
        photographer = credits.get("photographer", "")
        if (meta.get("skater") or "").lower() == "andrew reynollds":
            meta["skater"] = "andrew reynolds"
            changes.append(f"{record['filename']} cleaned skater spelling")
        # Pull a photographer surname out of a skater or trick that absorbed it.
        for field in ("skater", "trick"):
            current = meta.get(field) or ""
            if photographer and contains_name(current, photographer):
                meta[field] = strip_name(current, photographer)
                changes.append(f"{record['filename']} cleaned {field}")
        for field, value in credits.items():
            if field not in {"skater", "trick", "photographer", "location", "spot"}:
                continue
            if blank(meta.get(field)) and value:
                meta[field] = value
                changes.append(f"{record['filename']} {field}={value}")
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write credits into shortcuts_text_overlay_covers.json",
    )
    parser.add_argument("--since", type=int, default=2024, help="First year to research")
    args = parser.parse_args()

    try:
        shop = load_shop()
        archive = load_archive()
        current_alt = load_current_alt()
    except Exception as exc:
        print(f"Cover research skipped: {exc}")
        return 0
    issues = sorted(set(shop) | set(archive))
    issues = [issue for issue in issues if issue[0] >= args.since]
    records = [research_issue(issue, shop, archive, current_alt) for issue in issues]
    records = [record for record in records if record["credits"] or record["blurb"]]

    os.makedirs(os.path.dirname(RESEARCH_PATH), exist_ok=True)
    with open(RESEARCH_PATH, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "source": "Thrasher shop blurbs and covers archive filenames",
                "issues": records,
            },
            handle,
            indent=2,
            ensure_ascii=False,
        )
        handle.write("\n")
    print(f"Wrote {len(records)} researched issues -> {RESEARCH_PATH}")
    for record in records:
        credits = record["credits"]
        print(
            f"{record['filename']}: "
            f"skater={credits.get('skater', '')!r} "
            f"trick={credits.get('trick', '')!r} "
            f"photo={credits.get('photographer', '')!r} "
            f"loc={credits.get('location', '')!r} "
            f"spot={credits.get('spot', '')!r}"
        )

    if not args.apply:
        print("Dry run. Re-run with --apply to fill empty cover credits.")
        return 0

    with open(JSON_PATH, encoding="utf-8") as handle:
        data = json.load(handle)
    changes = apply_credits(data, records)
    if not changes:
        print("No empty credits to fill.")
        return 0
    with open(JSON_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(f"Updated {len(changes)} fields:")
    for line in changes:
        print(f"  {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
