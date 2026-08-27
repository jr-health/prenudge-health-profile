# PreNUDGE Health Profile Catalogue

A headless, CMS-driven catalogue of health **observations**, **indicator dimensions**,
**categories**, and **measurement instruments** used by the PreNUDGE platform.

The catalogue is maintained as versioned JSON data — there is no application build step.
Content is edited through [Sveltia CMS](https://github.com/sveltia/sveltia-cms) (a Decap CMS
fork) and consolidated into a single hierarchical profile plus human-readable reports by a
small Python pipeline.

> **Note:** This GitHub repository is a mirror of the previous Gitea repository
> <https://health.joanneum.at/git/PreNudge/prenudge-health-profile.git>.

## Data Model

```
Categories (hp-categories/)
  └── Indicator Dimensions (hp-dimensions/)
        └── Observations (hp-observations/)
              └── Measurement Instruments (embedded list per observation)

Data / App Providers (data-provider/)
```

- Each entity is one JSON file; the filename is derived from its `key`.
- Every file is bilingual (`single_file` i18n) with `de` (default) and `en` locales as
  top-level keys.
- Relations reference their parent by `key` (e.g. an observation points to a `dimension`
  and a `category`).
- Technical IDs and keys are **kebab-case** (e.g. `physical-activity`, `body-weight`).

## Repository Layout

| Path | Contents |
|------|----------|
| `admin/config.yml` | Central CMS schema — collections, fields, relations, i18n |
| `admin/index.html` | Loads Sveltia CMS + custom widget |
| `admin/widgets/` | Custom `id_tech_auto` widget (registered but not currently used — see note) |
| `hp-categories/`, `hp-dimensions/`, `hp-observations/` | Source content (one JSON per entry) |
| `data-provider/` | Data / app providers in the PreNUDGE ecosystem |
| `media/` | Images (logos, icons) referenced by content and the CMS media library |
| `scripts/` | Python pipeline (`validate.py`, `consolidate.py`, `render_doc.py`, `render_adoc.py`, `render_html.py`) + local update helper |
| `render/` | `sunburst.html` and `browse.{de,en}.html` visualizations, plus Jinja2 templates and the Word style reference in `render/templates/` |
| `health-profile.json` | Generated consolidated profile (do not edit by hand) |
| `health-profile.{de,en}.md` | Generated German / English Markdown reports (always the latest state — versioned copies live as GitHub Release assets, not in the repo) |
| `.github/workflows/` | GitHub Actions CI — see "Automation" below |
| `doc/` | Setup, release, and transform notes |

> **Note on the custom widget:** `admin/widgets/slug-from-title.js` registers an
> `id_tech_auto` widget (auto-generates a kebab-case ID from the English title). It is loaded
> by `admin/index.html` but is **not referenced by any active collection** — the current
> collections use plain `key` string fields. It only applies to the commented-out
> `subject-areas` / `observation-sources` collections in `config.yml`.

## Editing Content

Content is edited via the CMS UI at `/admin/`. The catalogue editor is hosted both on a
separate, manually maintained instance and, as of this pipeline, on GitHub Pages
[https://jr-health.github.io/prenudge-health-profile/](https://jr-health.github.io/prenudge-health-profile/) (deployed via
`.github/workflows/pages.yml`) — the manually maintained instance remains authoritative;
GitHub Pages is an additional, automatically deployed mirror.

- **Production backend:** GitHub repo `jr-health/prenudge-health-profile` (branch `main`),
  authenticated through the `sveltia-cms-auth` Cloudflare Worker.
- **Local editing:** with `local_backend: true` in `admin/config.yml`, Sveltia CMS writes
  directly to the local JSON files instead of committing remotely.

### Running the CMS locally

```bash
# 1. Start the local backend proxy (writes to local files)
npx netlify-cms-proxy-server

# 2. Serve the repo root
npx serve .

# 3. Open the editor
#    http://localhost:<port>/admin/
```

## Build Pipeline

The scripts turn the distributed JSON files into the consolidated profile and reports:

```bash
python scripts/validate.py       # check referential integrity + i18n key consistency
python scripts/consolidate.py    # build health-profile.json (categories → … → observations)
python scripts/render_doc.py     # render versioned de/en Markdown reports (needs jinja2)
python scripts/render_html.py    # render the de/en browse view (render/browse.{de,en}.html)
python scripts/render_adoc.py    # render versioned de/en AsciiDoc (feeds the Word export)
```

On Windows, `scripts/update-local.ps1` runs validation, consolidation, Markdown rendering, and
the browse view regeneration in one step:

```powershell
.\scripts\update-local.ps1            # or: .\scripts\update-local.ps1 -Version 1.2.0
```

## Automation (GitHub Actions)

| Workflow | Trigger | Does |
|---|---|---|
| `update-profile.yml` | Push to `main` touching content, `scripts/`, or `render/templates/` | Validates, consolidates, renders Markdown + the browse view, commits the generated files back |
| `release.yml` | Push of a `v*.*.*` tag, or manual dispatch with a version | Validates, consolidates, renders Markdown + AsciiDoc, converts AsciiDoc → DocBook → Word (`asciidoctor` + `pandoc`), then injects the real cover page/footers into the `.docx` (`scripts/inject_cover_page.py`, needs `python-docx`), publishes everything as a GitHub Release. Does not commit anything back to the repo. |
| `pages.yml` | After a successful `Release` run, or manual dispatch | Builds the GitHub Pages landing page (sunburst, browse view, CMS editor, download links to the latest release's Word exports) |

See `doc/release.md` for the full release/versioning process and `doc/github-actions-plan.md`
for the design rationale.
