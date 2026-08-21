# Data Sourcing Protocol
**Version:** 1.0.0 | **Created:** 2026-08-21

This rule governs how the Med Equivalence Agent sources drug data. All lookups MUST follow this priority order.

---

## 1. Data Sourcing Priority Order (MANDATORY)

For every medicine lookup, source data in this exact priority:

1. **Local Drug Cache** → `data/system/drug_cache/janaushadhi_medicines.json`
   - Fastest, zero network, always available offline
   - Check cache freshness: if `last_updated` > 7 days → flag as STALE
   - If found: return immediately; set `cache_hit: true` in lookup log

2. **Live Jan Aushadhi Scraper** → `scripts/shared/janaushadhi_scraper.py`
   - Scrapes `janaushadhi.gov.in/Product_List.aspx`
   - Only triggered when local cache misses or is STALE
   - Rate-limit: max 1 request/second; respect robots.txt
   - Cache result to `data/system/drug_cache/` after fetching

3. **Pharmacy Aggregators** (for images and buy links only)
   - 1mg: `https://www.1mg.com/search/all?name=<generic_name>`
   - PharmEasy: `https://pharmeasy.in/search/all?name=<generic_name>`
   - Apollo: `https://apollopharmacy.in/search-medicines/<generic_name>`

4. **LLM Fallback** (generic name mapping only)
   - ONLY if steps 1–3 fail to return a Jan Aushadhi match
   - LLM may suggest generic equivalents based on active ingredient
   - MANDATORY flag: `"source": "llm_fallback"` in every LLM-derived result
   - NEVER fabricate drug codes from LLM — drug_code must always come from official sources or be null

---

## 2. Cache Management Rules

- **Cache Location:** `data/system/drug_cache/janaushadhi_medicines.json`
- **Cache Schema:** See `data/system/schemas/drug_cache.schema.json`
- **Freshness Policy:** Cache is FRESH if `last_updated` within 7 days
- **Refresh Trigger:** Run `/refresh_drug_data` workflow or auto-refresh via GitHub Actions weekly cron
- **On Stale Cache:** Surface warning: `⚠️ Drug data last updated {N} days ago. Results may be outdated. Run /refresh_drug_data to update.`

---

## 3. Jan Aushadhi Drug Code Format

Official Jan Aushadhi drug codes follow the pattern: `PMBI-XXXXXX` or a numeric 4-6 digit code.

| Field | Source | Example |
|-------|--------|---------|
| `drug_code` | Jan Aushadhi portal only | `"JA-1234"` |
| `generic_name` | INN (International Non-proprietary Name) | `"Paracetamol"` |
| `brand_name` | Manufacturer brand | `"Crocin"` |
| `unit_size` | Pack size | `"10 Tablets"` |
| `mrp` | PMBJP MRP (₹) | `4.50` |
| `category` | PMBI therapeutic category | `"Analgesics"` |
| `manufacturer` | PMBI-approved manufacturer | `"ABC Pharma"` |

---

## 4. Data Integrity Rules

- **NEVER** present an MRP without verifying it against the official Jan Aushadhi portal
- **NEVER** claim a drug is available in Jan Aushadhi without a confirmed drug_code
- **ALWAYS** include a `last_verified` date on all price data
- **Flag** any drug not on the Jan Aushadhi list explicitly: `"Not available in Jan Aushadhi scheme"`
