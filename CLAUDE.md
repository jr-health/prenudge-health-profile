# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The PreNUDGE Health Profile Catalogue is a headless CMS-driven catalogue of health observations, indicators, and measurements. It uses [Sveltia CMS](https://github.com/sveltia/sveltia-cms) (a Decap CMS fork) with a GitHub backend. There is no build step — the project is static JSON data plus a CMS configuration, rendered to HTML/Markdown/AsciiDoc/Word by Python scripts in CI.

## Running the CMS Locally

The CMS UI runs by serving the repo root over HTTP and navigating to `/admin/`. With `local_backend: true` set in `admin/config.yml`, Sveltia CMS writes directly to local JSON files instead of committing through the git backend.

Unlike Decap CMS, Sveltia CMS does **not** use `netlify-cms-proxy-server`/`decap-server` for this — it uses the browser's File System Access API instead (Chromium-based browsers only: Chrome, Edge, Brave). Serve the repo root (e.g., `npx serve .` or VS Code Live Server), open `http://localhost:<port>/admin/`, click "Work with local repository", and pick the repo's root folder in the native directory picker.

For headless/scripted testing (no browser dialog available), temporarily swap the `backend:` block for `{ name: test-repo }` — Sveltia's built-in in-memory mock backend — then revert it; don't leave it committed.

The production CMS backend is GitHub: repo `jr-health/prenudge-health-profile`, branch `main`, authenticated through the OAuth proxy in `sveltia-cms-auth/` (a Cloudflare Worker, deployed at `https://sveltia-cms-auth.jr-health.workers.dev` and referenced as `base_url` in `admin/config.yml`). The project previously ran on a Gitea instance — if you see stale references to `health.joanneum.at`, they predate the GitHub migration.

## Commands

There is no `package.json`/`requirements.txt`/`Makefile` — Python dependencies are installed ad hoc (`pip install jinja2 python-docx`). Common scripts, run from the repo root:

- `python scripts/validate.py --strict` — checks reference integrity (dangling `key`/`id_tech` relations, duplicate keys); run before consolidating
- `python scripts/consolidate.py --version <ver> [--scope combined|minimalset|extended]` — merges all entity JSON into `health-profile.json`
- `python scripts/render_doc.py --version <ver> --latest` — renders the Markdown reports (`health-profile.{de,en}.md`)
- `python scripts/render_adoc.py --generated <date>` — renders the AsciiDoc reports (input to the Word export)
- `python scripts/render_html.py` — renders `render/browse.{de,en}.html` and `render/sunburst.{de,en}.html`
- `python scripts/render_index.py` — renders the Explore/Downloads landing pages
- `.\scripts\update-local.ps1 [-Version <ver>]` — runs validate → consolidate → render_doc → render_html locally, mirroring `update-profile.yml`
- `scripts/preview-pages.sh [port]` — builds a local mirror of the live GitHub Pages site (pinned to the latest GitHub Release, like `pages.yml`) into `_site_test/`

## Architecture

### Release & CI/CD Pipeline

Three GitHub Actions workflows drive the generated artifacts; see `doc/release.md` (release process, in German) and `doc/github-actions-plan.md` (design decisions) for full detail:

- **`release.yml`** — manually triggered via Actions → Release → Run workflow (not by pushing a tag directly — see `doc/release.md` for why). Validates, consolidates, renders Markdown/AsciiDoc/Word reports (three `dataset-scope` variants × two languages = six `.docx` files via `asciidoctor` → `pandoc` → `scripts/inject_cover_page.py`), commits `health-profile.json` and the browse/sunburst HTML back to `main`, tags that commit, and publishes a GitHub Release with all artifacts as assets. The versioned report files themselves are **not** committed to the repo — only attached to the Release.
- **`update-profile.yml`** — runs on pushes touching `hp-categories/`, `hp-dimensions/`, `hp-observations/`, `data-provider/`, `scripts/`, or `render/templates/`, and also after `release.yml` completes. Re-validates, re-consolidates, re-renders, and commits the regenerated files back to `main`.
- **`pages.yml`** — deploys GitHub Pages from the commit tagged by the latest Release (via `git archive`), copying `render/`, `admin/`, `media/` by explicit filename (see "Front-end scripts" below).

### Data Model Hierarchy

```
Subject Areas (hp-subject-areas/ — currently commented out in config)
  └── Categories (hp-categories/)
        └── Indicator Dimensions (hp-dimensions/)
              └── Observations (hp-observations/)
                    └── Measurement Instruments (embedded list in observation JSON)
Data/App Providers (data-provider/)
```

All entities are stored as individual JSON files. The filename is derived from the `key` or `id_tech` field of each entry.

Note: the `dimension` field on observations is now optional (`required: false` in `admin/config.yml`) and dimensions are no longer surfaced on the website, in reports, or in the sunburst chart — the hierarchy above still reflects the data model, but dimensions are being phased out as a *display* layer.

### i18n Structure

Every JSON file uses `single_file` i18n with `de` (default) and `en` locales. Top-level keys in each file are the locale codes:

```json
{
  "de": { "title": "Ernährung", "description": "..." },
  "en": { "title": "Nutrition", "description": "..." }
}
```

Fields marked `i18n: duplicate` share the same value across locales (e.g., `key`, `color`). Fields marked `i18n: translate` require separate values per locale.

### CMS Configuration

`admin/config.yml` is the central schema file. It defines:
- **Active collections**: `categories`, `dimensions`, `observations`, `data-provider`
- **Commented-out collections**: `subject-areas`, `observation-sources` (kept for reference)
- Slug patterns, field definitions, relation widgets, and i18n settings

To change what fields appear in the CMS editor or how data is structured, edit `admin/config.yml`.

### Adding/Changing Fields

When adding, renaming, or removing a field in `admin/config.yml` (especially in the `observations` collection), check whether it needs to be reflected in `render/templates/`:
- `health-profile.{de,en}.{md,adoc}.j2` — render individual field values (e.g. `population`, `citizen-info`); source for the Markdown report (`render_doc.py`) and the AsciiDoc → Word report (`render_adoc.py`)
- `browse.{de,en}.html.j2` — currently only render category/dimension-level summary data, not observation detail fields
- `_browse_table.{de,en}.html.j2` — the shared table partial; emits per-row `data-*` attributes that `browse.js` filters on
- `_base.{de,en}.html.j2` — shared layout extended by `index`, `downloads`, `browse`, and `sunburst` templates; holds the branding `<img>` tags and the corporate color CSS (see Key Conventions)
- `index.{de,en}.html.j2`, `downloads.{de,en}.html.j2`, `sunburst.{de,en}.html.j2` — landing/Explore, Downloads, and standalone sunburst pages, rendered by `render_index.py` / `render_html.py`
- `PräNUDGE Berichtsvorlage.docx` — the Word style template `pandoc` applies when converting the AsciiDoc/DocBook report to `.docx`

A new field is not automatically picked up by the templates — it must be added explicitly (e.g. `{% if o.get('field-name') %}...{% endif %}`).

### Data Sets (`dataset-scope`)

Categories, dimensions, and observations each carry a `dataset-scope` select
(`Minimalset` / `Extension`), defined in `admin/config.yml` right after the key field.

The filter rule lives in **two places that must stay in sync**:
- `scripts/consolidate.py` → `filter_tree()` (drives `--scope` and the `.docx` exports)
- `render/scope.js` → `filterProfile()` (drives the sunburst and table on the website)

Rule: *every level is selected by its own `dataset-scope`, and is additionally kept when any
descendant was selected.* A leaf-only rule is wrong here — most observations were added after
their dimensions, so a `Minimalset` dimension whose observations are all extensions would
vanish from the minimal set entirely.

### Front-end scripts are classic scripts, not modules

`render/scope.js`, `sunburst.js`, and `browse.js` are loaded as plain `<script>` tags and
**share one global scope**. `scope.js` and `browse.js` are wrapped in IIFEs; `sunburst.js`
still exposes dozens of top-level globals (`renderSunburst`, `buildHierarchy`, …).

A generic top-level name in a later script silently overwrites an earlier one. This already
happened once: a `function render()` in `browse.js` replaced the sunburst's `render()`, and
because the sunburst calls it asynchronously (after `d3.json` resolves) the only symptom was
a chart that never drew — no error. Wrap new scripts in an IIFE.

Load order matters: `scope.js` must come before `sunburst.js` and `browse.js`, which both call
`HPScope`. `pages.yml` copies these files **by name** — a new `render/*.js` must be added
there or it will be missing on GitHub Pages while working fine locally.

Local script tags carry `?v={{ version | urlencode }}`. The filenames never change, so without
it GitHub Pages serves a cached copy of the old JS against newly rendered HTML after a release
— which looks exactly like a broken feature. Add the query string to any new local `<script>`;
leave CDN tags (d3) alone, they are already version-pinned in the URL.

### Custom Widget

`admin/widgets/slug-from-title.js` registers the `id_tech_auto` widget, which auto-generates a kebab-case technical ID from the English title field. It is loaded via a `<script>` tag in `admin/index.html` and used as `widget: id_tech_auto` on the `key` field in the `categories`, `dimensions`, and `observations` collections in `admin/config.yml`. It only auto-fills while the field is untouched — once an editor types into `key` manually, auto-updates stop.

### CMS Runtime

`admin/index.html` loads Sveltia CMS from unpkg (`@sveltia/cms`) and the custom widget. The commented-out line shows the fallback to standard Decap CMS if needed.

## Key Conventions

- **Technical IDs / keys**: kebab-case (e.g., `physical-activity`, `body-weight`)
- **Slug source**: categories, dimensions, and observations all use `{{key}}`
- **Relations**: `dimension` references `category` via `key`; `observation` references `dimension` and `category` via `key`/`id_tech`
- **Measurement instruments**: embedded as a list within each observation (not a separate collection)
- **FHIR codes**: stored in `terminology-codes` list with `system`, `code`, and `display` fields
- **Status fields**: `pn-fhir-ig-status` and `vis-status` use `["published", "planned", "open", "amendment needed"]`
- **Bilingual branding**: German pages use the wording "PräNUDGE" and `media/PräNUDGE_Logo.png`; English pages use "PreNUDGE" and `media/PreNUDGE_Logo.png` (no umlaut). The `<img>` tags live in `render/templates/_base.{de,en}.html.j2`, the shared layout that `browse`, `index`, `downloads`, and `sunburst` templates all extend.
- **Corporate color palette** (2026-08-13): `#004E64` (Midnight green) is the established accent used across existing pages (headings, active nav state, links) — keep using it for that role. Full palette, for when more colors are needed (e.g. category swatches, charts):
  - Primary (logo): `#00A256` Pigment green, `#9BC6A0` Celadon
  - Secondary: `#004E64` Midnight green, `#007BA7` Deep Cerulean, `#6E4E69` Random Violet, `#E0D3DE` Pale purple, `#F2C57C` Sunset, `#E28913` Golden Bell, `#F8E4BF` Givry, `#C5DDC8` Random Mint
