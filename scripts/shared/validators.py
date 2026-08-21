"""
validators.py — Drug Data Validation Functions
Med Equivalence Agent Framework | scripts/shared/

Provides validation functions for medicine data integrity,
cache freshness, schema compliance, and safety classification.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
CACHE_FILE = PROJECT_ROOT / "data" / "system" / "drug_cache" / "janaushadhi_medicines.json"
SCHEMA_DIR = PROJECT_ROOT / "data" / "system" / "schemas"

# Narrow Therapeutic Index drugs (require extra caution for substitution)
NTI_DRUGS = {
    "digoxin", "warfarin", "lithium", "phenytoin", "carbamazepine",
    "theophylline", "levothyroxine", "cyclosporine", "tacrolimus",
    "methotrexate", "vancomycin", "aminoglycosides", "clonidine",
}

# Schedule H1 and X drugs (require strict prescription)
SCHEDULE_H1_DRUGS = {"alprazolam", "diazepam", "codeine", "tramadol", "buprenorphine"}
SCHEDULE_X_DRUGS = {"morphine", "oxycodone", "fentanyl", "ketamine"}

# Drug code pattern
DRUG_CODE_PATTERN = re.compile(r"^(JA-\d{4,6}|\d{4,6})$", re.IGNORECASE)


# ─────────────────────────────────────────────────────────────────────────────
# Cache Validation
# ─────────────────────────────────────────────────────────────────────────────

def validate_cache_freshness(max_age_days: int = 7) -> dict[str, Any]:
    """
    Check if the drug cache is fresh.

    Returns:
        dict with 'is_fresh', 'last_updated', 'age_days', 'warning' keys
    """
    if not CACHE_FILE.exists():
        return {
            "is_fresh": False,
            "last_updated": None,
            "age_days": None,
            "warning": "⚠️ Drug cache file does not exist. Run /refresh_drug_data to populate.",
        }

    with open(CACHE_FILE, encoding="utf-8") as f:
        cache = json.load(f)

    last_updated_str = cache.get("metadata", {}).get("last_updated")
    if not last_updated_str:
        return {
            "is_fresh": False,
            "last_updated": None,
            "age_days": None,
            "warning": "⚠️ Cache metadata missing last_updated. Run /refresh_drug_data.",
        }

    last_updated = datetime.strptime(last_updated_str, "%Y-%m-%d")
    age_days = (datetime.now() - last_updated).days
    is_fresh = age_days <= max_age_days

    return {
        "is_fresh": is_fresh,
        "last_updated": last_updated_str,
        "age_days": age_days,
        "medicine_count": cache.get("metadata", {}).get("medicine_count", 0),
        "warning": None if is_fresh else f"⚠️ Drug data is {age_days} days old (max: {max_age_days} days). Run /refresh_drug_data.",
    }


def validate_drug_record(record: dict[str, Any]) -> list[str]:
    """
    Validate a single drug record against the schema.

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Required fields
    required = ["drug_code", "product_name", "mrp", "last_verified"]
    for field in required:
        if not record.get(field):
            errors.append(f"Missing required field: '{field}'")

    # Drug code format
    drug_code = record.get("drug_code", "")
    if drug_code and not DRUG_CODE_PATTERN.match(str(drug_code)):
        errors.append(f"Invalid drug_code format: '{drug_code}' (expected JA-XXXX or numeric)")

    # MRP must be positive
    mrp = record.get("mrp", 0)
    try:
        if float(mrp) < 0:
            errors.append(f"MRP cannot be negative: {mrp}")
    except (ValueError, TypeError):
        errors.append(f"MRP must be numeric, got: '{mrp}'")

    return errors


def validate_cache_schema() -> dict[str, Any]:
    """
    Validate the entire cache against the schema.

    Returns:
        dict with 'valid', 'total_medicines', 'errors', 'stale_count'
    """
    freshness = validate_cache_freshness()
    if not CACHE_FILE.exists():
        return {"valid": False, "errors": [freshness["warning"]], "total_medicines": 0}

    with open(CACHE_FILE, encoding="utf-8") as f:
        cache = json.load(f)

    medicines = cache.get("medicines", {})
    errors = []
    stale_count = 0

    for name, record in medicines.items():
        record_errors = validate_drug_record(record)
        for err in record_errors:
            errors.append(f"{name}: {err}")

        # Check staleness of individual records
        last_verified = record.get("last_verified")
        if last_verified:
            verified_date = datetime.strptime(last_verified, "%Y-%m-%d")
            if (datetime.now() - verified_date).days > 30:
                stale_count += 1

    return {
        "valid": len(errors) == 0,
        "total_medicines": len(medicines),
        "errors": errors[:20],  # Cap at 20 errors for readability
        "error_count": len(errors),
        "stale_count": stale_count,
        "cache_freshness": freshness,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Safety Validation
# ─────────────────────────────────────────────────────────────────────────────

def is_nti_drug(generic_name: str) -> bool:
    """Check if a drug has a Narrow Therapeutic Index."""
    return generic_name.lower() in NTI_DRUGS


def get_schedule_classification(generic_name: str) -> str:
    """
    Return the Schedule classification for a drug.

    Returns:
        'X' | 'H1' | 'H' | 'OTC'
    """
    name_lower = generic_name.lower()
    if any(drug in name_lower for drug in SCHEDULE_X_DRUGS):
        return "X"
    if any(drug in name_lower for drug in SCHEDULE_H1_DRUGS):
        return "H1"
    # Common Schedule H drugs (antibiotics, antifungals, etc.)
    schedule_h_keywords = ["amoxicillin", "metformin", "atorvastatin", "omeprazole",
                           "azithromycin", "ciprofloxacin", "fluconazole", "metronidazole"]
    if any(keyword in name_lower for keyword in schedule_h_keywords):
        return "H"
    return "OTC"


def get_substitution_warning(generic_name: str, schedule: str) -> str:
    """Generate appropriate substitution warning for a drug."""
    if schedule == "X":
        return "🚫 SCHEDULE X: Do NOT substitute without explicit medical authorization."
    if schedule == "H1":
        return "🔴 SCHEDULE H1: Controlled substance. Substitution requires specialist consultation."
    if schedule == "H":
        return "⚠️ SCHEDULE H: Requires valid prescription. Consult your doctor before switching."
    if is_nti_drug(generic_name):
        return f"🔴 NTI DRUG: {generic_name} has a Narrow Therapeutic Index. Generic substitution MUST be supervised by a physician with therapeutic drug monitoring."
    return "✅ OTC: Generally safe for substitution. Consult pharmacist if unsure."


# ─────────────────────────────────────────────────────────────────────────────
# Savings Calculation
# ─────────────────────────────────────────────────────────────────────────────

def calculate_savings(jan_aushadhi_mrp: float, market_price: float) -> dict[str, Any]:
    """
    Calculate savings from switching to Jan Aushadhi.

    Returns:
        dict with 'amount_saved', 'savings_pct', 'display_string'
    """
    if market_price <= 0 or jan_aushadhi_mrp < 0:
        return {"amount_saved": 0, "savings_pct": 0, "display_string": "Savings unavailable"}

    amount_saved = max(0.0, market_price - jan_aushadhi_mrp)
    savings_pct = round((amount_saved / market_price) * 100, 1) if market_price > 0 else 0

    return {
        "amount_saved": round(amount_saved, 2),
        "savings_pct": savings_pct,
        "display_string": f"💰 Save ₹{amount_saved:.2f} per pack ({savings_pct}% cheaper than branded)",
    }
