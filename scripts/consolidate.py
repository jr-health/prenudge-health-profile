"""
Consolidates the distributed Health Profile JSON files into a single
hierarchical health-profile.json at the project root.

Structure: categories -> dimensions -> observations
Relations are resolved and embedded; orphaned entries are collected separately.

--scope restricts the output to one data set, based on the `dataset-scope`
field maintained in the CMS (see admin/config.yml). See SCOPES / scope_of()
below for the filter rule.

Usage:
    python scripts/consolidate.py
    python scripts/consolidate.py --version 1.2.0
    python scripts/consolidate.py --scope minimalset
    python scripts/consolidate.py --indent 2
    python scripts/consolidate.py --out path/to/output.json
"""

import json
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent

# --scope values. "combined" is the full catalogue (no filtering at all), so
# minimalset/extended are always strict subsets of it and the combined export
# stays identical to what was produced before scopes existed.
COMBINED = "combined"
SCOPES = (COMBINED, "minimalset", "extended")

# Maps the CMS select's option strings (admin/config.yml, field `dataset-scope`)
# onto the --scope values used here and in the filenames.
SCOPE_VALUES = {"Minimalset": "minimalset", "Extension": "extended"}


def git_commit_sha() -> str | None:
    """Return the current HEAD commit SHA, i.e. the source commit this profile was built from."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        return None


def git_activity() -> dict:
    """Return deduplicated list of (date, author) entries since the last git tag."""
    try:
        last_tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL,
        ).strip()
        rev_range = f"{last_tag}..HEAD"
    except subprocess.CalledProcessError:
        last_tag = None
        rev_range = "HEAD"

    try:
        raw = subprocess.check_output(
            ["git", "log", rev_range, "--format=%ad|%an", "--date=short"],
            cwd=ROOT, text=True,
        ).strip()
    except subprocess.CalledProcessError:
        return {"since": last_tag, "entries": []}

    seen: set[tuple] = set()
    entries = []
    for line in raw.splitlines():
        if "|" not in line:
            continue
        date, author = line.split("|", 1)
        date, author = date.strip(), author.strip()
        if author == "github-actions[bot]":
            continue
        key = (date, author)
        if key not in seen:
            seen.add(key)
            entries.append({"date": date, "author": author})

    return {"since": last_tag, "entries": entries}


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


def scope_of(entry: dict) -> str | None:
    """
    The entry's own --scope value, or None if it carries no (recognised)
    `dataset-scope`. `dataset-scope` is an i18n: duplicate field, so de and en
    always hold the same value and either may be read.
    """
    raw = entry.get("de", {}).get("dataset-scope") or entry.get("en", {}).get("dataset-scope")
    return SCOPE_VALUES.get(raw)


def in_scope(entry: dict, scope: str) -> bool:
    return scope == COMBINED or scope_of(entry) == scope


def filter_tree(categories: list[dict], scope: str) -> list[dict]:
    """
    Restrict an already-built category tree to one scope.

    Every level is selected by its own `dataset-scope`, and an entry is kept as
    well when any of its descendants was selected - so a category or dimension
    belongs to the set it is flagged for even while all of its observations
    still sit in the other set, and a selected observation is never orphaned by
    an ancestor flagged the other way.

    Selecting ancestors by their descendants alone is not enough: most
    observations were added after the categories and dimensions they hang
    under, so a leaf-only rule drops a Minimalset dimension the moment its
    observations happen to all be extensions.
    """
    if scope == COMBINED:
        return categories

    kept_categories = []
    for cat in categories:
        kept_dims = []
        for dim in cat["dimensions"]:
            kept_obs = [o for o in dim["observations"] if in_scope(o, scope)]
            if kept_obs or in_scope(dim, scope):
                kept_dims.append({**dim, "observations": kept_obs})

        if kept_dims or in_scope(cat, scope):
            kept_categories.append({**cat, "dimensions": kept_dims})

    return kept_categories


def consolidate(version: str | None = None, scope: str = COMBINED) -> dict:
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
        "scope": scope,
        "commit": git_commit_sha(),
        "activity": git_activity(),
        "categories": filter_tree(built_categories, scope),
        "data_providers": [clean(p) for p in data_providers],
    }

    # Orphans are filtered on their own value - they have no resolved ancestor
    # to be kept by, and (for dimensions) no resolved children to be kept for.
    orphaned_dimensions = [d for d in orphaned_dimensions if in_scope(d, scope)]
    orphaned_observations = [o for o in orphaned_observations if in_scope(o, scope)]

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
    parser.add_argument("--scope", default=COMBINED, choices=SCOPES,
                        help=f"Data set to emit (default: {COMBINED} = the full catalogue)")
    args = parser.parse_args()

    print("Consolidating Health Profile data...")
    result = consolidate(version=args.version, scope=args.scope)

    out_path = Path(args.out)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=args.indent), encoding="utf-8")

    cat_count = len(result["categories"])
    dim_count = sum(len(c["dimensions"]) for c in result["categories"])
    obs_count = sum(len(d["observations"]) for c in result["categories"] for d in c["dimensions"])
    prov_count = len(result["data_providers"])

    print(f"  Version: {result['version']}")
    print(f"  Scope:   {result['scope']}")
    print(f"  {cat_count} categories, {dim_count} dimensions, {obs_count} observations, {prov_count} data providers")
    print(f"  Written to: {out_path}")


if __name__ == "__main__":
    main()
