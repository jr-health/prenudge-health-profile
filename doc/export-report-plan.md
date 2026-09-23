# Export-Reports — Review-Plan

Dieses Dokument sammelt offene Fragen, bekannte Risiken und künftige Findings rund um die
generierten Export-Reports (Markdown, AsciiDoc, Word/`.docx` — Phase 2 und Phase 4 in
`doc/github-actions-plan.md`) — Phase 5, Schritt 27. Anders als `doc/interactive-catalogue-plan.md`
(zusammengeführt aus den früheren `doc/browse-view-plan.md`/`doc/landing-page-plan.md`) ist das hier **kein** abgeschlossener Design-Plan mit
Design-Entscheidungen, sondern ein lebendes Backlog: Der eigentliche Review kann erst
sinnvoll stattfinden, sobald mehr echte Gesundheitsindikatoren im Katalog erfasst sind —
aktuelle Testdaten sind zu dünn, um Layout/Tabellenstruktur abschließend zu beurteilen. Bis
dahin werden hier Beobachtungen/Risiken gesammelt, die beim eigentlichen Review als
Checkliste dienen — unabhängig vom konkreten Ausgabeformat.

## Zielgruppenspezifische Report-Varianten (geplante Ausbaustufe)

Vision (2026-08-13, aus `doc/interactive-catalogue-plan.md` hierher verschoben, da inhaltlich
eine Export-Report-Frage): Perspektivisch soll es nicht nur eine Version des
Gesundheitsprofil-Berichts geben, sondern mehrere, je nach Zielgruppe — der Download-Bereich
auf der Landing Page (siehe `doc/interactive-catalogue-plan.md`) würde dann pro Zielgruppe
verlinken.

**Ausbaustufe 1:**
- Healthcare Professionals
- Bürger:innen
- Entwickler:innen

**Ausbaustufe 2 (später):**
- Sekundärdatennutzer:innen
- Krankheitsbildspezifisch

**Noch offen:**
- Welche Felder/welcher Detailgrad pro Zielgruppe? (z. B. vermutlich brauchen
  Entwickler:innen technische Felder wie FHIR-Codes/`id_tech`/Messinstrument-Details,
  während Bürger:innen eher vereinfachte, IDs-freie Beschreibungen bräuchten — noch nicht
  fachlich spezifiziert.)
- Technische Umsetzung: separate Templates pro Zielgruppe (analog den heutigen
  `health-profile.{de,en}.md.j2`/`.adoc.j2`) oder ein gemeinsames Template mit
  Zielgruppen-Parameter zur Feld-Filterung? Vermutlich eher separate Templates, da sich
  vermutlich nicht nur einzelne Felder unterscheiden, sondern auch Struktur/Gliederung — noch
  nicht entschieden.
- Kein Blocker für die Umsetzungsphasen A–D in `doc/interactive-catalogue-plan.md` — der
  Download-Bereich kann mit der aktuell einzigen Version starten, Zielgruppen-Varianten
  werden unabhängig davon nachgezogen, sobald die obigen Punkte geklärt sind.

## Warum noch kein Review möglich ist

- Aktuell nur 1–2 Observations mit echtem Inhalt (`minutes-moderate-physical-activity`, dazu
  vereinzelt befüllte Dimensionen wie `consumption-frequency`) — die meisten Categories/
  Dimensions/Observations sind Platzhalter oder komplett leer.
- Tabellen, mehrzeilige Rich-Text-Felder (Beschreibungen, `verified-health-links`,
  Messinstrument-Details) und tief verschachtelte Strukturen (mehrere Messinstrumente pro
  Observation, mehrere `terminology-codes` pro Instrument) kommen im Bericht erst bei
  ausreichend befüllten Daten in ihrer vollen Breite vor — der Corporate-Table-Style-Fix aus
  Schritt 18 (Word) wurde nur gegen einen einzigen Beispieldatensatz verifiziert.

## Bekannte Risiken/Beobachtungen (aus Phase 2/4, zu prüfen sobald genug echte Daten vorliegen)

- **Rich-Text-Syntax-Mismatch zwischen Markdown und AsciiDoc (Schritt 16):**
  CMS-Rich-Text-Felder liefern Markdown-artigen Inhalt (Bilder, ATX-Überschriften,
  Pipe-Tabellen, `[text](url)`-Links, `- `-Listen). Das passt direkt für die `.md.j2`-Reports,
  aber AsciiDoc nutzt andere Syntax. **Teilweise behoben** (Commit `93072f0`, 2026-09-02, neuer
  `md_adoc`-Filter/`md_richtext_to_adoc()` in `scripts/render_adoc.py`): Bilder
  (`![alt](url)` → `image:url[alt]`), ATX-Überschriften (in einen Sentinel-umschlossenen
  fetten Absatz umgeschrieben, per `scripts/style_inline_headings.py` nachträglich gestylt)
  und Markdown-Pipe-Tabellen (auch verschachtelt in Messinstrument-Tabellenzellen → echte
  AsciiDoc `|===`-Tabelle) werden jetzt korrekt konvertiert. Zusätzlich behoben (Commit
  `8114d08`, 2026-09-22): eingebettete Zeilenumbrüche in Fließtext/Feldern (z. B.
  „min: <18,5\nmax: >= 40") wurden von AsciiDoc bisher zu einer Zeile zusammengezogen — ein
  neuer `adoc_br`-Filter fügt jetzt explizite AsciiDoc-Zeilenumbrüche (`" +"`) ein.
  **Weiterhin offen:** `md_richtext_to_adoc()` konvertiert **keine** Markdown-Links
  (`[text](url)`) oder Bullet-Listen (`- item`) — diese beiden bleiben ein reales Risiko für
  falsch gerendertes AsciiDoc/Word (rohe Markdown-Syntax landet unverändert im Export). Noch
  nicht gegen echten Rich-Text-Inhalt mit Links/Listen getestet.
- **`terminology-codes`-Ebenen-Mismatch — behoben (Commit `6caf017`, 2026-09-22):** Die
  Templates lasen die Codes bisher von der Observation-Ebene statt vom Messinstrument, wo sie
  laut `admin/config.yml` tatsächlich liegen — dadurch fehlten sie fast überall, und wo doch
  etwas erschien, zeigte jedes Messinstrument einer Observation dieselbe (falsche) Liste. Fix
  verschiebt den Lookup in die Pro-Instrument-Schleife und liest `instr['terminology-codes']`
  direkt; die Reports zeigen jetzt Codes für alle 21 betroffenen Messinstrument-Einträge statt
  nur 1.
- **`qualification`/`app-providers` nicht gerendert:** Felder pro Messinstrument in
  `admin/config.yml`, aber in keinem Report-Template (Markdown, AsciiDoc) berücksichtigt.
  Fachlich zu klären, ob das gewünscht ist — falls ja, Templates entsprechend erweitern.
- **Corporate-Table-Style-Patch (Schritt 18, nur Word):** Der `Table`-Style in
  `render/templates/PräNUDGE Berichtsvorlage.docx` wurde manuell in die `.docx`-Vorlage
  gepatcht (geklont von `Table Grid`). **Update 2026-08-27:** Style um `firstRow` (fett),
  `band1Horz`/`band2Horz` (abwechselnd hellgrau/weiß), hellgraue Rahmenfarbe und
  `tblCellMar` (mehr Zeilenabstand) erweitert (siehe "Word-Export-Überarbeitung" unten).
  **Update 2026-09-02 (Commit `93072f0`):** Bis dahin galt dieser Style nur für die vom
  Template selbst gebauten Messinstrument-Tabellen — Markdown-Pipe-Tabellen aus
  Rich-Text-CMS-Feldern wurden gar nicht erst zu echten AsciiDoc-Tabellen konvertiert. Jetzt
  laufen auch die aus Rich-Text konvertierten Tabellen durch denselben Style, inkl. der
  verschachtelten Variante innerhalb von Messinstrument-Tabellenzellen. Bei mehreren/größeren
  Tabellen (z. B. viele Messinstrumente mit vielen `terminology-codes`) weiterhin nicht in der
  Breite gegen viele reale Einträge gleichzeitig getestet.
- **Neu (2026-08, `disease-association`-Feld):** Wurde laut Commit `8653e16` bereits allen
  Observation-Templates (Markdown und AsciiDoc) hinzugefügt — beim nächsten Review mit echten
  Daten gegenprüfen, ob es in Markdown-Report **und** `.docx` korrekt erscheint (bisher nur an
  Testdaten verifiziert, nicht an einem inhaltlich befüllten Fall).

## Word-Export-Überarbeitung (2026-08-27, erledigt)

Auf Basis von direktem Feedback am gerenderten `.docx` wurde die Word-Ausgabe überarbeitet.
Zusammenfassung, weil die Details (insbesondere die zwei OOXML-Fallstricke unten) sonst
leicht erneut "entdeckt" werden müssten:

- Icons in den Kategorie-Überschriften entfernt (DE+EN).
- Inhaltsverzeichnis: von einer manuell gebauten Aufzählungsliste auf ein echtes
  Word-Feld umgestellt (`pandoc --toc --toc-depth=3`, lokalisierter Titel via `-M
  toc-title=…`). Dafür fehlte der Vorlage ein `toc 3`-Style (`Verzeichnis3`, geklont von
  `Verzeichnis2`) — ergänzt.
- Messinstrument-Bezeichnungen sind jetzt echte Heading-5-Absätze (`======` in AsciiDoc)
  statt fettem Fließtext — nummeriert sich über die bereits vorhandene
  Gliederungsnummerierung der Vorlage automatisch mit (kein neuer Style nötig, Heading 5
  war schon vollständig verdrahtet).
- „Verifizierte Gesundheitsinformation" umgebaut: Links stehen jetzt direkt unter
  „Beschreibung für Fachpersonal:", aufgeteilt nach Zielgruppe in zwei Listen
  („Weiterführende Links für Fachpersonal" / „…für Bürger:innen", die zweite nach
  „Information für Bevölkerung").
- Bearbeitungshistorie: `github-actions[bot]`-Commits werden in `consolidate.py`
  herausgefiltert.
- **Echtes Deckblatt statt Pandoc-Platzhalter:** Pandoc erzeugt aus dem AsciiDoc-Titel nur
  einen generischen "Title"-Absatz — kein echtes Deckblatt mit Logo/Layout, weil
  `--reference-doc` nur Styles kopiert, keinen Body-Inhalt. Neues Skript
  `scripts/inject_cover_page.py` (braucht `python-docx`) kopiert nach dem `pandoc`-Lauf
  das echte Deckblatt (Logo, Titel, Version/Datum, Link zum PreNUDGE Consortium) aus der
  Referenzvorlage in die generierte `.docx` und befüllt außerdem Version/Datum in beiden
  Fußzeilen (Deckblatt- und Standard-Fußzeile).
- Das angezeigte Datum ist das Datum des releaseten Commits (`git log -1 --date=short`),
  nicht der Build-Zeitpunkt — an `render_adoc.py`/`inject_cover_page.py` per `--generated`
  durchgereicht (siehe `doc/release.md`).

**Zwei nicht offensichtliche OOXML-Fallstricke, an denen unterwegs echte
"Word hat unlesbaren Inhalt gefunden"-Reparaturdialoge auftraten** — relevant, falls an
`inject_cover_page.py` oder der Referenzvorlage weitergearbeitet wird:

1. **Leere Links → kaputte Hyperlink-Relationship:** Ein `verified-health-links`-Eintrag
   mit leerer `url` (Restdaten aus einem nie ausgefüllten CMS-Listeneintrag, in
   `hp-dimensions/dietary-pattern.json`) rendert als `link:[]` im AsciiDoc → Word-Beziehung
   mit leerem `Target` → Reparaturdialog. Templates filtern Links ohne `url` jetzt heraus
   (siehe Abschnitt "Rich-Text-Syntax-Mismatch" oben, verwandtes Risiko).
2. **`w:dataBinding` auf ein `customXml`-Teil, das im Zielpaket gar nicht existiert:** Die
   Titel-/Autor-Inhaltssteuerelemente auf dem Deckblatt der Referenzvorlage sind an
   `docProps/core.xml` gebunden (`w:dataBinding` → `customXml/item1.xml`). Nur den
   sichtbaren Text zu ersetzen reicht nicht — die Bindung zeigt weiterhin auf ein
   `customXml`-Teil, das im von Pandoc erzeugten Paket nie existiert hat. Word erkennt das
   beim Öffnen als unlesbar. Fix: `inject_cover_page.py` entfernt die
   Inhaltssteuerelemente vollständig (`unwrap_sdt`) und lässt nur den reinen Text übrig.
   Ebenso zu beachten: Textfelder/Formen in Word liegen fast immer doppelt vor
   (`mc:AlternateContent` mit `Choice`/`Fallback` für neuere/ältere Word-Versionen) — das
   sieht beim ersten Blick in die XML wie ein versehentliches Duplikat aus, ist aber
   Standardverhalten und beide Zweige müssen befüllt werden.

Zusätzlich entdeckt und behoben: Die Fußzeile des Deckblatts enthielt ein echtes,
aktualisierbares Word-`DATE`-Feld statt eines festen Werts — hätte bei jedem Öffnen das
_aktuelle_ Datum angezeigt statt des Release-Datums. Jetzt durch festen Text ersetzt.

## Vorgehen, sobald genug echte Daten vorliegen

1. Diese Liste als Checkliste durchgehen, jeden Punkt gegen echte Inhalte verifizieren — in
   Markdown, AsciiDoc-Zwischenformat und dem finalen `.docx`.
2. Zusätzlich freies Durchblättern aller Ausgabeformate (DE **und** EN) auf Layout-Fragen,
   die sich erst bei echtem Fließtext zeigen (Zeilenumbrüche, Kapitel-Nummerierung,
   Inhaltsverzeichnis-Tiefe, Tabellen-Zeilenumbruch über Seitengrenzen im `.docx`).
3. Findings hier ergänzen (neue Zeilen in "Bekannte Risiken/Beobachtungen") oder, falls
   direkt behebbar, in `doc/github-actions-plan.md` (Phase 2/4) und in den Templates fixen.

## Nächste Schritte

- Warten, bis mehr echte Gesundheitsindikatoren erfasst sind (kein festes Datum, hängt vom
  fachlichen Fortschritt ab, nicht von diesem technischen Plan).
- Danach: Review gemäß „Vorgehen" oben durchführen.
