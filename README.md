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
│   ├── image/                             # Medicine & prescription image directory (gitignored)
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
"Extract generic details from image in inputs/image/1.jpeg"
"Scan image directory inputs/image/ and show generic options"
"What generic fever medicine is available under ₹10?"
"Scan my prescription in inputs/prescriptions/rx.jpg"
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

### 📋 Prescription & Image Scanning

| Command | What It Does | Example Prompt |
| :--- | :--- | :--- |
| `/scan_prescription` | Process medicine or prescription images from `inputs/image/` (e.g. `1.jpeg`) or `inputs/prescriptions/` → OCR extracts medicine names → auto-finds Jan Aushadhi generic details, drug codes, verified MRPs, savings %, and buy links. | *"Process image inputs/image/1.jpeg"* / *"Get generic details from inputs/image/"* / *"Scan my prescription"* |

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

## 🤝 Open Source Community & Contributing

We welcome contributions from developers, pharmacists, healthcare data specialists, and open-source enthusiasts worldwide! Please read our [Contribution Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting a PR.

### 🌐 Community Guidelines & Governance
- 🤝 **[Contribution Guidelines](CONTRIBUTING.md)** — Step-by-step developer setup, workflow standards, and PR requirements.
- 📜 **[Code of Conduct](CODE_OF_CONDUCT.md)** — Contributor Covenant v2.1 standards for an inclusive community.
- 🛡️ **[Security & Safety Policy](SECURITY.md)** — Vulnerability reporting and medical data safety guidelines.
- 💬 **[Support & Q&A](SUPPORT.md)** — Community channels, issue templates, and discussions.

**Quick Contribution Guide:**
1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make changes & run pre-submission checks:
   - `python .agent/scripts/workflow_linter.py`
   - `python scripts/maintenance/validate_data.py`
   - `python -m pytest tests/`
4. Open a Pull Request with our [PR Template](.github/PULL_REQUEST_TEMPLATE.md)

---

## ⚕️ Medical Disclaimer

> This tool is for **informational and educational purposes only**. It does not constitute medical advice, diagnosis, or treatment. Always consult a licensed pharmacist or qualified physician before changing, substituting, or discontinuing any medication. Generic equivalents contain the same active ingredient but may differ in formulation, excipients, or bioavailability.

---

## 📄 License

Apache License 2.0 — See [LICENSE](LICENSE)
