"""
test_ocr_processor.py — Unit Tests for OCR Processor & Directory Resolution
Med Equivalence Agent Framework | tests/unit/
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared.ocr_processor import IMAGE_DIR, parse_medicines_from_text


class TestOcrProcessor:
    def test_image_dir_constant_exists(self):
        assert IMAGE_DIR == PROJECT_ROOT / "inputs" / "image"

    def test_parse_medicines_from_text_paracetamol(self):
        sample_text = "Rx Paracetamol 500mg BD"
        medicines = parse_medicines_from_text(sample_text)
        assert len(medicines) == 1
        assert medicines[0]["medicine_name"] == "Paracetamol"
        assert medicines[0]["dosage"] == "500mg"
        assert medicines[0]["frequency"] == "Twice daily"

    def test_parse_medicines_from_text_multiple(self):
        sample_text = "Paracetamol 500mg BD\nAmoxicillin 250mg TDS"
        medicines = parse_medicines_from_text(sample_text)
        assert len(medicines) == 2
        assert medicines[0]["medicine_name"] == "Paracetamol"
        assert medicines[1]["medicine_name"] == "Amoxicillin"
