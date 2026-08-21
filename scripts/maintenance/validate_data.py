"""
validate_data.py — Drug Data Integrity Validator
Med Equivalence Agent Framework | scripts/maintenance/

Runs comprehensive validation checks on the drug cache and data files.
Used in CI/CD and by the /refresh_drug_data workflow.

Usage:
  .venv/bin/python scripts/maintenance/validate_data.py
  .venv/bin/python scripts/maintenance/validate_data.py --fix

Exit codes:
  0 — All checks passed
  1 — One or more validation errors found
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared.validators import (
    validate_cache_freshness,
    validate_cache_schema,
    validate_drug_record,
)

CACHE_FILE = PROJECT_ROOT / "data" / "system" / "drug_cache" / "janaushadhi_medicines.json"
SCHEMA_DIR = PROJECT_ROOT / "data" / "system" / "schemas"
LOG_DIR = PROJECT_ROOT / "data" / "system" / "logs"

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def check(name: str, passed: bool, message: str = "", warning: bool = False) -> bool:
    """Print a check result."""
    if passed:
        print(f"  {GREEN}✅ {name}{RESET}")
    elif warning:
        print(f"  {YELLOW}⚠️  {name}: {message}{RESET}")
    else:
        print(f"  {RED}❌ {name}: {message}{RESET}")
    return passed


def run_all_checks() -> int:
    """Run all validation checks. Returns exit code."""
    print(f"\n{BOLD}💊 Med Equivalence Agent — Data Validation{RESET}")
    print(f"{'─' * 60}")

    total_errors = 0
    total_warnings = 0

    # ─── Check 1: Drug cache file exists ─────────────────────────────────────
    print(f"\n{BOLD}Check 1: Drug Cache File Existence{RESET}")
    cache_exists = CACHE_FILE.exists()
    if not check("Drug cache file exists", cache_exists, f"Missing: {CACHE_FILE.relative_to(PROJECT_ROOT)}"):
        print(f"  {YELLOW}💡 Fix: Run .venv/bin/python scripts/maintenance/seed_database.py{RESET}")
        total_errors += 1

    # ─── Check 2: Cache freshness ─────────────────────────────────────────────
    print(f"\n{BOLD}Check 2: Cache Freshness{RESET}")
    if cache_exists:
        freshness = validate_cache_freshness(max_age_days=7)
        if freshness["is_fresh"]:
            check("Cache is fresh", True)
            print(f"     Last updated: {freshness['last_updated']} ({freshness['age_days']} days ago)")
        else:
            check("Cache freshness", False, freshness.get("warning", "Cache is stale"), warning=True)
            total_warnings += 1

    # ─── Check 3: Cache schema validation ────────────────────────────────────
    print(f"\n{BOLD}Check 3: Cache Schema Validation{RESET}")
    if cache_exists:
        schema_result = validate_cache_schema()
        check("Cache schema valid", schema_result["valid"],
              f"{schema_result['error_count']} error(s) found")
        print(f"     Total medicines in cache: {schema_result['total_medicines']}")
        if not schema_result["valid"]:
            for err in schema_result["errors"][:5]:
                print(f"     {RED}  • {err}{RESET}")
            if schema_result["error_count"] > 5:
                print(f"     {RED}  ... and {schema_result['error_count'] - 5} more errors{RESET}")
            total_errors += 1
        if schema_result.get("stale_count", 0) > 0:
            check("No stale records", False,
                  f"{schema_result['stale_count']} records unverified for > 30 days", warning=True)
            total_warnings += 1

    # ─── Check 4: JSON files parseable ───────────────────────────────────────
    print(f"\n{BOLD}Check 4: JSON File Integrity{RESET}")
    json_errors = []
    for json_file in PROJECT_ROOT.glob("data/**/*.json"):
        try:
            with open(json_file, encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            json_errors.append(f"{json_file.relative_to(PROJECT_ROOT)}: {e}")

    if check("All JSON files valid", len(json_errors) == 0,
             f"{len(json_errors)} invalid JSON file(s)"):
        pass
    else:
        for err in json_errors:
            print(f"     {RED}  • {err}{RESET}")
        total_errors += 1

    # ─── Check 5: Required directories ───────────────────────────────────────
    print(f"\n{BOLD}Check 5: Required Directory Structure{RESET}")
    required_dirs = [
        "data/system/drug_cache",
        "data/system/logs",
        "data/system/schemas",
        "data/results",
        "inputs/prescriptions",
        "scripts/shared",
        "scripts/maintenance",
        ".agent/workflows/lookup",
        ".agent/workflows/ocr",
        ".agent/workflows/data",
        ".agent/workflows/maintenance",
        ".agent/rules",
        ".agent/scripts",
    ]
    missing_dirs = []
    for d in required_dirs:
        if not (PROJECT_ROOT / d).exists():
            missing_dirs.append(d)

    if check("Required directories exist", len(missing_dirs) == 0,
             f"{len(missing_dirs)} directory/ies missing"):
        pass
    else:
        for d in missing_dirs:
            print(f"     {YELLOW}  • {d}{RESET}")
        total_warnings += 1

    # ─── Check 6: Workflow linter ─────────────────────────────────────────────
    print(f"\n{BOLD}Check 6: Workflow Linter{RESET}")
    workflows_dir = PROJECT_ROOT / ".agent" / "workflows"
    workflow_count = len(list(workflows_dir.rglob("*.md"))) if workflows_dir.exists() else 0
    check("Workflows directory populated", workflow_count > 0,
          "No workflow files found", warning=workflow_count == 0)
    print(f"     {workflow_count} workflow files found")

    # ─── Summary ─────────────────────────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print(f"{BOLD}VALIDATION SUMMARY{RESET}")
    print(f"  Errors:   {RED if total_errors else GREEN}{total_errors}{RESET}")
    print(f"  Warnings: {YELLOW if total_warnings else GREEN}{total_warnings}{RESET}")

    if total_errors == 0 and total_warnings == 0:
        print(f"\n{GREEN}{BOLD}✅ All checks passed! Data is healthy.{RESET}")
    elif total_errors == 0:
        print(f"\n{YELLOW}{BOLD}⚠️  Checks passed with warnings. Review above.{RESET}")
    else:
        print(f"\n{RED}{BOLD}❌ {total_errors} error(s) found. Fix before running workflows.{RESET}")

    print(f"{'─' * 60}\n")
    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(run_all_checks())
