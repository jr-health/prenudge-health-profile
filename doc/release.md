# Release-Workflow

Releases basieren auf **Git Tags** (`v1.2.0`) auf GitHub. Das `health-profile.json` enthält immer ein `version`-Feld, damit Konsumenten die Version ohne Git-Kenntnisse erkennen können.

## SemVer-Definition

| | Änderungstyp | Beispiele |
|---|---|---|
| **MAJOR** | Breaking — Konsumenten müssen angepasst werden | Key umbenannt; Feld entfernt; Feldtyp geändert (String → Liste); Collection-Struktur grundlegend geändert |
| **MINOR** | Additiv — bestehende Konsumenten funktionieren weiter | Neue Category / Dimension / Observation; neues optionales Feld; neue Collection aktiviert |
| **PATCH** | Inhaltliche Korrektur — kein Struktureinfluss | Tipp-/Inhaltsfehler; falscher FHIR-Code; Link aktualisiert; leeres Pflichtfeld befüllt; kaputte Referenz repariert |

---

## Release-Schritte

Der komplette Release-Prozess läuft automatisiert über `.github/workflows/release.yml` —
validieren, konsolidieren, Markdown-/AsciiDoc-Reports erzeugen, daraus den Word-Export bauen,
und alles als GitHub Release veröffentlichen. Manuell bleibt nur die Versionsentscheidung
selbst und das Auslösen des Workflows.

### 1. Version bestimmen

Siehe "Versionsnummer bestimmen" unten — welche SemVer-Kategorie (MAJOR/MINOR/PATCH) passt zu
den Änderungen seit dem letzten Release?

### 2. Release auslösen

Zwei gleichwertige Wege:

**a) Per Tag** (Standardweg):
```
git tag v1.2.0
git push origin v1.2.0
```

**b) Manuell über die GitHub-UI** (z. B. zum Testen, ohne lokal einen Tag zu setzen):
Unter **Actions → Release → Run workflow** die Versionsnummer (ohne führendes `v`) eingeben.
Erzeugt/aktualisiert denselben Tag und dasselbe Release wie Variante (a).

### 3. Was der Workflow automatisch macht

| Schritt | Was passiert |
|---|---|
| Validate | `validate.py --strict` — bricht bei kaputten Referenzen ab |
| Consolidate | `consolidate.py --version <Version>` → `health-profile.json` |
| Markdown | `render_doc.py` → `health-profile-v<Version>.{de,en}.md` |
| AsciiDoc | `render_adoc.py` → `health-profile-v<Version>.{de,en}.adoc` |
| Word-Export | `asciidoctor` (AsciiDoc → DocBook) → `pandoc` (mit `render/templates/PräNUDGE Berichtsvorlage.docx` als Stilvorlage) → `health-profile-v<Version>.{de,en}.docx` |
| Release | GitHub Release erstellen/aktualisieren mit Assets: `health-profile.json`, beide `.md`, beide `.docx` |

Der Workflow committet dabei **nichts** zurück ins Repo (siehe `doc/github-actions-plan.md`,
Design-Entscheidung 4) — die Release-Assets liegen ausschließlich am GitHub Release selbst,
nicht im Quellcode-Baum.

### 4. GitHub Page aktualisiert sich automatisch

Ein erfolgreicher `release.yml`-Lauf löst automatisch `pages.yml` aus (siehe
Design-Entscheidung 5) — Sunburst, Browse-Ansicht und die Download-Links auf der Landing Page
zeigen danach den neuen Release-Stand. Kein manueller Schritt nötig.

Die Anzeige "Version … · Generated: …" auf der Landing Page liest dafür `health-profile.json`
nicht aus dem `main`-Checkout (der Stand dort bleibt wegen Schritt 3 unverändert), sondern lädt
sie per `gh release download` direkt vom soeben erstellten Release-Asset — nur dort steht die
zur Version passende `generated`-Zeitangabe.

---

## Versionsnummer bestimmen

Die aktuelle Version ist im `health-profile.json` unter `"version"` ablesbar oder per Tag-Liste:

```
git tag --sort=-version:refname | head -5
```

Nächste Version ableiten:
- Gab es einen Key-Rename oder Feld-Entfernung? → **MAJOR** erhöhen, MINOR und PATCH auf 0
- Nur neue Einträge oder Felder hinzugekommen? → **MINOR** erhöhen, PATCH auf 0
- Nur Inhaltskorrekturen? → **PATCH** erhöhen
