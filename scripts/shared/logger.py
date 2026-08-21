"""
logger.py — Structured Execution & Lookup Logger
Med Equivalence Agent Framework | scripts/shared/

Writes append-only JSONL logs to data/system/logs/ for:
  - Execution tracing (workflow runs, steps, durations)
  - Lookup provenance (medicine search audit trail)
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
LOG_DIR = PROJECT_ROOT / "data" / "system" / "logs"
EXECUTION_LOG = LOG_DIR / "execution_log.jsonl"
LOOKUP_LOG = LOG_DIR / "lookup_log.jsonl"


def _ensure_log_dir() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _append_jsonl(filepath: Path, record: dict) -> None:
    """Append a single JSON record to a JSONL file."""
    _ensure_log_dir()
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# Execution Log
# ─────────────────────────────────────────────────────────────────────────────

def log_workflow_start(
    workflow: str,
    version: str,
    steps_total: int,
) -> str:
    """
    Log the start of a workflow execution.

    Returns:
        run_id string to pass to log_workflow_end()
    """
    run_id = f"{workflow}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    record = {
        "run_id": run_id,
        "workflow": workflow,
        "version": version,
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "duration_ms": None,
        "steps_completed": 0,
        "steps_total": steps_total,
        "status": "running",
        "errors": [],
        "outputs_written": [],
    }
    _append_jsonl(EXECUTION_LOG, record)
    return run_id


def log_workflow_end(
    run_id: str,
    workflow: str,
    version: str,
    started_at: datetime,
    steps_completed: int,
    steps_total: int,
    status: str,  # "success" | "partial" | "failed"
    errors: Optional[list[str]] = None,
    outputs_written: Optional[list[str]] = None,
) -> None:
    """Log the completion of a workflow execution."""
    completed_at = datetime.now()
    duration_ms = int((completed_at - started_at).total_seconds() * 1000)

    record = {
        "run_id": run_id,
        "workflow": workflow,
        "version": version,
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat(),
        "duration_ms": duration_ms,
        "steps_completed": steps_completed,
        "steps_total": steps_total,
        "status": status,
        "errors": errors or [],
        "outputs_written": outputs_written or [],
    }
    _append_jsonl(EXECUTION_LOG, record)


def log_step_error(
    run_id: str,
    step_num: int,
    step_name: str,
    error_msg: str,
    recovery_action: str,
) -> None:
    """Log a step-level error within a workflow execution."""
    record = {
        "type": "step_error",
        "run_id": run_id,
        "step": step_num,
        "step_name": step_name,
        "timestamp": datetime.now().isoformat(),
        "error": error_msg,
        "recovery": recovery_action,
    }
    _append_jsonl(EXECUTION_LOG, record)


# ─────────────────────────────────────────────────────────────────────────────
# Lookup Provenance Log
# ─────────────────────────────────────────────────────────────────────────────

def log_lookup(
    workflow: str,
    query: str,
    query_type: str,  # "brand" | "generic" | "drug_code" | "symptom" | "ocr"
    results_count: int,
    data_source: str,  # "local_db" | "live_scrape" | "llm_fallback"
    cache_hit: bool,
    top_result: Optional[dict[str, Any]] = None,
) -> str:
    """
    Log a medicine lookup with its full provenance.

    Returns:
        lookup_id for future reference
    """
    lookup_id = str(uuid.uuid4())[:8]
    record = {
        "lookup_id": lookup_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        "workflow": workflow,
        "query": query,
        "query_type": query_type,
        "results_count": results_count,
        "top_result": top_result or {},
        "data_source": data_source,
        "cache_hit": cache_hit,
    }
    _append_jsonl(LOOKUP_LOG, record)
    return lookup_id


# ─────────────────────────────────────────────────────────────────────────────
# Utility: Read Recent Lookups
# ─────────────────────────────────────────────────────────────────────────────

def get_recent_lookups(query: Optional[str] = None, days: int = 30) -> list[dict]:
    """
    Read recent lookup log entries, optionally filtered by query.

    Args:
        query: Filter by query string (case-insensitive substring match)
        days: Only return lookups from the last N days

    Returns:
        List of lookup records, newest first.
    """
    if not LOOKUP_LOG.exists():
        return []

    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=days)
    results = []

    with open(LOOKUP_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if record.get("type") == "step_error":
                    continue
                date_str = record.get("date", "")
                if date_str:
                    rec_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if rec_date < cutoff:
                        continue
                if query and query.lower() not in record.get("query", "").lower():
                    continue
                results.append(record)
            except (json.JSONDecodeError, ValueError):
                continue

    return list(reversed(results))


def get_cache_hit_rate(days: int = 7) -> dict[str, Any]:
    """Calculate cache hit rate over the last N days."""
    lookups = get_recent_lookups(days=days)
    if not lookups:
        return {"total": 0, "cache_hits": 0, "hit_rate_pct": 0.0}

    cache_hits = sum(1 for l in lookups if l.get("cache_hit"))
    return {
        "total": len(lookups),
        "cache_hits": cache_hits,
        "hit_rate_pct": round(cache_hits / len(lookups) * 100, 1),
        "period_days": days,
    }


def get_execution_summary(last_n: int = 20) -> list[dict]:
    """Return the last N workflow execution records."""
    if not EXECUTION_LOG.exists():
        return []

    records = []
    with open(EXECUTION_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if record.get("type") == "step_error":
                    continue
                if record.get("status") == "running":
                    continue
                records.append(record)
            except json.JSONDecodeError:
                continue

    return records[-last_n:]
