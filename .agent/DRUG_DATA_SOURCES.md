# Drug Data Sources
**Version:** 1.0.0 | **Created:** 2026-08-21

## Primary: Jan Aushadhi / PMBJP Official Sources
- **Jan Aushadhi Portal**: [janaushadhi.gov.in](https://janaushadhi.gov.in) — Official product & MRP list
- **PMBI Product List**: [janaushadhi.gov.in/Product_List.aspx](https://janaushadhi.gov.in/Product_List.aspx) — Search by drug code, name, MRP
- **Jan Aushadhi Sugam App**: Official government app for Kendra locator and product search

## National Drug Reference
- **NLEM (National List of Essential Medicines)**: [mohfw.gov.in](https://mohfw.gov.in) — Government essential medicines list
- **CDSCO (Central Drugs Standard Control Organisation)**: [cdsco.gov.in](https://cdsco.gov.in) — Drug approvals and Schedule classifications
- **NRCeS Common Drug Codes**: National Resource Centre for EHR Standards — standardized drug codes for interoperability

## Generic Medicine Databases
- **1mg Generic Search**: [1mg.com](https://www.1mg.com) — Generic alternatives, packaging images, prices
- **PharmEasy**: [pharmeasy.in](https://pharmeasy.in) — Generic medicine listings and buy links
- **Apollo Pharmacy**: [apollopharmacy.in](https://apollopharmacy.in) — Verified generic medicines
- **Netmeds**: [netmeds.com](https://netmeds.com) — Generic medicine search

## Drug Information & Safety
- **Medindia Drug Database**: [medindia.net/drug-price](https://www.medindia.net/drug-price/) — Drug composition, generic names
- **Drugs.com India**: [drugs.com](https://www.drugs.com) — Drug interactions and safety info
- **RxList**: [rxlist.com](https://www.rxlist.com) — Comprehensive drug monographs

## OCR & Prescription Parsing
- **Tesseract OCR**: Open-source OCR engine for prescription image text extraction
- **Google Vision API** (optional): For high-accuracy prescription parsing

## Usage Instruction
Always prioritize **official Jan Aushadhi sources** first for pricing. Use pharmacy aggregators (1mg, PharmEasy) for buy links and images only. Never hallucinate drug codes — use `data/system/drug_cache/janaushadhi_medicines.json` as the ground truth.
