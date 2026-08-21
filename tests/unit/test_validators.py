"""
test_validators.py — Unit Tests for Validator Functions
Med Equivalence Agent Framework | tests/unit/

Tests for scripts/shared/validators.py
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared.validators import (
    calculate_savings,
    get_schedule_classification,
    get_substitution_warning,
    is_nti_drug,
    validate_drug_record,
)


# ─────────────────────────────────────────────────────────────────────────────
# validate_drug_record Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestValidateDrugRecord:
    def test_valid_record_returns_no_errors(self):
        record = {
            "drug_code": "JA-0001",
            "product_name": "Paracetamol 500mg",
            "generic_name": "Paracetamol",
            "mrp": 4.50,
            "last_verified": "2026-08-01",
        }
        errors = validate_drug_record(record)
        assert errors == []

    def test_missing_drug_code_returns_error(self):
        record = {
            "product_name": "Paracetamol 500mg",
            "mrp": 4.50,
            "last_verified": "2026-08-01",
        }
        errors = validate_drug_record(record)
        assert any("drug_code" in e for e in errors)

    def test_missing_product_name_returns_error(self):
        record = {
            "drug_code": "JA-0001",
            "mrp": 4.50,
            "last_verified": "2026-08-01",
        }
        errors = validate_drug_record(record)
        assert any("product_name" in e for e in errors)

    def test_negative_mrp_returns_error(self):
        record = {
            "drug_code": "JA-0001",
            "product_name": "Paracetamol",
            "mrp": -5.00,
            "last_verified": "2026-08-01",
        }
        errors = validate_drug_record(record)
        assert any("MRP cannot be negative" in e for e in errors)

    def test_non_numeric_mrp_returns_error(self):
        record = {
            "drug_code": "JA-0001",
            "product_name": "Paracetamol",
            "mrp": "not-a-price",
            "last_verified": "2026-08-01",
        }
        errors = validate_drug_record(record)
        assert any("numeric" in e for e in errors)

    def test_invalid_drug_code_format_returns_error(self):
        record = {
            "drug_code": "INVALID-CODE-FORMAT",
            "product_name": "Paracetamol",
            "mrp": 4.50,
            "last_verified": "2026-08-01",
        }
        errors = validate_drug_record(record)
        assert any("drug_code format" in e for e in errors)

    def test_numeric_drug_code_is_valid(self):
        record = {
            "drug_code": "00453",
            "product_name": "Paracetamol",
            "mrp": 4.50,
            "last_verified": "2026-08-01",
        }
        errors = validate_drug_record(record)
        assert not any("drug_code format" in e for e in errors)

    def test_zero_mrp_is_valid(self):
        record = {
            "drug_code": "JA-0001",
            "product_name": "Paracetamol",
            "mrp": 0.0,
            "last_verified": "2026-08-01",
        }
        errors = validate_drug_record(record)
        assert not any("MRP" in e for e in errors)


# ─────────────────────────────────────────────────────────────────────────────
# is_nti_drug Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestIsNtiDrug:
    def test_known_nti_drug_returns_true(self):
        assert is_nti_drug("warfarin") is True
        assert is_nti_drug("digoxin") is True
        assert is_nti_drug("lithium") is True
        assert is_nti_drug("phenytoin") is True
        assert is_nti_drug("theophylline") is True
        assert is_nti_drug("methotrexate") is True

    def test_case_insensitive_nti_check(self):
        assert is_nti_drug("WARFARIN") is True
        assert is_nti_drug("Digoxin") is True
        assert is_nti_drug("LITHIUM") is True

    def test_common_otc_drug_is_not_nti(self):
        assert is_nti_drug("paracetamol") is False
        assert is_nti_drug("ibuprofen") is False
        assert is_nti_drug("cetirizine") is False
        assert is_nti_drug("amoxicillin") is False


# ─────────────────────────────────────────────────────────────────────────────
# get_schedule_classification Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestGetScheduleClassification:
    def test_paracetamol_is_otc(self):
        assert get_schedule_classification("paracetamol") == "OTC"

    def test_ibuprofen_is_otc_or_h(self):
        result = get_schedule_classification("ibuprofen")
        assert result in ("OTC", "H")

    def test_amoxicillin_is_schedule_h(self):
        assert get_schedule_classification("amoxicillin") == "H"

    def test_metformin_is_schedule_h(self):
        assert get_schedule_classification("metformin") == "H"

    def test_omeprazole_is_schedule_h(self):
        assert get_schedule_classification("omeprazole") == "H"

    def test_alprazolam_is_schedule_h1(self):
        assert get_schedule_classification("alprazolam") == "H1"

    def test_diazepam_is_schedule_h1(self):
        assert get_schedule_classification("diazepam") == "H1"

    def test_morphine_is_schedule_x(self):
        assert get_schedule_classification("morphine") == "X"


# ─────────────────────────────────────────────────────────────────────────────
# get_substitution_warning Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestGetSubstitutionWarning:
    def test_schedule_x_shows_do_not_substitute(self):
        warning = get_substitution_warning("morphine", "X")
        assert "Do NOT substitute" in warning
        assert "🚫" in warning

    def test_schedule_h1_shows_controlled_substance(self):
        warning = get_substitution_warning("alprazolam", "H1")
        assert "Controlled substance" in warning or "controlled" in warning.lower()
        assert "🔴" in warning

    def test_schedule_h_shows_prescription_required(self):
        warning = get_substitution_warning("amoxicillin", "H")
        assert "prescription" in warning.lower()
        assert "⚠️" in warning

    def test_nti_drug_shows_nti_warning(self):
        warning = get_substitution_warning("warfarin", "OTC")
        assert "NTI" in warning
        assert "🔴" in warning

    def test_otc_drug_shows_safe(self):
        warning = get_substitution_warning("paracetamol", "OTC")
        assert "✅" in warning


# ─────────────────────────────────────────────────────────────────────────────
# calculate_savings Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestCalculateSavings:
    def test_standard_savings_calculation(self):
        result = calculate_savings(jan_aushadhi_mrp=4.50, market_price=25.00)
        assert result["amount_saved"] == pytest.approx(20.50, rel=1e-2)
        assert result["savings_pct"] == pytest.approx(82.0, rel=1e-1)
        assert "💰" in result["display_string"]

    def test_zero_market_price_returns_zero_savings(self):
        result = calculate_savings(jan_aushadhi_mrp=4.50, market_price=0)
        assert result["amount_saved"] == 0
        assert result["savings_pct"] == 0

    def test_negative_market_price_returns_zero_savings(self):
        result = calculate_savings(jan_aushadhi_mrp=4.50, market_price=-10.0)
        assert result["amount_saved"] == 0

    def test_jan_aushadhi_more_expensive_returns_zero_savings(self):
        # Shouldn't happen in practice but test defensively
        result = calculate_savings(jan_aushadhi_mrp=50.0, market_price=10.0)
        assert result["amount_saved"] == 0

    def test_display_string_contains_rupee_symbol(self):
        result = calculate_savings(jan_aushadhi_mrp=4.50, market_price=25.00)
        assert "₹" in result["display_string"]

    def test_100_percent_cheaper_case(self):
        result = calculate_savings(jan_aushadhi_mrp=0.0, market_price=25.00)
        assert result["savings_pct"] == 100.0
        assert result["amount_saved"] == pytest.approx(25.00)

    def test_returns_rounded_values(self):
        result = calculate_savings(jan_aushadhi_mrp=3.33, market_price=10.0)
        assert isinstance(result["savings_pct"], float)
        assert isinstance(result["amount_saved"], float)
