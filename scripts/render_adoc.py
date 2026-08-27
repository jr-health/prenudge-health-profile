"""
Renders health-profile.json into versioned AsciiDoc documents via Jinja2 templates.
Intermediate step towards the Word export (see doc/github-actions-plan.md, Phase 4):
Jinja2 -> .adoc -> asciidoctor -> docbook -> pandoc -> .docx

Templates:  render/templates/health-profile.de.adoc.j2
            render/templates/health-profile.en.adoc.j2
Output:     health-profile-v<version>.de.adoc
            health-profile-v<version>.en.adoc

Usage:
    python scripts/render_adoc.py
    python scripts/render_adoc.py --version 1.2.0
    python scripts/render_adoc.py --version 1.2.0 --generated 2026-08-13
    python scripts/render_adoc.py --src path/to/health-profile.json
    python scripts/render_adoc.py --out-dir doc/output

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
    """Convert a heading to a slug usable both as a Markdown anchor and an AsciiDoc [[id]]."""
    text = str(text).lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "-", text.strip())
    return text


def main():
    parser = argparse.ArgumentParser(description="Render health-profile.json to AsciiDoc")
    parser.add_argument("--src", default=str(ROOT / "health-profile.json"), help="Input JSON file")
    parser.add_argument("--out-dir", default=str(ROOT), help="Output directory")
    parser.add_argument("--version", default=None, help="Override version (default: taken from JSON)")
    parser.add_argument("--generated", default=None, help="Override generation date, e.g. 2026-08-13 (default: taken from JSON)")
    args = parser.parse_args()

    src = Path(args.src)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    profile = json.loads(src.read_text(encoding="utf-8"))
    if args.version:
        profile["version"] = args.version
    if args.generated:
        profile["generated"] = args.generated

    version = profile.get("version", "unreleased")

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["anchor"] = anchor

    for locale in ("de", "en"):
        template = env.get_template(f"health-profile.{locale}.adoc.j2")
        content = template.render(profile=profile)
        out_path = out_dir / f"health-profile-v{version}.{locale}.adoc"
        out_path.write_text(content, encoding="utf-8")
        print(f"  Written: {out_path}")


if __name__ == "__main__":
    main()
