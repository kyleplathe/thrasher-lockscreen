# Archived scripts

One-off **layout experiments** and the **reapply overlays** migration tool. Not part of the monthly cover workflow.

Run from the repo root (the directory that contains `images/` and `text_overlay_config.json`):

```bash
cd thrasher-lockscreen/thrasher-lockscreen
python3 scripts/archive/test_final_layout.py
```

Active automation is documented in `../AUTOMATION_SETUP.md` and uses `process_single_cover.py`, `monthly_cover_scraper.py`, etc. in the parent `scripts/` folder.
