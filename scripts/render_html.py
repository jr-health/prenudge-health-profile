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

import html
import json
import re
import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = ROOT / "render" / "templates"

MD_ESCAPE_RE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!])")
MD_LINK_RE = re.compile(r'\[([^\]]+)\]\(\s*(https?://[^)\s]+)(?:\s+"[^"]*")?\s*\)')
MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
# word-bounded so blanks like "nämlich: _____" and snake_case stay literal
MD_ITALIC_RE = re.compile(r"(?<![\w*_])[_*](?![\s_*])(.+?)(?<![\s_*])[_*](?![\w*_])")
MD_STASH_RE = re.compile(r"\x00(\d+)\x00")


def md_html(text: str) -> Markup:
    """Render the small Markdown subset the CMS richtext fields use (bold, italic,
    links, backslash escapes, line/paragraph breaks) to HTML for table cells.

    Deliberately not a full Markdown parser - CI only installs jinja2, and these
    fields are short free-text notes. Input is HTML-escaped first."""
    if not text or not str(text).strip():
        return Markup("")
    escapes = []

    def stash(match):
        escapes.append(match.group(1))
        return f"\x00{len(escapes) - 1}\x00"

    text = str(text).strip().replace("\r\n", "\n")
    text = MD_ESCAPE_RE.sub(stash, text)
    text = html.escape(text, quote=False)
    text = MD_LINK_RE.sub(
        lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>', text
    )
    text = MD_BOLD_RE.sub(r"<strong>\1</strong>", text)
    text = MD_ITALIC_RE.sub(r"<em>\1</em>", text)
    text = MD_STASH_RE.sub(lambda m: html.escape(escapes[int(m.group(1))]), text)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return Markup("".join("<p>" + p.replace("\n", "<br>") + "</p>" for p in paragraphs))


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
    env.filters["md_html"] = md_html

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
