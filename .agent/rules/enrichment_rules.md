# Result Enrichment Rules
**Version:** 1.1.0 | **Created:** 2026-08-21 | **Updated:** 2026-08-21

This rule governs how the agent enriches medicine lookup results with price comparisons, alternative branded options, reported issues/recalls, images, buy links, and PDF links.

---

## 1. Multi-Tier Price Comparison Matrix (MANDATORY)

For every medicine lookup, construct a structured **Price Comparison Matrix** comparing:
1. **Jan Aushadhi Generic (PMBJP)** — Government scheme price (Drug Code & verified MRP)
2. **Open-Market Generic Brands** — Top trade generics (e.g., Cipla Generic, Mankind, Zydus)
3. **Premium Branded Alternatives** — Top innovator/branded options (e.g., USV, Torrent, Abbott, Sun Pharma)

**Display Format:**
```
### 📊 Multi-Tier Price Comparison Matrix (Per 10 Tablets)

| Tier / Category | Brand / Source | Manufacturer | MRP (₹) | Savings vs Branded |
| :--- | :--- | :--- | :---: | :---: |
| 🏛️ **Jan Aushadhi Generic** | **PMBJP (Drug Code: {code})** | **PMBI** | **₹XX.XX** | **Baseline (Cheapest)** |
| 💊 **Trade Generic Brand** | {Generic_Brand_Name} | {Generic_Mfr} | ₹XX.XX | ~XX% cheaper |
| 🏷️ **Queried / Popular Brand** | {Queried_Brand} | {Mfr_Name} | ₹XX.XX | Reference Price |
| 🏷️ **Alternative Brand 2** | {Alt_Brand_2} | {Alt_Mfr_2} | ₹XX.XX | Premium |
```

---

## 2. Alternative Branded & Generic Options Sourcing

In addition to Jan Aushadhi, always list 2–3 popular **Branded Market Alternatives** sharing the exact same active ingredients & strength.

**Fields to include per alternative:**
- Brand Name
- Manufacturer / Pharma company
- Pack Size & Estimated Price (₹)
- Bioequivalence / Form classification (e.g., Immediate Release vs Sustained/Extended Release)

---

## 3. Reported Issues, CDSCO Alerts & Safety History Audit (MANDATORY)

For every medicine, fetch and display a **Quality & Safety History Report**:

1. **CDSCO / Drug Controller Alerts:**
   - Check if any recent Not of Standard Quality (NSQ) warnings or batch recalls exist.
   - If clear: Flag `✅ CDSCO Quality Check: No active NSQ or recall alerts reported.`
   - If alerts exist: Flag `⚠️ Quality Warning: Batch recall alert issued on {date} for {mfr}.`

2. **User-Reported Concerns & Tolerability:**
   - Summarize common patient-reported issues (e.g., GI distress for Metformin, UTI risk for SGLT2 inhibitors).
   - Guidance on how to mitigate (e.g., take with meals, maintain hydration).

3. **Storage & Expiry Warnings:**
   - Moisture sensitivity, temperature constraints (< 25°C or < 30°C).

---

## 4. Savings Calculation

```
Savings % = ((Market Price - Jan Aushadhi MRP) / Market Price) × 100
```

**Display format:**
```
💰 Savings: ₹{saved_amount} per pack ({savings_pct}% cheaper than branded)
```

---

## 5. Buy Link Generation Rules

Generate purchase deep links for these platforms:

| Platform | Link Pattern | Priority |
|----------|-------------|---------|
| Jan Aushadhi Sugam App | `https://janaushadhi.gov.in/` (app link) | 1st (official) |
| 1mg | `https://www.1mg.com/search/all?name=<generic_name>` | 2nd |
| PharmEasy | `https://pharmeasy.in/search/all?name=<generic_name>` | 3rd |
| Apollo Pharmacy | `https://apollopharmacy.in/search-medicines/<generic_name>` | 4th |
| Netmeds | `https://www.netmeds.com/catalogsearch/result/index/?q=<generic_name>` | 5th |

---

## 6. Medicine Image Sourcing

**Priority order for images:**
1. PMBI official product image (from `janaushadhi.gov.in` if available)
2. 1mg product image (generic packaging)
3. PharmEasy product image
4. No image: Display `"📦 Image not available"` — do NOT use placeholder or hallucinate an image

---

## 7. PMBI Official PDF Links

For Jan Aushadhi medicines, try to surface:
- Product specification PDF from `pmbi.co.in`
- PMBI product list PDF: `https://janaushadhi.gov.in/Product_List.aspx` (export)

---

## 8. Nearby Jan Aushadhi Kendra

Offer to find the nearest Kendra:
```
📍 Find nearest Jan Aushadhi Kendra: https://janaushadhi.gov.in/KendraLocator.aspx
Or search on the Jan Aushadhi Sugam app (available on Play Store & App Store).
```

---

## 9. Enrichment Caching

- Cache enriched results (images, links, price comparisons, issue history) in `data/system/drug_cache/enriched/`
- Cache TTL: 24 hours for buy links & prices; 7 days for safety/issue reports
- Format: `{drug_code}_enriched.json`
