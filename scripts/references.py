"""
Builds the Literaturverzeichnis / References list for the reports.

Source data: the `reference` field on every observation's "Further information/links"
(`verified-health-links`) and on every measurement instrument's "Source/reference"
(`sources`) entry. The editor types the finished reference line, e.g.

    IQWIG. 2023a. Alkohol [Online]. Available: [URL] [Accessed 11.06.2026].
    FONDS GESUNDES ÖSTERREICH 2020. Österreichische Bewegungsempfehlungen. Wien: FGÖ.

`[URL]` is replaced by the URL of the entry itself (`url` on links, `system` on sources),
so URLs are not typed twice. An entry without a finished line is not part of the list; each field is exactly one
entry. It may still contain the unused CMS template line, which is ignored.

The same publication is usually referenced from several observations, so identical
lines collapse into one. The list is sorted by the text itself (it starts with author,
then year, so undated "n.d." entries follow the numbered years of the same author).

Used by render_adoc.py and render_doc.py as the Jinja global `references(profile, locale)`
and the filters `ref_adoc` / `ref_md`. validate.py reuses `iter_reference_items`.
"""

import re
import unicodedata

LOCALES = ("de", "en")
URL_TOKEN = "[URL]"
# A URL inside the text; trailing sentence punctuation is not part of it.
URL_RE = re.compile(r"https?://[^\s<>\]]+")
TRAILING = ".,;:)"


def iter_reference_items(obs_locale_data):
    """Yield (item, url_field) for every link and source of one observation locale."""
    for link in obs_locale_data.get("verified-health-links") or []:
        yield link, "url"
    for instr in obs_locale_data.get("measurement-instrument") or []:
        for src in instr.get("sources") or []:
            yield src, "system"


# Placeholders of the CMS template. A line that still contains one is unfinished and
# ignored, so an editor can leave the unused template line (Web or Book) in place.
PLACEHOLDER_RE = re.compile(r"\[(?:Author|Year|Title|Place|Publisher)\]|DD\.MM\.YYYY")


def resolve(item, url_field):
    """The reference of an item: ONE entry per field ('' if there is none yet). Lines that
    still contain template placeholders are dropped; the remaining lines are joined, so a
    long reference may wrap over several lines. [URL] is filled in."""
    if not isinstance(item, dict):
        return ""
    url = str(item.get(url_field) or "").strip()
    url = url if url.lower().startswith("http") else ""
    kept = [" ".join(l.split()) for l in str(item.get("reference") or "").splitlines()]
    kept = [l for l in kept if l and not PLACEHOLDER_RE.search(l)]
    return " ".join(kept).replace(URL_TOKEN, url).strip()


def _sort_key(text):
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def references(profile, locale="de"):
    """Sorted, de-duplicated reference lines for a (possibly scope-filtered) profile."""
    order = [locale] + [l for l in LOCALES if l != locale]
    found = set()
    for cat in profile.get("categories", []):
        for dim in cat.get("dimensions", []):
            for obs in dim.get("observations", []):
                for loc in order:
                    for item, url_field in iter_reference_items(obs.get(loc) or {}):
                        text = resolve(item, url_field)
                        if text:
                            found.add(text)
    return sorted(found, key=_sort_key)


def _segments(text):
    """Split into (is_url, part) pieces; punctuation after a URL stays text."""
    pos = 0
    for m in URL_RE.finditer(text):
        url = m.group(0)
        stripped = url.rstrip(TRAILING)
        yield False, text[pos:m.start()]
        yield True, stripped
        pos = m.start() + len(stripped)
    yield False, text[pos:]


def ref_adoc(text):
    """AsciiDoc paragraph text. Text and link label go through pass:c[] (special
    characters only), so '_', '*' or '&' in titles and URLs are not read as markup."""
    def lit(t):
        return "pass:c[" + t.replace("]", "\\]") + "]"
    out = ""
    for is_url, part in _segments(text):
        if not part:
            continue
        out += f"link:{part}[{lit(part)}]" if is_url else lit(part)
    return out


def ref_md(text):
    return "".join(f"<{p}>" if is_url else p for is_url, p in _segments(text) if p)
