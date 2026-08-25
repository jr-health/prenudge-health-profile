"""
Renders health-profile.json into the Browse table and Sunburst pages via Jinja2 templates.
Both extend the shared sidebar shell (render/templates/_base.{de,en}.html.j2) — same as
the Explore/Downloads pages rendered by render_index.py, but one directory deeper (render/),
so base_path/nav hrefs are computed relative to render/ instead of the site root.

Templates:  render/templates/browse.{de,en}.html.j2
            render/templates/sunburst.{de,en}.html.j2
Output:     render/browse.de.html
            render/browse.en.html
            render/sunburst.de.html
            render/sunburst.en.html

Usage:
    python scripts/render_html.py
    python scripts/render_html.py --src path/to/health-profile.json
    python scripts/render_html.py --out-dir render

Requires:
    pip install jinja2
"""

import json
import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = ROOT / "render" / "templates"

PAGES = [
    {"name": "browse", "active": "table"},
    {"name": "sunburst", "active": "sunburst"},
]


def main():
    parser = argparse.ArgumentParser(description="Render health-profile.json to the Browse/Sunburst pages")
    parser.add_argument("--src", default=str(ROOT / "health-profile.json"), help="Input JSON file")
    parser.add_argument("--out-dir", default=str(ROOT / "render"), help="Output directory")
    args = parser.parse_args()

    src = Path(args.src)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    profile = json.loads(src.read_text(encoding="utf-8"))
    version = profile.get("version", "")
    generated = (profile.get("generated") or "")[:10]

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    for page in PAGES:
        for locale in ("de", "en"):
            template = env.get_template(f"{page['name']}.{locale}.html.j2")
            content = template.render(
                profile=profile,
                version=version,
                generated=generated,
                base_path="../",
                active=page["active"],
                nav_explore_href="../index.html",
                nav_downloads_href=f"../downloads.{locale}.html",
                nav_sunburst_href=f"sunburst.{locale}.html",
                nav_table_href=f"browse.{locale}.html",
                href_en=f"{page['name']}.en.html",
                href_de=f"{page['name']}.de.html",
            )
            out_path = out_dir / f"{page['name']}.{locale}.html"
            out_path.write_text(content, encoding="utf-8")
            print(f"  Written: {out_path}")


if __name__ == "__main__":
    main()
