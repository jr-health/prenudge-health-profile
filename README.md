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
| `scripts/` | Python pipeline + local update helper |
| `render/` | `sunburst.html` visualization and Markdown Jinja2 templates |
| `health-profile.json` | Generated consolidated profile (do not edit by hand) |
| `health-profile-v*.md` | Generated German / English reports |
| `.gitea/workflows/` | Legacy Gitea Actions CI (does not run on GitHub — see note below) |
| `doc/` | Setup, release, and transform notes |

> **Note on the custom widget:** `admin/widgets/slug-from-title.js` registers an
> `id_tech_auto` widget (auto-generates a kebab-case ID from the English title). It is loaded
> by `admin/index.html` but is **not referenced by any active collection** — the current
> collections use plain `key` string fields. It only applies to the commented-out
> `subject-areas` / `observation-sources` collections in `config.yml`.

## Editing Content

Content is edited via the CMS UI at `/admin/`. The catalogue editor is hosted both on a
separate, manually maintained instance and, as of this pipeline, on GitHub Pages (deployed
via `.github/workflows/pages.yml`) — the manually maintained instance remains authoritative;
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
```

On Windows, `scripts/update-local.ps1` runs validation and regeneration in one step:

```powershell
.\scripts\update-local.ps1            # or: .\scripts\update-local.ps1 -Version 1.2.0
```

> **⚠️ CI setup is still open on GitHub.** The existing workflow
> (`.gitea/workflows/update-profile.yml`) targets **Gitea Actions** and does not run on
> GitHub. A GitHub Actions workflow (e.g. `.github/workflows/`) still needs to be set up to
> regenerate these files automatically on push to `main`. Until then, run the pipeline
> locally (see above) and commit the generated files. See `doc/ci-setup.md` for the original
> Gitea runner setup and `doc/release.md` for the release flow.
