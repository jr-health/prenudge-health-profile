# Browse-Ansicht — Design-Plan

Dieses Dokument hält die geplanten Schritte für eine tabellarische Browse-Ansicht des Health
Profile Katalogs fest (Phase 3, Schritt 12–15 in `doc/github-actions-plan.md`). Es dient der
Nachvollziehbarkeit — die Umsetzung erfolgt in einem separaten Schritt, sobald hier
Einigkeit besteht.

## Ausgangslage

- `doc/transform-plan.md` sieht bereits `scripts/render_html.py` → Jinja2 →
  `render/templates/browse.html.j2` als Ansatz vor (analog zu `render_doc.py`, das
  `health-profile.json` in Markdown-Reports rendert).
- Das Projekt hat bewusst **keinen Build-Step** (siehe `CLAUDE.md`) — nur statisches JSON,
  Python-Skripte ohne Bundler, und `render/sunburst.html` als Vanilla-JS + D3, direkt per
  `<script>`-Tag im Browser geladen.
- `health-profile.json` enthält bereits alle Daten, die die Browse-Ansicht braucht
  (Categories → Dimensions → Observations → Measurement Instruments, jeweils DE/EN).

## Design-Entscheidungen

| # | Frage | Entscheidung | Begründung |
|---|---|---|---|
| 1 | Server-seitig (Jinja2, wie die Reports) oder client-seitig (Fetch + JS-Rendering, wie der Sunburst)? | **Server-seitig gerendert** (statisches HTML, Zeilen bereits beim Build vorhanden) | Konsistent mit `render_doc.py`/`consolidate.py`-Pipeline; Tabelle funktioniert auch ganz ohne JavaScript (progressive enhancement); Suche/Filter wird später als reine DOM-Manipulation über die bereits vorhandenen Zeilen ergänzt, kein doppeltes Datenladen nötig. |
| 2 | Framework (React o. ä.) oder Vanilla JS? | **Vanilla JS**, kein Build-Step | Passt zur bestehenden Projektphilosophie (siehe `CLAUDE.md`). Eine filterbare/suchbare Tabelle über bereits vorhandene DOM-Zeilen braucht kein Framework. React würde i. d. R. einen Bundler in die CI-Pipeline (`pages.yml`) einführen — vermeidbarer Mehraufwand für diesen Anwendungsfall. |
| 3 | Umsetzung in zwei Stufen? | **Ja** — Stufe 1: simple statische Tabelle ohne Interaktivität. Stufe 2: Suche/Filter per Vanilla JS obendrauf. | Reduziert Risiko, liefert schnell einen sichtbaren Zwischenstand; Stufe 2 kann unabhängig verworfen/verschoben werden, ohne Stufe 1 zu gefährden. |

## Stufe 1 — Statische Tabelle (MVP)

**Ziel:** Eine Seite `render/browse.html`, die alle Observations (mit Category/Dimension-
Zuordnung) als flache Tabelle zeigt — ohne Suche/Filter, nur zum Überblick/Review.

1. `render/templates/browse.{de,en}.html.j2` anlegen (Jinja2, analog zu
   `health-profile.{de,en}.md.j2`), mit einer Tabelle. **Spalten** orientieren sich an dem,
   was der Sunburst bereits zeigt, plus zwei Ergänzungen:
   - Category (Titel + Farb-Swatch aus `color`, wie im Sunburst)
   - Dimension (Titel)
   - Observation (Titel)
   - Anzahl Messinstrumente
   - Source Type(s) der Messinstrumente (`source-type`, z. B. "Wearable device / sensor ·
     automated" / "Questionnaire · manual (self-reported)") — eine Observation kann mehrere
     Messinstrumente mit unterschiedlichem Source Type haben (siehe z. B.
     `hp-observations/minutes-moderate-physical-activity.json`: ein Wearable- und ein
     Questionnaire-Instrument); die Zelle zeigt dann beide Werte (z. B. kommagetrennt oder
     als zwei kleine Badges).
   - Weitere Sunburst-Felder (FHIR IG Status, `vis-status` u. a.) sind laut Plan-Dokument
     aktuell **nicht** im Sunburst ausgewertet — daher vorerst nicht in der Tabelle, können
     aber bei Bedarf jederzeit ergänzt werden.
   - Jede Zeile bekommt ein `data-*`-Attribut je Spalte (z. B.
     `data-category="physical-activity"`), das Stufe 2 für Filterung nutzt, ohne die
     Zeilen neu parsen zu müssen.
2. `scripts/render_html.py` anlegen (analog `render_doc.py`): lädt `health-profile.json`,
   rendert `browse.{de,en}.html.j2` → `render/browse.{de,en}.html`.
3. In `.github/workflows/update-profile.yml` als zusätzlichen Schritt ergänzen (gleicher
   Ort wie `render_doc.py`), damit die Browse-Seite bei jedem Push mit aktualisiert wird.
4. `.github/workflows/pages.yml` (Phase 1) um `render/browse.*.html` im `_site/`-Build
   ergänzen; Landing Page (`_site/index.html`, siehe Phase 3, Schritt 14) verlinkt darauf.
5. Lokal testbar wie gehabt: `python -m http.server` + `render/browse.de.html` öffnen.

## Stufe 2 — Suche & Filter (später)

**Ziel:** Client-seitige Suche/Filter über die in Stufe 1 bereits gerenderten Zeilen —
ähnlich den Sveltia-CMS-Übersichtslisten, aber mit allen Feldern sichtbar statt nur dem
`summary`-Feld.

**Entschieden:** Freitextsuche über alle Spalten ist der Ausgangspunkt für Stufe 2. Details
zu weiterem Filterverhalten (Dropdown je Spalte, Sortierung, Mehrfachauswahl) werden erst
spezifiziert, wenn Stufe 2 ansteht.

1. Ein kleines Vanilla-JS-Script (`render/browse.js`, kein Framework, keine Abhängigkeit)
   ergänzt:
   - Freitextsuche über **alle** sichtbaren Zellen einer Zeile (einfacher `includes()`-Check
     über den gesamten Zeilentext, kein Suchindex nötig bei der aktuellen Datenmenge).
   - Zeilen werden per `element.style.display` ein-/ausgeblendet, keine Neu-Anfrage an
     `health-profile.json` nötig (Daten stecken schon im DOM).
   - Weiteres (Dropdown-Filter je Spalte, Sortierung, Mehrfachauswahl) — offen, wird bei
     Bedarf später spezifiziert und ergänzt; die `data-*`-Attribute aus Stufe 1 sind darauf
     bereits vorbereitet.
2. Kein Build-Step nötig — das Script wird wie `sunburst.html` per `<script src="browse.js">`
   eingebunden.
3. Bei Bedarf (falls die Datenmenge deutlich wächst): Umstieg auf eine kleine No-Build-
   Bibliothek wie [List.js](https://listjs.com/) prüfen — aber erst, wenn Handgeschriebenes
   spürbar an Grenzen stößt, nicht vorab.

## Ideen für spätere Ausbaustufen (noch nicht geplant, nur festgehalten)

- **Pagination** — bei Bedarf, falls die Datenmenge deutlich wächst (siehe auch
  "Nicht-Ziele" unten).
- **Collapsables** — mehr Detailinformation pro Gesundheitsindikator aufklappbar machen
  (z. B. via natives `<details>`/`<summary>`, kein JS nötig), statt alles flach in der
  Tabelle zu zeigen.
- **Ein Export-Button mit Format-Auswahl (CSV / Word / …)** — kombiniert zwei technisch
  unterschiedliche Mechanismen hinter einer UI:
  - **CSV:** rein client-seitiger Export der aktuell sichtbaren/gefilterten Zeilen (nach
    Stufe 2) — trivial umsetzbar, kein Bundler/Framework nötig, spiegelt den Live-Filter.
  - **Word:** die in Phase 4 (`doc/github-actions-plan.md`) geplante Kette
    (Jinja2 → AsciiDoc → `asciidoctor` → `pandoc` → `.docx`) läuft server-seitig in CI,
    nur beim Release, und erzeugt den **vollständigen, kuratierten** Bericht — nicht die
    gerade gefilterte Tabellenansicht. Der "Word"-Eintrag im Export-Dropdown würde also auf
    den zuletzt veröffentlichten Release-Bericht verlinken, nicht live filtern. Ein
    client-seitiger Live-Export nach Word (z. B. über eine JS-Bibliothek wie `docx.js`) wäre
    technisch möglich, aber eine eigenständige, neue Umsetzung mit vermutlich geringerer
    Qualität als die Pandoc-Kette — eigene Entscheidung, falls das gewünscht ist.
- **Sunburst — `vis-status` auswerten:** Das Feld `vis-status` (pro Measurement Instrument,
  Werte u. a. `draft`/`published`) ist laut Hint-Text im Schema für genau diesen Zweck
  gedacht ("PreNUDGE Sunburst Chart Status"), wird aber von `render/sunburst.html` aktuell
  nicht ausgewertet. Könnte ergänzend zur Release-Gate-Entscheidung (Design-Entscheidung 5 in
  `doc/github-actions-plan.md`) genutzt werden, um selbst innerhalb eines Releases einzelne
  noch nicht fertige Einträge aus dem Sunburst auszublenden — kein Blocker für den Start, da
  vorerst kein Eintrag öffentlich sichtbar wird, der nicht zumindest durch einen Release
  gelaufen ist.

## Nicht-Ziele (vorerst)

- Kein Server/Backend — bleibt eine rein statische Seite wie der Sunburst.
- Keine Paginierung — bei der aktuellen Datenmenge (10 Categories, 8 Dimensions, 2
  Observations) unnötig; bei deutlichem Wachstum später nachrüstbar.
- Kein Framework-Wechsel (React o. ä.) — siehe Design-Entscheidung 2.

## Nächste Schritte

1. Umsetzung Stufe 1 (Schritte 1–5) — Spalten sind geklärt.
2. Stufe 2 (Freitextsuche) erst nach Freigabe von Stufe 1; weiteres Filterverhalten wird
   dann bei Bedarf nachgeschärft.
