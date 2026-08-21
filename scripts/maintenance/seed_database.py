"""
seed_database.py — Drug Cache Seeder
Med Equivalence Agent Framework | scripts/maintenance/

Seeds the local drug cache from the bundled CSV dataset.
Run this first to populate the cache before using the agent.

Usage:
  .venv/bin/python scripts/maintenance/seed_database.py
  .venv/bin/python scripts/maintenance/seed_database.py --force  # Overwrite existing cache
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
SEED_CSV = PROJECT_ROOT / "data" / "seeds" / "janaushadhi_medicines.csv"
CACHE_DIR = PROJECT_ROOT / "data" / "system" / "drug_cache"
CACHE_FILE = CACHE_DIR / "janaushadhi_medicines.json"

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def seed_from_csv(force: bool = False) -> int:
    """
    Seed the drug cache from the bundled CSV file.

    Args:
        force: If True, overwrite existing cache even if fresh

    Returns:
        Exit code (0=success, 1=error)
    """
    print(f"\n{BOLD}💊 Med Equivalence Agent — Database Seeder{RESET}")
    print(f"{'─' * 50}")

    # Check if seed CSV exists
    if not SEED_CSV.exists():
        print(f"{RED}❌ Seed CSV not found: {SEED_CSV.relative_to(PROJECT_ROOT)}{RESET}")
        return 1

    # Check if cache already exists (and not forcing)
    if CACHE_FILE.exists() and not force:
        print(f"{YELLOW}⚠️  Cache already exists at {CACHE_FILE.relative_to(PROJECT_ROOT)}{RESET}")
        print(f"   Use --force to overwrite. Skipping seed.")
        return 0

    # Create cache directory
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Load CSV and convert to cache format
    medicines = {}
    errors = []

    print(f"📂 Loading seed data from: {SEED_CSV.relative_to(PROJECT_ROOT)}")

    with open(SEED_CSV, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (row 1 is header)
            try:
                generic_name = row.get("generic_name", "").strip()
                product_name = row.get("product_name", "").strip()
                drug_code = row.get("drug_code", "").strip()
                mrp_str = row.get("mrp", "0").strip()

                if not generic_name or not drug_code:
                    errors.append(f"Row {row_num}: Missing generic_name or drug_code")
                    continue

                try:
                    mrp = float(mrp_str)
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid MRP '{mrp_str}'")
                    mrp = 0.0

                # Use generic_name as the key; allow multiple entries (different dosages)
                # Use product_name as key to preserve dosage variations
                key = product_name or generic_name

                medicines[key] = {
                    "drug_code": drug_code,
                    "product_name": product_name,
                    "generic_name": generic_name,
                    "unit_size": row.get("unit_size", "").strip(),
                    "mrp": mrp,
                    "category": row.get("category", "").strip(),
                    "manufacturer": row.get("manufacturer", "PMBI-Approved").strip(),
                    "schedule": row.get("schedule", "OTC").strip(),
                    "source": "seed_csv",
                    "last_verified": row.get("last_verified", datetime.now().strftime("%Y-%m-%d")).strip(),
                    "brand_aliases": [],  # Can be enriched later
                }

            except Exception as e:
                errors.append(f"Row {row_num}: {e}")

    # Write cache
    cache = {
        "metadata": {
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "medicine_count": len(medicines),
            "source": "seed_csv",
            "seed_file": str(SEED_CSV.relative_to(PROJECT_ROOT)),
            "version": "1.0.0",
        },
        "medicines": medicines,
    }

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    # Report
    print(f"{GREEN}✅ Seeded {len(medicines)} medicines into cache{RESET}")
    print(f"   Output: {CACHE_FILE.relative_to(PROJECT_ROOT)}")

    if errors:
        print(f"\n{YELLOW}⚠️  {len(errors)} warning(s):{RESET}")
        for err in errors[:5]:
            print(f"   • {err}")

    print(f"\n{GREEN}{BOLD}✅ Database seeding complete!{RESET}")
    print(f"{'─' * 50}\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Med Equivalence Agent — Database Seeder",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing cache")
    args = parser.parse_args()
    return seed_from_csv(force=args.force)


if __name__ == "__main__":
    sys.exit(main())
