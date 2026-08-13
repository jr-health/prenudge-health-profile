# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The PreNUDGE Health Profile Catalogue is a headless CMS-driven catalogue of health observations, indicators, and measurements. It uses [Sveltia CMS](https://github.com/sveltia/sveltia-cms) (a Decap CMS fork) with a Gitea backend. There is no build step — the project is static JSON data plus a CMS configuration.

## Running the CMS Locally

The CMS UI runs by serving the repo root over HTTP and navigating to `/admin/`. With `local_backend: true` set in `admin/config.yml`, Sveltia CMS writes directly to local JSON files instead of committing through Gitea.

To start a local backend server, Decap/Sveltia CMS requires the `netlify-cms-proxy-server` (or compatible):
```
npx netlify-cms-proxy-server
```
Then serve the repo (e.g., `npx serve .` or VS Code Live Server) and open `http://localhost:<port>/admin/`.

The production CMS backend is the Gitea instance at `https://health.joanneum.at/git`, repo `PreNudge/prenudge-health-profile`, branch `main`.

## Architecture

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
- `health-profile.{de,en}.{md,adoc}.j2` — render individual field values (e.g. `population`, `citizen-info`)
- `browse.{de,en}.html.j2` — currently only render category/dimension-level summary data, not observation detail fields

A new field is not automatically picked up by the templates — it must be added explicitly (e.g. `{% if o.get('field-name') %}...{% endif %}`).

### Custom Widget

`admin/widgets/slug-from-title.js` registers the `id_tech_auto` widget, which auto-generates a kebab-case technical ID from the English title field. It is loaded via a `<script>` tag in `admin/index.html`.

### CMS Runtime

`admin/index.html` loads Sveltia CMS from unpkg (`@sveltia/cms`) and the custom widget. The commented-out line shows the fallback to standard Decap CMS if needed.

## Key Conventions

- **Technical IDs / keys**: kebab-case (e.g., `physical-activity`, `body-weight`)
- **Slug source**: categories and dimensions use `{{key}}`; observations use `{{id_tech}}`
- **Relations**: `dimension` references `category` via `key`; `observation` references `dimension` and `category` via `key`/`id_tech`
- **Measurement instruments**: embedded as a list within each observation (not a separate collection)
- **FHIR codes**: stored in `terminology-codes` list with `system`, `code`, and `display` fields
- **Status fields**: `pn-fhir-ig-status` and `vis-status` use `["published", "planned", "open", "amendment needed"]`
