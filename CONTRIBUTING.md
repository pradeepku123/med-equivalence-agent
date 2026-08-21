# 🤝 Contributing to Med Equivalence Agent

Thank you for your interest in contributing to **Med Equivalence Agent**! 💊  
Our mission is to help India's 1.4 billion citizens discover, verify, and switch to affordable **Jan Aushadhi generic medicines (PMBJP)** — saving 50%–90% on essential healthcare costs.

We welcome all types of contributions: bug fixes, new agent workflows, drug data enrichments, documentation improvements, OCR enhancements, and automated tests.

---

## 📜 Table of Contents

1. [Code of Conduct](#-code-of-conduct)
2. [How Can I Contribute?](#-how-can-i-contribute)
   - [Reporting Drug Code or Data Discrepancies](#1-reporting-drug-code-or-data-discrepancies)
   - [Adding or Updating Workflows](#2-adding-or-updating-workflows)
   - [Improving Python Execution Engine & OCR](#3-improving-python-execution-engine--ocr)
3. [Development Environment Setup](#-development-environment-setup)
4. [Pre-Submission Verification Checklist](#-pre-submission-verification-checklist)
5. [Pull Request Workflow & Conventions](#-pull-request-workflow--conventions)
6. [Medical & Data Safety Guardrails](#-medical--data-safety-guardrails)

---

## 📜 Code of Conduct

This project is governed by the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold a welcoming, empathetic, and inclusive environment for all community members.

---

## 💡 How Can I Contribute?

### 1. Reporting Drug Code or Data Discrepancies

If you spot an outdated MRP, missing medicine, or incorrect Jan Aushadhi drug code:
1. Open a **[Drug Data Update Issue](.github/ISSUE_TEMPLATE/drug_data_update.md)**.
2. Provide the official PMBJP product link or PMBI notification reference.
3. Or submit a PR updating `data/seeds/janaushadhi_medicines.csv` and re-run `.venv/bin/python scripts/maintenance/seed_database.py --force`.

### 2. Adding or Updating Workflows

All agent workflows live in `.agent/workflows/` and must adhere strictly to [`.agent/WORKFLOW_STANDARD.md`](.agent/WORKFLOW_STANDARD.md):
- Workflows must use standard YAML front-matter (`name`, `version`, `description`, `command`, `category`, `schedule`, `error_handling`, `changelog`).
- File paths declared in `inputs:` MUST be referenced in the workflow body text.
- Must include the mandatory **Medical Disclaimer** block.
- Must pass `python .agent/scripts/workflow_linter.py`.

### 3. Improving Python Execution Engine & OCR

Our core Python utilities live in `scripts/shared/`:
- `validators.py`: Price comparison, safety classification, drug code pattern, canonical lookup engine.
- `ocr_processor.py`: Tesseract OCR processing, prescription text parsing, image directory support (`inputs/image/`).
- `janaushadhi_scraper.py`: PMBJP portal search scraper.
- `logger.py`: Execution audit trail and lookup provenance logger.

---

## 🛠️ Development Environment Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/med-equivalence-agent.git
cd med-equivalence-agent

# 2. Create and activate a Python 3.10+ virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install core dependencies
pip install httpx beautifulsoup4 lxml pytesseract Pillow pyyaml pytest

# 4. Seed local drug cache
python scripts/maintenance/seed_database.py --force

# 5. Run health validation
python scripts/maintenance/validate_data.py
```

---

## ✅ Pre-Submission Verification Checklist

Before opening a pull request, ensure **all three verification suites pass cleanly**:

```bash
# 1. Run Workflow Linter (All 11 rules)
python .agent/scripts/workflow_linter.py

# 2. Run Data Health & Integrity Validator
python scripts/maintenance/validate_data.py

# 3. Run Automated Unit & Integration Tests
python -m pytest tests/ -v
```

---

## 🔀 Pull Request Workflow & Conventions

### Branch Naming Convention

Use descriptive branch names with appropriate prefixes:
- `feat/add-new-workflow-name` (New features/workflows)
- `fix/drug-code-pantoprazole` (Bug fixes)
- `data/refresh-july-2026-mrp` (Drug catalog updates)
- `docs/update-readme-prompts` (Documentation changes)

### Commit Message Guidelines

Keep commit messages clear and structured:
```
feat(workflow): add new /symptom_to_medicine workflow
fix(validator): correct official PMBJP drug code for Pantoprazole 40mg
docs(readme): add example prompts for inputs/image/ directory
```

---

## ⚕️ Medical & Data Safety Guardrails

- **No Medical Advice:** This tool is for informational/educational generic discovery only.
- **Schedule H/H1/X & NTI Guardrails:** Do NOT bypass safety warnings or substitution guardrails defined in `.agent/rules/safety_guardrails.md`.
- **Verified Sources:** All MRPs and drug codes must map to official PMBJP (janaushadhi.gov.in / PMBI) data.

---

Thank you for contributing to affordable healthcare for all! 🇮🇳
