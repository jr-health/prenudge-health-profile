"""
Renders the GitHub Pages landing page (Explore) and the Downloads page via Jinja2
templates.

Unlike render_html.py/render_doc.py, version/generated/release-base are not read from
health-profile.json in the checkout — pages.yml resolves them from the actual GitHub
Release at build time (see Design-Entscheidung 5 in doc/github-actions-plan.md) and
passes them in as CLI args. health-profile.json itself IS read (via --profile) to embed
the sunburst/browse partial on the Explore page (Phase C, interactive-catalogue-plan.md) —
pages.yml points --profile at the freshly downloaded release asset in _site/, not the
possibly-stale repo checkout.

Both pages share one sidebar layout via Jinja2 template inheritance
(render/templates/_base.{de,en}.html.j2).

Templates:  render/templates/_base.{de,en}.html.j2        (shared sidebar/shell)
            render/templates/index.{de,en}.html.j2          (Explore)
            render/templates/downloads.{de,en}.html.j2       (Downloads)
            render/templates/_browse_table.{de,en}.html.j2 (embedded on Explore, shared
                                                             with browse.{de,en}.html.j2)
Output:     index.html          (English Explore page, served at the Pages root)
            index.de.html
            downloads.en.html
            downloads.de.html

Usage:
    python scripts/render_index.py --version 0.1.2 --generated 2026-08-13 \
        --release-base https://github.com/jr-health/prenudge-health-profile/releases/latest/download \
        --profile health-profile.json --out-dir _site

Requires:
    pip install jinja2
"""

import argparse
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = ROOT / "render" / "templates"

# One entry per rendered page. "out" for the English Explore page is unsuffixed
# because it's served at the Pages root; every other page follows the {name}.{locale}.html
# convention already used by the browse pages.
PAGES = [
    {"name": "index", "locale": "en", "active": "explore", "out": "index.html"},
    {"name": "index", "locale": "de", "active": "explore", "out": "index.de.html"},
    {"name": "downloads", "locale": "en", "active": "downloads", "out": "downloads.en.html"},
    {"name": "downloads", "locale": "de", "active": "downloads", "out": "downloads.de.html"},
]


def nav_href(name, locale):
    return next(p["out"] for p in PAGES if p["name"] == name and p["locale"] == locale)


def main():
    parser = argparse.ArgumentParser(description="Render the GitHub Pages landing/downloads pages")
    parser.add_argument("--version", required=True, help="Release version, e.g. 0.1.2")
    parser.add_argument("--generated", required=True, help="Generated date, e.g. 2026-08-13")
    parser.add_argument("--release-base", required=True, help="Base URL for release download assets")
    parser.add_argument("--profile", default=str(ROOT / "health-profile.json"),
                         help="health-profile.json to embed the browse table on the Explore page")
    parser.add_argument("--out-dir", default=str(ROOT / "_site"), help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    for page in PAGES:
        template = env.get_template(f"{page['name']}.{page['locale']}.html.j2")
        content = template.render(
            version=args.version,
            generated=args.generated,
            release_base=args.release_base,
            profile=profile,
            active=page["active"],
            base_path="",
            href_en=nav_href(page["name"], "en"),
            href_de=nav_href(page["name"], "de"),
            nav_explore_href=nav_href("index", page["locale"]),
            nav_downloads_href=nav_href("downloads", page["locale"]),
            nav_sunburst_href=f"render/sunburst.{page['locale']}.html",
            nav_table_href=f"render/browse.{page['locale']}.html",
        )
        out_path = out_dir / page["out"]
        out_path.write_text(content, encoding="utf-8")
        print(f"  Written: {out_path}")


if __name__ == "__main__":
    main()
