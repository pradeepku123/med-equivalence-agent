"""
test_workflow_linter.py — Integration Tests for Workflow Linter
Med Equivalence Agent Framework | tests/integration/

Tests for .agent/scripts/workflow_linter.py
"""

import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / ".agent" / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT))

from workflow_linter import LintIssue, extract_frontmatter, lint_file


VALID_WORKFLOW = """\
---
name: Test Lookup Workflow
version: 1.0.0
description: A valid test workflow for generic medicine lookup
command: /test_lookup
category: lookup
schedule: as_needed
inputs:
  - data/system/drug_cache/janaushadhi_medicines.json
outputs:
  - data/results/test_result.md
error_handling:
  on_web_search_failure: use_cached
  on_missing_input: abort
  on_script_failure: warn
changelog:
  - version: 1.0.0
    date: '2026-08-21'
    change: Initial test version
---

## Step 1: Load Drug Cache

Load the janaushadhi_medicines.json cache and search for the medicine.

**Tool:** `view_file`

**Input:** `data/system/drug_cache/janaushadhi_medicines.json`

**Output / Deliverable:** Drug record with drug_code and MRP.

**On Failure:** Use cached data.

## Step 2: Save Result

Save to `data/results/test_result.md`.

**Output / Deliverable:** Result saved.

> ⚕️ **Disclaimer:** This tool is for informational purposes only. Always consult a licensed pharmacist or physician before switching medications.
"""

MISSING_DISCLAIMER = """\
---
name: Test Without Disclaimer
version: 1.0.0
description: A workflow missing the medical disclaimer
command: /test_no_disclaimer
category: lookup
schedule: as_needed
error_handling:
  on_web_search_failure: use_cached
  on_missing_input: abort
  on_script_failure: warn
changelog:
  - version: 1.0.0
    date: '2026-08-21'
    change: Initial version
---

## Step 1: Search

Search for medicine by name.

**Tool:** `view_file`

**Output / Deliverable:** Drug record.

**On Failure:** Use cached data.
"""

MISSING_FIELDS_WORKFLOW = """\
---
name: Incomplete Workflow
version: 1.0.0
description: Missing several required fields
---

## Step 1: Search

This body has no disclaimer.
"""

INVALID_VERSION_WORKFLOW = """\
---
name: Bad Version
version: bad-version
description: A workflow with invalid semver
command: /bad_version
category: lookup
schedule: as_needed
error_handling:
  on_web_search_failure: use_cached
  on_missing_input: abort
  on_script_failure: warn
changelog:
  - version: 1.0.0
    date: '2026-08-21'
    change: Initial version
---

## Step 1: Search

Body content here.

> ⚕️ Disclaimer: Always consult a pharmacist.
"""

INVALID_CATEGORY_WORKFLOW = """\
---
name: Bad Category
version: 1.0.0
description: A workflow with invalid category
command: /bad_category
category: invalid_cat
schedule: as_needed
error_handling:
  on_web_search_failure: use_cached
  on_missing_input: abort
  on_script_failure: warn
changelog:
  - version: 1.0.0
    date: '2026-08-21'
    change: Initial version
---

## Step 1: Search

Body content here.

> ⚕️ Disclaimer: Always consult a pharmacist.
"""


def write_temp_workflow(content: str) -> Path:
    """Write workflow content to a temporary file."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    )
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


class TestExtractFrontmatter:
    def test_valid_yaml_extracted(self):
        content = "---\nname: Test\nversion: 1.0.0\n---\n\nBody"
        fm, body = extract_frontmatter(content)
        assert fm is not None
        assert fm["name"] == "Test"
        assert "Body" in body

    def test_no_frontmatter_returns_none(self):
        content = "No front matter here"
        fm, body = extract_frontmatter(content)
        assert fm is None

    def test_invalid_yaml_returns_parse_error(self):
        content = "---\nname: [unclosed\n---\nBody"
        fm, body = extract_frontmatter(content)
        assert fm is not None
        assert "_parse_error" in fm


class TestLintFile:
    def test_valid_workflow_has_no_errors(self):
        tmp = write_temp_workflow(VALID_WORKFLOW)
        issues = lint_file(tmp)
        errors = [i for i in issues if i.level == "error"]
        assert len(errors) == 0, f"Unexpected errors: {[str(i) for i in errors]}"

    def test_missing_disclaimer_returns_r11_error(self):
        tmp = write_temp_workflow(MISSING_DISCLAIMER)
        issues = lint_file(tmp)
        assert any(i.rule == "R11-DISCLAIMER" for i in issues), "Expected R11-DISCLAIMER error"

    def test_missing_fields_returns_r1_errors(self):
        tmp = write_temp_workflow(MISSING_FIELDS_WORKFLOW)
        issues = lint_file(tmp)
        r1_errors = [i for i in issues if i.rule == "R1-MISSING-FIELD"]
        assert len(r1_errors) > 0, "Expected R1-MISSING-FIELD errors for missing fields"

    def test_invalid_version_returns_r2_error(self):
        tmp = write_temp_workflow(INVALID_VERSION_WORKFLOW)
        issues = lint_file(tmp)
        assert any(i.rule == "R2-VERSION" for i in issues), "Expected R2-VERSION error"

    def test_invalid_category_returns_r3_error(self):
        tmp = write_temp_workflow(INVALID_CATEGORY_WORKFLOW)
        issues = lint_file(tmp)
        assert any(i.rule == "R3-CATEGORY" for i in issues), "Expected R3-CATEGORY error"

    def test_no_frontmatter_returns_r0_error(self):
        tmp = write_temp_workflow("No frontmatter at all, just body text here.")
        issues = lint_file(tmp)
        assert any(i.rule == "R0-FRONTMATTER" for i in issues), "Expected R0-FRONTMATTER error"


class TestLintIssue:
    def test_error_has_red_icon(self):
        issue = LintIssue("error", "R1-TEST", "Test error")
        output = str(issue)
        assert "❌" in output
        assert "R1-TEST" in output

    def test_warning_has_warning_icon(self):
        issue = LintIssue("warning", "R6-TEST", "Test warning")
        output = str(issue)
        assert "⚠️" in output
