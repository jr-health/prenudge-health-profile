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
9. ✅ Prüfen, ob auf `main` Branch-Protection-Regeln aktiv sind (z. B. „Require pull request before merging"). Falls ja: Bot als Bypass-Actor erlauben, oder Commit über einen PAT statt `GITHUB_TOKEN` durchführen. — **erledigt** (2026-07-24): Laut GitHub-Einstellungen sind keine Classic Branch Protections für `main` konfiguriert — der Commit-back des Workflows mit dem Standard-`GITHUB_TOKEN` sollte also ohne Bypass/PAT funktionieren.
10. ✅ Workflow einmal manuell (`workflow_dispatch`) testen, bevor er auf Push scharf geschaltet wird. — **erledigt** (2026-07-24): Testlauf grün, `github-actions[bot]` hat `health-profile.json` + beide Reports mit `chore: regenerate health profile v0.1.0 [skip ci]` zurückcommitted. Push-Trigger daraufhin aktiviert.
11. ✅ Entscheiden, ob `.gitea/workflows/update-profile.yml` und die Gitea-Runner-Infrastruktur parallel weiterlaufen (falls `health.joanneum.at/git` noch aktiv genutzt wird) oder stillgelegt werden — liegt außerhalb dieses Plans. — **erledigt** (2026-07-24): Das Gitea-Repository ist aktuell eingefroren und wird nicht weiter bearbeitet — es bleibt unverändert auf dem Stand vor der GitHub-Migration. `.gitea/workflows/update-profile.yml` wurde daher aus diesem Repo entfernt.

### Phase 3 — Sammel-/Browse-Ansicht + Sunburst auf der Page

12. ✅ Offener Punkt (siehe unten): zusätzlich zur Sunburst-Visualisierung eine tabellarische Browse-Ansicht (`scripts/render_html.py`, in `doc/transform-plan.md` vorgesehen, bisher nicht umgesetzt)? — **erledigt** (2026-07-24): Ja — als eigenes Design-Dokument `doc/browse-view-plan.md` ausgearbeitet und als Stufe 1 (MVP) umgesetzt.
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
    — **erledigt** (2026-07-24): `release.yml` angelegt. `pandoc` ist auf `ubuntu-latest`-Runnern bereits vorinstalliert (kein `apt-get`/Action nötig, damit auch der zugehörige offene Punkt erledigt), `asciidoctor` wird per `gem install` ergänzt. Version wird aus dem Tag-Namen (`vX.Y.Z` → `X.Y.Z`) abgeleitet. `pages.yml` um `workflow_run`-Trigger (wartet auf erfolgreichen `Release`-Lauf, nur bei `conclusion == 'success'`) ergänzt, zusätzlich `workflow_dispatch` als manuelles Handventil erhalten; Checkout nutzt `github.event.workflow_run.head_sha`, damit die Page exakt den getaggten Commit baut. Noch nicht mit einem echten Tag getestet (kein `asciidoctor`/`pandoc`-Testlauf in GitHub Actions selbst, nur lokal manuell verifiziert in Schritt 18).
20. ✅ Downloadlinks auf der Landing Page zeigen auf
    `https://github.com/jr-health/prenudge-health-profile/releases/latest/download/health-profile-v<version>.<lang>.docx`
    — bleibt stabil, auch unabhängig vom genauen Pages-Rebuild-Zeitpunkt. — **erledigt** (2026-07-24): Platzhalter-`index.html` in `pages.yml` zeigt jetzt zusätzlich zwei Downloadlinks (DE/EN) auf genau dieses stabile `releases/latest/download/...`-Muster.
21. `doc/release.md` um den neuen Word-Export-Schritt ergänzen.

### Phase 5 — Test & Abnahme

22. Laufenden Arbeitsstand durchspielen: CMS-Änderung → Push → `update-profile.yml` regeneriert `health-profile.json`/Berichte → lokal per `python -m http.server` + `render/sunburst.html` reviewen (kein Pages-Deploy in diesem Schritt).
23. Release-Zyklus durchspielen: Tag pushen → `release.yml` → Release mit Assets → `pages.yml` läuft automatisch an → Sunburst/Downloadlinks auf der Page zeigen den neuen Stand.
24. Rollback-Check: `ig.dev.prenudge.at` läuft unabhängig weiter (da ohnehin nie von dieser Pipeline berührt), falls GitHub Pages/Actions ausfällt.

## Offene Punkte

- Landing Page `_site/index.html` (Phase 3.14): echte Gestaltung statt Platzhalter folgt später (Downloadlinks sind jetzt drin, siehe Schritt 20)
- **Neu:** Ideen für Browse-Ansicht Stufe 2+ (Suche/Filter, Pagination, Collapsables,
  kombinierter Export-Button CSV/Word) sind in `doc/browse-view-plan.md` festgehalten, aber
  noch nicht umgesetzt/final spezifiziert
- **Neu:** Beim Ausarbeiten der AsciiDoc-Templates (Schritt 16) entdeckt: `terminology-codes`
  ist laut aktuellem `admin/config.yml` dem Messinstrument zugeordnet (verschachteltes Feld),
  in den bestehenden JSON-Daten (z. B. `hp-observations/minutes-moderate-physical-activity.json`)
  aber weiterhin auf Observation-Ebene abgelegt. Templates (Markdown **und** AsciiDoc) lesen
  bewusst weiterhin von der Observation-Ebene, um bestehende Inhalte nicht unsichtbar zu
  machen — echte Migration der Daten auf Messinstrument-Ebene wäre nötig, falls das
  behoben werden soll.
- **Neu:** `qualification` (App-Provider-Anforderung) und `app-providers` (Qualifizierte
  App-Provider) sind Felder pro Messinstrument in `admin/config.yml`, werden aber in keinem
  der Report-Templates (Markdown, AsciiDoc) gerendert — fachlich zu klären, ob das gewünscht
  ist.
- **Neu (später, optional):** Das Feld `vis-status` (pro Measurement Instrument, Werte
  u. a. `draft`/`published`) ist laut Hint-Text im Schema für genau diesen Zweck gedacht
  ("PreNUDGE Sunburst Chart Status"), wird aber von `render/sunburst.html` aktuell nicht
  ausgewertet. Könnte ergänzend zur Release-Gate-Entscheidung (Design-Entscheidung 5)
  genutzt werden, um selbst innerhalb eines Releases einzelne noch nicht fertige Einträge
  aus dem Sunburst auszublenden — kein Blocker für den Start, da vorerst kein Eintrag
  öffentlich sichtbar wird, der nicht zumindest durch einen Release gelaufen ist.
