"""
Consolidates the distributed Health Profile JSON files into a single
hierarchical health-profile.json at the project root.

Structure: categories -> dimensions -> observations
Relations are resolved and embedded; orphaned entries are collected separately.

Usage:
    python scripts/consolidate.py
    python scripts/consolidate.py --version 1.2.0
    python scripts/consolidate.py --indent 2
    python scripts/consolidate.py --out path/to/output.json
"""

import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent


def load_collection(folder: str) -> list[dict]:
    """Load all JSON files from a collection folder, keyed by de.key."""
    entries = []
    for path in sorted((ROOT / folder).glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        data["_file"] = path.name
        entries.append(data)
    return entries


def key_of(entry: dict) -> str:
    return entry.get("de", {}).get("key") or entry.get("en", {}).get("key", "")


def clean(entry: dict) -> dict:
    """Remove internal loader metadata before output."""
    return {k: v for k, v in entry.items() if not k.startswith("_")}


def consolidate(version: str | None = None) -> dict:
    categories = load_collection("hp-categories")
    dimensions = load_collection("hp-dimensions")
    observations = load_collection("hp-observations")
    data_providers = load_collection("data-provider")

    # Index by key for relation lookups
    cat_index = {key_of(c): c for c in categories}
    dim_index = {key_of(d): d for d in dimensions}

    # Group dimensions by category key
    dims_by_category: dict[str, list] = {k: [] for k in cat_index}
    orphaned_dimensions = []
    for dim in dimensions:
        cat_key = dim.get("de", {}).get("category") or dim.get("en", {}).get("category")
        if cat_key in dims_by_category:
            dims_by_category[cat_key].append(dim)
        else:
            orphaned_dimensions.append(clean(dim))
            print(f"  WARNING: dimension '{key_of(dim)}' references unknown category '{cat_key}'")

    # Group observations by dimension key
    obs_by_dimension: dict[str, list] = {k: [] for k in dim_index}
    orphaned_observations = []
    for obs in observations:
        dim_key = obs.get("de", {}).get("dimension") or obs.get("en", {}).get("dimension")
        if dim_key in obs_by_dimension:
            obs_by_dimension[dim_key].append(obs)
        else:
            orphaned_observations.append(clean(obs))
            print(f"  WARNING: observation '{key_of(obs)}' references unknown dimension '{dim_key}'")

    # Build the tree
    built_categories = []
    for cat in categories:
        cat_key = key_of(cat)
        built_dims = []
        for dim in dims_by_category.get(cat_key, []):
            dim_key = key_of(dim)
            built_dim = {
                **clean(dim),
                "observations": [clean(o) for o in obs_by_dimension.get(dim_key, [])],
            }
            built_dims.append(built_dim)

        built_cat = {
            **clean(cat),
            "dimensions": built_dims,
        }
        built_categories.append(built_cat)

    result = {
        "version": version or "unreleased",
        "generated": datetime.now(timezone.utc).isoformat(),
        "categories": built_categories,
        "data_providers": [clean(p) for p in data_providers],
    }

    if orphaned_dimensions:
        result["orphaned_dimensions"] = orphaned_dimensions
    if orphaned_observations:
        result["orphaned_observations"] = orphaned_observations

    return result


def main():
    parser = argparse.ArgumentParser(description="Consolidate Health Profile JSONs")
    parser.add_argument("--out", default=str(ROOT / "health-profile.json"), help="Output file path")
    parser.add_argument("--indent", type=int, default=2, help="JSON indent (default: 2)")
    parser.add_argument("--version", default=None, help="Semantic version to embed, e.g. 1.2.0")
    args = parser.parse_args()

    print("Consolidating Health Profile data...")
    result = consolidate(version=args.version)

    out_path = Path(args.out)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=args.indent), encoding="utf-8")

    cat_count = len(result["categories"])
    dim_count = sum(len(c["dimensions"]) for c in result["categories"])
    obs_count = sum(len(d["observations"]) for c in result["categories"] for d in c["dimensions"])
    prov_count = len(result["data_providers"])

    print(f"  Version: {result['version']}")
    print(f"  {cat_count} categories, {dim_count} dimensions, {obs_count} observations, {prov_count} data providers")
    print(f"  Written to: {out_path}")


if __name__ == "__main__":
    main()
