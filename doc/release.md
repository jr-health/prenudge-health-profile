# Release-Workflow

Releases basieren auf **Git Tags** (`v1.2.0`) auf GitHub. Das `health-profile.json` enthält immer ein `version`-Feld, damit Konsumenten die Version ohne Git-Kenntnisse erkennen können.

## SemVer-Definition

| | Änderungstyp | Beispiele |
|---|---|---|
| **MAJOR** | Breaking — Konsumenten müssen angepasst werden | Key umbenannt; Feld entfernt; Feldtyp geändert (String → Liste); Collection-Struktur grundlegend geändert |
| **MINOR** | Additiv — bestehende Konsumenten funktionieren weiter | Neue Category / Dimension / Observation; neues optionales Feld (z. B. `dataset-scope`); neue Collection aktiviert |
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

**Nur noch über die GitHub-UI** (seit 2026-09-22, siehe `doc/github-actions-plan.md`,
Design-Entscheidung 7): Unter **Actions → Release → Run workflow** die Versionsnummer (ohne
führendes `v`) eingeben.

Ein direkter Tag-Push (`git tag v1.2.0 && git push origin v1.2.0`) wird **nicht mehr**
unterstützt — der Tag würde dabei schon vor dem Workflow-Start auf dem aktuellen
`main`-Commit feststehen, sodass die in Schritt 3 unten beschriebene Regenerierung nicht mehr
rechtzeitig vor dem Tag landen kann (siehe Design-Entscheidung 7). `workflow_dispatch` erzeugt
denselben Tag und dasselbe Release, aber in der richtigen Reihenfolge.

### 3. Was der Workflow automatisch macht

| Schritt | Was passiert |
|---|---|
| Validate | `validate.py --strict` — bricht bei kaputten Referenzen ab |
| Consolidate | `consolidate.py --version <Version>` → `health-profile.json` |
| Browse/Sunburst | `render_html.py` → `render/browse.{de,en}.html`, `render/sunburst.{de,en}.html` |
| Commit | `health-profile.json` + die vier Browse/Sunburst-Dateien werden auf `main` committet — **bevor** der Tag unten erstellt wird (Design-Entscheidung 7) |
| Markdown | `render_doc.py` → `health-profile-v<Version>-<Datum>.{de,en}.md` |
| AsciiDoc | `render_adoc.py` → `health-profile-v<Version>-<Datum>[-<Datensatz>].{de,en}.adoc` |
| Word-Export | `asciidoctor` (AsciiDoc → DocBook) → `pandoc` (mit `render/templates/PräNUDGE Berichtsvorlage.docx` als Stilvorlage, `--toc` für ein echtes Word-Inhaltsverzeichnis) → `health-profile-v<Version>-<Datum>[-<Datensatz>].{de,en}.docx` |
| Cover/Footer | `scripts/inject_cover_page.py` (braucht `python-docx`) ersetzt Pandocs generischen Titel-Absatz durch das echte Deckblatt aus der Stilvorlage (Titel/Version/Datum, PreNUDGE-Consortium-Link) und befüllt Version/Datum in beiden Fußzeilen (Deckblatt- und Standard-Fußzeile) |
| Release | GitHub Release erstellen mit Assets: `health-profile.json`, beide `.md`, **sechs** `.docx` — getaggt auf den frisch erstellten Commit von oben, nicht auf den Stand vor dem Lauf |

#### Word-Export pro Datensatz

Der Word-Export läuft seit 2026-08-28 dreimal — einmal je Datensatz (siehe `dataset-scope`
im README) — mal zwei Sprachen, also **sechs `.docx`**:

| Datensatz | `consolidate.py --scope` | Dateiname |
|---|---|---|
| Gesamt | `combined` (Default, ungefiltert) | `health-profile-v<Version>-<Datum>.{de,en}.docx` |
| Minimalset | `minimalset` | `health-profile-v<Version>-<Datum>-minimalset.{de,en}.docx` |
| Erweitert | `extended` | `health-profile-v<Version>-<Datum>-extended.{de,en}.docx` |

Der Gesamt-Export behält bewusst den **unveränderten Dateinamen ohne Suffix**, damit
bestehende Download-Links und die Downloads-Seite weiter funktionieren. Das Deckblatt der
beiden gefilterten Exporte trägt den Datensatz im Titel (z. B. „… — Katalog (Minimalset)").

Die versionierten `.md`/`.adoc`/`.docx`-Reportdateien selbst committet der Workflow **nicht**
zurück ins Repo — sie liegen ausschließlich am GitHub Release selbst, nicht im Quellcode-Baum.
`health-profile.json` und die vier Browse/Sunburst-Dateien dagegen schon (siehe Schritt 3 oben
und Design-Entscheidung 7) — und zwar **vor** der Tag-Erstellung, damit der Tag einen Commit
mit zur eigenen Version passenden Ansichten trifft.

Das im Word-Export gezeigte Datum ("Generiert: …") ist bewusst das Datum des **releaseten
Commits** (`git log -1 --date=short`), nicht der Build-Zeitpunkt — ein späterer erneuter
`workflow_dispatch`-Lauf auf demselben Tag ändert das Datum im Bericht also nicht. Dasselbe
Datum wird an `render_doc.py --generated`, `render_adoc.py --generated` und
`inject_cover_page.py --generated` durchgereicht, damit `.md`/`.adoc`/`.docx` konsistent
bleiben — und steht seit 2026-08-27 auch im jeweiligen Dateinamen
(`health-profile-v<Version>-<Datum>.{de,en}.{md,adoc,docx}`), damit mehrere
heruntergeladene Versionen sich nicht gegenseitig überschreiben.

### 4. GitHub Page aktualisiert sich automatisch

Ein erfolgreicher `release.yml`-Lauf löst automatisch `pages.yml` aus (siehe
Design-Entscheidung 5) — Sunburst, Browse-Ansicht und die Download-Links auf der Landing Page
zeigen danach den neuen Release-Stand. Kein manueller Schritt nötig.

Die Anzeige "Version … · Generated: …" auf der Explore-Seite liest `health-profile.json` per
`gh release download` direkt vom soeben erstellten Release-Asset, nicht aus dem `main`-Checkout
— unabhängig davon, ob `main` inzwischen weitergelaufen ist. Sunburst/Browse zeigen seit
Design-Entscheidung 7 dieselbe Version, weil `pages.yml` sie von dem Commit kopiert, auf den der
Release-Tag zeigt — und `release.yml` sorgt jetzt dafür, dass genau dieser Commit bereits die
zur Version passenden Ansichten enthält (statt wie vorher vom nächsten, erst später folgenden
`update-profile.yml`-Lauf).

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
