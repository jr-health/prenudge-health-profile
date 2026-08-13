# GitHub Actions & Pages Rollout-Plan

Dieses Dokument hält die geplanten Schritte fest, um (1) das Sveltia-CMS zusätzlich über
GitHub Actions/Pages zu hosten, (2) die bestehende Gitea-CI-Pipeline nach GitHub zu
portieren, und (3) eine gesammelte Auswertung (Sunburst-Visualisierung + Word-Export) auf
einer GitHub Page bereitzustellen. Es dient der Nachvollziehbarkeit — die Umsetzung erfolgt
in einem separaten Schritt.

## Ist-Stand (bereits vorhanden, Basis für diesen Plan)

- Das CMS-Backend zeigt bereits auf GitHub: `admin/config.yml` → `backend.repo:
  jr-health/prenudge-health-profile`, `branch: main`. Dieses Repository **ist** dieses Ziel-Repo.
- Der GitHub-Login läuft über einen bereits deployten Cloudflare Worker
  (`base_url: https://sveltia-cms-auth.jr-health.workers.dev`) — funktioniert laut README
  produktiv.
- Das CMS wird aktuell zusätzlich extern unter `ig.dev.prenudge.at/admin/index.html`
  gehostet — dieses Deployment erfolgt **manuell** und bleibt außerhalb des Scopes dieses
  Plans (siehe Design-Entscheidung 1).
- `.gitea/workflows/update-profile.yml` validiert/konsolidiert/rendert bei jedem Push,
  läuft aber nur auf dem Gitea-Runner unter `health.joanneum.at/git` — **nicht** auf GitHub.
- `scripts/consolidate.py` (Stufe 1) ist fertig implementiert und schemaunabhängig — es
  reicht Felder unverändert durch und löst nur `key`/`category`/`dimension`-Relationen auf,
  die weiterhin zum aktuellen `admin/config.yml` passen.
- `scripts/render_doc.py` (Stufe 2, Jinja2 → Markdown DE/EN) ist implementiert, aber die
  zugehörigen Templates (`render/templates/health-profile.{de,en}.md.j2`) sind seit einer
  Überarbeitung von `admin/config.yml` **nicht mehr vollständig deckungsgleich** mit dem
  aktuellen Feldschema — Details siehe Abschnitt "Bekannter Template/Schema-Drift" unten.
- `render/sunburst.html` ist ein fertiger, interaktiver D3-Sunburst, der `health-profile.json`
  relativ lädt — funktionsfähig, aber noch nicht auf einer Page deployed. Er nutzt nur
  `title`/`color`, die im Schema unverändert geblieben sind, und ist vom Drift nicht betroffen.
- `doc/transform-plan.md` sieht zusätzlich ein noch nicht umgesetztes
  `scripts/render_html.py` (statische Browse-Ansicht) und einen Word/PDF-Export als offene
  Punkte vor.
- ~~Im Arbeitsverzeichnis liegt ein frisch geklontes `sveltia-cms-auth/`~~ — **erledigt**:
  Der Ordner ist ein unveränderter lokaler Clone des Auth-Worker-Quellcodes (genutzt, um den
  bereits laufenden Worker per `wrangler` aufzusetzen) und wurde am 2026-07-23 in die
  Root-`.gitignore` aufgenommen, da er für diesen Plan nicht gebraucht wird
  (siehe Design-Entscheidung 2).

### Bekannter Template/Schema-Drift (neu entdeckt)

Beim Vergleich von `admin/config.yml` mit den Jinja2-Templates und den bestehenden
JSON-Daten zeigt sich, dass sich das CMS-Feldschema geändert hat, **nachdem** die Templates
geschrieben wurden:

| Collection | Template erwartet | Aktuelles Feld in `config.yml` | Auswirkung |
|---|---|---|---|
| categories | `c.description` | `description-professional`, `description-laymen` (zwei getrennte Felder) | Kategorie-Beschreibungen, die über die aktuellen CMS-Felder gepflegt werden, erscheinen **nicht** im gerenderten Bericht — das Template liest ein Feld, das es nicht mehr gibt. |
| dimensions | `d.description` | `description_professional`, `description_layman` (Unterstrich statt Bindestrich, Singular „layman") | Gleiches Problem wie bei categories. |
| observations | `o.population`, `o['target-info']` | *(kein entsprechendes Feld mehr in `config.yml`)* | Diese Felder existieren nur noch als Altlast in ein paar bestehenden JSON-Dateien (z. B. `hp-observations/minutes-moderate-physical-activity-per-week.json`), sind aber über das aktuelle CMS gar nicht mehr befüllbar. |

Verifiziert per Grep über `hp-categories/`, `hp-dimensions/`, `hp-observations/`: nur
vereinzelte ältere Dateien (`alcohol.json`, `consumption-frequency.json`,
`minutes-moderate-physical-activity-per-week.json`) enthalten noch das alte, flache
`"description"`-Feld — und dort meist leer (`""`). Kein bestehender Eintrag nutzt bereits
die neuen Felder `description-professional`/`description-laymen` bzw.
`description_professional`/`description_layman`, das Problem ist also aktuell noch "still",
würde aber bei den ersten inhaltlich befüllten Einträgen sofort sichtbar (leere
Kategorie-/Dimension-Abschnitte im Bericht trotz gepflegter Beschreibung).

**Konsequenz:** `scripts/consolidate.py` selbst muss nicht angepasst werden (es ist
feldagnostisch). `scripts/render_doc.py` als Skript ebenfalls nicht — der Fix betrifft die
**Templates** `render/templates/health-profile.{de,en}.md.j2`. Das wird als Voraussetzung
in Phase 2 aufgenommen (siehe Schritt 6), **bevor** die GitHub-Pipeline produktiv geschaltet
wird, damit nicht von Anfang an fehlerhafte Reports generiert werden.

### Hinweis: Mehrbenutzer-Bearbeitung im CMS (organisatorisch zu lösen)

Sveltia CMS committet jede Speicherung einzeln über die GitHub-API. Ein Konflikt kann nur
entstehen, wenn zwei Personen **exakt denselben Eintrag** (dieselbe JSON-Datei, z. B.
dieselbe Observation) **gleichzeitig** bearbeiten — unterschiedliche Einträge sind immer
unabhängig. Laut einer offiziellen Sveltia-CMS-Diskussion
([„Multi User Editor" #94](https://github.com/sveltia/sveltia-cms/discussions/94)) ist
echtes Multi-User-Konfliktmanagement aktuell **nicht** eingebaut — im Konfliktfall könnte im
schlechtesten Fall die zweite Speicherung die erste unbemerkt überschreiben, statt sauber
abgefangen zu werden. Das ist ein reines CMS-Verhalten, unabhängig von der GitHub-Actions-
Pipeline (und unabhängig von der `concurrency`-Einstellung aus Design-Entscheidung 3, die nur
die *generierten* Dateien betrifft, nicht die Inhalts-Commits der Nutzer:innen).

**Wird organisatorisch gelöst**, mit folgenden Empfehlungen für alle CMS-Nutzer:innen:

- Vor dem Bearbeiten eines Eintrags die Seite neu laden, wenn sie schon länger offen war —
  damit sichergestellt ist, dass man auf dem aktuellen Stand arbeitet.
- Zwischendurch öfter speichern, statt eine lange Bearbeitungssession erst am Ende in einem
  großen Schritt zu sichern — reduziert im Konfliktfall den Umfang möglicher Verluste.
- Kurze Absprache im Team, wer welchen Eintrag gerade bearbeitet — besonders in Phasen mit
  vielen parallelen Änderungen (z. B. zu Beginn der Migration).

## Design-Entscheidungen

| # | Frage | Entscheidung | Begründung / Konsequenz |
|---|---|---|---|
| 1 | CMS-Hosting: GitHub Pages statt oder zusätzlich zu `ig.dev.prenudge.at`? | **Zusätzlich.** GitHub Pages wird ein neuer, unabhängiger Deployment-Weg über GitHub Actions. Das bestehende manuelle Deployment auf `ig.dev.prenudge.at` bleibt **unverändert und komplett manuell** — es wird von dieser Pipeline weder ausgelöst noch ersetzt. | Rein statische Dateien, kein Entweder-Oder nötig, kein Risiko für den bestehenden Weg. `ig.dev.prenudge.at` bleibt der vom Nutzer selbst kontrollierte Fallback. Zu prüfen: `ALLOWED_DOMAINS` am Worker ggf. um die neue GitHub-Pages-Domain ergänzen. |
| 2 | OAuth-Worker neu aufsetzen oder bestehenden nutzen? | **Bestehenden Worker weiterverwenden** | Kein Zusatzaufwand, bereits produktiv. `sveltia-cms-auth/` (lokaler Clone) wird für dieses Vorhaben nicht benötigt — in `.gitignore` aufgenommen. |
| 3 | Commit-back der generierten Dateien beibehalten? Trigger push oder zeitgesteuert? | **Commit-back wie bisher**; Trigger **push-basiert** (kein Cron alle 4h) | CMS-Edits laufen über die GitHub-Backend-API des CMS — jede inhaltliche Änderung *ist* bereits ein Push auf `main`. Ein zusätzlicher Cron würde nur redundante Runs erzeugen, ohne neue Fälle abzudecken. Push mit Pfad-Filter (wie im Gitea-Workflow) reicht. Optional später: ein niedrig-frequenter Cron (z. B. täglich) als reines Sicherheitsnetz — kein Muss für den Start. |
| 4 | Word-Export: Kette und Ablageort? | **AsciiDoc als Zwischenformat**, Erzeugung **nur beim Release** (Tag-Push), Ablage als **Release-Asset**, von der GitHub Page aus **verlinkt** | Der Word-Bericht ist ein versioniertes Deliverable (analog `doc/release.md`), nicht jeder Zwischenstand. Braucht eine neue Rendererkette: Jinja2 → `.adoc` → asciidoctor → docbook → pandoc → `.docx` (bessere Tabellen-/Kapitel-Fidelity als direkte Markdown→docx-Konvertierung). |
| 5 | Zeigt die GitHub Page (Sunburst + Bericht) immer den **aktuellen** Stand von `main` oder immer den letzten **released** Stand? | **Released Stand.** `pages.yml` wird von `release.yml` ausgelöst (+ `workflow_dispatch` als Handventil), **nicht** von jedem Push auf `main`. | Da das Repo öffentlich wird, ist "Drafts vor der Öffentlichkeit verstecken" ohnehin keine echte Sicherheitsgrenze — jeder Rohstand ist über die Git-Historie einsehbar. Der eigentliche Grund für die Entscheidung ist Kuratierung: Die Page soll den kuratierten, releaseten Stand zeigen (konsistent mit `doc/release.md`), nicht jeden Zwischenstand. Konsequenz: Redakteur:innen sehen ihre frischen Änderungen **nicht** sofort auf der Page — dafür bleibt der bereits heute funktionierende lokale Weg (`python -m http.server` + `render/sunburst.html`, siehe README) die Review-Methode vor einem Release. |
| 6 | Soll `pages.yml` auch bei Schema-Änderungen (`admin/**`) automatisch laufen, ohne die Kuratierung aus Entscheidung 5 aufzuweichen? (2026-08) | **Ja, zusätzlicher `push`-Trigger, gefiltert auf `paths: ['admin/**']`** (nicht auf ganz `main`). Im Build wird dafür sauber getrennt: `admin/` im `_site/`-Ergebnis folgt immer dem auslösenden Checkout (kann also frische, noch nicht releaste Schema-Änderungen zeigen); `render/sunburst.html` und `render/browse.{de,en}.html` werden unabhängig davon per zweitem `actions/checkout` (`ref: <letzter Release-Tag>`, Zielordner `released/`) auf den **exakten Commit des letzten Release-Tags** gepinnt, bevor sie nach `_site/render/` kopiert werden. `health-profile.json`/`.docx` waren als Release-Assets ohnehin schon gepinnt. | Der CMS-Editor liest/schreibt laut `admin/config.yml` (Backend `github`, Branch `main`) ohnehin immer live die einzelnen Entity-Dateien (`hp-categories/`, `hp-dimensions/`, `hp-observations/`, `data-provider/`) über die GitHub-API — nie das release-gated `health-profile.json`. Ihn hinter einem Release zu verstecken diente also nie der Kuratierung aus Entscheidung 5, sondern war nur eine Nebenwirkung des fehlenden Pfad-Filters. Sunburst/Browse/Reports bleiben strikt release-gated wie in Entscheidung 5, jetzt aber auch dann garantiert konsistent, wenn ein `admin/**`-Push oder ein manueller `workflow_dispatch` mit unreleastem `main`-Stand die Page baut (vorher konnte in diesen beiden Fällen `render/sunburst.html` versehentlich einen `main`-Stand zeigen, der neuer als der zuletzt releaste ist). |

## Zielarchitektur (Übersicht)

```
Push auf main (CMS-Edit oder manueller Commit)
  └─ .github/workflows/update-profile.yml
       validate.py → consolidate.py → render_doc.py (md) → commit [skip ci]
       (hält health-profile.json + Berichte im Arbeitsstand aktuell — Vorstufe für den
        nächsten Release, löst KEIN Pages-Deploy aus)

       Review vor dem Release: lokal via `python -m http.server` + render/sunburst.html
       (bestehender Weg, siehe README) — kein Pages-Deploy nötig.

Tag-Push (vX.Y.Z)
  └─ .github/workflows/release.yml
       validate.py → consolidate.py --version → render_doc.py (md)
       → render_adoc.py (adoc) → asciidoctor → docbook → pandoc (docx)
       → GitHub Release mit Assets (json, md de/en, docx de/en)
       └─ .github/workflows/pages.yml (on: workflow_run von release.yml, + workflow_dispatch)
            baut _site/ (admin/, index.html, sunburst.html, health-profile.json, ggf. browse.html)
            aus dem soeben getaggten (=released) Stand
            → GitHub Pages (Source: GitHub Actions)

ig.dev.prenudge.at  ── weiterhin rein manuelles Deployment, außerhalb dieser Pipeline ──
```

Die Trennung spiegelt Design-Entscheidung 5: `update-profile.yml` hält nur den internen
Arbeitsstand synchron; `pages.yml` (und damit alles, was die Öffentlichkeit sieht) wird
ausschließlich durch einen tatsächlichen Release angestoßen.

## Umsetzungsschritte

### Phase 1 — GitHub Pages Grundgerüst & CMS-Spiegel

1. ✅ GitHub → Settings → Pages → Source auf **„GitHub Actions"** stellen (kein `gh-pages`-Branch, kein `/docs`-Ordner). — **erledigt** (2026-07-24).
2. ✅ Neuen Workflow `.github/workflows/pages.yml` anlegen (Trigger vorerst `workflow_dispatch`; `workflow_run` von `release.yml` folgt in Phase 4, siehe Design-Entscheidung 5), der einen `_site/`-Ordner baut:
   - `admin/` 1:1 nach `_site/admin/` (identischer CMS-Editor wie auf `ig.dev.prenudge.at`)
   - `media/` nach `_site/media/` (Icons, CMS-Logo)
   - `health-profile.json` nach `_site/health-profile.json`
   - `render/sunburst.html` in die Page einbinden (siehe Phase 3 für die genaue Landing-Page-Struktur)
   - Veröffentlichung via `actions/upload-pages-artifact@v3` + `actions/deploy-pages@v4`
   - Workflow-Permissions: `pages: write`, `id-token: write`
   — **erledigt** (2026-07-24): `.github/workflows/pages.yml` angelegt und committed; Feinschliff der Landing Page folgt in Phase 3.
3. ✅ Prüfen, ob am Cloudflare Worker `sveltia-cms-auth` eine `ALLOWED_DOMAINS`-Variable gesetzt ist; falls ja, die neue `*.github.io`- bzw. Custom-Domain ergänzen. — **erledigt** (2026-07-24): `jr-health.github.io` ist als erlaubte Domain hinterlegt. Ausreichend, da der Worker (`handleAuth` in `sveltia-cms-auth/src/index.js`) nur den vom CMS gesendeten `site_id`-Hostnamen exakt matcht, nicht Pfad oder Protokoll — der Pfad `/prenudge-health-profile/` der Project Page spielt daher keine Rolle. Bei einer späteren Custom Domain müsste diese zusätzlich ergänzt werden.
4. Smoke-Test: CMS unter der neuen GitHub-Pages-URL öffnen, Login testen, Teständerung speichern, prüfen dass sie als Commit auf `main` landet — identisch zum Verhalten auf `ig.dev.prenudge.at`.
5. ✅ `sveltia-cms-auth/` aus dem Arbeitsverzeichnis entfernen oder in `.gitignore` aufnehmen — **erledigt** (2026-07-23): Eintrag in der Root-`.gitignore` ergänzt, bestehender Worker bleibt unverändert in Betrieb.
6. ✅ Klarstellen (z. B. in `README.md`), dass `ig.dev.prenudge.at` weiterhin der manuell gepflegte Host ist und GitHub Pages ein zusätzlicher, automatisiert deployter Spiegel ist — damit künftig klar ist, welcher Weg wofür zuständig ist. — **erledigt** (2026-07-24): README-Hinweis ergänzt, ohne die interne Domain öffentlich zu nennen (siehe Design-Entscheidung 1 / Public-Repo-Rücksicht).

### Phase 2 — GitHub Actions Pipeline (Validate → Consolidate → Render)

7. ✅ **Voraussetzung — Templates an aktuelles Schema anpassen:** `render/templates/health-profile.{de,en}.md.j2` korrigieren, bevor die Pipeline produktiv geschaltet wird (siehe "Bekannter Template/Schema-Drift" oben):
   - categories: `c.description` → `c['description-professional']` und `c['description-laymen']`, beide nacheinander mit Zwischenüberschrift ("Beschreibung für Fachpersonal:" / "Information für Bevölkerung:")
   - dimensions: `d.description` → `d['description_professional']` und `d['description_layman']`, gleiches Muster
   - observations: `o.population` / `o['target-info']` entfernt (Testdaten zeigten reale Altlast-Inhalte in 2 Dateien, aber laut Nutzer aktuell reine Testdaten — Verlust akzeptiert)
   - observations: `o.description`/`o['citizen-info']` zusätzlich mit denselben Zwischenüberschriften ("Beschreibung für Fachpersonal:" / "Information für Bevölkerung:") versehen und direkt untereinander an den Anfang des Beobachtungsblocks verschoben (vorher stand die Bürgerinformation ganz am Ende, nach allen Messinstrument-Details, und war dadurch leicht zu übersehen)
   — **erledigt** (2026-07-24): Templates angepasst und lokal via `.\scripts\update-local.ps1` gegen echte Observation-Daten ("Minuten in moderater und intensiver körperlichen Aktivität") getestet — Report sieht wie erwartet aus. Categories/Dimensions-Zweig strukturell identisch, aber noch ohne befüllte Testdaten verifiziert.
8. ✅ `.github/workflows/update-profile.yml` neu anlegen, nach Vorbild von `.gitea/workflows/update-profile.yml`, mit folgenden Anpassungen:
   - `permissions: contents: write` explizit setzen (GitHub braucht das, Gitea nicht)
   - Trigger/Pfad-Filter unverändert übernehmen (`hp-categories/**`, `hp-dimensions/**`, `hp-observations/**`, `data-provider/**`, `scripts/**`, `render/templates/**`)
   - Committer-Identität auf `github-actions[bot]` ändern
   - Schritte (validate.py --strict, consolidate.py, render_doc.py, Commit mit `[skip ci]`) unverändert übernehmen
   — **erledigt** (2026-07-24): Datei angelegt; Push-Trigger vorerst auskommentiert (nur `workflow_dispatch` aktiv), bis Schritt 10 erfolgreich getestet wurde.
   **Nachtrag (2026-08-13):** Die committeten Markdown-Reports hießen ursprünglich
   `health-profile-v<Version>.{de,en}.md` — bei jedem Release/Test-Tag kam eine neue,
   versionierte Datei dazu, ohne dass alte je entfernt wurden (8 Dateien nach nur 3 echten
   Versionen, plus 2 kaputte Duplikate durch einen früheren Doppel-"v"-Bug). `render_doc.py`
   bekam ein `--latest`-Flag; `update-profile.yml` committet damit jetzt die unversionierten
   `health-profile.{de,en}.md` (analog zu `health-profile.json`, das ja auch nie versioniert
   war) — die Versionshistorie bleibt über Git-Log und die GitHub-Release-Assets erhalten,
   die `.md` (und `.docx`) sowieso schon pro Release ablegen (siehe Schritt 19/20). Alle acht
   alten versionierten Dateien aus dem Repo entfernt. `release.yml` (Schritt 19) ruft
   `render_doc.py` bewusst weiterhin **ohne** `--latest` auf, da dort der versionierte Name
   für das Release-Asset gebraucht wird.
9. ✅ Prüfen, ob auf `main` Branch-Protection-Regeln aktiv sind (z. B. „Require pull request before merging"). Falls ja: Bot als Bypass-Actor erlauben, oder Commit über einen PAT statt `GITHUB_TOKEN` durchführen. — **erledigt** (2026-07-24): Laut GitHub-Einstellungen sind keine Classic Branch Protections für `main` konfiguriert — der Commit-back des Workflows mit dem Standard-`GITHUB_TOKEN` sollte also ohne Bypass/PAT funktionieren.
10. ✅ Workflow einmal manuell (`workflow_dispatch`) testen, bevor er auf Push scharf geschaltet wird. — **erledigt** (2026-07-24): Testlauf grün, `github-actions[bot]` hat `health-profile.json` + beide Reports mit `chore: regenerate health profile v0.1.0 [skip ci]` zurückcommitted. Push-Trigger daraufhin aktiviert.
11. ✅ Entscheiden, ob `.gitea/workflows/update-profile.yml` und die Gitea-Runner-Infrastruktur parallel weiterlaufen (falls `health.joanneum.at/git` noch aktiv genutzt wird) oder stillgelegt werden — liegt außerhalb dieses Plans. — **erledigt** (2026-07-24): Das Gitea-Repository ist aktuell eingefroren und wird nicht weiter bearbeitet — es bleibt unverändert auf dem Stand vor der GitHub-Migration. `.gitea/workflows/update-profile.yml` wurde daher aus diesem Repo entfernt.

### Phase 3 — Sammel-/Browse-Ansicht + Sunburst auf der Page

12. ✅ Offener Punkt (siehe unten): zusätzlich zur Sunburst-Visualisierung eine tabellarische Browse-Ansicht (`scripts/render_html.py`, in `doc/transform-plan.md` vorgesehen, bisher nicht umgesetzt)? — **erledigt** (2026-07-24): Ja — als eigenes Design-Dokument `doc/browse-view-plan.md` ausgearbeitet und als Stufe 1 (MVP) umgesetzt. (Dokument am 2026-08-13 mit `doc/landing-page-plan.md` zu `doc/interactive-catalogue-plan.md` zusammengeführt, siehe dort.)
13. ✅ Falls ja: `scripts/render_html.py` + `render/templates/browse.html.j2` bauen (Jinja2, analog `render_doc.py`), Output nach `_site/browse.html`. — **erledigt** (2026-07-24): `scripts/render_html.py` + `render/templates/browse.{de,en}.html.j2` gebaut. Output sind zwei lokalisierte Dateien `render/browse.de.html` / `render/browse.en.html` (statt einer einzelnen `browse.html`), inkl. DE/EN-Sprachumschalter, Category/Dimension/Observation/Source-Type/FHIR-IG-Status/Sunburst-Status-Spalten, Commit-Link, Logo + Footer-Link zu `prenudge.at`, Corporate-Design-Farbe/-Schrift. Details und offene Ideen für Stufe 2 (Suche/Filter) siehe `doc/browse-view-plan.md`.
14. ✅ Landing Page `_site/index.html` erstellen: verlinkt Sunburst, ggf. Browse-Ansicht, Downloadlinks (Markdown, Word — siehe Phase 4), zeigt Version/Stand aus `health-profile.json` (`version`, `generated`). — **teilweise erledigt** (2026-07-24): Die Platzhalter-`index.html` in `pages.yml` verlinkt Sunburst, Browse (DE/EN) und CMS-Admin, und zeigt jetzt zusätzlich Version/Stand aus `health-profile.json` (via `jq` im Build-Schritt). Offen bleibt nur: Downloadlinks — die hängen an Phase 4 (Word-Export), die noch nicht umgesetzt ist. Eine richtige, gestaltete Landing Page (statt Platzhalter) folgt später.
15. ✅ `pages.yml` (Phase 1) um den Build-Schritt für `render_html.py` erweitern, falls Punkt 13 umgesetzt wird. — **erledigt** (2026-07-24): `_site/`-Build kopiert jetzt zusätzlich `render/browse.de.html` und `render/browse.en.html`.

### Phase 4 — Word-Export über AsciiDoc, gebunden an Releases

16. ✅ Neue Jinja2-Templates `render/templates/health-profile.de.adoc.j2` und `.en.adoc.j2` anlegen (Struktur analog zu den — dann korrigierten — `.md.j2`-Templates aus Phase 2, Schritt 7). — **erledigt** (2026-07-24): Templates angelegt, 1:1 strukturell analog (gleiche Sektionen/Reihenfolge/Fallbacks wie die `.md.j2`-Templates), inkl. expliziter `[[anchor]]`-IDs (via denselben `anchor`-Jinja-Filter) für die manuelle Inhaltsverzeichnis-Verlinkung. Noch nicht lauffähig getestet — dafür fehlen noch `scripts/render_adoc.py`/die Erweiterung von `render_doc.py` (Schritt 17) und die Konvertierungskette (Schritt 18). Bekannte Einschränkung: Rich-Text-Felder aus dem CMS liefern Markdown-artigen Inhalt (z. B. `[text](url)`-Links, `- `-Listen); das passt direkt für die `.md.j2`-Reports, aber AsciiDoc-Linksyntax (`link:url[text]`) und Listensyntax (`* item`) unterscheiden sich — bei reinem Fettdruck (`**text**`) kein Problem (in AsciiDoc auch gültig), bei Links/Listen innerhalb von Rich-Text-Feldern aber ein Real-Risiko für falsch gerendertes Word-Dokument. Zu prüfen, sobald in Schritt 17/18 gegen echte Testdaten gerendert wird.
17. ✅ `scripts/render_doc.py` um ein Ausgabeformat erweitern (z. B. `--format md,adoc`) oder separates `scripts/render_adoc.py` schreiben. — **erledigt** (2026-07-24): Separates `scripts/render_adoc.py` geschrieben (analog `render_doc.py`, gleicher `anchor`-Filter), statt `render_doc.py` zu erweitern — konsistent mit dem bereits für die Browse-Ansicht etablierten Muster "ein Skript pro Ausgabeformat" (`render_html.py`). Output: `health-profile-vX.Y.Z.<lang>.adoc` im Repo-Root, analog zu den `.md`-Reports. **Bewusst nicht** in `update-profile.yml` eingebunden — laut Design-Entscheidung 4 soll die AsciiDoc/Word-Erzeugung nur beim Release laufen, nicht bei jedem Push; Einbindung erfolgt erst in `release.yml` (Schritt 19).
18. ✅ Konvertierungs-Toolchain: `asciidoctor health-profile-vX.Y.Z.<lang>.adoc -b docbook -o -.xml | pandoc -f docbook -t docx -o health-profile-vX.Y.Z.<lang>.docx`. — **erledigt** (2026-07-24): Manuell End-to-End verifiziert (lokal `asciidoctor` per `gem install` ergänzt, `pandoc` war schon vorhanden). Titel/Überschriften 1–4 werden korrekt auf die Styles der Corporate-Vorlage (`render/templates/PräNUDGE Berichtsvorlage.docx`) gemappt, Aufzählungen (auch in Tabellenzellen) werden zu echten Word-Listen. Tabellen fielen zunächst auf Pandocs generischen `Table`-Style zurück (Vorlage hatte keinen Style exakt namens `Table`) — behoben durch einen geklonten Tabellen-Style (gleiche Formatierung wie `Table Grid`/„Tabellenraster", nur unter dem Namen `Table`), direkt in die `.docx` gepatcht und erneut verifiziert. Noch nicht in ein Skript/Workflow gegossen — folgt in Schritt 19 (`release.yml`).
19. ✅ Neuen Workflow `.github/workflows/release.yml` anlegen (Trigger: `push: tags: ['v*.*.*']`):
    - Checkout, Setup Python, Installation `asciidoctor` (Ruby) + `pandoc`
    - `validate.py --strict`, `consolidate.py --version <Tag ohne "v">`, `render_doc.py`
    - Neuer Adoc/Docx-Schritt aus 16–18
    - GitHub Release erstellen (z. B. `softprops/action-gh-release`) mit Assets: `health-profile.json`, beide `.md`, beide `.docx`
    - Löst darüber (Phase 1, Schritt 2) automatisch den `pages.yml`-Lauf aus, damit Sunburst + Downloadlinks unmittelbar den neuen Release zeigen (siehe Design-Entscheidung 5)
    — **erledigt** (2026-07-24): `release.yml` angelegt, zusätzlich mit `workflow_dispatch`-Input (Version) zum direkten Testen ohne Tag-Push, `tag_name` im Release-Schritt explizit gesetzt, damit beide Trigger-Wege denselben echten Tag/Release erzeugen. Version wird aus dem Tag-Namen (`vX.Y.Z` → `X.Y.Z`) bzw. dem manuellen Input abgeleitet. `pages.yml` um `workflow_run`-Trigger (wartet auf erfolgreichen `Release`-Lauf, nur bei `conclusion == 'success'`) ergänzt, zusätzlich `workflow_dispatch` als manuelles Handventil erhalten; Checkout nutzt `github.event.workflow_run.head_sha`, damit die Page exakt den getaggten Commit baut.
    Beim ersten echten Testlauf in GitHub Actions (nicht nur lokal wie in Schritt 18) zwei Fehler gefunden und behoben: (1) `gem install asciidoctor` schlug ohne `sudo` mit `Gem::FilePermissionError` fehl — der Runner-User hat keine Schreibrechte auf das System-Ruby-Gem-Verzeichnis, anders als bei einer lokalen Ruby-Installation. (2) Die ursprüngliche Annahme "`pandoc` ist auf `ubuntu-latest` vorinstalliert" war **falsch** — `pandoc: command not found`; jetzt per `sudo apt-get install -y pandoc` explizit installiert.
20. ✅ Downloadlinks auf der Landing Page zeigen auf
    `https://github.com/jr-health/prenudge-health-profile/releases/latest/download/health-profile-v<version>.<lang>.docx`
    — bleibt stabil, auch unabhängig vom genauen Pages-Rebuild-Zeitpunkt. — **erledigt** (2026-07-24): Platzhalter-`index.html` in `pages.yml` zeigt jetzt einen Downloadlink-Bereich ("Download Health Profile Metadata (DE | EN)") auf genau dieses stabile `releases/latest/download/...`-Muster. Beim ersten echten Test einen Bug gefunden und behoben: Die Version für den Link wurde ursprünglich aus dem committeten `health-profile.json` gelesen — da `release.yml` aber nichts zurückcommittet (Design-Entscheidung 4), konnte das von der tatsächlich released Version abweichen (v. a. beim Testen per `workflow_dispatch` mit frei gewählter Version). Jetzt wird die Version per `gh release view` direkt vom tatsächlichen GitHub-Release abgefragt. Zusätzlich: Branding-Angleichung an die Browse-Seiten (Logo `PräNUDGE_Logo.png`, `#004E64`, Verdana, "PreNUDGE Consortium"-Footer), "CMS editor" → "Metadata CMS Editor" umbenannt.
21. ✅ `doc/release.md` um den neuen Word-Export-Schritt ergänzen. — **erledigt** (2026-07-24): `doc/release.md` überarbeitet — beschreibt jetzt den automatisierten `release.yml`-Ablauf (inkl. Word-Export-Schritt: AsciiDoc → DocBook → Pandoc) statt des alten manuellen Gitea-Prozesses.

### Phase 5 — Test & Abnahme

22. ✅ Laufenden Arbeitsstand durchspielen: CMS-Änderung → Push → `update-profile.yml` regeneriert `health-profile.json`/Berichte → lokal per `python -m http.server` + `render/sunburst.html` reviewen (kein Pages-Deploy in diesem Schritt). — **erledigt** (2026-08-13): Vier neue Indicator Dimensions (`age`, `dietary-pattern`, `gender`, `socio-economic-status`) über die lokale CMS-Instanz angelegt, Commit `868a92f` auf `main` gepusht. `update-profile.yml` lief grün durch und hat per Bot-Commit `3ed72c7` (`chore: regenerate health profile v0.1.1-test [skip ci]`) `health-profile.json`, beide Markdown-Reports und die Browse-Views aktualisiert.
23. ✅ Release-Zyklus durchspielen: Tag pushen → `release.yml` → Release mit Assets → `pages.yml` läuft automatisch an → Sunburst/Downloadlinks auf der Page zeigen den neuen Stand. — **erledigt** (2026-08-13): Test-Tag `v0.1.2-test` gepusht, `release.yml` lief grün (Run erstellt Release `v0.1.2-test` mit allen 5 Assets: `health-profile.json`, beide `.md`, beide `.docx`), `pages.yml` sprang automatisch per `workflow_run` an und deployte erfolgreich. Live-Page zeigt „Version 0.1.2-test", Generiert `2026-08-13`, funktionierende Downloadlinks.
    **Dabei entdeckter Bug (bisher unbekannter Gotcha) — an der Wurzel behoben:** Ein Tag, der exakt auf einen Bot-Regenerate-Commit von `update-profile.yml` zeigt (Message enthielt `[skip ci]`), unterdrückte bei GitHub Actions **alle** Workflow-Läufe des Push-Events — nicht nur den ursprünglich gemeinten `update-profile.yml`-Lauf, sondern auch `release.yml`. Der erste Testversuch (Tag auf dem `[skip ci]`-Commit `3ed72c7`) löste dadurch **keinen** Release-Lauf aus, trotz korrektem Trigger-Pattern (`v*.*.*`), aktivem Workflow und unrestriktiven Actions-Permissions — verifiziert über die GitHub-API (`/actions/runs`, `/actions/workflows`, `/actions/permissions`) und den öffentlichen GitHub-Statuspage (keine Störung). Nach Neusetzen des Tags auf den vorherigen Commit (ohne `[skip ci]` in der Message) lief `release.yml` sofort korrekt an.
    **Root-Cause-Fix** (2026-08-13): `[skip ci]` in der Bot-Commit-Message (`update-profile.yml`) war für seinen eigentlichen Zweck (Loop-Prävention) redundant — der bestehende Pfad-Filter (`hp-categories/**`, `hp-dimensions/**`, `hp-observations/**`, `data-provider/**`, `scripts/**`, `render/templates/**`) schließt die vom Bot committeten Dateien (`health-profile.json`, `health-profile-v*.md`, `render/browse.*.html`) bereits vollständig aus — ein erneuter `push`-Lauf war also auch ohne `[skip ci]` nie möglich. Geprüft, dass kein anderer Workflow auf die Zeichenfolge angewiesen ist (kein `if: contains(..., '[skip ci]')` irgendwo im Repo). `[skip ci]` daher aus `update-profile.yml` entfernt (Commit-Message, Kommentar) und aus `doc/ci-setup.md`/`README.md` rausgenommen — damit kann künftig **jeder** Commit, auch ein Bot-Regenerate-Commit, gefahrlos als Tag-Ziel verwendet werden.
24. Rollback-Check: `ig.dev.prenudge.at` läuft unabhängig weiter (da ohnehin nie von dieser Pipeline berührt), falls GitHub Pages/Actions ausfällt. — **Code-seitig verifiziert** (2026-08-13): Keiner der drei Workflows (`update-profile.yml`, `release.yml`, `pages.yml`) referenziert oder deployt nach `ig.dev.prenudge.at`. **Noch offen:** praktische Bestätigung, dass der Host aktuell tatsächlich unabhängig erreichbar/funktionsfähig ist — noch nicht durchgeführt, muss nachgeholt werden.
25. ✅ `README.md` auf den aktuellen Stand bringen — beschreibt aktuell noch nicht die vollständige GitHub-Actions-/Pages-/Release-Pipeline, die im Zuge dieses Plans entstanden ist. — **erledigt** (2026-08-06, Commit `f92b2bb`): README beschreibt jetzt Datenmodell, Repository-Layout, lokale Build-Pipeline und alle drei Workflows (`update-profile.yml`, `release.yml`, `pages.yml`) inkl. Trigger/Wirkung, mit Verweis auf `doc/release.md` und `doc/github-actions-plan.md`.
26. Landing Page (`_site/index.html`) inhaltlich/gestalterisch überarbeiten — über die reine Branding-Angleichung aus Schritt 20 hinaus (echtes Layout statt Platzhalter-Listen). — **ausgelagert** in `doc/landing-page-plan.md` (2026-08-13): Ausgangslage, offene Fragen und Ideen dort festgehalten, analog zu `doc/browse-view-plan.md`. Umsetzung erfolgt erst, sobald dort Einigkeit besteht. (Am selben Tag mit `doc/browse-view-plan.md` zu `doc/interactive-catalogue-plan.md` zusammengeführt — die Vision hat sich erweitert: Sunburst wird direkt in die Landing Page eingebettet und steuert die Browse-Tabelle, statt beide Seiten nur zu verlinken.)
27. Word-Reports (`.docx`) nochmal durchsehen, sobald mehr echte Gesundheitsindikatoren erfasst sind — aktuelle Testdaten sind zu dünn, um Layout/Tabellenstruktur abschließend zu beurteilen (siehe auch Rückmeldung beim AsciiDoc-Ausarbeiten in Schritt 16/17). — **ausgelagert** in `doc/export-report-plan.md` (2026-08-13): als lebendes Backlog angelegt (kein abgeschlossener Plan wie bei Browse/Landing Page), da hier laut Rückmeldung noch einiges dazukommen wird, bevor überhaupt ein sinnvoller Review möglich ist.
