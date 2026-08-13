"""
Renders the GitHub Pages landing page via Jinja2 templates.

Unlike render_html.py/render_doc.py, this does not read health-profile.json from the
checkout — pages.yml resolves version/generated/release-base from the actual GitHub
Release at build time (see Design-Entscheidung 5 in doc/github-actions-plan.md) and
passes them in as CLI args.

Templates:  render/templates/index.de.html.j2
            render/templates/index.en.html.j2
Output:     index.html    (English, served at the Pages root)
            index.de.html

Usage:
    python scripts/render_index.py --version 0.1.2 --generated 2026-08-13 \
        --release-base https://github.com/jr-health/prenudge-health-profile/releases/latest/download \
        --out-dir _site

Requires:
    pip install jinja2
"""

import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = ROOT / "render" / "templates"


def main():
    parser = argparse.ArgumentParser(description="Render the GitHub Pages landing page")
    parser.add_argument("--version", required=True, help="Release version, e.g. 0.1.2")
    parser.add_argument("--generated", required=True, help="Generated date, e.g. 2026-08-13")
    parser.add_argument("--release-base", required=True, help="Base URL for release download assets")
    parser.add_argument("--out-dir", default=str(ROOT / "_site"), help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    context = {
        "version": args.version,
        "generated": args.generated,
        "release_base": args.release_base,
    }

    for locale, filename in (("en", "index.html"), ("de", "index.de.html")):
        template = env.get_template(f"index.{locale}.html.j2")
        content = template.render(**context)
        out_path = out_dir / filename
        out_path.write_text(content, encoding="utf-8")
        print(f"  Written: {out_path}")


if __name__ == "__main__":
    main()
