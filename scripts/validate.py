"""
Validates referential integrity across all Health Profile JSON collections.

Checks:
  - No duplicate keys within a collection
  - dimension.category  -> valid category key
  - observation.dimension -> valid dimension key
  - observation.category  -> valid category key
  - de.key == en.key for every entry (i18n:duplicate consistency)

Usage:
    python scripts/validate.py
    python scripts/validate.py --strict   # exit code 1 on any warning
"""

import json
import argparse
from pathlib import Path

ROOT = Path(__file__).parent.parent

COLLECTIONS = {
    "categories":  "hp-categories",
    "dimensions":  "hp-dimensions",
    "observations": "hp-observations",
    "data_providers": "data-provider",
}


def load_collection(folder: str) -> list[dict]:
    entries = []
    for path in sorted((ROOT / folder).glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            data = {}
            _error(f"Invalid JSON in {path.name}: {e}")
        data["_file"] = path.name
        entries.append(data)
    return entries


errors: list[str] = []
warnings: list[str] = []


def _error(msg: str):
    errors.append(msg)
    print(f"  ERROR   {msg}")


def _warn(msg: str):
    warnings.append(msg)
    print(f"  WARNING {msg}")


def key_of(entry: dict) -> str:
    return entry.get("de", {}).get("key") or entry.get("en", {}).get("key", "")


def check_duplicate_keys(name: str, entries: list[dict]):
    seen: dict[str, str] = {}
    for e in entries:
        k = key_of(e)
        if not k:
            _error(f"[{name}] {e.get('_file')} has no key field")
            continue
        if k in seen:
            _error(f"[{name}] duplicate key '{k}' in {e['_file']} (first seen in {seen[k]})")
        else:
            seen[k] = e["_file"]


def check_locale_key_mismatch(name: str, entries: list[dict]):
    for e in entries:
        de_key = e.get("de", {}).get("key")
        en_key = e.get("en", {}).get("key")
        if de_key and en_key and de_key != en_key:
            _error(f"[{name}] {e['_file']}: de.key '{de_key}' != en.key '{en_key}'")


def check_references(
    name: str,
    entries: list[dict],
    field: str,
    target_name: str,
    target_keys: set[str],
):
    for e in entries:
        ref = e.get("de", {}).get(field) or e.get("en", {}).get(field)
        if not ref:
            _warn(f"[{name}] {e['_file']} (key='{key_of(e)}'): missing '{field}'")
            continue
        if ref not in target_keys:
            _error(
                f"[{name}] {e['_file']} (key='{key_of(e)}'): "
                f"'{field}' = '{ref}' not found in [{target_name}]"
            )


def main():
    parser = argparse.ArgumentParser(description="Validate Health Profile referential integrity")
    parser.add_argument("--strict", action="store_true", help="Exit with code 1 on warnings too")
    args = parser.parse_args()

    print("Loading collections...")
    categories   = load_collection(COLLECTIONS["categories"])
    dimensions   = load_collection(COLLECTIONS["dimensions"])
    observations = load_collection(COLLECTIONS["observations"])
    providers    = load_collection(COLLECTIONS["data_providers"])

    cat_keys  = {key_of(e) for e in categories}
    dim_keys  = {key_of(e) for e in dimensions}

    print("\nChecking for duplicate keys...")
    check_duplicate_keys("categories",    categories)
    check_duplicate_keys("dimensions",    dimensions)
    check_duplicate_keys("observations",  observations)
    check_duplicate_keys("data_providers", providers)

    print("Checking de.key == en.key consistency...")
    check_locale_key_mismatch("categories",    categories)
    check_locale_key_mismatch("dimensions",    dimensions)
    check_locale_key_mismatch("observations",  observations)
    check_locale_key_mismatch("data_providers", providers)

    print("Checking references...")
    check_references("dimensions",   dimensions,   "category",  "categories",  cat_keys)
    check_references("observations", observations, "dimension", "dimensions",  dim_keys)
    check_references("observations", observations, "category",  "categories",  cat_keys)

    print()
    if not errors and not warnings:
        print("OK — no issues found.")
        return

    print(f"{'='*50}")
    print(f"  {len(errors)} error(s), {len(warnings)} warning(s)")

    if errors or (args.strict and warnings):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
