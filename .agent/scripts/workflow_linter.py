#!/usr/bin/env python3
"""
workflow_linter.py — Workflow YAML Front-Matter Validator
Med Equivalence Agent Framework | .agent/scripts/

Validates all .agent/workflows/**/*.md files against the
WORKFLOW_STANDARD.md specification.

Usage:
  python3 .agent/scripts/workflow_linter.py          # Lint all workflows
  python3 .agent/scripts/workflow_linter.py --fix    # Show fix suggestions
  python3 .agent/scripts/workflow_linter.py <path>   # Lint a single file

Exit codes:
  0 — All workflows pass linting
  1 — One or more linting errors found
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    print("❌ PyYAML not installed. Run: .venv/bin/pip install pyyaml")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent.parent
WORKFLOWS_DIR = PROJECT_ROOT / ".agent" / "workflows"

MANDATORY_FIELDS = ["name", "version", "description", "command", "category", "schedule", "error_handling", "changelog"]
OPTIONAL_FIELDS = ["inputs", "outputs", "dependencies", "cron_expression", "parameters"]

VALID_CATEGORIES = {"lookup", "enrichment", "ocr", "maintenance", "data"}
VALID_SCHEDULES = {"daily", "weekly", "monthly", "as_needed", "manual"}
ERROR_HANDLING_KEYS = {"on_web_search_failure", "on_missing_input", "on_script_failure"}
VALID_EH_VALUES = {"use_cached", "abort", "warn_and_continue", "warn_and_use_defaults", "warn"}

SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
STEP_HEADER_PATTERN = re.compile(r"^## Step \d+:", re.MULTILINE)
COMMAND_PATTERN = re.compile(r"^/[a-z0-9_]+$")
DISCLAIMER_PATTERN = re.compile(r"Disclaimer|disclaimer|⚕️|medical advice", re.MULTILINE)

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"


# ─────────────────────────────────────────────────────────────────────────────
# Lint Result
# ─────────────────────────────────────────────────────────────────────────────

class LintIssue:
    def __init__(self, level: str, rule: str, message: str, fix: Optional[str] = None):
        self.level = level  # "error" or "warning"
        self.rule = rule
        self.message = message
        self.fix = fix

    def __str__(self) -> str:
        icon = "❌" if self.level == "error" else "⚠️ "
        color = RED if self.level == "error" else YELLOW
        return f"  {color}{icon} [{self.rule}] {self.message}{RESET}"


# ─────────────────────────────────────────────────────────────────────────────
# YAML Parser
# ─────────────────────────────────────────────────────────────────────────────

def extract_frontmatter(content: str) -> tuple[Optional[dict], str]:
    """Extract YAML front-matter from a markdown file."""
    if not content.startswith("---"):
        return None, content

    end_idx = content.find("---", 3)
    if end_idx == -1:
        return None, content

    yaml_str = content[3:end_idx].strip()
    body = content[end_idx + 3:].strip()

    try:
        fm = yaml.safe_load(yaml_str)
        return fm, body
    except yaml.YAMLError as e:
        return {"_parse_error": str(e)}, body


# ─────────────────────────────────────────────────────────────────────────────
# Rule Checkers
# ─────────────────────────────────────────────────────────────────────────────

def lint_file(filepath: Path) -> list[LintIssue]:
    """Run all lint rules against a single workflow file."""
    issues: list[LintIssue] = []
    content = filepath.read_text(encoding="utf-8")

    # Rule 0: YAML front-matter must exist and be parseable
    fm, body = extract_frontmatter(content)
    if fm is None:
        issues.append(LintIssue("error", "R0-FRONTMATTER", "No YAML front-matter block found", "Add --- ... --- block at top of file"))
        return issues

    if "_parse_error" in fm:
        issues.append(LintIssue("error", "R0-YAML-PARSE", f"YAML parse error: {fm['_parse_error']}"))
        return issues

    # Rule 1: Mandatory fields
    for field in MANDATORY_FIELDS:
        if field not in fm or fm[field] is None:
            issues.append(LintIssue("error", "R1-MISSING-FIELD", f"Mandatory field '{field}' is missing or null",
                                    f"Add '{field}: <value>' to front-matter"))

    # Rule 2: version must match semver
    version = fm.get("version", "")
    if version and not SEMVER_PATTERN.match(str(version)):
        issues.append(LintIssue("error", "R2-VERSION", f"version '{version}' is not valid semver (expected X.Y.Z)",
                                "Use format: version: '1.0.0'"))

    # Rule 3: category must be valid
    category = fm.get("category", "")
    if category and category not in VALID_CATEGORIES:
        issues.append(LintIssue("error", "R3-CATEGORY", f"category '{category}' is invalid (valid: {VALID_CATEGORIES})",
                                f"Set category to one of: {', '.join(sorted(VALID_CATEGORIES))}"))

    # Rule 4: schedule must be valid
    schedule = fm.get("schedule", "")
    if schedule and schedule not in VALID_SCHEDULES:
        issues.append(LintIssue("error", "R4-SCHEDULE", f"schedule '{schedule}' is invalid (valid: {VALID_SCHEDULES})",
                                f"Set schedule to one of: {', '.join(sorted(VALID_SCHEDULES))}"))

    # Rule 5: command must match /slug pattern
    command = fm.get("command", "")
    if command and not COMMAND_PATTERN.match(str(command)):
        issues.append(LintIssue("warning", "R5-COMMAND", f"command '{command}' should match /snake_case pattern"))

    # Rule 6: error_handling block completeness
    eh = fm.get("error_handling", {})
    if isinstance(eh, dict):
        missing_keys = ERROR_HANDLING_KEYS - set(eh.keys())
        if missing_keys:
            issues.append(LintIssue("warning", "R6-ERROR-HANDLING",
                                    f"error_handling missing keys: {missing_keys}",
                                    f"Add missing keys with valid values: {VALID_EH_VALUES}"))
        for key, val in eh.items():
            if val not in VALID_EH_VALUES:
                issues.append(LintIssue("warning", "R6-ERROR-HANDLING-VALUE",
                                        f"error_handling.{key} = '{val}' is not a recognized value",
                                        f"Valid values: {VALID_EH_VALUES}"))
    elif eh is not None:
        issues.append(LintIssue("error", "R6-ERROR-HANDLING", "error_handling must be a YAML object (dict)"))

    # Rule 7: changelog must have at least one entry
    changelog = fm.get("changelog", [])
    if isinstance(changelog, list) and len(changelog) == 0:
        issues.append(LintIssue("warning", "R7-CHANGELOG", "changelog is empty — add at least one entry",
                                "Add: changelog:\n  - version: '1.0.0'\n    date: YYYY-MM-DD\n    change: Initial version"))
    elif not isinstance(changelog, list) and changelog is not None:
        issues.append(LintIssue("error", "R7-CHANGELOG", "changelog must be a YAML list"))

    # Rule 8: inputs paths should be referenced in body (check at least one match)
    inputs = fm.get("inputs", []) or []
    for inp in inputs:
        if isinstance(inp, str):
            basename = Path(inp).name
            if basename not in body and inp not in body:
                issues.append(LintIssue("warning", "R8-INPUTS-REFERENCED",
                                        f"Input '{inp}' declared but not referenced in workflow body"))

    # Rule 9: Step headers follow ## Step N: convention
    if body.count("## Step") > 0:
        bad_steps = [line.strip() for line in body.split("\n")
                     if line.strip().startswith("## Step") and not STEP_HEADER_PATTERN.match(line)]
        for bad in bad_steps:
            issues.append(LintIssue("warning", "R9-STEP-NAMING",
                                    f"Step header doesn't follow '## Step N: <name>' convention: '{bad[:60]}'"))

    # Rule 10: file must have some body content
    if len(body.strip()) < 50:
        issues.append(LintIssue("error", "R10-EMPTY-BODY", "Workflow body is too short (< 50 chars) — add step descriptions"))

    # Rule 11: Medical disclaimer must be present (domain-specific)
    if not DISCLAIMER_PATTERN.search(body):
        issues.append(LintIssue("error", "R11-DISCLAIMER",
                                "Medical disclaimer not found in workflow body",
                                "Add: > ⚕️ **Disclaimer:** This tool is for informational purposes only. Always consult a licensed pharmacist or physician."))

    return issues


# ─────────────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────────────

def lint_all(show_fix: bool = False) -> int:
    """Lint all workflow files. Returns exit code (0=OK, 1=errors)."""
    workflow_files = list(WORKFLOWS_DIR.rglob("*.md"))

    if not workflow_files:
        print(f"{YELLOW}No workflow files found in {WORKFLOWS_DIR}{RESET}")
        return 0

    total_errors = 0
    total_warnings = 0
    files_with_issues = 0

    print(f"\n{BOLD}💊 Med Equivalence Agent Workflow Linter{RESET}")
    print(f"Scanning {len(workflow_files)} workflow files in {WORKFLOWS_DIR.relative_to(PROJECT_ROOT)}/\n")

    for wf_file in sorted(workflow_files):
        rel_path = wf_file.relative_to(PROJECT_ROOT)
        issues = lint_file(wf_file)
        errors = [i for i in issues if i.level == "error"]
        warnings = [i for i in issues if i.level == "warning"]

        if not issues:
            print(f"  {GREEN}✅ {rel_path}{RESET}")
        else:
            files_with_issues += 1
            status = f"{RED}❌" if errors else f"{YELLOW}⚠️ "
            print(f"\n  {status} {rel_path}{RESET}")
            for issue in issues:
                print(str(issue))
                if show_fix and issue.fix:
                    print(f"     {CYAN}💡 Fix: {issue.fix}{RESET}")
            total_errors += len(errors)
            total_warnings += len(warnings)

    # Summary
    print(f"\n{'─' * 60}")
    print(f"{BOLD}LINTING SUMMARY{RESET}")
    print(f"  Files scanned:        {len(workflow_files)}")
    print(f"  Files with issues:    {files_with_issues}")
    print(f"  Errors:               {RED if total_errors else GREEN}{total_errors}{RESET}")
    print(f"  Warnings:             {YELLOW if total_warnings else GREEN}{total_warnings}{RESET}")

    if total_errors == 0 and total_warnings == 0:
        print(f"\n{GREEN}{BOLD}✅ All workflows pass linting!{RESET}")
    elif total_errors == 0:
        print(f"\n{YELLOW}{BOLD}⚠️  Linting passed with warnings. Consider addressing them.{RESET}")
    else:
        print(f"\n{RED}{BOLD}❌ Linting failed. Fix {total_errors} error(s) before deploying.{RESET}")
        print(f"   Run with --fix to see suggested fixes.")

    print(f"{'─' * 60}\n")
    return 1 if total_errors > 0 else 0


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    show_fix = "--fix" in sys.argv
    target_args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if target_args:
        # Lint a single file
        target = Path(target_args[0])
        if not target.exists():
            target = PROJECT_ROOT / target_args[0]
        if not target.exists():
            print(f"{RED}File not found: {target_args[0]}{RESET}")
            sys.exit(1)
        issues = lint_file(target)
        for i in issues:
            print(str(i))
            if show_fix and i.fix:
                print(f"  {CYAN}💡 Fix: {i.fix}{RESET}")
        sys.exit(1 if any(i.level == "error" for i in issues) else 0)
    else:
        sys.exit(lint_all(show_fix=show_fix))
