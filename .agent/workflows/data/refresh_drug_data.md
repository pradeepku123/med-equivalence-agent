---
name: Refresh Drug Data
version: 1.0.0
description: Refresh the local Jan Aushadhi medicine cache by scraping the official PMBI portal and validating the resulting dataset.
command: /refresh_drug_data
category: data
schedule: weekly
cron_expression: "0 2 * * 0"

inputs: []

outputs:
  - data/system/drug_cache/janaushadhi_medicines.json
  - data/system/logs/data_refresh_{date}.log

dependencies:
  - scripts/shared/janaushadhi_scraper.py
  - scripts/maintenance/validate_data.py

error_handling:
  on_web_search_failure: use_cached
  on_missing_input: warn_and_use_defaults
  on_script_failure: warn

changelog:
  - version: 1.0.0
    date: '2026-08-21'
    change: Initial version — weekly Jan Aushadhi data refresh workflow
---

# PURPOSE
Refresh the local Jan Aushadhi drug cache (`data/system/drug_cache/janaushadhi_medicines.json`) by scraping the official PMBI portal. This ensures price data and drug codes are up to date.

# DATA SOURCING
Source: `janaushadhi.gov.in/Product_List.aspx` (live scrape)
Fallback: Existing `janaushadhi_medicines.json` (no update if scrape fails)

## Step 1: Check Cache Freshness

Read `data/system/drug_cache/janaushadhi_medicines.json` → `last_updated` field.
If `last_updated` is within 24 hours → Skip refresh; inform user: "Cache is fresh (updated {hours}h ago). No refresh needed."

**Tool:** `view_file data/system/drug_cache/janaushadhi_medicines.json`

**Input:** `data/system/drug_cache/janaushadhi_medicines.json`

**Output / Deliverable:** `last_updated` timestamp and freshness decision.

**On Failure:** Proceed with full scrape.

## Step 2: Backup Current Cache

Copy the current `janaushadhi_medicines.json` to `data/system/drug_cache/backups/janaushadhi_medicines_{date}.json.bak` before overwriting.

**Tool:** `run_command cp data/system/drug_cache/janaushadhi_medicines.json data/system/drug_cache/backups/janaushadhi_medicines_$(date +%Y%m%d).json.bak`

**On Failure:** Warn; proceed without backup (log warning).

## Step 3: Run Jan Aushadhi Scraper

**Tool:** `run_command .venv/bin/python scripts/shared/janaushadhi_scraper.py --mode full --output data/system/drug_cache/janaushadhi_medicines.json`

**Output / Deliverable:** Updated `janaushadhi_medicines.json` with fresh medicine data.

**On Failure:** `use_cached` — retain existing cache. Log scrape failure to `data/system/logs/data_refresh_{date}.log`.

## Step 4: Validate Refreshed Data

**Tool:** `run_command .venv/bin/python scripts/maintenance/validate_data.py`

**Input:** `data/system/drug_cache/janaushadhi_medicines.json`

**Output / Deliverable:** Validation report — count of medicines, schema errors, missing fields.

**On Failure:** Restore from backup (Step 2). Alert user.

## Step 5: Update Metadata

Update `last_updated` timestamp in `janaushadhi_medicines.json`:
```json
{"metadata": {"last_updated": "YYYY-MM-DD", "medicine_count": N, "source": "janaushadhi.gov.in"}}
```

**Output / Deliverable:**
> ✅ Drug data refreshed → `data/system/drug_cache/janaushadhi_medicines.json`
> 📊 {N} medicines loaded | Last updated: {date}

---

> ⚕️ **Disclaimer:** Drug pricing data is sourced from the official Jan Aushadhi portal. Prices may change; always verify at the point of purchase at your nearest Jan Aushadhi Kendra.

---
ALWAYS end your response by asking: "Would you like to search for another medicine, upload a prescription, or find a nearby Jan Aushadhi Kendra?"
