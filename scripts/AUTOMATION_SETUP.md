# Thrasher Cover Monthly Automation Setup

## Overview
This automation system allows you to automatically check for and download new Thrasher magazine covers on a monthly basis.

## Scripts

### 1. `monthly_cover_scraper.py`
**Purpose**: Checks Thrasher's website for new covers and downloads them.

**What it does**:
- Fetches the Thrasher magazine archive page **and** the Thrasher shop magazines JSON feed
- Extracts cover information for recent/upcoming years (see scraper filters)
- Compares against existing covers in JSON (and local image files)
- Downloads new covers to `images/original/`
- Adds new covers to `shortcuts_text_overlay_covers.json`
- Writes `data/cover_shop_publish_timestamps.json` with Shopify **`published_at`** / `created_at` / `updated_at` per issue (shop listings are the best signal for *when* an issue went live)

**When are new covers “posted”?**
- The **magazine archive HTML** does not expose a reliable timestamp on cover images.
- The **shop** (`products.json`) includes **`published_at`** — that’s usually when the product listing went live; use it to tune how often you run the scraper or your GitHub Actions cron.

**Usage**:
```bash
python3 scripts/monthly_cover_scraper.py
```

### 2. `prune_orphan_optimized_covers.py` (housekeeping)
**Purpose**: Deletes JPGs in `images/optimized_final_with_text/` that are **not** listed in `shortcuts_text_overlay_covers.json`, so the folder matches the Shortcut feed and sorts cleanly (`YYYY_MM.jpg`).

```bash
python3 scripts/prune_orphan_optimized_covers.py --dry-run   # preview
python3 scripts/prune_orphan_optimized_covers.py              # remove orphans
```

### 3. `process_single_cover.py`
**Purpose**: Processes a single cover image with the final text overlay layout.

**What it does**:
- Loads a cover from `images/original/`
- Optimizes it to iPhone Pro Max dimensions (1179x2556)
- Adds text overlay using final layout
- Saves to `images/optimized_final_with_text/`

**Usage**:
```bash
python3 scripts/process_single_cover.py 2025_12.jpg
```

## Schedule & best practice

**Why not only the 1st of the month?**  
New issues often show up in the Thrasher shop or on the site **mid-month**. Running only on the 1st can miss them for weeks.

**What works well here**
- **Multiple runs per month** (e.g. days **1, 8, 15, 22** at the same UTC time). Each run is **idempotent**: if nothing is new, it exits quickly; no duplicate downloads.
- **`workflow_dispatch`** — run the workflow manually anytime from GitHub → Actions.
- **Track timing over time**
  - `data/cover_shop_publish_timestamps.json` — Shopify `published_at` per issue (when the listing went live).
  - `data/cover_first_seen.json` — **first time this automation** saved a given `YYYY_MM.jpg` (UTC). Compare to `published_at` to see how early/late your schedule catches issues; adjust crons after a few months of data.

**Alternatives:** weekly cron (e.g. Mondays), or keep monthly but accept slower updates.

## Push notifications when a **new** cover ships

The workflow only notifies when it **committed and pushed** real changes (not on empty runs).

### Option A — **Email** (fun subject line + short blurb)

Uses [Resend](https://resend.com) (free tier is enough for occasional cover drops).

1. Create a Resend account and create an **API key**.
2. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**
   - **`RESEND_API_KEY`** — your Resend API key  
   - **`NOTIFY_EMAIL`** — where to send (e.g. your iCloud address) — **never commit this in the repo**  
   - *(Optional)* **`EMAIL_FROM`** — a **verified sender** in Resend, e.g. `Thrasher Covers <covers@yourdomain.com>`.  
     If you skip this, the workflow uses Resend’s test sender `onboarding@resend.dev`, which only works for **testing** per Resend’s rules (often same email as your Resend account). For production, verify a domain in Resend and set `EMAIL_FROM`.

The script `scripts/send_new_cover_email.py` builds a promotional HTML email (Thrasher Cover Shortcut Automation + **Get the shortcut** button), emoji subjects, and—when present—**skater / trick / location** from `shortcuts_text_overlay_covers.json`. The default iCloud link is embedded in the script; you can override it with a **`SHORTCUTS_URL`** secret if you publish a new shortcut later.

### Option B — **ntfy** (works great on iPhone / Android)

1. Install **ntfy** from the [App Store](https://apps.apple.com/app/ntfy/id1625396346) or [Google Play](https://play.google.com/store/apps/details?id=io.heckel.ntfy).
2. Open the app → **Subscribe to topic** → choose a **long random topic name** (treat it like a password; anyone who knows it can send you messages on the public server).
3. In GitHub: **Repo → Settings → Secrets and variables → Actions → New repository secret**
   - **`NTFY_TOPIC`** = that topic name  
   - *(Optional)* **`NTFY_TOKEN`** = if you use a **private** topic / access token on [ntfy.sh](https://ntfy.sh) or your own server ([docs](https://docs.ntfy.sh/config/#access-tokens)).

The workflow step **Notify phone (ntfy.sh)** runs only after a successful “new cover” commit. You’ll get a title + the commit line + changed file names.

### Option C — GitHub only (no extra app)

GitHub can email you about **workflow runs**, but it’s usually **all** runs (including no-op), so it’s noisier than ntfy.  
**Profile → Settings → Notifications** → adjust **Actions** / watched repos as you like.

## Monthly Workflow

To check for new covers and process them:

1. **Check for new covers**:
   ```bash
   cd thrasher-lockscreen/thrasher-lockscreen
   python3 scripts/monthly_cover_scraper.py
   ```

2. **If new covers are found, process them**:
   ```bash
   # Process each new cover
   python3 scripts/process_single_cover.py 2025_12.jpg
   ```

3. **Verify the results**:
   ```bash
   # Check that files were created
   ls -lh images/optimized_final_with_text/
   ```

4. **Commit and push to GitHub**:
   ```bash
   git add images/optimized_final_with_text/ shortcuts_text_overlay_covers.json
   git commit -m "Add [month] [year] Thrasher cover"
   git push origin main
   ```

## Automated Setup (macOS)

You can set up a cron job or LaunchAgent to run this monthly:

### Option 1: Cron Job
Add to your crontab:
```bash
crontab -e
```

Add this line (runs on the 1st of every month at 9:00 AM):
```
0 9 1 * * cd /path/to/thrasher-lockscreen/thrasher-lockscreen && /usr/bin/python3 scripts/monthly_cover_scraper.py >> logs/monthly_scraper.log 2>&1
```

### Option 2: LaunchAgent (macOS)
Create a LaunchAgent plist file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thrasher.monthly-scraper</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/thrasher-lockscreen/thrasher-lockscreen/scripts/monthly_cover_scraper.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Day</key>
        <integer>1</integer>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/path/to/thrasher-lockscreen/thrasher-lockscreen/logs/monthly_scraper.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/thrasher-lockscreen/thrasher-lockscreen/logs/monthly_scraper_error.log</string>
</dict>
</plist>
```

Save to: `~/Library/LaunchAgents/com.thrasher.monthly-scraper.plist`

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.thrasher.monthly-scraper.plist
```

## Notes

- The scraper only considers recent issue years (about 2024–2029) and `CV1TH…` filenames so the magazine index page does not pull in the full historical archive
- Images are saved in both original and optimized formats
- The JSON file is automatically updated with new covers
- Processing preserves the final text overlay layout with centered, bold dates
- All images are optimized to iPhone Pro Max dimensions (1179x2556)

## GitHub Actions (repo automation)

The workflow [`.github/workflows/monthly-cover.yml`](../.github/workflows/monthly-cover.yml) runs in GitHub so you do not need cron on your Mac for the monthly check.

**What it does**

1. Checks out the repo on a Linux runner.
2. Installs Python deps from `requirements.txt`.
3. Runs `scripts/monthly_cover_scraper.py`.
4. For each `images/original/*.jpg` that has no matching file in `images/optimized_final_with_text/`, runs `scripts/process_single_cover.py`.
5. If anything changed, commits and pushes to the default branch (using the built-in `GITHUB_TOKEN`).

**Enable and test**

1. Push the workflow file to GitHub (on your default branch, usually `main`).
2. In the repo on GitHub: **Actions** → **Monthly Thrasher cover** → **Run workflow** to test without waiting for the schedule.
3. Confirm the run completes and, if there were changes, that a new commit appears on `main`.

**Schedule**

The cron in the workflow is `0 14 1 * *` (14:00 UTC on the 1st of each month). Edit the `cron` line in the workflow YAML to change timing ([syntax](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule)).

**Permissions**

`contents: write` lets the workflow push. If **branch protection** blocks the Actions bot from pushing to `main`, either allow GitHub Actions to bypass protection for that branch (repo **Settings** → **Branches** / **Rules**) or push automation to a separate branch and use a pull request workflow instead.

**Secrets**

No personal access token is required for pushing to the same repository; the default `GITHUB_TOKEN` is enough.

## Future Enhancements

- Notifications when new covers are found (Slack, email, GitHub Issues)
- Add metadata extraction from alt text for skater/trick info

