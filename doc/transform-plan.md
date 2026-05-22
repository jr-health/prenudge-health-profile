# Transform Plan: Health Profile Metadata Exports

Die im CMS erfassten Metadaten liegen auf viele JSON-Files verteilt in `hp-categories/`, `hp-dimensions/`, `hp-observations/` und `data-provider/`. Dieser Plan beschreibt eine zweistufige Pipeline, um diese Daten in verschiedene Ausgabeformate zu überführen.

## Architektur: Zweistufige Pipeline

```
hp-categories/*.json
hp-dimensions/*.json      →  [1] consolidate  →  health-profile.json  →  [2] render-*
hp-observations/*.json
data-provider/*.json
```

---

## Stufe 1 — Konsolidierung

**Skript**: `scripts/consolidate.py`  
**Output**: `health-profile.json` (ins Repo eingecheckt)

Das Skript liest alle Verzeichnisse, löst die Relations auf (`dimension.category` → vollständiges Category-Objekt) und schreibt eine eingebettete Baumstruktur:

```json
{
  "categories": [{
    "key": "physical-activity",
    "de": { "title": "..." },
    "en": { "title": "..." },
    "dimensions": [{
      "key": "everyday-activity",
      "observations": [{ "..." : "..." }]
    }]
  }]
}
```

Keine externen Abhängigkeiten — nur Python-Stdlib (`json`, `glob`, `pathlib`).

Das `health-profile.json` dient gleichzeitig als **Export 1 (Single-JSON)** und als gemeinsame Datenquelle für alle weiteren Renderer.

---

## Stufe 2 — Renderer

| Export | Skript / Tool | Abhängigkeiten | Aufwand |
|---|---|---|---|
| Single JSON | *(= Output von Stufe 1)* | — | — |
| Word / PDF | `scripts/render_doc.py` → Jinja2 → `.md` → `pandoc` | `jinja2`, `pandoc` | mittel |
| Statisches HTML | `scripts/render_html.py` → Jinja2 → `.html` | `jinja2` | gering |
| Interaktiver Sunburst | `render/sunburst.html` mit D3.js | D3.js (CDN) | mittel |
| SVG-Sunburst | `scripts/render_svg.py` | `svgwrite` o. `cairosvg` | hoch |

---

## Designentscheidung: Wann wird konsolidiert?

**Option A — Manuell (empfohlen als Start)**
```
python scripts/consolidate.py
```
Das `health-profile.json` wird nach CMS-Änderungen manuell neu generiert und ins Repo eingecheckt. Einfach, keine Infrastruktur nötig.

**Option B — Git Hook / Gitea CI (späterer Ausbau)**
Eine Gitea-Action oder ein Pre-Commit-Hook triggert `consolidate.py` automatisch. Das `health-profile.json` ist damit immer aktuell, ohne manuellen Schritt.

**Option C — Zur Laufzeit im Browser** (nicht empfohlen)
Jeder Renderer liest die Roh-JSONs selbst. Für den Sunburst bedeutet das viele parallele Fetch-Requests; Relations müssten im Browser aufgelöst werden.

**Empfehlung**: Mit Option A starten. Das `health-profile.json` ins Repo einchecken, damit Downstream-Konsumenten (Sunburst-App, Dokumentation) es direkt per HTTP laden können.

---

## Umsetzungsreihenfolge

1. **`consolidate.py`** — Fundament, alle anderen hängen davon ab
2. **Interaktiver D3-Sunburst** — größter Mehrwert, direkt sichtbar
3. **Statisches HTML-Browse** — gut für interne Dokumentation
4. **Word/PDF via pandoc** — für formelle Berichte und Deliverables
5. **SVG-Sunburst** — nur wenn Print/Export-Format konkret benötigt wird

---

## Versionierung

Das `health-profile.json` wird mit Semantic Versioning versioniert. Die Version wird beim Generieren per `--version`-Argument übergeben und ist im JSON-Output unter `"version"` sichtbar.

Releases werden als **Git Tags** (`v1.2.0`) auf Gitea angelegt. Gitea erzeugt daraus automatisch einen Download-Link für das JSON-Artefakt. Der Release-Prozess ist in `doc/release.md` beschrieben.

### SemVer-Definition für Health Profile Metadata

| | Änderungstyp | Beispiele |
|---|---|---|
| **MAJOR** | Breaking — Konsumenten (Scripts, Apps) müssen angepasst werden | Key umbenannt; Feld entfernt; Feldtyp geändert (String → Liste); Collection-Struktur grundlegend geändert |
| **MINOR** | Additiv — bestehende Konsumenten funktionieren weiter | Neue Category / Dimension / Observation; neues optionales Feld; neue Collection aktiviert |
| **PATCH** | Inhaltliche Korrektur — kein Struktureinfluss | Tipp-/Inhaltsfehler; falscher FHIR-Code; Link aktualisiert; leeres Pflichtfeld befüllt; kaputte Referenz repariert |

---

## Verzeichnisstruktur (geplant)

```
prenudge-health-profile/
├── scripts/
│   ├── consolidate.py
│   ├── validate.py
│   ├── render_doc.py
│   ├── render_html.py
│   └── render_svg.py
├── render/
│   ├── sunburst.html
│   └── templates/
│       ├── doc.md.j2
│       └── browse.html.j2
├── health-profile.json       ← generiert, aber eingecheckt
└── doc/
    ├── transform-plan.md     ← dieses Dokument
    └── release.md            ← Release-Workflow
```
