# Result Enrichment Rules
**Version:** 1.2.0 | **Created:** 2026-08-21 | **Updated:** 2026-08-21

This rule governs how the agent enriches medicine lookup results with active buying links across ALL options, multi-tier price comparisons, alternative branded options, reported issues/recalls, images, buy links, and PDF links.

---

## 1. Active Buying Deep Links for ALL Recommended Options (MANDATORY)

Every option presented in the **Alternative Options Table** and **Multi-Tier Price Comparison Matrix** MUST include direct, clickable **Active Buying Deep Links**.

**Rules:**
- **Jan Aushadhi Generic:** Include `[🏥 Find Jan Aushadhi Store](https://janaushadhi.gov.in/KendraLocator.aspx)` + `[🛒 Buy on 1mg](https://www.1mg.com/search/all?name=...)`
- **Branded Alternatives & Generics:** Include `[🛒 Buy on 1mg](https://www.1mg.com/search/all?name=...)` and `[🛒 Buy on PharmEasy](https://pharmeasy.in/search/all?name=...)` for THAT specific brand
- All URLs MUST be URL-encoded (spaces converted to `%20` or `+`)
- Never present a medicine row in a table without an active buying link column

---

## 2. Multi-Tier Price Comparison Matrix (MANDATORY)

For every medicine lookup, construct a structured **Price Comparison Matrix** with active buying links for EVERY row:

```
### 📊 Multi-Tier Price Comparison Matrix (Per 10 Tablets)

| Tier / Category | Brand / Source | Manufacturer | MRP (₹) | Savings vs Ref | Active Buying Link |
| :--- | :--- | :--- | :---: | :---: | :---: |
| 🏛️ **Jan Aushadhi Generic** | **PMBJP (Drug Code: {code})** | **PMBI** | **₹XX.XX** | **Baseline (Cheapest)** | [🏥 Store Locator](https://janaushadhi.gov.in/KendraLocator.aspx) \| [🛒 1mg](https://www.1mg.com/search/all?name=...) |
| 💊 **Trade Generic Brand** | {Generic_Brand_Name} | {Generic_Mfr} | ₹XX.XX | ~XX% cheaper | [🛒 Buy on 1mg](https://www.1mg.com/search/all?name=...) \| [🛒 PharmEasy](https://pharmeasy.in/search/all?name=...) |
| 🏷️ **Queried / Popular Brand** | {Queried_Brand} | {Mfr_Name} | ₹XX.XX | Reference Price | [🛒 Buy on 1mg](https://www.1mg.com/search/all?name=...) \| [🛒 PharmEasy](https://pharmeasy.in/search/all?name=...) |
| 🏷️ **Alternative Brand 2** | {Alt_Brand_2} | {Alt_Mfr_2} | ₹XX.XX | Premium | [🛒 Buy on 1mg](https://www.1mg.com/search/all?name=...) \| [🛒 PharmEasy](https://pharmeasy.in/search/all?name=...) |
```

---

## 3. Alternative Branded & Generic Options Sourcing

List 2–3 popular **Branded Market Alternatives** with active buying links for each option:

| Option Name | Category | Manufacturer | Approx MRP (10 Tabs) | Active Buying Links |
| :--- | :--- | :--- | :---: | :--- |
| **PMBJP (Drug Code {code})** | Jan Aushadhi Generic | PMBI-Approved | **₹XX.XX** | [🏥 Find Kendra](https://janaushadhi.gov.in/KendraLocator.aspx) \| [🛒 Buy 1mg](https://www.1mg.com/search/all?name=...) |
| **{Trade_Generic}** | Open-Market Generic | {Mfr} | ₹XX.XX | [🛒 Buy 1mg](https://www.1mg.com/search/all?name=...) \| [🛒 Buy PharmEasy](https://pharmeasy.in/search/all?name=...) |
| **{Brand_1}** | Alternative Brand 1 | {Mfr_1} | ₹XX.XX | [🛒 Buy 1mg](https://www.1mg.com/search/all?name=...) \| [🛒 Buy PharmEasy](https://pharmeasy.in/search/all?name=...) |
| **{Brand_2}** | Alternative Brand 2 | {Mfr_2} | ₹XX.XX | [🛒 Buy 1mg](https://www.1mg.com/search/all?name=...) \| [🛒 Buy PharmEasy](https://pharmeasy.in/search/all?name=...) |

---

## 4. Reported Issues, CDSCO Alerts & Safety History Audit

1. **CDSCO Alerts:** Check for Not of Standard Quality (NSQ) reports or batch recalls.
2. **User-Reported Concerns:** Tolerability notes, dietary precautions (e.g. hydration, with meals).
3. **Storage Instructions:** Temp (< 30°C) and moisture protection.

---

## 5. Buy Link URL Generation Patterns

| Platform | Link Pattern |
|----------|-------------|
| Jan Aushadhi Kendra Locator | `https://janaushadhi.gov.in/KendraLocator.aspx` |
| 1mg Search | `https://www.1mg.com/search/all?name=<medicine_name>` |
| PharmEasy Search | `https://pharmeasy.in/search/all?name=<medicine_name>` |
| Apollo Pharmacy Search | `https://apollopharmacy.in/search-medicines/<medicine_name>` |
| Netmeds Search | `https://www.netmeds.com/catalogsearch/result/index/?q=<medicine_name>` |

---

## 6. Enrichment Caching

- Cache enriched results (images, links, price comparisons, issue history) in `data/system/drug_cache/enriched/`
- Cache TTL: 24 hours for buy links & prices; 7 days for safety reports
