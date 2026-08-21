# Memory Retrieval Protocol
**Version:** 1.0.0 | **Created:** 2026-08-21

This rule governs how the Med Equivalence Agent retrieves and uses information from its persistent memory systems before performing any lookup or research.

---

## 1. Pre-Lookup Memory Check (MANDATORY)

Before running ANY of the following workflows, you MUST check for cached/recent results:
- `/find_generic`
- `/lookup_drug_code`
- `/scan_prescription`
- `/symptom_to_medicine`

### Step 1a: Check Drug Cache

Read `data/system/drug_cache/janaushadhi_medicines.json` and look up the target medicine:

```json
{
  "medicines": {
    "Paracetamol": {
      "drug_code": "JA-0453",
      "jan_aushadhi_mrp": 4.50,
      "unit_size": "10 Tablets",
      "category": "Analgesics",
      "last_verified": "2026-08-15",
      "cache_file": "data/system/drug_cache/enriched/JA-0453_enriched.json"
    }
  }
}
```

**Staleness rule:** If `last_verified` within 7 days → Cache is **FRESH**. Use it directly.
If older than 7 days OR not found → Cache is **STALE**. Proceed with live scrape.

### Step 1b: Check Lookup Archive (for identical past queries)

Scan `data/system/knowledge/lookup_archive/` for files with matching query slug.
- If found within 30 days → Present cached result; ask if they want a fresh lookup
- Use similarity matching: "Crocin" and "Crocin 500" are the same query

---

## 2. Drug Cache Update (MANDATORY AFTER LIVE SCRAPE)

After a successful live scrape, update `data/system/drug_cache/janaushadhi_medicines.json`:

```json
"medicines": {
  "{generic_name}": {
    "drug_code": "<fetched_code>",
    "jan_aushadhi_mrp": <fetched_mrp>,
    "unit_size": "<fetched_size>",
    "category": "<fetched_category>",
    "manufacturer": "<fetched_manufacturer>",
    "last_verified": "YYYY-MM-DD",
    "cache_file": "data/system/drug_cache/enriched/{drug_code}_enriched.json"
  }
}
```

---

## 3. Staleness Scan Integration

The `scripts/maintenance/validate_data.py` automatically scans the cache for:
- Any medicine cached more than 7 days ago
- Any medicine with a missing `drug_code` (incomplete data)

Stale entries are surfaced as ⚠️ warnings. The user should run `/refresh_drug_data` to refresh.

---

## 4. Retrieval Priority Order

When a user queries a medicine, retrieve context in this priority order:

1. **Drug Cache** → Quick result with drug code, MRP, category (fastest)
2. **Enriched Cache** → Full result with images, buy links from `data/system/drug_cache/enriched/`
3. **Lookup Archive** → Past identical query result from `data/system/knowledge/lookup_archive/`
4. **Live Jan Aushadhi Scraper** → Fresh data from portal (medium speed)
5. **Pharmacy Aggregators** → Buy links and images only (for enrichment)
6. **LLM Fallback** → Generic name extraction only (slowest, last resort)
