# Workflow Execution Rules & Protocols
**Version:** 1.0.0 | **Created:** 2026-08-21

This rule file governs how the Med Equivalence Agent **executes, monitors, and recovers from** workflow runs.

---

## 1. Pre-Flight Input Validation (MANDATORY BEFORE ANY STEP)

Before executing the first step of ANY workflow, you MUST:

1. **Read the workflow's declared `inputs:`** from its YAML front-matter.
2. **Verify each input file exists and is non-empty** using `view_file` or `run_command ls -la`.
3. **If a required input is missing:**
   - If `on_missing_input: abort` → Stop immediately and tell the user: "⛔ Workflow aborted: required file `{path}` is missing. Run `/refresh_drug_data` to populate it."
   - If `on_missing_input: warn_and_use_defaults` → Proceed with safe defaults, clearly flagging all assumptions in bold.

---

## 2. Execution Logging (MANDATORY FOR EVERY WORKFLOW)

**At workflow START**, write to `data/system/logs/execution_log.jsonl` by running:
```python
import scripts.shared.logger as logger
run_id = logger.log_workflow_start(workflow="/{command}", version="X.Y.Z", steps_total=N)
```

**At workflow END**, write the completion record:
```python
logger.log_workflow_end(run_id=run_id, workflow="/{command}", version="X.Y.Z",
    started_at=start_time, steps_completed=N, steps_total=N,
    status="success",  # or "partial" or "failed"
    outputs_written=["data/path/to/output.md"])
```

**If a step fails**, log it before applying recovery:
```python
logger.log_step_error(run_id=run_id, step_num=3, step_name="Scrape Jan Aushadhi",
    error_msg="Portal returned 503",
    recovery_action="use_cached: using data from janaushadhi_medicines.json")
```

> **Note:** If the shared logger module is not yet importable, write a minimal JSON record directly to `data/system/logs/execution_log.jsonl`.

---

## 3. Error Recovery Policy

| Failure Type | Policy Key | Recovery Actions |
|---|---|---|
| Jan Aushadhi portal unreachable | `on_web_search_failure` | `use_cached`: read from `data/system/drug_cache/janaushadhi_medicines.json`; flag data as **[STALE — from cache]** |
| Required input file missing | `on_missing_input` | `abort`: stop and report missing file |
| Scraper script fails | `on_script_failure` | `warn`: report error but include partial results; `abort`: stop workflow |
| Image/buy link fetch fails | `warn_and_continue` | Log to `execution_log.jsonl`, add ⚠️ to output, continue with text-only result |

**Never silently fail.** Every data gap must be surfaced to the user with:
> ⚠️ **Data Gap [Step X]:** {what failed}. Using cached value from {source} (last updated: {date}).

---

## 4. Idempotency Protocol

For workflows that write result files:
1. **Check if the output already exists** for the same query today.
2. **If output exists for today** → Do NOT regenerate silently. Present existing output and ask: "A result for '{query}' already exists today. Do you want to re-fetch or view the existing one?"

---

## 5. Lookup Provenance Logging (MANDATORY FOR EVERY RESULT)

Every medicine lookup result MUST be logged to `data/system/logs/lookup_log.jsonl` AFTER delivery.

**Format:**
```json
{
  "lookup_id": "<8-char-uuid>",
  "date": "YYYY-MM-DD",
  "workflow": "/<command>",
  "query": "<user input>",
  "query_type": "brand|generic|drug_code|symptom|ocr",
  "results_count": 0,
  "top_result": {"drug_code": "", "generic_name": "", "jan_aushadhi_mrp": 0, "savings_pct": 0},
  "data_source": "local_db|live_scrape|llm_fallback",
  "cache_hit": false
}
```

> **Purpose:** Builds a permanent audit trail. Enables analytics on most-searched drugs, cache hit rates, and system health monitoring.

---

## 6. Output Validation

After writing any declared `outputs:`, verify:

1. **File exists** at the declared path (use `run_command ls -la {path}`)
2. **File is non-empty** (size > 0 bytes)
3. **JSON outputs** pass parse validation
4. **Report to user:** `✅ Result saved → {path}`

---

## 7. Python Environment

Whenever executing Python scripts, MUST use the local virtual environment:
```bash
source .venv/bin/activate
# OR
.venv/bin/python scripts/shared/janaushadhi_scraper.py
```
Never use the global Python environment.
