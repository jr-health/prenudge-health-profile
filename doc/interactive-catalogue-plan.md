# Interaktiver Katalog (Landing Page + Browse-Ansicht) — Design-Plan

Dieses Dokument führt `doc/browse-view-plan.md` und `doc/landing-page-plan.md` zusammen
(2026-08-13). Grund: Die ursprüngliche Trennung (Landing Page = Linkliste, Browse-Ansicht =
eigene Tabellen-Seite) passt nicht mehr zur Vision — die Landing Page **selbst** soll den
Sunburst interaktiv einbetten und darüber die tabellarische Detailansicht steuern. Beide
Themen hängen damit an derselben Architekturentscheidung und werden hier gemeinsam
weitergeführt. Dient der Nachvollziehbarkeit — Umsetzung erfolgt erst, sobald hier Einigkeit
besteht.

## Vision (Stand 2026-08-13)

- `https://jr-health.github.io/prenudge-health-profile/` wird die zentrale interaktive
  Einstiegsseite: Der Sunburst ist direkt eingebettet (nicht mehr nur verlinkt).
- Auswahl im Sunburst verändert die tabellarische Detailansicht darunter/daneben — mehr
  Details zu den ausgewählten Gesundheitsindikatoren, statt einer separat verlinkten
  Browse-Seite.
- Link zum Metadaten-CMS-Editor bleibt bestehen.
- Ein Download-Bereich, der künftig verschiedene Versionen der Gesundheitsprofil-Metadaten
  anbietet, z. B. zielgruppenspezifisch für Healthcare Professionals vs. Bürger:innen.
- Eine Übersicht über ältere Releases.
- Navigation seitlich (Sidebar) oder oben (Top-Nav).

## Ausgangslage

- Kein Build-Step (siehe `CLAUDE.md`) — nur statisches JSON, Python-Skripte ohne Bundler,
  `render/sunburst.html` als Vanilla-JS + D3 (per `<script>`-Tag im Browser geladen).
- Browse-Tabelle bereits als Stufe 1 (MVP) umgesetzt: `scripts/render_html.py` rendert
  `render/templates/browse.{de,en}.html.j2` (Jinja2, analog `render_doc.py`) →
  `render/browse.{de,en}.html`, eingebunden in `update-profile.yml`/`pages.yml`. Jede
  Tabellenzeile hat bereits `data-*`-Attribute je Spalte (Category, Dimension, Observation,
  Source-Type, FHIR-IG-Status, Sunburst-Status) — vorbereitet für Filterung ohne
  Neu-Parsen der Daten.
- `_site/index.html` wird aktuell **nicht** aus einer eigenen Datei gebaut, sondern per
  `cat > _site/index.html <<EOF ... EOF` inline im Build-Schritt von
  `.github/workflows/pages.yml` erzeugt — pragmatisch für den Start, aber ohne
  Syntax-Highlighting/lokale Vorschau, HTML/CSS/Bash-Variablen gemischt.
- Aktueller Landing-Page-Inhalt: Logo + Titel + Version/Generiert-Datum, "Under
  construction"-Disclaimer, Linklisten (Sunburst/Browse DE+EN/CMS-Editor;
  `.docx`-Downloadlinks DE+EN via `releases/latest/download/...`), Footer-Link zum
  PreNUDGE-Konsortium. Nur Englisch (`<html lang="en">`), kein visuelles Layout-Konzept
  (reine `<ul>`-Aufzählung).
- Branding (bereits erledigt): Logo `PräNUDGE_Logo.png`, Farbe `#004E64`, Schrift Verdana.

## Design-Entscheidungen (bereits getroffen, aus der Browse-Ansicht übernommen)

| # | Frage | Entscheidung | Begründung |
|---|---|---|---|
| 1 | Server-seitig (Jinja2) oder client-seitig gerendert? | **Server-seitig** für die Tabellendaten (statisches HTML, Zeilen bereits beim Build vorhanden) | Konsistent mit `render_doc.py`/`consolidate.py`; funktioniert auch ohne JavaScript; Filterung/Sunburst-Kopplung ergänzt reine DOM-Manipulation über bereits vorhandene Zeilen, kein doppeltes Datenladen. |
| 2 | Zwei Stufen für die Browse-Tabelle? | **Ja** — Stufe 1: statische Tabelle (erledigt). Stufe 2: Interaktivität (Suche/Filter, jetzt auch Sunburst-Kopplung) obendrauf. | Reduziert Risiko, liefert schnell sichtbaren Zwischenstand; Stufe 2 unabhängig erweiterbar. |
| 3 | Zweisprachigkeit (DE/EN) der Landing Page? (2026-08-13) | **Ja, DE/EN wie der Rest** | Konsistent mit Sunburst/Browse/Reports; nötig, da die Landing Page jetzt selbst interaktive Inhalte (nicht nur Links) zeigt. |
| 4 | Release-Historie: reiner Link auf GitHub-Releases oder eigene Seite? (2026-08-13) | **Eigene Übersicht**, erreichbar über die Navbar (Platzierung Sidebar/Top-Nav noch offen, siehe Offene Frage 2) | Nutzer:in möchte die Historie als eigenen Navigationspunkt statt als externen Link — mehr Kontrolle über Darstellung/Branding, wird bei Umsetzung mit einem Render-Schritt verbunden sein (analog Browse-Tabelle). |
| 5 | React/anderes Framework für die Sunburst↔Tabellen-Interaktivität, oder bei Vanilla JS bleiben? (2026-08-13) | **Vanilla JS beibehalten** | Die Interaktion (Klick filtert/hebt Zeilen hervor, ggf. zeigt zusätzliche Detailinhalte aus `health-profile.json` an) braucht keinen komplexen State und lässt sich ohne Bundler lösen; ein Framework-Wechsel würde die bewusste No-Build-Entscheidung (`CLAUDE.md`) kippen und Node/npm als zweiten Tech-Stack neben Python in `pages.yml` einführen. **Aufwand bei späterem Umstieg auf React** (bewusst in Kauf genommenes Risiko, nicht ausgeschlossen): (1) die bis dahin gebaute Vanilla-JS-Interaktionsschicht (Event-Handling, DOM-Filterung) ist Wegwerf-Code, kein Migrationspfad — die Datenschicht (`health-profile.json`) bleibt aber unverändert nutzbar; (2) neuer Build-Schritt in `pages.yml` (`npm install && npm run build`) inkl. Bundler (z. B. Vite), `package.json`/Lockfile; (3) neuer lokaler Dev-Workflow (Dev-Server statt `python -m http.server`, Dev-Vorschau ≠ Produktionsbundle); (4) laufende Wartung (React-/Bundler-Versionsupdates, ggf. TypeScript-Konfiguration). |
| 6 | Sunburst-Auswahl → Tabellenfilter/Detailansicht: technische Umsetzung? (2026-08-13) | **Vanilla-JS-Event-Kopplung**, aufbauend auf Entscheidung 5 | `render/sunburst.html` löst beim Segment-Klick ein Event aus (z. B. `CustomEvent` mit Category-/Dimension-Key), auf das ein Script auf derselben Seite reagiert. Für reines Filtern/Hervorheben reicht das bereits vorhandene `data-*`-Attribut je Tabellenzeile (`element.style.display`) — dieselbe Mechanik wie die für Stufe 2 der Browse-Tabelle geplante Freitextsuche, nur mit dem Sunburst-Klick statt einem Suchfeld als Trigger. Sollen zusätzlich mehr Felder aus `health-profile.json` angezeigt werden, als aktuell in den Tabellenspalten stecken, ist auch das mit Vanilla JS möglich — entweder als beim Build bereits mitgerenderter, versteckter Detailblock pro Zeile (nur Sichtbarkeit umschalten) oder per clientseitigem `fetch('health-profile.json')` + DOM-Aufbau (wie `sunburst.html` es mit D3 bereits tut, nur ohne D3). Details dazu erst bei Bedarf ausarbeiten. Setzt voraus, dass Sunburst und Tabelle auf derselben Seite eingebettet sind (siehe Vision). |
| 7 | Inline-HTML im `pages.yml`-Build-Schritt auslagern? (2026-08-13) | **Ja** — eigene Template-Datei(en), Jinja2-gerendert wie Browse/Reports | Folgt direkt aus Entscheidung 5 (Vanilla JS bleibt, JS/HTML-Umfang der Landing Page wächst durch Sunburst-Einbettung, Event-Kopplung, ggf. Detailansicht, Downloadbereich, Navigation) — der bisherige `cat > _site/index.html <<EOF`-Block in der YAML-Datei wird dafür unhandlich (kein Syntax-Highlighting, kein lokales Preview ohne Actions-Lauf). |

## Offene Fragen

| # | Frage | Notiz |
|---|---|---|
| 1 | Layout: Sunburst + Tabelle auf einer Seite kombinieren — welche Anordnung (nebeneinander, übereinander, Tabelle erst nach Auswahl sichtbar)? | Offen. Hängt auch von Offener Frage 2 (Navigation) ab. Wird per Wireframe geklärt, siehe Umsetzungsplan Phase B. |
| 2 | Navigation: Sidebar oder Top-Nav — welche Bereiche enthält sie (Sunburst+Tabelle / Downloads / Release-Historie / CMS-Editor-Link)? | Noch unentschieden (2026-08-13) — Nutzer:in möchte erst ein Layout-Wireframe sehen, bevor sie sich festlegt. Siehe Umsetzungsplan Phase B. |
| 3 | "Under construction"-Disclaimer: wann entfernen? | Nutzer:in gibt den Zeitpunkt selbst an, sobald Inhalte reif genug sind (2026-08-13) — kein technischer Trigger, kein festes Datum. |
| 4 | Kurzüberblick/Teaser-Zahlen (Anzahl Categories/Dimensions/Observations) zusätzlich zeigen? | Aktuell keine Priorität (2026-08-13) — kann später aufgegriffen werden, kein Blocker für die Umsetzung. |

## Umsetzungsplan

Phase A ist Voraussetzung für B–D. Phase E ist unabhängig und wartet auf die
Zielgruppen-Spezifikation in `doc/export-report-plan.md`. Phase F läuft nebenher, ohne festen
Zeitpunkt. Checkboxen werden abgehakt, sobald der jeweilige Schritt umgesetzt und verifiziert
ist.

### Phase A — Landing Page aus `pages.yml` auslagern (Grundlage) — ✅ erledigt (2026-08-13)

- [x] `render/templates/index.{de,en}.html.j2` angelegt, Inhalt aus dem alten `cat`-Block in
      `pages.yml` übernommen (reiner Refactor, keine optische Änderung außer der DE-Variante)
- [x] Neues Render-Skript `scripts/render_index.py` (analog `render_html.py`) — nimmt
      `--version`/`--generated`/`--release-base` als CLI-Args entgegen (statt aus
      `health-profile.json` zu lesen), da diese Werte in `pages.yml` erst zur Build-Zeit aus
      dem echten GitHub-Release ermittelt werden, nicht aus dem Repo-Checkout
- [x] DE/EN-Sprachumschalter ergänzt (Design-Entscheidung 3), analog Browse-Seiten — Output
      ist `index.html` (EN, Standard-Pages-Root) + `index.de.html`, mit Lang-Switch-Nav
- [x] `pages.yml`: `cat`-Block durch `python scripts/render_index.py ...` ersetzt; dafür
      `Set up Python`/`Install dependencies`-Schritte ergänzt (Jinja2). Kein Schritt in
      `update-profile.yml` nötig — die Landing Page wird ausschließlich in `pages.yml` zur
      Build-Zeit gerendert, nicht bei jedem Push committed (anders als die Browse-Tabelle)
- [x] Lokal verifiziert: Skript gerendert, per `python -m http.server` (Miniconda-Python)
      serviert, beide Sprachvarianten + Logo-Assets liefern HTTP 200, Inhalt entspricht
      1:1 der bisherigen Live-Page (nur Version/Datum als Platzhalterwerte getestet)

**Nebenbei gefunden und behoben:** Die bisherige EN-Vorlage referenzierte
`media/PräNUDGE_Logo.png` (Umlaut-Datei) im `<img src>`, aber `alt="PreNUDGE"` (ohne Umlaut)
— inkonsistent mit der bereits etablierten Konvention der Browse-Seiten (EN nutzt
`PreNUDGE_Logo.png` ohne Umlaut, DE nutzt `PräNUDGE_Logo.png` mit Umlaut). In den neuen
Templates an die Browse-Konvention angeglichen.

### Phase B — Wireframe & Layout-/Navigation-Entscheidung

- [ ] 1–2 statische HTML/CSS-Wireframes bauen (Sunburst+Tabelle-Anordnung, Sidebar vs.
      Top-Nav) — ohne echte Interaktivität/Daten
- [ ] Wireframes für mind. zwei Breakpoints prüfen (Desktop + Mobile/schmaler Viewport) —
      Responsivität ist primär eine CSS-Frage (Media Queries, `flexbox`/`grid`, SVG-`viewBox`
      für den Sunburst), unabhängig von der Vanilla-JS-Entscheidung; kein Framework nötig
- [ ] Mit Nutzer:in durchsprechen → Offene Fragen 1 (Layout) und 2 (Navigation) klären
- [ ] Gewähltes Layout in `index.{de,en}.html.j2` übernehmen

### Phase C — Sunburst↔Tabelle-Kopplung (Kernfeature)

- [ ] `render/sunburst.html` erweitern: Segment-Klick löst Event aus (Category-/Dimension-Key)
- [ ] `render/browse.js` (Stufe 2 der Browse-Tabelle, siehe unten) auf dieses Event reagieren
      lassen — Zeilen per vorhandenem `data-*`-Attribut filtern/hervorheben
- [ ] Erste Version ohne Detailansicht ausliefern und verifizieren (lokal + einmal live)
- [ ] Danach optional: Detailansicht mit zusätzlichen `health-profile.json`-Feldern ergänzen
      (Weg A oder B aus Design-Entscheidung 6, je nachdem was sich beim Bauen als sinnvoller
      zeigt)

### Phase D — Release-Historie-Seite

- [ ] Render-Schritt, der die Release-Liste (Version, Datum, Downloadlinks) aufbereitet —
      Datenquelle analog zur bestehenden `gh release view`-Abfrage in `pages.yml`
- [ ] Template (eigene Seite oder Abschnitt auf der Landing Page, je nach Layout-Entscheidung
      aus Phase B)
- [ ] In Navigation einhängen

### Phase E — Download-Bereich für Zielgruppen *(wartet auf `doc/export-report-plan.md`)*

- [ ] Zielgruppen-Spezifikation aus `doc/export-report-plan.md` abwarten (Felder/Detailgrad,
      Template-Struktur pro Zielgruppe)
- [ ] Zusätzliche Templates + Export-Kette pro Zielgruppe umsetzen
- [ ] Download-Bereich auf der Landing Page um die neuen Varianten erweitern

### Phase F — Laufende Anpassungen (kein festes Datum)

- [ ] "Under construction"-Disclaimer entfernen — Nutzer:in gibt den Zeitpunkt an
- [ ] Teaser-Zahlen (Anzahl Categories/Dimensions/Observations) — aktuell keine Priorität,
      ggf. später aufgreifen

## Stufe 2 der Browse-Tabelle — Interaktivität (Details)

**Ziel:** Client-seitige Interaktivität über die bereits gerenderten Tabellenzeilen aus
Stufe 1 — ursprünglich als Freitextsuche geplant, jetzt zusätzlich gekoppelt an
Sunburst-Auswahl (siehe Design-Entscheidung 6, umgesetzt in Umsetzungsplan Phase C).

1. Ein kleines Vanilla-JS-Script (`render/browse.js`, kein Framework, keine Abhängigkeit):
   - Freitextsuche über **alle** sichtbaren Zellen einer Zeile (einfacher `includes()`-Check,
     kein Suchindex nötig bei der aktuellen Datenmenge).
   - Zeilen werden per `element.style.display` ein-/ausgeblendet, keine Neu-Anfrage an
     `health-profile.json` nötig (Daten stecken schon im DOM).
   - Sunburst-Segment-Klick als zusätzlicher Filter-Trigger (siehe Design-Entscheidung 6).
   - Weiteres (Dropdown-Filter je Spalte, Sortierung, Mehrfachauswahl) — offen, wird bei
     Bedarf später spezifiziert; die `data-*`-Attribute aus Stufe 1 sind darauf bereits
     vorbereitet.
2. Kein Build-Step nötig — Script wird wie `sunburst.html` per `<script src="browse.js">`
   eingebunden.
3. Bei Bedarf (falls die Datenmenge deutlich wächst): Umstieg auf eine kleine No-Build-
   Bibliothek wie [List.js](https://listjs.com/) prüfen — erst, wenn Handgeschriebenes
   spürbar an Grenzen stößt.

## Ideen für spätere Ausbaustufen (noch nicht geplant, nur festgehalten)

- **Pagination** — bei Bedarf, falls die Datenmenge deutlich wächst.
- **Collapsables** — mehr Detailinformation pro Gesundheitsindikator aufklappbar machen
  (z. B. natives `<details>`/`<summary>`, kein JS nötig).
- **Ein Export-Button mit Format-Auswahl (CSV / Word / …)**:
  - **CSV:** rein client-seitiger Export der aktuell sichtbaren/gefilterten Zeilen — trivial,
    kein Bundler/Framework nötig, spiegelt den Live-Filter.
  - **Word:** die in Phase 4 (`doc/github-actions-plan.md`) geplante Kette
    (Jinja2 → AsciiDoc → `asciidoctor` → `pandoc` → `.docx`) läuft server-seitig in CI, nur
    beim Release, und erzeugt den vollständigen, kuratierten Bericht — nicht die gerade
    gefilterte Tabellenansicht. Der "Word"-Eintrag würde auf den zuletzt veröffentlichten
    Release-Bericht verlinken, nicht live filtern. Sobald die zielgruppenspezifischen
    Report-Varianten aus `doc/export-report-plan.md` existieren (Umsetzungsplan Phase E),
    müsste dieser Eintrag vermutlich zu einer Auswahl pro Zielgruppe werden statt auf einen
    einzelnen Bericht zu verlinken — noch nicht spezifiziert.
- **Sunburst — `vis-status` auswerten:** Das Feld `vis-status` (pro Measurement Instrument,
  z. B. `draft`/`published`) ist laut Schema-Hint dafür gedacht, wird von
  `render/sunburst.html` aber noch nicht ausgewertet. Könnte genutzt werden, um innerhalb
  eines Releases einzelne noch nicht fertige Einträge aus dem Sunburst auszublenden.
- Kurzbeschreibung des PreNUDGE-Projekts/Katalogs für Erstbesucher:innen ohne Vorwissen.

## Nicht-Ziele (vorerst)

- Kein Server/Backend — bleibt eine rein statische Seite.
- Keine Paginierung — bei der aktuellen Datenmenge unnötig, bei Wachstum später nachrüstbar.
- Kein Framework-Wechsel (React o. ä.) — entschieden, siehe Design-Entscheidung 5. Migration
  bleibt möglich, ist aber ein Rewrite der Interaktionsschicht, kein einfacher Aufsatz.

