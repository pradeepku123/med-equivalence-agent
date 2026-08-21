# 💊 Med Equivalence Agent

> An AI-powered agentic system to find **Jan Aushadhi generic medicine equivalents** for branded drugs — with drug codes, verified MRPs, purchase links, images, and prescription OCR. Built for India's 1.4 billion citizens to save 50–90% on medicine costs.

[![CI](https://github.com/your-org/med-equivalence-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/med-equivalence-agent/actions)
[![Framework](https://img.shields.io/badge/Framework-Production--Grade%20v1.0-blue)](#)
[![Data](https://img.shields.io/badge/Jan%20Aushadhi-2000%2B%20Medicines-green)](#)
[![Workflows](https://img.shields.io/badge/Workflows-8%20Versioned-orange)](#)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)

---

## 📁 Project Structure

```
med-equivalence-agent/
│
├── .agent/                                 # 🧠 AI Agent Brain
│   ├── skills/                            # Core AI persona definitions
│   │   └── med_equivalence_agent.md       # Agent role, mission, rules reference
│   ├── WORKFLOW_STANDARD.md               # Canonical workflow authoring standard (11 rules)
│   ├── DRUG_DATA_SOURCES.md               # Official & community data source reference
│   ├── scripts/                           # Agent tooling scripts
│   │   └── workflow_linter.py             # YAML front-matter validator (11 rules)
│   ├── rules/                             # Agent operational rules & guardrails
│   │   ├── data_sourcing.md               # Data priority: cache → scrape → LLM fallback
│   │   ├── medicine_lookup.md             # Phased lookup protocol (3 phases)
│   │   ├── enrichment_rules.md            # Buy links, images, savings calc rules
│   │   ├── safety_guardrails.md           # NTI drugs, Schedule H/H1/X, disclaimers
│   │   ├── workflow_execution.md          # Pre-flight validation, logging, error recovery
│   │   └── memory_retrieval.md            # Cache-first retrieval protocol
│   └── workflows/                         # Agent Workflows (8 total, all versioned v1.0+)
│       ├── lookup/                        # Medicine search workflows
│       │   ├── find_generic.md            # /find_generic — core generic finder
│       │   └── symptom_to_medicine.md     # /symptom_to_medicine — symptom-based lookup
│       ├── ocr/                           # Prescription parsing workflows
│       │   └── scan_prescription.md       # /scan_prescription — OCR + generic lookup
│       ├── data/                          # Data ingestion workflows
│       │   └── refresh_drug_data.md       # /refresh_drug_data — weekly data refresh
│       └── maintenance/                   # Cleanup and validation workflows
│           └── (add maintenance workflows here)
│
├── .github/
│   └── workflows/
│       ├── ci.yml                         # GitHub Actions CI (lint + test + validate)
│       └── data_refresh.yml               # Weekly drug data refresh (cron: Sunday 2AM)
│
├── data/                                   # 🗄️ Drug Data Vault
│   ├── seeds/                             # Bundled seed dataset
│   │   └── janaushadhi_medicines.csv      # 50+ Jan Aushadhi medicines (seed)
│   ├── results/                           # Auto-generated lookup results
│   ├── system/
│   │   ├── drug_cache/                    # Local drug cache (JSON)
│   │   │   ├── janaushadhi_medicines.json # Primary cache (populated by seeder/scraper)
│   │   │   ├── enriched/                  # Per-drug enriched data (images, links)
│   │   │   └── backups/                   # Pre-refresh backups
│   │   ├── logs/                          # Execution & lookup audit trails
│   │   │   ├── execution_log.jsonl        # Workflow step-level audit trail
│   │   │   └── lookup_log.jsonl           # Medicine lookup provenance log
│   │   ├── schemas/                       # JSON schema files for validation
│   │   └── knowledge/
│   │       └── lookup_archive/            # Auto-saved lookup results (QA archive)
│   │           └── LOOKUP_INDEX.md        # Index of all past lookups
│
├── inputs/                                 # Raw uploaded files
│   └── prescriptions/                     # User prescription images/PDFs (gitignored)
│
├── scripts/                                # 🐍 Python Execution Engine
│   ├── shared/                            # Shared utility package
│   │   ├── __init__.py
│   │   ├── logger.py                      # Structured JSONL execution & lookup logger
│   │   ├── validators.py                  # Drug validation, safety classification, savings calc
│   │   ├── janaushadhi_scraper.py         # Jan Aushadhi portal scraper
│   │   └── ocr_processor.py              # Prescription OCR (Tesseract, Hindi+English)
│   └── maintenance/                       # Maintenance scripts
│       ├── __init__.py
│       ├── seed_database.py               # Seed local cache from bundled CSV
│       └── validate_data.py               # 6-check data integrity validator
│
├── tests/                                  # 🧪 Automated Test Suite
│   ├── unit/                              # Unit tests
│   │   └── test_validators.py             # 30+ validator tests
│   └── integration/                       # Integration tests
│       └── test_workflow_linter.py        # Linter rule coverage tests
│
├── specs/                                  # Feature specifications
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Step 1: Clone & Setup

```bash
git clone https://github.com/your-org/med-equivalence-agent.git
cd med-equivalence-agent
python3 -m venv .venv
source .venv/bin/activate
pip install httpx beautifulsoup4 lxml pytesseract Pillow pyyaml pytest
```

### Step 2: Seed the Drug Database

```bash
.venv/bin/python scripts/maintenance/seed_database.py
```

This loads the bundled Jan Aushadhi seed dataset into `data/system/drug_cache/janaushadhi_medicines.json`.

### Step 3: Validate Setup

```bash
.venv/bin/python scripts/maintenance/validate_data.py
```

### Step 4: Run Tests

```bash
.venv/bin/python -m pytest tests/unit/ -v
```

### Step 5: Talk to the AI Agent

Open this project in your AI coding assistant (e.g., Gemini, Claude, Copilot Workspace) and simply describe what you need:

```
"Find the Jan Aushadhi equivalent of Crocin 650mg"
"What generic fever medicine is available under ₹10?"
"Scan my prescription" (upload an image)
"Lookup drug code JA-0001"
```

The agent automatically selects the right workflow, checks the cache, validates inputs, and logs the execution.

---

## ⚡ Workflows — Complete Reference

All workflows are invoked via **slash commands** or natural language. Each is versioned (v1.0.0+) with declared inputs, outputs, error handling, and a changelog.

### 💊 Medicine Lookup

| Command | What It Does | Example Prompt |
| :--- | :--- | :--- |
| `/find_generic` | Find Jan Aushadhi equivalent for any branded medicine. Returns drug code, MRP, savings %, buy links, image, and PDF. | *"Find generic for Crocin"* / *"Paracetamol generic"* |
| `/symptom_to_medicine` | Find the most affordable Jan Aushadhi medicines for a given symptom, sorted by MRP. | *"Fever medicine under ₹10"* / *"Acidity tablets"* |

### 📋 Prescription

| Command | What It Does | Example Prompt |
| :--- | :--- | :--- |
| `/scan_prescription` | Upload a prescription image or PDF → OCR extracts medicine names → auto-finds generic equivalents for each → shows total savings. | *"Scan my prescription"* (upload image) |

### 🔄 Data Management

| Command | What It Does | Example Prompt |
| :--- | :--- | :--- |
| `/refresh_drug_data` | Refresh the local Jan Aushadhi drug cache from the official PMBI portal. Run weekly or when data is stale. | *"Refresh drug data"* |

---

## 📊 Data Sources

| Source | URL | Used For |
|--------|-----|---------|
| **Jan Aushadhi (PMBI)** | [janaushadhi.gov.in](https://janaushadhi.gov.in) | Drug codes, official MRPs |
| **NLEM** | [mohfw.gov.in](https://mohfw.gov.in) | Essential medicines list |
| **1mg** | [1mg.com](https://1mg.com) | Buy links, market prices |
| **PharmEasy** | [pharmeasy.in](https://pharmeasy.in) | Buy links, images |
| **Apollo Pharmacy** | [apollopharmacy.in](https://apollopharmacy.in) | Buy links |

See [`.agent/DRUG_DATA_SOURCES.md`](.agent/DRUG_DATA_SOURCES.md) for the full reference.

---

## 🏗️ Architecture

```
User Query (text / drug code / image / symptom)
    │
    ▼
[Intent Parser] ─── Classifies: brand | generic | drug_code | symptom | ocr
    │
    ▼
[Memory Check] ─── Local cache first (data/system/drug_cache/)
    │
    ├── Cache HIT → Return instantly
    │
    └── Cache MISS ──►
                      │
                  [Jan Aushadhi Scraper]
                  janaushadhi.gov.in
                      │
                      ▼
                  [Enricher]
                  Images · Buy Links · Savings
                      │
                      ▼
                  [Safety Guardrails]
                  Schedule · NTI flag · Disclaimer
                      │
                      ▼
                  [Logger + Archive]
                  lookup_log.jsonl · LOOKUP_INDEX.md
                      │
                      ▼
                  Final Result Card
```

---

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

**Quick Contribution Guide:**
1. Fork the repo
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make changes & add tests
4. Run `python .agent/scripts/workflow_linter.py` — all workflows must pass
5. Run `python -m pytest tests/` — all tests must pass
6. Open a PR with a clear description

**Adding a New Workflow:**
- Follow [`.agent/WORKFLOW_STANDARD.md`](.agent/WORKFLOW_STANDARD.md) exactly
- All 11 linting rules must pass (including R11: medical disclaimer)
- Place in the correct category subfolder

---

## ⚕️ Medical Disclaimer

> This tool is for **informational and educational purposes only**. It does not constitute medical advice, diagnosis, or treatment. Always consult a licensed pharmacist or qualified physician before changing, substituting, or discontinuing any medication. Generic equivalents contain the same active ingredient but may differ in formulation, excipients, or bioavailability.

---

## 📄 License

Apache License 2.0 — See [LICENSE](LICENSE)
