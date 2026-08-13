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
  CMS-Rich-Text-Felder liefern Markdown-artigen Inhalt (`[text](url)`-Links, `- `-Listen).
  Das passt direkt für die `.md.j2`-Reports, aber AsciiDoc nutzt andere Syntax
  (`link:url[text]`, `* item`). Reiner Fettdruck (`**text**`) ist in beiden Formaten gültig
  und unproblematisch — Links/Listen innerhalb von Rich-Text-Feldern sind aber ein reales
  Risiko für falsch gerendertes AsciiDoc/Word-Dokument (rohe Markdown-Syntax landet
  unverändert im Export, statt als Link/Liste interpretiert zu werden). Noch nicht gegen
  echten Rich-Text-Inhalt mit Links/Listen getestet.
- **`terminology-codes`-Ebenen-Mismatch (siehe „Offene Punkte" in
  `doc/github-actions-plan.md`):** Laut aktuellem `admin/config.yml` dem Messinstrument
  zugeordnet, in bestehenden JSON-Daten aber weiterhin auf Observation-Ebene abgelegt. Alle
  Templates (Markdown **und** AsciiDoc) lesen bewusst von der Observation-Ebene, um
  bestehende Inhalte nicht unsichtbar zu machen — bei neuen, über das aktuelle CMS
  gepflegten Einträgen mit Codes auf Messinstrument-Ebene würde das in **allen**
  Export-Formaten **fehlen**. Zu prüfen, sobald ein neuer Eintrag mit echten
  `terminology-codes` über das CMS angelegt wird.
- **`qualification`/`app-providers` nicht gerendert:** Felder pro Messinstrument in
  `admin/config.yml`, aber in keinem Report-Template (Markdown, AsciiDoc) berücksichtigt.
  Fachlich zu klären, ob das gewünscht ist — falls ja, Templates entsprechend erweitern.
- **Corporate-Table-Style-Patch (Schritt 18, nur Word):** Der `Table`-Style in
  `render/templates/PräNUDGE Berichtsvorlage.docx` wurde manuell in die `.docx`-Vorlage
  gepatcht (geklont von `Table Grid`). Bei mehreren/größeren Tabellen (z. B. viele
  Messinstrumente mit vielen `terminology-codes`) noch nicht in der Breite getestet.
- **Neu (2026-08, `disease-association`-Feld):** Wurde laut Commit `8653e16` bereits allen
  Observation-Templates (Markdown und AsciiDoc) hinzugefügt — beim nächsten Review mit echten
  Daten gegenprüfen, ob es in Markdown-Report **und** `.docx` korrekt erscheint (bisher nur an
  Testdaten verifiziert, nicht an einem inhaltlich befüllten Fall).

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
