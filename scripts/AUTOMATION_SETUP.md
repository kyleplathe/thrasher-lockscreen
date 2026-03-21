# Thrasher Cover Monthly Automation Setup

## Overview
This automation system allows you to automatically check for and download new Thrasher magazine covers on a monthly basis.

## Scripts

### 1. `monthly_cover_scraper.py`
**Purpose**: Checks Thrasher's website for new covers and downloads them.

**What it does**:
- Fetches the Thrasher magazine archive page
- Extracts cover information for recent years (2024-2025)
- Compares against existing covers in JSON
- Downloads new covers to `images/original/`
- Adds new covers to `shortcuts_text_overlay_covers.json`

**Usage**:
```bash
python3 scripts/monthly_cover_scraper.py
```

### 2. `process_single_cover.py`
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

- The scraper only looks for recent covers (2024-2025) to avoid processing old archives
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

