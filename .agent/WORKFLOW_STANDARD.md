# Workflow Authoring Standard
**Version:** 1.0.0 | **Created:** 2026-08-21 | **Owner:** Med Equivalence Agent Framework

This document defines the **canonical standard** for all workflows in the `.agent/workflows/` directory. Every workflow file MUST conform to this standard. The `workflow_linter.py` script validates compliance.

---

## 1. Required YAML Front-Matter

Every workflow file must begin with a valid YAML front-matter block containing these **mandatory** fields:

```yaml
---
name: <Human-readable workflow name>
version: <MAJOR.MINOR.PATCH>   # Semantic versioning — bump MINOR for new steps, PATCH for fixes
description: <One-sentence description of what this workflow does>
command: /<slash_command_name>  # The slash command that triggers this workflow
category: <lookup|enrichment|ocr|maintenance|data>
schedule: <daily|weekly|monthly|as_needed|manual>

inputs:                         # Files this workflow reads (for pre-flight validation)
  - path/to/input/file.json

outputs:                        # Files this workflow writes (for post-run validation)
  - path/to/output/file.md

dependencies:                   # Other workflows or scripts this workflow calls
  - /other_workflow_command     # or scripts/path/to/script.py

error_handling:
  on_web_search_failure: <use_cached|abort|warn_and_continue>
  on_missing_input: <abort|warn_and_use_defaults>
  on_script_failure: <abort|warn>

changelog:
  - version: <MAJOR.MINOR.PATCH>
    date: YYYY-MM-DD
    change: <What changed>
---
```

### Optional Front-Matter Fields

```yaml
# Only for workflows with scheduled automation:
cron_expression: "0 2 * * 0"   # e.g., weekly Sunday at 2 AM for data refresh

# Only for workflows that accept parameters:
parameters:
  - name: medicine_name
    type: string
    required: true
    description: Brand or generic medicine name (e.g., Paracetamol, Crocin)
```

---

## 2. Front-Matter Field Definitions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | string | Full human-readable name | `"Jan Aushadhi Medicine Lookup"` |
| `version` | string | Semantic version (see §3) | `"1.2.0"` |
| `description` | string | ≤ 120 chars, plain English | `"Search Jan Aushadhi drug database by name or code"` |
| `command` | string | Exact slash command | `"/find_generic"` |
| `category` | enum | One of 5 categories | `"lookup"` |
| `schedule` | enum | Review cadence | `"as_needed"` |
| `inputs` | list[path] | Files read before executing | `["data/system/drug_cache/janaushadhi_medicines.json"]` |
| `outputs` | list[path] | Files written upon completion | `["data/results/{drug_code}_result_{date}.md"]` |
| `dependencies` | list | Downstream workflows/scripts | `["/find_generic"]` |
| `error_handling` | object | Error recovery policy | see §5 |
| `changelog` | list | Version history | see §3 |

---

## 3. Versioning Rules

Use **Semantic Versioning** (`MAJOR.MINOR.PATCH`):

| Change Type | Bump | Example |
|------------|------|---------|
| New step added | MINOR | 1.0.0 → 1.1.0 |
| Existing step modified (output format changed) | MINOR | 1.1.0 → 1.2.0 |
| Bug fix / clarification / reword | PATCH | 1.2.0 → 1.2.1 |
| Breaking change (new required input, schema change) | MAJOR | 1.2.1 → 2.0.0 |

**All new workflows start at `1.0.0`.**

---

## 4. Step Naming & Structure

Each workflow body must use consistent step numbering:

```markdown
## Step N: <Action Verb> + <Object>

Brief one-paragraph description of what this step does and why.

**Tool:** `search_web` / `view_file` / `run_command` / `write_to_file`

**Input:** What data this step consumes (file path or previous step output)

**Output / Deliverable:** What this step produces (table, JSON, file write)

**On Failure:** What to do if this step fails (per `error_handling` policy)
```

---

## 5. Error Handling Policy Reference

| Policy Value | Meaning |
|-------------|---------|
| `use_cached` | Use the most recent cached value from `data/system/drug_cache/`; flag result as STALE |
| `abort` | Stop workflow immediately; report error to user |
| `warn_and_continue` | Log warning to `data/system/logs/execution_log.jsonl`; continue with available data |
| `warn_and_use_defaults` | Use defined default values; surface warning in response |

---

## 6. Logging Requirements

Every workflow execution MUST log to `data/system/logs/execution_log.jsonl`:

```json
{
  "run_id": "<workflow_command>_<YYYYMMDD_HHMMSS>",
  "workflow": "<command>",
  "version": "<version>",
  "started_at": "ISO-8601",
  "completed_at": "ISO-8601",
  "duration_ms": 0,
  "steps_completed": 0,
  "steps_total": 0,
  "status": "success|partial|failed",
  "errors": [],
  "outputs_written": []
}
```

Every **medicine lookup result** MUST log to `data/system/logs/lookup_log.jsonl`:

```json
{
  "lookup_id": "<uuid>",
  "date": "YYYY-MM-DD",
  "workflow": "<command>",
  "query": "<user input>",
  "query_type": "brand|generic|drug_code|symptom|ocr",
  "results_count": 0,
  "top_result": {
    "drug_code": "",
    "generic_name": "",
    "jan_aushadhi_mrp": 0,
    "savings_pct": 0
  },
  "data_source": "local_db|live_scrape|llm_fallback",
  "cache_hit": false
}
```

---

## 7. Output Validation Rules

After writing any output file, the agent MUST verify:

1. **File exists** at the declared output path
2. **File is non-empty** (> 0 bytes)
3. **JSON outputs** are valid JSON (parse test)
4. **Markdown outputs** contain the mandatory medical disclaimer header

If output validation fails → log to `execution_log.jsonl` with `status: "partial"` and surface error to user.

---

## 8. Pre-Flight Input Validation

Before executing any step, the agent MUST verify all `inputs:` files exist and are non-empty.

**If a required input is missing:**
- `on_missing_input: abort` → Stop and tell the user which file is missing and how to populate it.
- `on_missing_input: warn_and_use_defaults` → Proceed with sensible defaults, but clearly flag the assumption.

---

## 9. Category Definitions

| Category | Directory | Purpose |
|----------|-----------|---------| 
| `lookup` | `.agent/workflows/lookup/` | Medicine search, drug code lookup, generic finder workflows |
| `enrichment` | `.agent/workflows/enrichment/` | Image fetch, buy links, PDF links, savings calc workflows |
| `ocr` | `.agent/workflows/ocr/` | Prescription image/PDF parsing workflows |
| `maintenance` | `.agent/workflows/maintenance/` | Data refresh, cache validation, cleanup workflows |
| `data` | `.agent/workflows/data/` | Jan Aushadhi data ingestion and schema validation workflows |

---

## 10. Linting Compliance

Run `python3 .agent/scripts/workflow_linter.py` to validate all workflows. The linter checks:

1. ✅ YAML front-matter is valid and parseable
2. ✅ All mandatory fields present
3. ✅ `version` matches semantic versioning pattern
4. ✅ `category` is one of the 5 valid values
5. ✅ `schedule` is one of the 5 valid values
6. ✅ All `inputs:` file paths referenced in the body text
7. ✅ All `outputs:` file paths referenced in the body text
8. ✅ `error_handling` block present with all 3 keys
9. ✅ `changelog` has at least 1 entry
10. ✅ Step headers follow the `## Step N:` naming convention
11. ✅ Medical disclaimer present in workflow body

---

## 11. Medical Disclaimer Requirement

Every workflow output that presents medicine information MUST include:
```
> ⚕️ **Disclaimer:** This tool is for informational purposes only. Always consult a licensed pharmacist or physician before switching medications.
```

Workflows that omit this disclaimer will **FAIL** linting (Rule R11-DISCLAIMER).

---

*This standard applies to all workflows created after 2026-08-21. Legacy workflows must be migrated via `scripts/maintenance/migrate_workflows.py`.*
