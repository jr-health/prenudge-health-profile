# Landing Page — Design-Plan

Dieses Dokument hält die geplanten Schritte für die inhaltliche/gestalterische Überarbeitung
der GitHub-Pages-Landingpage (`_site/index.html`) fest — Phase 3, Schritt 14 (Platzhalter +
Branding) und Phase 5, Schritt 26 in `doc/github-actions-plan.md`. Es dient der
Nachvollziehbarkeit — die Umsetzung erfolgt in einem separaten Schritt, sobald hier
Einigkeit besteht.

## Ausgangslage

- `_site/index.html` wird **nicht** aus einer eigenen Datei/Template gebaut, sondern per
  `cat > _site/index.html <<EOF ... EOF` **inline im Build-Schritt von
  `.github/workflows/pages.yml`** erzeugt (siehe dort, Schritt „Build `_site`"). Das war für
  den schnellen Start pragmatisch, ist aber auf Dauer unhandlich (kein Syntax-Highlighting,
  keine lokale Vorschau ohne Actions-Lauf, HTML/CSS/Bash-Variablen gemischt).
- Aktueller Inhalt: Logo + Titel + Version/Generiert-Datum (aus dem Release-Asset
  `health-profile.json`, nicht aus dem Repo-Checkout — siehe Kommentar im Workflow zu
  Design-Entscheidung 5), ein "Under construction"-Disclaimer, zwei einfache `<ul>`-Listen
  (Sunburst/Browse DE+EN/CMS-Editor; Downloadlinks DE+EN zu den `.docx`-Release-Assets) und
  ein Footer-Link zum PreNUDGE-Konsortium.
- Branding (Schritt 20, bereits erledigt): Logo `PräNUDGE_Logo.png`, Farbe `#004E64`,
  Schrift Verdana — an die Browse-Seiten angeglichen.
- Sprache: aktuell nur **Englisch** (`<html lang="en">`), obwohl Sunburst/Browse/Reports
  durchgehend DE+EN anbieten — Landing Page selbst ist noch nicht zweisprachig.
- Es gibt noch **kein** eigenes Layout-Konzept — die aktuelle Struktur ist eine reine
  Aufzählungsliste ("Platzhalter-Listen" laut Schritt 26), kein visuelles Konzept
  (Hero-Bereich, Karten, Hervorhebung des Sunburst als Hauptinhalt o. ä.).

## Offene Fragen (noch nicht entschieden)

| # | Frage | Notiz |
|---|---|---|
| 1 | Inline-HTML im Workflow beibehalten oder in eine eigene Datei (`render/templates/index.html.j2` + Jinja2-Rendering, analog zu Browse/Reports, oder ein statisches Template mit Platzhalter-Ersetzung) auslagern? | Inline ist aktuell der einzige Ort ohne Jinja2-Template; eine eigene Datei wäre wartbarer und lokal vorschaubar, bräuchte aber einen eigenen kleinen Render-Schritt (die Variablen `$RELEASE_VERSION`/`$GENERATED`/`$RELEASE_BASE` kommen aus `gh release`/`jq`, nicht aus `health-profile.json` direkt beim Build). |
| 2 | Zweisprachigkeit (DE/EN) wie bei Sunburst-Umgebung/Browse? | Aktuell nur EN. Müsste analog zum Sprachumschalter der Browse-Seiten gelöst werden, oder die Landing Page bleibt bewusst einsprachig (Englisch) als neutrale Einstiegsseite, während Sunburst/Browse/Reports die eigentliche DE/EN-Aufteilung übernehmen. |
| 3 | Visuelles Konzept: reine Linklisten wie jetzt, oder ein strukturierteres Layout (z. B. Sunburst als eingebettete Vorschau/Kachel, Browse und Downloads als eigene Karten/Sektionen)? | Noch keine Design-Vorgabe; aktuell nur Branding-Farbe/-Schrift/-Logo übernommen, kein Layout-Konzept. |
| 4 | "Under construction"-Disclaimer: wann entfernen? | An echte Inhalte gekoppelt (siehe auch `doc/word-report-plan.md` für die Report-Seite der gleichen Frage) — sinnvoll erst, wenn genug echte Gesundheitsindikatoren erfasst sind, dass die Seite nicht mehr nach Testdaten aussieht. |
| 5 | Soll die Landing Page zusätzlich einen Kurzüberblick/Teaser über den Katalog zeigen (z. B. Anzahl Categories/Dimensions/Observations aus `health-profile.json`), oder bleibt sie eine reine Link-Sammlung? | Offen. |

## Ideen (noch nicht geplant, nur festgehalten)

- Sunburst-Diagramm direkt als Vorschau/Thumbnail auf der Landing Page einbetten (per
  `<iframe>` oder direktem Einbau des SVG), statt nur zu verlinken.
- Kurzbeschreibung des PreNUDGE-Projekts/Katalogs für Erstbesucher:innen, die die Seite ohne
  Vorwissen öffnen (aktuell reine Link-/Downloadliste ohne Kontext-Text).
- Sichtbare Historie/Changelog früherer Releases (Link auf die GitHub-Releases-Seite als
  einfachster erster Schritt).

## Nicht-Ziele (vorerst)

- Kein Framework/Build-Step (siehe `CLAUDE.md` und Design-Entscheidung 2 in
  `doc/browse-view-plan.md`) — bleibt statisches HTML, ggf. mit Jinja2 serverseitig gerendert
  wie die anderen Reports.

## Nächste Schritte

1. Offene Fragen 1–5 klären.
2. Danach Umsetzung (ggf. inkl. Auslagerung aus dem Inline-`cat`-Block in
   `.github/workflows/pages.yml` in eine eigene Template-Datei).
