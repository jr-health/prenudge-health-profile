"""
Renders health-profile.json into versioned AsciiDoc documents via Jinja2 templates.
Intermediate step towards the Word export (see doc/github-actions-plan.md, Phase 4):
Jinja2 -> .adoc -> asciidoctor -> docbook -> pandoc -> .docx

Templates:  render/templates/health-profile.de.adoc.j2
            render/templates/health-profile.en.adoc.j2
Output:     health-profile-v<version>-<generated><suffix>.de.adoc
            health-profile-v<version>-<generated><suffix>.en.adoc

--suffix tags the filename with the data set the input JSON was consolidated
for (see scripts/consolidate.py --scope). The combined export passes no suffix,
so its filename stays exactly as it was before scopes existed.

Usage:
    python scripts/render_adoc.py
    python scripts/render_adoc.py --version 1.2.0
    python scripts/render_adoc.py --version 1.2.0 --generated 2026-08-13
    python scripts/render_adoc.py --src path/to/health-profile.json
    python scripts/render_adoc.py --suffix -minimalset
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

# Sveltia's richtext widget writes standard Markdown, so its raw output can't be
# dropped as-is into the .adoc templates -- two constructs need rewriting before
# asciidoctor sees them:
#
# Images: ![alt text](/media/foo.png "title"). AsciiDoc doesn't understand that
# syntax at all -- asciidoctor passes it through as literal text -- so it has to
# become an AsciiDoc inline image macro. The public_folder (/media/...) is
# root-relative for the website; render_adoc.py writes its output next to the
# media/ folder (repo root), so stripping the leading slash gives a path
# asciidoctor/pandoc can resolve from their working directory.
#
# ATX headings: "# Foo" / "## Foo". Unlike Markdown, a line starting with #
# in AsciiDoc is not inert text -- Asciidoctor accepts it as a Markdown-style
# section heading (# ~ level 0, ## ~ level 1, ...), which is real document
# structure. Dropped into the middle of an observation's already-nested
# section (category/dimension/observation/instrument), it closes out all of
# those sections early and starts a new top-level one, silently swapping
# everything that follows into the wrong branch of the document tree and
# corrupting the table of contents (asciidoctor only logs an ERROR, it
# doesn't fail the build). So instead of an AsciiDoc heading, it becomes a
# plain bold paragraph wrapped in a pair of private-use-area sentinel
# characters the CMS itself would never produce; style_inline_headings.py
# finds that sentinel after the docx is built and turns it into a bigger,
# accent-colored run with no section/numbering attached.
# GFM pipe tables: a header row, a "|---|---|" separator row, then data rows.
# AsciiDoc tables use the same "|" cell separator on the wire, but nothing
# else about the syntax matches (no separator row, a different table-open/
# close delimiter) -- left alone, a Markdown table just becomes a run of
# broken-looking paragraphs full of stray pipes and dashes. Rewritten into a
# real |=== table instead. When the richtext field lands inside a cell of
# the report's own measurement-instrument table (nested=True), |=== would
# collide with the outer table's own cell parser -- a literal "|" inside a
# cell's text is still a cell separator to AsciiDoc, nesting or not -- so the
# nested form uses AsciiDoc's alternate "!===" / "!" delimiter instead, and
# the target cell has to be an AsciiDoc ("a|") cell to parse block content
# (a table) at all; plain cells only ever get a single inline paragraph.
MD_IMAGE_RE = re.compile(r'!\[([^\]]*)\]\(\s*(\S+?)(?:\s+"[^"]*")?\s*\)')
MD_HEADING_RE = re.compile(r"^#{1,6}[ \t]+(.+?)[ \t]*$", re.MULTILINE)
INLINE_HEADING_START = ""
INLINE_HEADING_END = ""


MD_TABLE_SEPARATOR_CELL_RE = re.compile(r"^:?-+:?$")


def _split_table_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def _is_table_separator_row(line):
    cells = _split_table_row(line)
    return bool(cells) and all(MD_TABLE_SEPARATOR_CELL_RE.match(cell) for cell in cells)


def _looks_like_table_row(line):
    """A line with 2+ pipe-delimited cells, leading and trailing "|". Real CMS
    content doesn't always include a GFM header/separator row ("|---|---|") --
    editors just type consecutive "| a | b | c |" lines -- so this alone (not
    the separator row) is what actually marks a run of lines as a table."""
    stripped = line.strip()
    if len(stripped) < 3 or not (stripped.startswith("|") and stripped.endswith("|")):
        return False
    return len(_split_table_row(stripped)) >= 2


def _convert_md_tables(text, nested):
    """Rewrite Markdown pipe tables into an AsciiDoc table block. Handles both
    a GFM table (header row + "|---|---|" separator) and a header-less run of
    plain "| a | b | c |" rows -- if a separator row follows the first row,
    that row becomes the table header; otherwise every row is a body row."""
    open_close = "!===" if nested else "|==="
    cell = "!" if nested else "|"
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if _looks_like_table_row(line):
            has_header = i + 1 < len(lines) and _is_table_separator_row(lines[i + 1])
            header = None
            body = []
            if has_header:
                header = _split_table_row(line)
                i += 2
            else:
                body.append(_split_table_row(line))
                i += 1
            while i < len(lines) and _looks_like_table_row(lines[i]):
                body.append(_split_table_row(lines[i]))
                i += 1
            out.append(open_close)
            if header:
                out.append(f"{cell} " + f" {cell} ".join(header))
                out.append("")
            for row in body:
                out.append(f"{cell} " + f" {cell} ".join(row))
            out.append(open_close)
        else:
            out.append(line)
            i += 1
    return "\n".join(out)


def md_richtext_to_adoc(text: str, nested: bool = False) -> str:
    """Rewrite Markdown images, ATX headings and pipe tables into AsciiDoc-safe equivalents."""
    if not text:
        return text

    text = _convert_md_tables(text, nested)

    def heading_repl(match: "re.Match[str]") -> str:
        return f"**{INLINE_HEADING_START}{match.group(1)}{INLINE_HEADING_END}**"

    text = MD_HEADING_RE.sub(heading_repl, text)

    def image_repl(match: "re.Match[str]") -> str:
        alt, url = match.group(1), match.group(2)
        url = url.lstrip("/")
        alt = alt.replace("[", "(").replace("]", ")")
        if not alt:
            return f"image:{url}[]"
        # A bare comma in the positional attribute would be parsed as the
        # start of the width/height attributes, so quote whenever one is
        # present (quoting unconditionally is also safe, but noisier to read).
        if "," in alt:
            alt = '"' + alt.replace('"', "'") + '"'
        return f"image:{url}[{alt}]"

    return MD_IMAGE_RE.sub(image_repl, text)


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
    parser.add_argument("--suffix", default="", help="Filename suffix after the date, e.g. -minimalset (default: none)")
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
    generated = profile.get("generated", "")[:10] or "undated"

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["anchor"] = anchor
    env.filters["md_adoc"] = md_richtext_to_adoc

    for locale in ("de", "en"):
        template = env.get_template(f"health-profile.{locale}.adoc.j2")
        content = template.render(profile=profile)
        out_path = out_dir / f"health-profile-v{version}-{generated}{args.suffix}.{locale}.adoc"
        out_path.write_text(content, encoding="utf-8")
        print(f"  Written: {out_path}")


if __name__ == "__main__":
    main()
