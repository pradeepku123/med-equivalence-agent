"""
ocr_processor.py — Prescription OCR Text Extractor
Med Equivalence Agent Framework | scripts/shared/

Extracts text from prescription images (JPG/PNG) or PDFs
using Tesseract OCR with English + Hindi language support.

Usage:
  .venv/bin/python scripts/shared/ocr_processor.py --input inputs/prescriptions/rx.jpg
  .venv/bin/python scripts/shared/ocr_processor.py --input inputs/prescriptions/rx.pdf --lang eng+hin

Exit codes:
  0 — Success
  1 — OCR failed or file not found
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import pytesseract
    from PIL import Image
except ImportError:
    print("❌ Missing dependencies. Run: .venv/bin/pip install pytesseract Pillow")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent.parent
PRESCRIPTIONS_DIR = PROJECT_ROOT / "inputs" / "prescriptions"
IMAGE_DIR = PROJECT_ROOT / "inputs" / "image"
RESULTS_DIR = PROJECT_ROOT / "data" / "results"

# Common medicine frequency abbreviations seen in Indian prescriptions
FREQUENCY_MAP = {
    "OD": "Once daily",
    "BD": "Twice daily",
    "TDS": "Three times daily",
    "QID": "Four times daily",
    "SOS": "As needed",
    "HS": "At bedtime",
    "AC": "Before meals",
    "PC": "After meals",
}

# Dosage unit patterns
DOSAGE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(mg|mcg|µg|ml|g|iu|units?|tabs?|caps?|tablets?|capsules?)",
    re.IGNORECASE,
)

# Medicine line pattern (captures drug name + dosage)
MEDICINE_LINE_PATTERN = re.compile(
    r"(?:Rx\.?\s+)?([A-Za-z][A-Za-z\s\-]+?)\s+"
    r"(\d+(?:\.\d+)?\s*(?:mg|mcg|ml|g|iu))"
    r"(?:\s+([A-Z]{2,3}|[×x]\s*\d+))?",
    re.IGNORECASE,
)


def extract_text_from_image(image_path: Path, lang: str = "eng+hin") -> str:
    """
    Extract text from a prescription image using Tesseract OCR.

    Args:
        image_path: Path to the image file (JPG/PNG)
        lang: Tesseract language string

    Returns:
        Extracted text string
    """
    print(f"📸 OCR processing: {image_path.name}")

    try:
        img = Image.open(image_path)

        # Pre-process: convert to grayscale for better OCR accuracy
        img = img.convert("L")

        # Run Tesseract
        config = f"--psm 6 -l {lang}"  # PSM 6: Assume uniform block of text
        text = pytesseract.image_to_string(img, config=config)

        print(f"✅ OCR extracted {len(text)} characters")
        return text

    except pytesseract.TesseractNotFoundError:
        print("❌ Tesseract not found. Install with: sudo apt-get install tesseract-ocr tesseract-ocr-hin")
        return ""
    except Exception as e:
        print(f"❌ OCR error: {e}")
        return ""


def extract_text_from_pdf(pdf_path: Path, lang: str = "eng+hin") -> str:
    """
    Extract text from a PDF prescription using pdftotext + Tesseract fallback.

    Args:
        pdf_path: Path to the PDF file
        lang: Tesseract language string

    Returns:
        Extracted text string
    """
    print(f"📄 Processing PDF: {pdf_path.name}")

    # Try pdftotext first (faster for text-based PDFs)
    try:
        import subprocess
        result = subprocess.run(
            ["pdftotext", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and len(result.stdout.strip()) > 50:
            print(f"✅ PDF text extracted ({len(result.stdout)} chars)")
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: Convert PDF to image then run Tesseract
    try:
        from pdf2image import convert_from_path
        print("📸 Converting PDF to image for OCR...")
        images = convert_from_path(str(pdf_path), dpi=300)
        full_text = ""
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image.convert("L"), config=f"--psm 6 -l {lang}")
            full_text += f"\n--- Page {i + 1} ---\n{text}"
        print(f"✅ PDF OCR extracted {len(full_text)} characters")
        return full_text
    except ImportError:
        print("❌ pdf2image not installed. Run: .venv/bin/pip install pdf2image")
        return ""
    except Exception as e:
        print(f"❌ PDF OCR error: {e}")
        return ""


def parse_medicines_from_text(ocr_text: str) -> list[dict[str, str]]:
    """
    Parse structured medicine data from OCR text.

    Args:
        ocr_text: Raw text from OCR

    Returns:
        List of dicts with 'medicine_name', 'dosage', 'frequency', 'raw_line'
    """
    medicines = []
    lines = ocr_text.split("\n")

    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue

        match = MEDICINE_LINE_PATTERN.search(line)
        if match:
            medicine_name = match.group(1).strip()
            dosage = match.group(2).strip()
            frequency_raw = match.group(3) or ""

            # Map frequency abbreviation
            freq_upper = frequency_raw.upper()
            frequency = FREQUENCY_MAP.get(freq_upper, frequency_raw)

            if len(medicine_name) > 2:  # Filter noise
                medicines.append({
                    "medicine_name": medicine_name,
                    "dosage": dosage,
                    "frequency": frequency,
                    "raw_line": line,
                })

    return medicines


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prescription OCR Processor — Med Equivalence Agent",
    )
    parser.add_argument("--input", "-i", required=True, help="Path to prescription image or PDF")
    parser.add_argument("--lang", default="eng+hin", help="OCR language(s) (default: eng+hin)")
    parser.add_argument("--output-json", action="store_true", help="Output parsed medicines as JSON")

    args = parser.parse_args()
    input_path = Path(args.input)

    if not input_path.exists():
        # Check project root, inputs/image, and inputs/prescriptions
        candidates = [
            PROJECT_ROOT / args.input,
            IMAGE_DIR / args.input,
            PRESCRIPTIONS_DIR / args.input,
        ]
        found = False
        for candidate in candidates:
            if candidate.exists():
                input_path = candidate
                found = True
                break
        if not found:
            print(f"❌ File or directory not found: {args.input}")
            return 1

    if input_path.is_dir():
        image_files = sorted([
            f for f in input_path.glob("*")
            if f.suffix.lower() in {".jpeg", ".jpg", ".png", ".pdf"}
        ])
        if not image_files:
            print(f"❌ No supported image or PDF files found in directory: {input_path}")
            return 1
        rel_display = image_files[0].resolve().relative_to(PROJECT_ROOT.resolve())
        print(f"📁 Processing first image in directory: {rel_display}")
        input_path = image_files[0]

    # Extract text
    if input_path.suffix.lower() == ".pdf":
        text = extract_text_from_pdf(input_path, args.lang)
    else:
        text = extract_text_from_image(input_path, args.lang)

    if not text:
        print("❌ No text extracted from prescription")
        return 1

    # Parse medicines
    medicines = parse_medicines_from_text(text)

    if args.output_json:
        import json
        print(json.dumps({"raw_text": text, "medicines": medicines}, ensure_ascii=False, indent=2))
    else:
        print("\n📋 Extracted Medicines:")
        print("─" * 50)
        for med in medicines:
            print(f"  💊 {med['medicine_name']} {med['dosage']}")
            if med["frequency"]:
                print(f"     Frequency: {med['frequency']}")
        print(f"\n✅ Found {len(medicines)} medicine(s)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
