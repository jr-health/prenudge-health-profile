"""
Renders health-profile.json into Markdown documents via Jinja2 templates.

Templates:  render/templates/health-profile.de.md.j2
            render/templates/health-profile.en.md.j2
Output:     health-profile-v<version>.de.md / .en.md (default)
            health-profile.de.md / .en.md (with --latest)

--latest writes the unversioned filename instead - used for the copy committed to the
repo by update-profile.yml, so the git tree doesn't accumulate one file pair per release
forever (see doc/export-report-plan.md). release.yml keeps using the versioned filename
(without --latest) since that's what's attached to the GitHub Release as a per-version asset.

Usage:
    python scripts/render_doc.py
    python scripts/render_doc.py --version 1.2.0
    python scripts/render_doc.py --version 1.2.0 --latest
    python scripts/render_doc.py --src path/to/health-profile.json
    python scripts/render_doc.py --out-dir doc/output

Requires:
    pip install jinja2
"""

import re
import json
import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = ROOT / "render" / "templates"


def anchor(text: str) -> str:
    """Convert a heading to a Markdown anchor slug (compatible with GitHub/pandoc)."""
    text = str(text).lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "-", text.strip())
    return text


def main():
    parser = argparse.ArgumentParser(description="Render health-profile.json to Markdown")
    parser.add_argument("--src", default=str(ROOT / "health-profile.json"), help="Input JSON file")
    parser.add_argument("--out-dir", default=str(ROOT), help="Output directory")
    parser.add_argument("--version", default=None, help="Override version (default: taken from JSON)")
    parser.add_argument("--latest", action="store_true",
                         help="Write health-profile.<locale>.md instead of health-profile-v<version>.<locale>.md")
    args = parser.parse_args()

    src = Path(args.src)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    profile = json.loads(src.read_text(encoding="utf-8"))
    if args.version:
        profile["version"] = args.version

    version = profile.get("version", "unreleased")

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["anchor"] = anchor

    for locale in ("de", "en"):
        template = env.get_template(f"health-profile.{locale}.md.j2")
        content = template.render(profile=profile)
        filename = f"health-profile.{locale}.md" if args.latest else f"health-profile-v{version}.{locale}.md"
        out_path = out_dir / filename
        out_path.write_text(content, encoding="utf-8")
        print(f"  Written: {out_path}")


if __name__ == "__main__":
    main()
