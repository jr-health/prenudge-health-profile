"""
Restyles embedded Markdown headings after the pandoc conversion.

render_adoc.py's md_adoc filter can't turn a Markdown ATX heading ("## Foo")
from a richtext CMS field into a real AsciiDoc heading (`==`) - that would
register as an actual document section and corrupt the report's chapter
nesting (see the comment above MD_HEADING_RE in render_adoc.py). Instead it
rewrites it into a plain bold paragraph wrapped in a pair of private-use-area
sentinel characters (U+E000/U+E001) that survive the asciidoctor -> docbook ->
pandoc conversion as an ordinary Word paragraph. This script finds that
sentinel and turns the paragraph into something that reads as a heading -
bigger font, accent color - with no Heading style/number attached, since it
isn't one.

Runs after the asciidoctor -> docbook -> pandoc conversion (see release.yml,
Phase 4 in doc/github-actions-plan.md). Order relative to inject_cover_page.py
doesn't matter - they touch disjoint content.

Usage:
    python scripts/style_inline_headings.py health-profile-v1.2.0-2026-08-26.de.docx

Requires:
    pip install python-docx
"""

import argparse
from pathlib import Path

import docx
from docx.shared import Pt, RGBColor

START, END = "", ""
FONT_SIZE = Pt(14)
FONT_COLOR = RGBColor(0x00, 0x4E, 0x64)  # Midnight green - the established accent color


def iter_paragraphs(container):
    """Yield every paragraph in a document or table cell, including inside
    nested tables - the sentinel can land in a measurement-instrument table
    cell (specific-questions, scoring-algorithm, norms.specific-norm)."""
    for paragraph in container.paragraphs:
        yield paragraph
    for table in getattr(container, "tables", []):
        for row in table.rows:
            for cell in row.cells:
                yield from iter_paragraphs(cell)


def style_inline_headings(docx_path: Path) -> int:
    document = docx.Document(str(docx_path))
    count = 0

    for paragraph in iter_paragraphs(document):
        text = paragraph.text
        if not (text.startswith(START) and text.endswith(END)):
            continue

        runs = paragraph.runs
        if not runs:
            continue

        if len(runs) == 1:
            runs[0].text = runs[0].text[len(START):-len(END)]
        else:
            runs[0].text = runs[0].text[len(START):]
            runs[-1].text = runs[-1].text[:-len(END)]

        for run in runs:
            run.font.size = FONT_SIZE
            run.font.color.rgb = FONT_COLOR
        count += 1

    document.save(str(docx_path))
    return count


def main():
    parser = argparse.ArgumentParser(description="Restyle embedded Markdown headings in a rendered health profile .docx")
    parser.add_argument("docx_path", help="Path to the pandoc-generated .docx (edited in place)")
    args = parser.parse_args()

    count = style_inline_headings(Path(args.docx_path))
    print(f"  Restyled {count} inline heading(s): {args.docx_path}")


if __name__ == "__main__":
    main()
