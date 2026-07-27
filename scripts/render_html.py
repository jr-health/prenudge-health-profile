"""
Renders health-profile.json into a static, tabular browse view via Jinja2 templates.

Templates:  render/templates/browse.de.html.j2
            render/templates/browse.en.html.j2
Output:     render/browse.de.html
            render/browse.en.html

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


def main():
    parser = argparse.ArgumentParser(description="Render health-profile.json to a browse HTML table")
    parser.add_argument("--src", default=str(ROOT / "health-profile.json"), help="Input JSON file")
    parser.add_argument("--out-dir", default=str(ROOT / "render"), help="Output directory")
    args = parser.parse_args()

    src = Path(args.src)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    profile = json.loads(src.read_text(encoding="utf-8"))

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    for locale in ("de", "en"):
        template = env.get_template(f"browse.{locale}.html.j2")
        content = template.render(profile=profile)
        out_path = out_dir / f"browse.{locale}.html"
        out_path.write_text(content, encoding="utf-8")
        print(f"  Written: {out_path}")


if __name__ == "__main__":
    main()
