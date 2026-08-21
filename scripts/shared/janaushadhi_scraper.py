"""
janaushadhi_scraper.py — Jan Aushadhi Portal Scraper
Med Equivalence Agent Framework | scripts/shared/

Scrapes the official PMBI portal (janaushadhi.gov.in) to fetch
medicine names, drug codes, MRPs, and categories.

Usage:
  .venv/bin/python scripts/shared/janaushadhi_scraper.py --query "Paracetamol"
  .venv/bin/python scripts/shared/janaushadhi_scraper.py --mode full --output data/system/drug_cache/janaushadhi_medicines.json
  .venv/bin/python scripts/shared/janaushadhi_scraper.py --drug-code JA-0453

Exit codes:
  0 — Success
  1 — Scrape failed (portal unreachable or no results)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

try:
    import httpx
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Missing dependencies. Run: .venv/bin/pip install httpx beautifulsoup4 lxml")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent.parent
CACHE_DIR = PROJECT_ROOT / "data" / "system" / "drug_cache"
CACHE_FILE = CACHE_DIR / "janaushadhi_medicines.json"

JANAUSHADHI_URL = "https://janaushadhi.gov.in/Product_List.aspx"
REQUEST_TIMEOUT = 30
RATE_LIMIT_DELAY = 1.0  # seconds between requests

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def _get_headers() -> dict[str, str]:
    """Return browser-like headers to avoid bot detection."""
    return {
        "User-Agent": "Mozilla/5.0 (compatible; MedEquivalenceAgent/1.0; +https://github.com/your-org/med-equivalence-agent)",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
        "Referer": "https://janaushadhi.gov.in/",
    }


def search_by_name(medicine_name: str) -> list[dict[str, Any]]:
    """
    Search Jan Aushadhi portal for medicines by name.

    Args:
        medicine_name: Brand name or generic name to search

    Returns:
        List of medicine records with drug_code, product_name, unit_size, mrp, category
    """
    print(f"🔍 Searching Jan Aushadhi portal for: '{medicine_name}'")

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            # First GET to get the ASP.NET session and viewstate
            response = client.get(JANAUSHADHI_URL, headers=_get_headers())
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            # Extract ASP.NET form fields
            viewstate = _extract_field(soup, "__VIEWSTATE")
            eventvalidation = _extract_field(soup, "__EVENTVALIDATION")
            viewstategenerator = _extract_field(soup, "__VIEWSTATEGENERATOR")

            time.sleep(RATE_LIMIT_DELAY)

            # POST search form
            form_data = {
                "__VIEWSTATE": viewstate,
                "__EVENTVALIDATION": eventvalidation,
                "__VIEWSTATEGENERATOR": viewstategenerator,
                "ctl00$ContentPlaceHolder1$txtProductName": medicine_name,
                "ctl00$ContentPlaceHolder1$btnSearch": "Search",
            }

            search_response = client.post(
                JANAUSHADHI_URL,
                data=form_data,
                headers=_get_headers(),
            )
            search_response.raise_for_status()

            return _parse_results(search_response.text)

    except httpx.TimeoutException:
        print(f"{RED}❌ Timeout: Jan Aushadhi portal did not respond within {REQUEST_TIMEOUT}s{RESET}")
        return []
    except httpx.HTTPStatusError as e:
        print(f"{RED}❌ HTTP error {e.response.status_code} from Jan Aushadhi portal{RESET}")
        return []
    except Exception as e:
        print(f"{RED}❌ Scrape error: {e}{RESET}")
        return []


def search_by_drug_code(drug_code: str) -> Optional[dict[str, Any]]:
    """
    Search Jan Aushadhi portal for a specific drug code.

    Args:
        drug_code: Drug code (e.g., "JA-0453" or "0453")

    Returns:
        Medicine record or None if not found
    """
    print(f"🔍 Looking up drug code: {drug_code}")

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            response = client.get(JANAUSHADHI_URL, headers=_get_headers())
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            viewstate = _extract_field(soup, "__VIEWSTATE")
            eventvalidation = _extract_field(soup, "__EVENTVALIDATION")
            viewstategenerator = _extract_field(soup, "__VIEWSTATEGENERATOR")

            time.sleep(RATE_LIMIT_DELAY)

            # Normalize drug code
            code = drug_code.replace("JA-", "").strip()

            form_data = {
                "__VIEWSTATE": viewstate,
                "__EVENTVALIDATION": eventvalidation,
                "__VIEWSTATEGENERATOR": viewstategenerator,
                "ctl00$ContentPlaceHolder1$txtDrugCode": code,
                "ctl00$ContentPlaceHolder1$btnSearch": "Search",
            }

            search_response = client.post(
                JANAUSHADHI_URL,
                data=form_data,
                headers=_get_headers(),
            )
            search_response.raise_for_status()

            results = _parse_results(search_response.text)
            return results[0] if results else None

    except Exception as e:
        print(f"{RED}❌ Drug code lookup error: {e}{RESET}")
        return None


def _extract_field(soup: BeautifulSoup, field_name: str) -> str:
    """Extract a hidden form field value."""
    tag = soup.find("input", {"name": field_name})
    return tag["value"] if tag else ""


def _parse_results(html: str) -> list[dict[str, Any]]:
    """Parse the search results table from Jan Aushadhi HTML response."""
    soup = BeautifulSoup(html, "lxml")
    results = []

    # Find the results GridView table
    table = soup.find("table", {"id": lambda x: x and "GridView" in str(x)})
    if not table:
        # Try alternate table selectors
        table = soup.find("table", {"class": lambda x: x and "grid" in str(x).lower()})

    if not table:
        print(f"{YELLOW}⚠️  No results table found in response{RESET}")
        return results

    rows = table.find_all("tr")
    for row in rows[1:]:  # Skip header row
        cells = row.find_all("td")
        if len(cells) >= 5:
            results.append({
                "drug_code": cells[0].get_text(strip=True),
                "product_name": cells[1].get_text(strip=True),
                "unit_size": cells[2].get_text(strip=True),
                "mrp": _parse_price(cells[3].get_text(strip=True)),
                "category": cells[4].get_text(strip=True) if len(cells) > 4 else "Unknown",
                "source": "janaushadhi.gov.in",
                "last_verified": datetime.now().strftime("%Y-%m-%d"),
            })

    print(f"{GREEN}✅ Found {len(results)} result(s){RESET}")
    return results


def _parse_price(price_str: str) -> float:
    """Parse price string to float."""
    try:
        # Remove ₹, Rs., commas
        cleaned = price_str.replace("₹", "").replace("Rs.", "").replace(",", "").strip()
        return float(cleaned)
    except ValueError:
        return 0.0


def load_cache() -> dict[str, Any]:
    """Load the local drug cache from disk."""
    if not CACHE_FILE.exists():
        return {"metadata": {"last_updated": None, "medicine_count": 0, "source": "janaushadhi.gov.in"}, "medicines": {}}

    with open(CACHE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_cache(cache: dict[str, Any]) -> None:
    """Save the drug cache to disk."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    cache["metadata"]["medicine_count"] = len(cache.get("medicines", {}))

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    print(f"{GREEN}✅ Cache updated → {CACHE_FILE.relative_to(PROJECT_ROOT)}{RESET}")
    print(f"   {cache['metadata']['medicine_count']} medicines in cache")


def search_cache(query: str) -> list[dict[str, Any]]:
    """Search the local cache with fuzzy matching."""
    cache = load_cache()
    medicines = cache.get("medicines", {})
    query_lower = query.lower()
    results = []

    for name, data in medicines.items():
        score = 0
        # Exact match
        if query_lower == name.lower():
            score = 100
        # Contains match
        elif query_lower in name.lower() or name.lower() in query_lower:
            score = 80
        # Drug code match
        elif query_lower.replace("ja-", "") == data.get("drug_code", "").replace("JA-", "").lower():
            score = 100
        # Brand alias match
        elif any(query_lower in alias.lower() for alias in data.get("brand_aliases", [])):
            score = 75

        if score >= 75:
            results.append({**data, "generic_name": name, "match_score": score})

    return sorted(results, key=lambda x: x["match_score"], reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Jan Aushadhi Portal Scraper — Med Equivalence Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--query", "-q", type=str, help="Medicine name to search")
    parser.add_argument("--drug-code", "-c", type=str, help="Drug code to look up")
    parser.add_argument("--mode", choices=["query", "full"], default="query",
                        help="'query' for single search, 'full' for full data refresh")
    parser.add_argument("--output", "-o", type=str, help="Output JSON file path (for --mode full)")
    parser.add_argument("--use-cache", action="store_true", help="Check local cache first before scraping")

    args = parser.parse_args()

    if args.use_cache and args.query:
        print(f"\n{BOLD}💊 Med Equivalence Agent — Cache Search{RESET}")
        cache_results = search_cache(args.query)
        if cache_results:
            print(f"{GREEN}✅ Found {len(cache_results)} result(s) in local cache{RESET}")
            print(json.dumps(cache_results, ensure_ascii=False, indent=2))
            return 0
        else:
            print(f"{YELLOW}⚠️  Not in cache — proceeding to live scrape{RESET}")

    if args.drug_code:
        print(f"\n{BOLD}💊 Med Equivalence Agent — Drug Code Lookup{RESET}")
        result = search_by_drug_code(args.drug_code)
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        else:
            print(f"{RED}❌ Drug code '{args.drug_code}' not found{RESET}")
            return 1

    elif args.query:
        print(f"\n{BOLD}💊 Med Equivalence Agent — Medicine Search{RESET}")
        results = search_by_name(args.query)
        if results:
            print(json.dumps(results, ensure_ascii=False, indent=2))
            # Update cache with new results
            cache = load_cache()
            for r in results:
                name = r.get("product_name", "")
                if name:
                    cache["medicines"][name] = r
            save_cache(cache)
            return 0
        else:
            print(f"{YELLOW}⚠️  No results found for '{args.query}'{RESET}")
            return 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
