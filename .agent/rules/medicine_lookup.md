# Medicine Lookup Protocol
**Version:** 1.1.0 | **Created:** 2026-08-21 | **Updated:** 2026-08-21

This rule governs how the agent handles medicine lookup queries — by name, drug code, image, or symptom — incorporating alternative branded options, multi-tier price comparisons, and reported issue histories.

---

## 1. Query Classification (MANDATORY FIRST STEP)

Before any lookup, classify the user's input into one of these types:

| Query Type | Pattern | Example |
|-----------|---------|---------|
| `brand_name` | Recognizable brand with no drug code | `"Crocin"`, `"Dolo 650"`, `"Justoza M"` |
| `generic_name` | INN/generic chemical name | `"Paracetamol 500mg"`, `"Dapagliflozin + Metformin"` |
| `drug_code` | Numeric or `JA-XXXX` pattern | `"JA-0453"`, `"2100"` |
| `symptom` | Symptom or condition description | `"fever medicine under ₹10"` |
| `ocr` | Uploaded image or PDF prescription | (binary input) |

---

## 2. Phased Lookup & Comprehensive Audit Protocol

### Phase 1: Quick Match & Local Cache Search
- Search `data/system/drug_cache/janaushadhi_medicines.json` for exact or fuzzy match
- Fields to match: `generic_name`, `brand_aliases`, `drug_code`
- **Threshold:** Fuzzy match ≥ 85% similarity counts as a match

### Phase 2: Live Scrape & Sourcing
- Run `scripts/shared/janaushadhi_scraper.py --query "<input>"` if cache misses
- Update local cache with newly fetched data

### Phase 3: Market Alternatives & Multi-Tier Pricing Audit
- Identify 2–3 top **Alternative Branded & Generic Market Options** sharing the exact active ingredient & strength (e.g. Xigduo XR, Oxra MET, Forxiga M).
- Construct the **Multi-Tier Price Comparison Matrix** comparing:
  - 🏛️ Jan Aushadhi Generic (Drug Code & MRP)
  - 💊 Trade Generic Brands (Cipla, Mankind, Zydus)
  - 🏷️ Premium / Popular Branded Options (Torrent, USV, AstraZeneca)

### Phase 4: Quality, CDSCO Alerts & Reported Issue History Audit
- Scan for CDSCO quality alerts, batch recalls, or Not of Standard Quality (NSQ) reports.
- Summarize reported user concerns, tolerability notes, side-effect profile, and dietary/dosing precautions.

---

## 3. Result Formatting Requirements

Every lookup result MUST include:

```
1. Active Composition & Queried Brand Summary
2. Jan Aushadhi Generic Equivalent (Drug Code, MRP, Pack Size)
3. Other Alternative Branded & Generic Market Options
4. Multi-Tier Price Comparison Matrix (Per 10 Units & Savings %)
5. History of Reported Issues, CDSCO Alerts & Tolerability Notes
6. Buy Deep Links & Kendra Locator
7. Schedule & NTI Safety Warnings
8. Medical Disclaimer
```

---

## 4. Symptom-Based Lookup Rules

When `query_type = "symptom"`:
1. Extract underlying condition
2. Filter Jan Aushadhi medicines by therapeutic category
3. Sort by MRP ascending
4. Return top options with drug codes, safety classification, and buy links

---

## 5. QA Auto-Save Protocol (MANDATORY)

Every successful medicine lookup MUST be auto-saved:
- **Directory:** `data/system/knowledge/lookup_archive/`
- **Filename:** `LOOKUP_YYYY-MM-DD_<query-slug>.md`
- **No exceptions. No prompting the user.**
- **Append to** `data/system/knowledge/lookup_archive/LOOKUP_INDEX.md`
