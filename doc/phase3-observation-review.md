# Phase 3 review sheet: observation titles/content after hiding indicator dimensions

Draft for review — nothing in `hp-observations/*.json` has been edited yet. Once you've
marked up decisions below (inline comments, or however you prefer), Phase 4 applies the
approved changes to the JSON files.

Drafted by reading every category/dimension/observation JSON file in full (both `de` and
`en` blocks), then spot-checked against source for factual accuracy (data-bug claims,
key/filename mismatches, placeholder text) before being compiled here.

## How to read this

Each observation gets: current title, proposed title (or "no change"), proposed
description-professional / description-laymen text, proposed `verified-health-links`, and
notes. Two note tags recur throughout:

- **NEEDS YOUR DECISION** — a judgment call with no clearly-correct default (usually: what
  happens to a multi-observation dimension's shared content, or a title/scope ambiguity).
- **PRE-EXISTING ISSUE** — a data bug or content-quality problem that predates this
  flattening work, surfaced because drafting this sheet required reading every file closely.
  Most are proposed as fixed inline (typos, formatting); a few are flagged only, where fixing
  them isn't a formatting call.

## Top-level summary — things most worth your attention first

**Real data bugs found (independent of the dimension-merge):**
- `potential-access-barriers` (dimension `access-to-care`, category `psychosocial-factors`)
  has `category: "sociodemographic-data"` in its own JSON — filed under the wrong category.
- `workability-worksoc-wai`'s professional description contains a literal unresolved author
  note: `"Illmarinen, J. – hier fehlt die Referenz"` (reference missing) — still in production
  content.
- `hp-observations/minutes-moderate-physical-activity-per-week.json` has `key: "steps-per-day"`
  and `id_tech: "minutes-moderate-physical-activity-per-week"` — filename, key, and id_tech are
  three different strings.
- `hp-observations/residence-and-housing-type.json` has `key: "residence"` — filename doesn't
  match key.
- `hp-dimensions/e-zigaretten-tabakerhitzer.json`'s EN `title` is literally `"Anzahl pro Woche"`
  (German for "number per week") — an EN field left in German. Same defect on the *observation*
  level for `stark-verarbeitete-lebensmittel` (EN title = the German phrase verbatim).
- `steps-per-day`'s DE `target-info` ("Mindestens 150–300 Minuten moderater oder intensiver
  körperlicher Aktivität pro Woche…") is the **endurance-oriented-activity** guideline copy-pasted
  in — contradicts its own dimension's "no scientific target exists" statement.

**Multi-observation dimensions needing an explicit fold/duplicate/drop decision:**
`heigth-weight` (3 obs), `dietary-pattern` (7 obs), `everyday-activity` (2 obs),
`sleep-quality` (2 obs), `socio-economic-status` (3 obs), `workability` (4 obs). Defaults are
proposed per case below; none are applied yet.

**Systemic, catalogue-wide gap (not fixed here):** almost every EN `description`/`citizen-info`
field is empty where DE has full text. Flagged per-observation below as "needs translation,"
not translated by this pass — likely the largest follow-up task after this merge lands.

---

## Category: Alcohol (alcohol)

Category DE has no `description`; EN has an empty `"description": ""`. Not otherwise in scope.

### Dimension: Consumption frequency (consumption-frequency) — 1 observation

#### Observation: alcohol-consumption-frequency
- Current title: EN "Alcohol consumption frequency" / DE "Konsumhäufigkeit"
- Proposed title: EN unchanged / DE **"Konsumhäufigkeit von Alkohol"** — DE currently duplicates the dimension title and gives no context once the dimension no longer renders; EN already stands alone.
- Proposed description-professional (DE): unchanged text, minus the inline "Weiterführende Links:" + 4 URLs (moved to the links field below):
  > Dieser Gesundheitsindikator zeigt auf, wie häufig die Personen in den vergangenen 12 Monaten Alkohol konsumiert haben.
  > Definition: nicht erforderlich
  > Empfehlung: 0 Getränke pro Tag:
  > „To identify a "safe" level of alcohol consumption... [World Health Organization, 2023, full quote unchanged]
- Proposed description-professional (EN): empty — **NEEDS YOUR DECISION** (needs translation, not fabricated here).
- Proposed description-laymen (DE, citizen-info): unchanged text minus the "Weiterführende Links:" + 6 URLs + bare "Handbuch..." title-with-no-URL line (moved below):
  > „Gesundheitliche Vorteile hat Alkohol nicht..." (IQWiG, 2023a/b quotes, unchanged)
- Proposed description-laymen (EN): empty — same NEEDS YOUR DECISION.
- Proposed verified-health-links (carried verbatim from the dimension's own list, all `audience: []` in the source):
```json
[
  {"title":"Alkoholleitlinie","url":"https://alkoholleitlinie.de/","audience":[],"note":""},
  {"title":"S3-Leitlinie alkoholbezogene Störungen","url":"https://register.awmf.org/assets/guidelines/076-001l_S3-Screening-Diagnose-Behandlung-alkoholbezogene-Stoerungen_2025-01-verlaengert.pdf","audience":[],"note":""},
  {"title":"Deutsche Hauptstelle für Suchtfragen","url":"https://www.dhs.de/","audience":[],"note":""},
  {"title":"Deutsche Gesellschaft für Suchtforschung","url":"https://www.dg-sucht.de/","audience":[],"note":""},
  {"title":"Alkoholprävention (Gesundheitsfonds Steiermark)","url":"https://gesundheitsfonds-steiermark.at/alkoholpraevention/","audience":[],"note":""},
  {"title":"gesundheitsinformation.de: Alkohol","url":"https://www.gesundheitsinformation.de/alkohol.html","audience":[],"note":""},
  {"title":"gesundheitsinformation.de: Acht Fakten über Alkohol","url":"https://www.gesundheitsinformation.de/acht-fakten-ueber-alkohol.html","audience":[],"note":""},
  {"title":"gesundheitsinformation.de: Ab wann ist Alkohol schädlich?","url":"https://www.gesundheitsinformation.de/ab-wann-ist-alkohol-schaedlich.html","audience":[],"note":""},
  {"title":"gesundheitsinformation.de: Wie wirkt Alkohol?","url":"https://www.gesundheitsinformation.de/wie-wirkt-alkohol-und-wie-schnell-wird-er-abgebaut.html","audience":[],"note":""},
  {"title":"Sozialministerium: Alkohol","url":"https://www.sozialministerium.gv.at/Themen/Gesundheit/Drogen-und-Sucht/Alkohol.html","audience":[],"note":""}
]
```
- Notes:
  - **NEEDS YOUR DECISION** — dimension `audience` is `[]` on all 10 links, but the pre-existing manual split (4 in the professional prose, 6 in layman) implies an intended split. Default keeps `audience: []` (matches the authoritative source); optionally tag the first 4 `["Healthcare professionals"]` and the rest `["Laymen / citizens"]` if you want to preserve that inferred split.
  - **NEEDS YOUR DECISION** — "Handbuch: Alkoholkonsum und mögliche Folgen (Bundesministerium...)" is referenced by title with no URL anywhere. Either find the URL and add an 11th link, or drop the mention.
  - **PRE-EXISTING ISSUE** — EN `description`/`citizen-info` entirely empty (dimension's EN was too) — no English text exists yet at all, only German.

---

## Category: Anthropometry (anthropometry)

### Dimension: Height, weight (heigth-weight) — 3 observations — NEEDS YOUR DECISION

The dimension's BMI definition/formula/categories and its one link are already duplicated into
**body-height-weight-bmi** only — not relevant to its siblings' own self-contained content.
**Default: fold into body-height-weight-bmi only; drop for the other two.**

#### Observation: body-height-weight-bmi
- Current title: EN "Body height, weight and BMI" / DE "Körpergröße und Körpergewicht" — no change.
- Proposed description-professional: unchanged (already merged in verbatim; no inline URL dump inside `description` itself to clean up).
- Proposed description-laymen (DE, citizen-info): unchanged minus the inline "Weiterführende Links:" URL (moved below).
- Proposed verified-health-links:
```json
[{"title":"Was sagt der Body-Mass-Index über die Gesundheit aus?","url":"https://www.gesundheitsinformation.de/was-sagt-der-body-mass-index-ueber-die-gesundheit-aus.html","audience":[],"note":""}]
```
- Notes: EN description/laymen empty — needs translation.

#### Observation: waist-circumference
- Current title: EN "Waist circumference (cm)" / DE "Taillen-/Bauchumfang (cm)" — no change, already standalone.
- Proposed description-professional/laymen: no change (empty; dimension's BMI content not applicable).
- Proposed verified-health-links: none — **NEEDS YOUR DECISION**: confirm "drop, not applicable" default.
- Notes: **PRE-EXISTING ISSUE** — DE `norms.specific-norm` ("Bei über 88 cm bei Frauen und 102 cm bei Männern...") has no EN equivalent; out of scope here but worth a translation ticket.

#### Observation: waist-to-hip-ratio
- Current title: EN "Waist-to-hip ratio (WHR)" / DE "Hüft-Taillen-Verhältnis" — no change, already standalone.
- Proposed description-professional/laymen: no change (self-contained WHR text already, unrelated to BMI).
- Proposed verified-health-links: none — **NEEDS YOUR DECISION**: confirm "drop, not applicable" default.
- Notes: **PRE-EXISTING ISSUE (minor, not part of this merge)** — DE title "Hüft-Taillen-Verhältnis" vs. body text "Hüft-Taille-Verhältnis" (singular/plural inconsistency), and title word order doesn't match the WHR/EN convention. **PRE-EXISTING ISSUE** — DE `norms.specific-norm` contains a broken markdown table (missing header row) that likely won't render correctly.

---

## Category: Nutrition (nutrition)

### Dimension: Dietary pattern (dietary-pattern) — 7 observations — NEEDS YOUR DECISION

The dimension's general food-pyramid/FBDG text and all 8 links are already duplicated into
**dietary-pattern-athis** only. The other 6 food-group observations each have their own
distinct, self-contained text unrelated to the general framing. **Default: fold into
dietary-pattern-athis only; drop for the other six** (with one link-level exception noted below).

#### Observation: dietary-pattern-athis
- Current title: EN "Dietary pattern (ATHIS)" / DE "Gemüse- und Obstkonsum (Portionen/Tag)"
- Proposed title: DE unchanged / EN **"Fruit and vegetable consumption (portions/day) (ATHIS)"** — **PRE-EXISTING ISSUE**: current EN title names the whole dimension theme, not what this observation actually measures (fruit/veg portions); doesn't match DE's scope at all.
- Proposed description-professional (DE): unchanged minus the inline "Weiterführende Links:" + 3 URLs (moved below):
  > Bei diesem Gesundheitsindikator werden die konsumierten Portionen an Obst und Gemüse sowie die Konsumhäufigkeit von fett-, zucker- und salzreichen Lebensmitteln abgefragt.
  > Definition: „Bei den österreichischen Ernährungsempfehlungen..." (BMASGPK, 2026b, unchanged)
  > Empfehlung: 2 Ernährungspyramiden (Bilder) (AGES, n.d.)
- Proposed description-laymen (DE): unchanged minus "Weiterführende Links:" + 5 URLs (moved below).
- Proposed verified-health-links:
```json
[
  {"title":"Ernährungsempfehlungen: Fleisch und Fisch","url":"https://ernaehrungsempfehlung.at/empfehlungen/fleisch-und-fisch/","audience":[],"note":""},
  {"title":"DGEM-Leitlinien","url":"https://www.dgem.de/leitlinien","audience":[],"note":""},
  {"title":"AWMF-Leitlinien Ernährungsmedizin","url":"https://register.awmf.org/de/leitlinien/aktuelle-leitlinien/fachgesellschaft/073","audience":[],"note":""},
  {"title":"Österreichische Ernährungspyramide","url":"https://ernaehrungsempfehlung.at/empfehlungen/#mit-fisch-und-fleisch","audience":[],"note":""},
  {"title":"Rezepte zum Nachkochen","url":"https://ernaehrungsempfehlung.at/rezepte-zum-nachkochen/","audience":[],"note":""},
  {"title":"Fragen und Antworten rund um die Ernährungsempfehlungen","url":"https://ernaehrungsempfehlung.at/wichtig-zu-wissen/","audience":[],"note":""},
  {"title":"FGÖ-Ernährungsbroschüre 2025","url":"https://fgoe.org/sites/fgoe.org/files/2025-01/fgoe_ernaehrungsbroschuere_2025_bfrei.pdf","audience":[],"note":""},
  {"title":"Gesunde Ernährung (Gesundheitsfonds Steiermark)","url":"https://gesundheitsfonds-steiermark.at/gesunde-ernaehrung/","audience":[],"note":""}
]
```
- Notes:
  - **NEEDS YOUR DECISION** — "Ernährungsempfehlungen: Fleisch und Fisch" is also directly relevant to `fisch-fleisch-portionen-woche` (see below); default duplicates it there too.
  - **NEEDS YOUR DECISION** — should the general FBDG framing sentence instead live on the `nutrition` category's own description field (currently empty) rather than one specific observation, since it describes the whole food-pyramid approach, not just fruit/veg? Default keeps it here to minimize scope.

#### Observation: milchprodukte-oele-fette-nuesse-samen-portionen-pro-tag
- Current title: unchanged (EN "Dairy products, oils, fats, nuts, and seeds – portions per day" / DE "Milchprodukte/Öle/Fette/Nüsse/Samen (Portionen/Tag)") — already standalone.
- Proposed description-professional/laymen: no change — has its own self-contained dairy-portion text.
- Proposed verified-health-links: none — **NEEDS YOUR DECISION**: confirm "drop, not applicable."

#### Observation: getreide-erdaepfel-portionen-pro-tag
- Current title: EN "Cereales Potatoes Portions per day" / DE "Getreide/Erdäpfel/Reis/Nudeln (Portionen/Tag)"
- Proposed title: DE unchanged / EN **"Cereals, potatoes, rice, and pasta – portions per day"** — **PRE-EXISTING ISSUE**: "Cereales" is a spelling error (not an English word), and the EN title omits "Reis/Nudeln" (rice/pasta) that DE explicitly includes — a content mismatch, not just a typo. Formatting aligned to the en-dash convention used by siblings.
- Proposed description-professional/laymen: no change — has its own self-contained grains/potatoes text.
- Proposed verified-health-links: none — **NEEDS YOUR DECISION**: confirm "drop, not applicable."

#### Observation: fisch-fleisch-portionen-woche
- Current title: EN "fish-meat portions week" / DE "Fisch/Fleisch (Portionen/Woche)"
- Proposed title: DE unchanged / EN **"Fish and meat – portions per week"** — **PRE-EXISTING ISSUE**: all-lowercase, missing "and"/"per", doesn't match sibling formatting.
- Proposed description-professional/laymen: no change — has its own self-contained meat/fish guidance.
- Proposed verified-health-links — **NEEDS YOUR DECISION**: default adds the one dimension link that's topically specific to this observation:
```json
[{"title":"Ernährungsempfehlungen: Fleisch und Fisch","url":"https://ernaehrungsempfehlung.at/empfehlungen/fleisch-und-fisch/","audience":[],"note":""}]
```

#### Observation: alkoholfreie-ungesuesste-getraenke-glaeser-tag
- Current title: unchanged — already standalone, well-formatted.
- Proposed description-professional/laymen: no change — self-contained fluid-intake guidance.
- Proposed verified-health-links: none — **NEEDS YOUR DECISION**: confirm "drop, not applicable."

#### Observation: stark-verarbeitete-lebensmittel
- Current title: EN "stark verarbeitete Lebensmittel" / DE "stark verarbeitete Lebensmittel (Portionen/Tag)"
- Proposed title: DE **"Stark verarbeitete Lebensmittel (Portionen/Tag)"** (capitalize, matching sibling convention) / EN **"Highly processed foods (portions/day)"** — **PRE-EXISTING ISSUE**: this is the "EN title left in German" case — the EN field currently just contains the German phrase verbatim, untranslated.
- Proposed description-professional/laymen: no change — both empty; general dietary-pattern text isn't a good fit for processed foods specifically.
- Proposed verified-health-links: none.
- Notes: this is currently the most content-sparse of the 7 (no description, citizen-info, norms, sources, terminology codes) — worth a separate content pass outside this task.

#### Observation: huelsenfruechte-portionen-pro-woche
- Current title: unchanged (EN "Legume portions per week" / DE "Hülsenfrüchte (Portionen/Woche)") — both standalone.
- Proposed description-professional/laymen: no change — self-contained legume-portion guidance.
- Proposed verified-health-links: none — **NEEDS YOUR DECISION**: confirm "drop, not applicable."

---

## Category: Physical Activity (physical-activity)

**PRE-EXISTING ISSUE (category-level, relevant to this whole effort):** the category's DE
`description-professional`/`description-laymen` literally enumerates the (now-hidden) dimensions
by name and number ("...zu welcher die folgenden Gesundheitsindikatoren gehören: 1.
Ausdauerorientierte Aktivität 2. Muskelkräftigende Übungen 3. Alltagsaktivität sowie 4.
Sitzen") — missing the 5th dimension (**Flexibility and Balance**) entirely, and about to point
readers at headings that no longer exist once dimensions stop rendering. EN category has no such
fields at all (DE-only). **NEEDS YOUR DECISION**: rewrite this text (drop the enumeration entirely,
list observations instead, or at minimum add the missing 5th item) — and write an EN version once
decided.

### Dimension: Sitting (sitting) — 1 observation

#### Observation: sitting-hours-per-day
- Current title: EN "Sitting time (hours/day)" / DE "Sitzen"
- Proposed title: EN unchanged / DE **"Sitzzeit (Stunden/Tag)"** — DE duplicates the dimension title with no unit; mirrors EN's pattern.
- Proposed description-professional: unchanged (dimension's WHO(2020) definition already merged in verbatim; no inline URLs inside `description` itself).
- Proposed description-laymen (DE): unchanged minus "Nähere Informationen..." + "Weiterführende Links:" block (4 URLs total, moved below).
- Proposed verified-health-links:
```json
[
  {"title":"Österreichische Bewegungsempfehlungen","url":"https://fgoe.org/sites/fgoe.org/files/2022-01/WB_17_bewegungsempfehlungen_bfrei.pdf","audience":[],"note":""},
  {"title":"Die Bewegungsrevolution (Gesundheitsfonds Steiermark)","url":"https://diebewegungsrevolution.at/bewegung-tipps/","audience":[],"note":""},
  {"title":"Sitzverhalten (Robert Koch-Institut)","url":"https://www.gbe.rki.de/DE/Themen/EinflussfaktorenAufDieGesundheit/GesundheitsUndRisikoverhalten/KoerperlicheAktivitaet/Sitzen/sitzen_node.html?darstellung=0&kennzahl=1&zeit=2019&geschlecht=0&standardisierung=0","audience":[],"note":""},
  {"title":"WHO guidelines on physical activity and sedentary behaviour","url":"https://iris.who.int/server/api/core/bitstreams/faa83413-d89e-4be9-bb01-b24671aef7ca/content","audience":[],"note":""}
]
```

### Dimension: Muscle-strengthening exercises (muscle-strengthening-exercises) — 1 observation

#### Observation: muscle-strengthening-exercises-daysweek
- Current title: EN "Muscle-strengthening exercises (days/week)" / DE "Muskelkräftigende Übungen"
- Proposed title: EN unchanged / DE **"Muskelkräftigende Übungen (Tage/Woche)"** — same "DE title = bare dimension title" pattern as sitting.
- Proposed description-professional: unchanged minus the inline "Weiterführende Links:" (2 URLs, moved below) that sat between "Definition" and "Empfehlung."
- Proposed description-laymen: unchanged minus trailing "Weiterführende Links:" (2 URLs, moved below).
- Proposed verified-health-links (WB_17 appeared twice in source prose; deduplicated to match the dimension's own 3-item list):
```json
[
  {"title":"Österreichische Bewegungsempfehlungen","url":"https://fgoe.org/sites/fgoe.org/files/2022-01/WB_17_bewegungsempfehlungen_bfrei.pdf","audience":[],"note":""},
  {"title":"WHO guidelines on physical activity and sedentary behaviour","url":"https://iris.who.int/server/api/core/bitstreams/faa83413-d89e-4be9-bb01-b24671aef7ca/content","audience":[],"note":""},
  {"title":"Broschüre Bewegung","url":"https://fgoe.org/sites/fgoe.org/files/2023-03/Broschuere_Bewegung_2023_bfrei_0.pdf","audience":[],"note":""}
]
```

### Dimension: Everyday activity (everyday-activity) — 2 observations — NEEDS YOUR DECISION

The dimension's Alltagsbewegung text (walking, gardening, stairs) and its 3 links are already
duplicated into **steps-per-day** (plausible — the dimension's own examples are step/walking-
centric). Its sibling **zeit-leichte-koerperliche-aktivitaet** has nothing folded in and is
currently a completely bare stub (no description, citizen-info, discussion, norms, sources, or
terminology codes at all). **Default: fold into steps-per-day only; leave the light-activity
observation as a stub for now** — but it will read contextless once the dimension heading is
gone; flagging that gap rather than inventing content for it.

#### Observation: steps-per-day (file: `hp-observations/minutes-moderate-physical-activity-per-week.json`)
- **PRE-EXISTING ISSUE** (confirmed against source): file is named `minutes-moderate-physical-activity-per-week.json`, but `key` = `"steps-per-day"` and `id_tech` = `"minutes-moderate-physical-activity-per-week"` — three different names where CLAUDE.md says the filename should derive from `key`. Looks like a repurposed/renamed observation where filename and id_tech were never updated.
- Current title: EN "Steps (per day)" / DE "Schrittzahl (pro Tag)" — no change, already standalone and consistent.
- Proposed description-professional: unchanged (dimension's definition already merged in, own intro sentence kept).
- Proposed description-laymen (DE): unchanged minus trailing "Weiterführende Links:" (3 URLs, moved below).
- Proposed verified-health-links:
```json
[
  {"title":"Die Bewegungsrevolution (Gesundheitsfonds Steiermark)","url":"https://diebewegungsrevolution.at/bewegung-tipps/","audience":[],"note":""},
  {"title":"Österreichische Bewegungsempfehlungen","url":"https://fgoe.org/sites/fgoe.org/files/2022-01/WB_17_bewegungsempfehlungen_bfrei.pdf","audience":[],"note":""},
  {"title":"Broschüre Bewegung","url":"https://fgoe.org/sites/fgoe.org/files/2023-03/Broschuere_Bewegung_2023_bfrei_0.pdf","audience":[],"note":""}
]
```
- **PRE-EXISTING ISSUE (significant, found while reading, confirmed against source):** DE `target-info` reads "Mindestens 150–300 Minuten moderater oder intensiver körperlicher Aktivität pro Woche…" — this is literally the **endurance-oriented-activity** dimension's guideline (150–300 min moderate/vigorous activity/week), not a steps target, and directly contradicts the everyday-activity dimension's own "Empfehlung: Kein wissenschaftlicher Zielwert vorhanden" (no scientific target exists). Looks copy-pasted from `minutes-moderate-physical-activity`. Needs a real steps target or removal — a content fix independent of the merge, but surfaced by this review.

#### Observation: zeit-leichte-koerperliche-aktivitaet
- Current title: EN "Time of light physical activity per day" / DE "leicht körperlicher Aktivität (Minuten/Tag)"
- Proposed title: DE **"Leichte körperliche Aktivität (Minuten/Tag)"** (capitalize + fix adjective agreement: "leicht"→"leichte") / EN **"Light physical activity (minutes/day)"** (aligns to sibling's "(unit/period)" pattern) — **PRE-EXISTING ISSUE**: DE grammar error + lowercase start; EN uses a different structural pattern than its sibling.
- Proposed description-professional/laymen: **NEEDS YOUR DECISION** — both empty, and per the default above the dimension's shared text is routed to `steps-per-day` instead. If this observation should read as more than a bare title once the dimension disappears, it needs new standalone content — not proposed here since there's no leftover dimension-specific text to give it.
- Proposed verified-health-links: none (per default above).
- Notes: thinnest entry found across the whole review — no description, citizen-info, discussion, norms, sources, or terminology codes.

### Dimension: Endurance oriented activity (endurance-oriented-activity) — 1 observation

#### Observation: minutes-moderate-physical-activity
- Current title: EN "Minutes in moderate and vigouros physical activity" / DE "Moderater und intensiver körperlichen Aktivität (Minuten/Woche)"
- Proposed title: DE **"Moderate und intensive körperliche Aktivität (Minuten/Woche)"** (fixes broken adjective declension) / EN **"Minutes of moderate and vigorous physical activity (per week)"** (fixes typo "vigouros"→"vigorous"; "Minutes of" flagged as an optional wording improvement beyond the pure typo fix).
- Proposed description-professional (DE) — fresh merge, this observation's DE description had not yet had the dimension text copied in (previously just the intro sentence):
  > Dieser Gesundheitsindikator zeigt auf, wie viel ausdauerorientierte Aktivität die Personen pro Woche betreiben.
  > Definition: „Ausdauerorientierte Bewegung/Ausdauertraining..." (Fonds Gesundes Österreich, 2020, full text unchanged)
  > Empfehlung für gesunde Erwachsene: „Die Österreichischen Bewegungsempfehlungen..." (unchanged)
- Proposed description-professional (EN): keep existing text unchanged — it's already a standalone English summary (independently written, not a translation): "_Endurance based physical activity indicator dimension covers total weekly minutes of moderate and vigorous aerobic activity and compliance with recommended thresholds (≥150 min moderate or ≥75 min vigorous activity/week)._"
- Proposed description-laymen (DE) — fresh merge, was previously completely empty: dimension's full layman text (Fonds Gesundes Österreich 2020 + Robert Koch-Institut 2025 quotes), unchanged.
- Proposed description-laymen (EN): keep existing text, but fix a confirmed typo: "endenced-based" → **"evidence-based"**.
- Proposed verified-health-links (dimension has real audience tags here — carried over):
```json
[
  {"title":"Österreichische Bewegungsempfehlungen","url":"https://fgoe.org/sites/fgoe.org/files/2022-01/WB_17_bewegungsempfehlungen_bfrei.pdf","audience":["Healthcare professionals","Laymen / citizens"],"note":""},
  {"title":"Broschüre Bewegung","url":"https://fgoe.org/sites/fgoe.org/files/2023-03/Broschuere_Bewegung_2023_bfrei_0.pdf","audience":["Laymen / citizens"],"note":""},
  {"title":"WHO guidelines on physical activity and sedentary behaviour","url":"https://iris.who.int/server/api/core/bitstreams/faa83413-d89e-4be9-bb01-b24671aef7ca/content","audience":["Healthcare professionals"],"note":""},
  {"title":"Broschürenbestellung","url":"https://fgoe.org/broschuerenbestellung","audience":["Laymen / citizens"],"note":""}
]
```
- Notes: **PRE-EXISTING ISSUE** — dimension's EN links list had a duplicated audience value (`["Laymen / citizens","Laymen / citizens"]`) on "Broschürenbestellung," cleaned to a single value above. **PRE-EXISTING ISSUE (out of scope)** — this observation's first measurement-instrument EN `sources` array has a duplicate identical entry; noted, not part of this task's target fields.

### Dimension: Flexibility and balance (flexibility-and-balance) — 1 observation

#### Observation: lessons-per-week
- Current title: EN "lessons per week" / DE "Beweglichkeits/Flexibilitätseinheiten (Einheiten/Woche)"
- Proposed title: EN **"Flexibility units (units/week)"** / DE unchanged — **PRE-EXISTING ISSUE**: EN title is generic, lowercase, and doesn't reflect the DE title's actual meaning at all; won't stand alone once the dimension disappears.
- Proposed description-professional/laymen: no change — dimension is completely empty (no description, no links).
- Proposed verified-health-links: none.
- Notes: **NEEDS YOUR DECISION** — the dimension is titled "Flexibility **and Balance**," but neither the dimension nor its one child (flexibility-only) addresses balance at all. Once the dimension vanishes, the "balance" half of this indicator area has no home anywhere. Options: leave as-is, add a note to this observation that balance isn't yet covered, or create a dedicated balance observation later — flagging, not resolving. **PRE-EXISTING ISSUE** — DE `specific-questions` field literally contains placeholder text ("Frage hinein! Antwortmöglichkeiten") — this observation is still a stub.

---

## Category: Psychosocial Factors (psychosocial-factors)

Category file has no description fields — nothing to flag there.

### Dimension: Access to care (access-to-care) — 1 observation
Dimension completely empty (both locales) — nothing to merge.

#### Observation: potential-access-barriers
- Current title: unchanged (EN "Potential access barriers" / DE "Potenzielle Zugangshindernisse") — already stands alone.
- Proposed description-professional/laymen: no change — dimension had nothing to contribute.
- Proposed verified-health-links: none.
- Notes:
  - **PRE-EXISTING ISSUE, confirmed against source** — this observation's own `category` field is `"sociodemographic-data"` in both locales, but its dimension (`access-to-care`) belongs to `psychosocial-factors`. Recommend correcting the `category` field to `"psychosocial-factors"` — right now it files under the wrong category page/sunburst wedge, independent of this merge.
  - **PRE-EXISTING ISSUE** — EN `citizen-info` empty while DE has content — missing translation.

### Dimension: Chronic stress (chronic-stress) — 1 observation
Dimension's DE text (WHO 2026/APA 2024 definitions) is already fully duplicated into the
observation, verbatim — nothing further to merge. EN empty on both sides, no links either side.

#### Observation: perceived-stress-pss
- Current title: unchanged (EN "Perceived stress (PSS-4 / PSS-10)" / DE "Chronischer Stress") — DE duplicates the dimension title but still reads fine standalone (age/gender precedent).
- Proposed description-professional/laymen (DE): unchanged — already the dimension's own text verbatim, no dedup or trimming needed.
- Proposed verified-health-links: none.
- Notes: **NEEDS YOUR DECISION** — EN description/laymen empty on both dimension and observation; who supplies the EN text (direct translation, or reuse the English-language WHO/APA quotes already embedded in the DE field)? **Optional cosmetic** — DE title could gain the instrument suffix "(PSS-4 / PSS-10)" for parity with EN, not required.

### Dimension: Coping ability (coping-ability) — 1 observation
Dimension completely empty — nothing to merge.

#### Observation: self-reported-resilience
- Current title: unchanged — no change needed.
- Proposed description-professional/laymen: no change (empty, nothing to merge).
- Proposed verified-health-links: none.
- Notes: not merge-related, but surfaced while reading — the observation's own `discussion` field (identical DE/EN) says "*Es muss erst entschieden werden, ob wir diesen Indikator behalten oder nicht" (still undecided whether to keep this indicator at all) — a pre-existing open question, unrelated to this task.

### Dimension: Emotional distress (emotional-distress) — 1 observation
Dimension has DE definition text (RKI 2026) + 7 titled links (`audience: []` each); EN
description empty, EN links list has the same 7 URLs with blank titles plus 4 stray fully-blank
entries.

#### Observation: emotional-distress-phq2
- Current title: unchanged (EN "Emotional distress (PHQ-2)" / DE "Emotionale Belastung") — DE duplicates dimension title but reads fine standalone.
- Proposed description-professional (DE): unchanged minus the inline "Weiterführende Links:" (3 URLs, moved below).
- Proposed description-laymen (DE): kept the dimension's own intro sentence, dropped the redundant "Laienhafte Information:" label, removed the inline "Weiterführende Links:" (5 URLs, moved below).
- Proposed verified-health-links (4 stray blank EN entries dropped; titles filled in since they're organization names):
```json
[
  {"title":"pro mente Austria","url":"https://www.promenteaustria.at/","audience":["Healthcare professionals"],"note":""},
  {"title":"Erste Hilfe für die Seele","url":"https://www.erstehilfefuerdieseele.at/","audience":[],"note":""},
  {"title":"Leitlinie Unipolare Depression","url":"https://register.awmf.org/assets/guidelines/nvl-005l_S3_Unipolare-Depression_2023-07.pdf","audience":["Healthcare professionals"],"note":""},
  {"title":"Plattform Psyche (Gesundheitsfonds Steiermark)","url":"https://gesundheitsfonds-steiermark.at/plattform-psyche/","audience":["Laymen / citizens"],"note":""},
  {"title":"ÖGK: Broschüre psychische Gesundheit","url":"https://www.gesundheitskasse.at/cdscontent/load?contentid=10008.784946&version=1704794297","audience":["Laymen / citizens"],"note":""},
  {"title":"oesterreich.gv.at: Psychosoziale Gesundheit","url":"https://www.oesterreich.gv.at/de/themen/hilfe_und_finanzielle_unterstuetzung_erhalten/2/psychosoziale-gesundheit","audience":["Laymen / citizens"],"note":""},
  {"title":"ÖGK: Psychische Gesundheit","url":"https://www.oegk.at/cdscontent/?contentid=10007.895362&portal=oegkportal","audience":["Laymen / citizens"],"note":""}
]
```
- Notes: **NEEDS YOUR DECISION** — dimension's `audience` is `[]` on all 7, but the manual prose split (3 professional-side, 5 layman-side, one link appearing in both) implies an intended split, encoded above as a default — confirm or revert to all-`[]`. **PRE-EXISTING ISSUE** — EN links list had 4 fully-blank stray entries plus blank titles on the real 7; cleaned up above. Same EN-empty gap as elsewhere.

### Dimension: Fatigue / decline in performance (fatigue-decline-in-performance) — 1 observation
Dimension completely empty — nothing to merge.

#### Observation: daily-energy-and-performance-capacity
- Current title: unchanged — already distinct from and more specific than the dimension title.
- Proposed description-professional/laymen: no change. Proposed verified-health-links: none.

### Dimension: Life events (lifeevents) — 1 observation
Dimension completely empty — nothing to merge.

#### Observation: self-reported-significant-life-events
- Current title: unchanged.
- Proposed description-laymen (DE): one grammar fix — "schweren Erkrankung" → **"schwere Erkrankung"** (wrong case ending in an example list); EN citizen-info still empty (missing translation).
- Proposed verified-health-links: none.

### Dimension: Loneliness / Social support (loneliness-social-support) — 3 observations
Dimension completely empty (both locales) — **no shared content exists to distribute**, so no
fold/duplicate/drop decision is actually needed here despite it being a multi-observation
dimension.

#### Observation: number-of-close-relationships
Unchanged — no dimension content to merge.

#### Observation: self-reported-social-integration
- **PRE-EXISTING ISSUE**: DE title grammar error — "Selbstbericht über sozialer Einbindung" → **"Selbstbericht über soziale Einbindung"** ("über" + accusative feminine phrase takes "-e" not "-er").
- Otherwise unchanged — no dimension content to merge.

#### Observation: subjective-sense-of-support
Unchanged — no dimension content to merge.

### Dimension: Susceptibility to infection (susceptibility-to-infection) — 1 observation
Dimension completely empty — observation `number-of-infections` unchanged, nothing to merge.

### Dimension: Weight changes (weight-changes) — 1 observation
Dimension completely empty — observation `change-in-body-weight` unchanged, nothing to merge.

---

## Category: Quality of Life (quality-of-life)

### Dimension: Physical, mental, social, environmental domains (physical-mental-social-environmental-domains) — 1 observation

Dimension has DE WHOQOL (1998) definition + Fonds Gesundes Österreich layman quote + 1 link
(`audience: []`). EN description empty; EN link entry is missing the `title`/`audience`/`note`
keys outright (not just blank — structurally malformed).

#### Observation: quality-of-life-whoqol-bref
- Current title: unchanged (EN "Quality of life (WHOQOL-BREF)" / DE "Körperliche, mentale, soziale, umweltbezogene Lebensqualität") — DE duplicates dimension title exactly but is still a complete standalone phrase; EN already standalone with the instrument name.
- Proposed description-professional (DE): unchanged minus the inline "Weiterführende Informationen: User Manual: [URL]" line (URL already matches the dimension's structured entry, moved below).
- Proposed description-laymen (DE): unchanged, dropped the redundant "Laienhafte Information:" label prefix (no URL dump here to remove).
- Proposed verified-health-links:
```json
[{"title":"WHOQOL-BREF User Manual (WHO)","url":"https://iris.who.int/server/api/core/bitstreams/4c5cd94a-599e-450f-9141-4a21a7b74849/content","audience":[],"note":""}]
```
- Notes: **PRE-EXISTING ISSUE** — dimension's EN link entry was missing `title`/`audience`/`note` keys entirely (structurally malformed), fixed above. **NEEDS YOUR DECISION** — EN description empty on both dimension and observation; the WHO 1998 quote is already available in English inside the DE field and could be reused verbatim for EN, but that substitution isn't made here (translation policy call). Also worth a look: this instrument's own item 21 ("Wie zufrieden sind Sie mit Ihrem Sexualleben?") carries an internal footnote flagging overlap with the sleep indicator — not an action item for this pass, just worth knowing when reviewing `self-reported-sexual-satisfaction` (Sexuality category, below) for redundancy.

---

## Category: Self-management (self-management)

Category has empty description/discussion fields — nothing to flag.

### Dimension: Communication/Understanding (communication-understanding) — 2 observations
Dimension completely empty — nothing to distribute to either `health-literacy` or
`reporting-symptoms-or-changes`; both unchanged.

### Dimension: Medication management (medication-management) — 1 observation
Dimension completely empty — `monitoring-of-medication-and-vaccination-status` unchanged, already distinct from the dimension title.

### Dimension: Self-monitoring (self-monitoring) — 3 observations — NEEDS YOUR DECISION

Dimension completely empty — no shared *content* to distribute, but reading the three children
together surfaced a real **title-consistency** issue with an explicit author instruction buried
in the data:

#### Observation: documentation-of-heart-rate
- Its own `discussion` field (identical DE & EN) literally says: **"Eigenständige Dokumentation --> überall streichen"** — i.e. the author already decided "Independent documentation of" / "Eigenständige Dokumentation" should be struck from titles **everywhere** in this dimension. This file's DE title already complies ("Herzfrequenz (bpm)"), but:
  - DE `documentation-of-blood-pressure` still has "Eigenständige Dokumentation von Blutdruck"
  - **all three EN titles** in this dimension still carry "Independent documentation of..."
- **NEEDS YOUR DECISION**: apply the author's own instruction consistently. Suggested default —
  drop "Eigenständige"/"Independent documentation of" from all three titles, collapsing to:
  - `documentation-of-blood-glucose-level`: DE "Blutzuckerwert (mmol/l?)" / EN "Blood glucose level (mmol/l?)"
  - `documentation-of-blood-pressure`: DE "Blutdruck (mmHg)" / EN "Blood pressure (mmHg?)"
  - `documentation-of-heart-rate`: DE "Herzfrequenz (bpm)" (unchanged) / EN "Heart rate (bpm?)"
  This is a title-style call for you to make, not applied here.
- Also note the DE/EN unit-certainty mismatch on blood pressure ("(mmHg)" vs "(mmHg?)") should be resolved the same way across all three once the prefix question is settled.
- Proposed description-professional/laymen for all three: no change (dimension empty).
- Proposed verified-health-links: none for all three.

---

## Category: Sexuality (sexuality)

### Dimension: Sexual satisfaction (sexual-satisfaction) — 1 observation
Dimension completely empty — `self-reported-sexual-satisfaction` unchanged, already distinct from and more specific than the dimension title.
- Notes: see the WHOQOL-BREF cross-reference under Quality of Life above (item 21 overlap flag) — not an action item, just context for whoever reviews this observation.

---

## Category: Sleep (sleep)

### Dimension: Sleep Quality (sleep-quality) — 2 observations — NEEDS YOUR DECISION

Dimension has DE definition (IQWiG 2024 + shift-work special case) + DE layman text (Heidinger
2019) + 4 links (`audience: []`; EN link list has the same 4 real entries plus **4 stray blank
placeholder entries** — don't carry those over). Already manually merged into `sleep-quality`
only; sibling `einschlafzeit` is a bare stub (no unit, no questions filled in yet). **Default:
treat the general "what is good sleep" framing as belonging to `sleep-quality` only** — flagging
as a judgment call since it's plausible either way.

#### Observation: sleep-quality
- Current title: unchanged (EN "Sleep quality" / DE "Schlafqualität") — DE duplicates dimension title but stands alone fine (age/gender precedent).
- Proposed description-professional (DE): unchanged minus the trailing "Weiterführende Links:" (4 URLs, moved below).
- Proposed description-laymen (DE): unchanged minus "Weiterführende Links:" + duplicate URL (kept the "Informationsbroschüre: Gesund schlafen... (Heidinger, 2019)" citation since it isn't itself a URL entry in the dimension's structured list).
- Proposed verified-health-links:
```json
[
  {"title":"Was ist normaler Schlaf?","url":"https://www.gesundheitsinformation.de/was-ist-normaler-schlaf.html","audience":[],"note":""},
  {"title":"S3-Leitlinie Schlafbezogene Atmungsstörungen","url":"https://register.awmf.org/assets/guidelines/063-001l_S3_SBAS_2023-01_verlaengert_und_Hinweis_Teil-Aktualisierung.pdf","audience":[],"note":""},
  {"title":"S3-Leitlinie Insomnie bei Erwachsenen","url":"https://register.awmf.org/assets/guidelines/063-003l_S3_Insomnie-bei-Erwachsenen_2025-04.pdf","audience":[],"note":""},
  {"title":"S2k-Leitlinie Gestaltung Nacht- und Schichtarbeit","url":"https://register.awmf.org/assets/guidelines/002-030l_S2k_Gesundheitliche-Aspekte-Gestaltung-Nacht-und-Schichtarbeit_2020-03-abgelaufen.pdf","audience":[],"note":""}
]
```

#### Observation: einschlafzeit
- Current title: EN "time taken to fall asleep" / DE "Dauer der Einschlafzeit (durchschnittliche Minuten)"
- Proposed title: EN **"Time taken to fall asleep (average minutes)"** (capitalized, unit clarifier added to match DE) / DE unchanged.
- Proposed description-professional/laymen: **NEEDS YOUR DECISION** — currently empty on both locales; either (a) leave empty since this looks like an unfinished draft (default), or (b) duplicate the `sleep-quality` framing here too since "time to fall asleep" is conceptually a facet of sleep quality.
- Proposed verified-health-links: none by default; if you pick option (b) above, the same 4-link list from `sleep-quality` would apply here too.

### Dimension: Sleep duration (sleep-duration) — 1 observation

#### Observation: sleep-duration
- Current title: unchanged (EN "Sleep duration (hours/night)" / DE "Schlafdauer") — already standalone.
- Proposed description-professional (DE): unchanged — dimension's text already fully merged in verbatim, no URL dump here to trim.
- Proposed description-laymen (DE): unchanged minus "Weiterführende Links:" + duplicate URL (moved below).
- Proposed verified-health-links:
```json
[{"title":"Was ist normaler Schlaf?","url":"https://www.gesundheitsinformation.de/was-ist-normaler-schlaf.html","audience":[],"note":""}]
```
- Notes: **PRE-EXISTING ISSUE** — DE professional text still has a literal "Empfehlung: ???" placeholder — needs a real recommendation value before publishing; not resolved here.

### Dimension: Schlafhygiene (schlafhygiene) — 1 observation
Dimension completely empty — nothing to merge.

#### Observation: haeufigkeit-einhaltung-schlaffoerdernder-routinen
- Current title: EN "Frequency of adherence to sleep-promoting routines" / DE "schlaffördernden Routinen (Häufigkeit/Woche)"
- Proposed title: DE **"Einhaltung schlaffördernder Routinen (Häufigkeit/Woche)"** — **PRE-EXISTING ISSUE**: DE title starts lowercase and is missing "Einhaltung" (adherence), reading as a dangling adjective phrase; the observation's own key confirms "Einhaltung" belongs. EN unchanged.
- Proposed description-professional/laymen: no change (dimension empty). Proposed verified-health-links: none.
- Notes: dimension's own EN title "sleephygiene" (no space, lowercase) is inconsistent with Title Case elsewhere — low priority since it disappears from view, noting anyway.

### Dimension: Chronotyp (chronotyp) — 1 observation
Dimension completely empty — nothing to merge.

#### Observation: selbstberichteter-chronotyp
- Current title: EN "self_reports_chronotype" / DE "Selbstberichteter Chronotyp"
- Proposed title: EN **"Self-reported chronotype"** — **PRE-EXISTING ISSUE**: EN was in snake_case, reading like a variable name, inconsistent with every sibling's Title Case. DE unchanged.
- Proposed description-professional/laymen: no change. Proposed verified-health-links: none.

---

## Category: Smoking (smoking)

The dimension `verified-health-links[].audience` field is empty (`[]`) on **every** dimension in
this category — none have audience tagging filled in.

### Dimension: Smoking Status (smoking-status) — 1 observation

Dimension has DE definitions (Herold 2026 + WHO 2025 quotes) + DE layman text (IQWiG 2022) + 7
links. The observation's existing manual split — 1 URL embedded in `description`, 6 in
`citizen-info` — is a clean, self-consistent professional/layman split used to infer audience
tags below.

#### Observation: smoking-status
- Current title: unchanged (EN "Smoking status" / DE "Raucher:innenstatus") — stands alone already.
- Proposed description-professional (DE): unchanged minus "Weiterführende Links:" + 1 URL (moved below).
- Proposed description-laymen (DE): unchanged minus "Nähere Informationen..." + 6-URL dump (moved below).
- Proposed verified-health-links — **NEEDS YOUR DECISION** on the inferred audience split:
```json
[
  {"title":"S3-Leitlinie Rauchen und Tabakabhängigkeit","url":"https://register.awmf.org/assets/guidelines/076-006l_S3_Rauchen-_Tabakabhaengigkeit-Screening-Diagnostik-Behandlung_2021-03.pdf","audience":["Healthcare professionals"],"note":""},
  {"title":"gesundheitsinformation.de: Rauchen","url":"https://www.gesundheitsinformation.de/rauchen.html","audience":["Laymen / citizens"],"note":""},
  {"title":"rauchfrei.at","url":"https://rauchfrei.at/","audience":["Laymen / citizens"],"note":""},
  {"title":"rauchfrei-programm.de","url":"https://rauchfrei-programm.de/","audience":["Laymen / citizens"],"note":""},
  {"title":"Stabsstelle Krebsprävention (DKFZ)","url":"https://www.dkfz.de/forschung/translationale-zentren/ncpc/stabsstelle-krebspraevention","audience":["Laymen / citizens"],"note":""},
  {"title":"WHO: Tobacco","url":"https://iris.who.int/server/api/core/bitstreams/2deb01bc-1be9-4e9c-b113-5efbb67780c7/content","audience":["Laymen / citizens"],"note":""},
  {"title":"Prävention und Tabakentwöhnung (Sozialministerium)","url":"https://www.sozialministerium.gv.at/Themen/Gesundheit/Drogen-und-Sucht/Tabak-und-verwandte-Erzeugnisse/Pr%C3%A4vention-und-Tabakentw%C3%B6hnung.html","audience":["Laymen / citizens"],"note":""}
]
```
- Notes: **NEEDS YOUR DECISION** — audience split above is *inferred* from where each URL sat in the prose, not from the dimension's own (blank) `audience` field. URL/title themselves are authoritative (from the dimension). Please confirm, especially the WHO Tobacco link, which could arguably be tagged for both audiences rather than layman-only.

### Dimension: Zigarren-Zigarillos (zigarren-zigarillos) — 1 observation
Dimension completely empty — nothing to merge.

#### Observation: zigarren-zigarillos-pro-woche
- Current title: EN "cigarres or cigarrilos per week" / DE "Zigarren/Zigarillos (Anzahl/Woche)"
- Proposed title: EN **"Cigars or cigarillos (number/week)"** — **PRE-EXISTING ISSUE**: two spelling errors ("cigarres"→"cigars", "cigarrilos"→"cigarillos"), lowercase, doesn't follow the "(unit/period)" convention. DE unchanged.
- Proposed description-professional/laymen: no change. Proposed verified-health-links: none.

### Dimension: Zigaretten (zigaretten) — 4 observations — NEEDS YOUR DECISION

Dimension has **no content at all** — nothing to fold/duplicate/drop. But none of the 4
children's titles mention cigarettes/smoking at all, so once "Zigaretten" as a heading
disappears, their scope becomes ambiguous. Default below makes the smoking/cigarette object
explicit in each title, but the cigarette-vs-smoking-generally scope question needs your call.

#### Observation: entwoehnungsmotivation
- Current title: EN "motivation to quit" / DE "Entwöhnungsmotivation"
- Proposed title: EN **"Motivation to quit smoking"** / DE **"Entwöhnungsmotivation (Rauchen)"** — **NEEDS YOUR DECISION**: neither title stands alone without the vanishing "Zigaretten" heading. Default adds "(Rauchen)"/"smoking" as the object, but that's *broader* than the dimension's literal cigarette-only scope (quit-motivation instruments rarely restrict to cigarettes specifically) — confirm the intended scope.
- Proposed description-professional/laymen: no change (dimension empty). Proposed verified-health-links: none.

#### Observation: entwoehnungsversuche
- Current title: EN "attempts to give up" / DE "Entwöhnungsversuche (Anzahl/Jahr)"
- Proposed title: EN **"Attempts to quit smoking (number/year)"** — **PRE-EXISTING ISSUE**: lowercase, informal "give up" vs. "quit" (aligned with the sibling above once fixed), missing unit suffix that DE has. DE unchanged.
- Notes: **NEEDS YOUR DECISION** — same cigarette-vs-smoking scope question as `entwoehnungsmotivation`; kept "smoking" here for consistency.

#### Observation: nikotinabhaengigkeit
- Current title: EN "nicotine addiction" / DE "Nikotinabhängigkeit"
- Proposed title: EN **"Nicotine dependence"** — **PRE-EXISTING ISSUE**: EN uses "addiction" where DE uses the clinical term "Abhängigkeit" (dependence) — a terminology mismatch, not just casing. DE unchanged.
- Notes: **NEEDS YOUR DECISION** — unlike its 3 siblings, this title already stands alone ("nicotine dependence" doesn't need a cigarette/smoking qualifier), so no "(Rauchen)"/"smoking" suffix was added here — confirm this asymmetry with its siblings is intentional.

#### Observation: pack-years
- Current title: EN "Pack Years" / DE "Pack years"
- Proposed title: align capitalization on both to **"Pack Years"** — **PRE-EXISTING ISSUE**: DE/EN disagree on capitalization of the same loanword term. Title otherwise stands alone fine, no dimension context needed.
- Proposed description-professional/laymen: no change. Proposed verified-health-links: none.

### Dimension: Pfeife-Wasserpfeife (pfeife-wasserpfeife) — 1 observation
Dimension completely empty — nothing to merge.

#### Observation: pfeife-wasserpfeife-anzahl-pro-woche
- Current title: EN "pipe hookah numbers per week" / DE "Pfeife/Wasserpfeife (Anzahl/Woche)"
- Proposed title: EN **"Pipe or hookah (number/week)"** — **PRE-EXISTING ISSUE**: lowercase, missing connector between "pipe" and "hookah," plural "numbers" instead of singular, doesn't follow sibling format. DE unchanged.
- Proposed description-professional/laymen: no change. Proposed verified-health-links: none.

### Dimension: E-Zigaretten/Tabakerhitzer (e-zigaretten-tabakerhitzer) — 1 observation

Dimension has no description content, but **its own EN `title` field is literally the German
phrase "Anzahl pro Woche"** ("number per week") — confirmed against source — the exact "EN title
accidentally left in German" defect, just at the dimension level. Flagging even though this
dimension disappears from view, since it's a quick CMS fix regardless (proposed EN dimension
title: "E-cigarettes / tobacco heaters").

#### Observation: e-zigaretten-tabakerhitzer-anzahl-pro-woche
- Current title: EN "e-cigarettes tabacco heaters-number-per-week" / DE "E-Zigaretten/Tabakerhitzer (Anzahl/Woche)"
- Proposed title: EN **"E-cigarettes or tobacco heaters (number/week)"** — **PRE-EXISTING ISSUE**: spelling error ("tabacco"→"tobacco"), broken hyphenation ("heaters-number-per-week"), no separator between the two product types. DE unchanged.
- Proposed description-professional/laymen: no change. Proposed verified-health-links: none.

---

## Category: Sociodemographic Data (sociodemographic-data)

### Dimension: Socio-economic Status (socio-economic-status) — 3 observations — NEEDS YOUR DECISION

Dimension has a DE general SES definition (education/income/employment jointly affect health;
BMASGPK 2026a) + "Nicht erforderlich" layman text, no links. Only `education-level-isced`
absorbed this — and it absorbed the *whole dimension title*, not a definition scoped to
education specifically. That mislabeling is the core problem here.

#### Observation: education-level-isced
- Current title: EN "Highest level of education (ISCED)" / DE "Sozioökonomischer Status"
- Proposed title: DE **"Höchste abgeschlossene Ausbildung (ISCED-Level)"** — **the primary fix needed here**: DE currently duplicates the *dimension's* title verbatim even though this observation covers only one of three SES facets (siblings `employment-status-income`, `native-language` cover the others). Once the dimension disappears, three siblings would sit under "Sociodemographic Data" — education / employment+income / native language — one mislabeled as the whole umbrella construct. Proposed DE title mirrors EN's already-correct scoping.
- Proposed description-professional (DE): unchanged — dimension's professional text already duplicated verbatim, no URL dump to trim.
- Proposed description-laymen (DE): unchanged ("Nicht erforderlich," identical to dimension, already deduplicated).
- Proposed verified-health-links: none (dimension has none).
- Notes: see dimension-level decision below.

#### Observation: employment-status-income
- Current title: EN "Employment status / Income" / DE "Berufliche Situation Einkommen"
- Proposed title: DE **"Berufliche Situation / Einkommen"** — **PRE-EXISTING ISSUE**: DE concatenates two nouns with no separator (reads as a run-on); EN correctly uses "/". EN unchanged.
- Proposed description-professional/laymen: **NEEDS YOUR DECISION** — currently completely empty. Should the dimension's general SES framing be duplicated here, since employment/income is one of the three factors that definition explicitly names? Default: yes, duplicate the same DE professional text as `education-level-isced` (intro adjusted to reference employment/income) and the "Nicht erforderlich" layman value — but flagged rather than applied.
- Proposed verified-health-links: none.

#### Observation: native-language
- Current title: unchanged (EN "Native language" / DE "Muttersprache") — stands alone fine.
- Proposed description-professional/laymen: **NEEDS YOUR DECISION** — same question as above: does the general SES definition apply, or is "native language" a distinct-enough construct (more a migration-background/language-barrier proxy than SES per se) that it shouldn't inherit the SES framing? Default leans toward **drop as not applicable**, but genuinely uncertain.
- Proposed verified-health-links: none.

**Dimension-level note (all 3 children):** default recommendation is to duplicate the SES
definition to `employment-status-income` (clearly in-scope) but not `native-language` (arguably
out of scope), plus fix `education-level-isced`'s title so it stops usurping the dimension's
name. Alternative: fold the general definition into the `sociodemographic-data` category's own
description field instead of duplicating across children — note that field is currently **not
populated at all** for this category (unlike `work`, which has the field present-but-empty), so
worth checking in `admin/config.yml` whether that's even wired up before choosing this option.

### Dimension: Gender (gender) — 1 observation
Already fully and correctly merged — no action needed; flagging only to confirm it's done right (matches the age/gender precedent cited throughout this sheet).

### Dimension: Age (age) — 1 observation
Already fully and correctly merged — no action needed, same confirmation as gender.

### Dimension: Origin (origin) — 1 observation
Dimension completely empty — nothing to merge.

#### Observation: ethnicity
- Current title: unchanged — stands alone; doesn't repeat "Origin/Herkunft" but is self-explanatory.
- Notes: **NEEDS YOUR DECISION (scope, not content)** — the dimension "Origin/Herkunft" is broader than "ethnicity" alone (could also cover country of birth/migration background). This sole child narrows scope to ethnicity specifically; once the dimension disappears, any broader intent becomes invisible. Flagging in case a broader observation (e.g. country of birth) was planned but never created — if not, no action needed.

### Dimension: Marital status (marital-status) — 1 observation
Dimension completely empty — but this is the single most important title fix in the whole sheet.

#### Observation: single-married-partnership-separated-widowed
- Current title: EN "single, married, in a partnership, separated, widowed" / DE "ledig, verheiratet, in Partnerschaft, getrennt, verwitwet"
- Proposed title: EN **"Marital status (single, married, in a partnership, separated, widowed)"** / DE **"Familienstand (ledig, verheiratet, in Partnerschaft, getrennt, verwitwet)"** — **this is exactly the "titles need to read standalone" problem**, not a formatting nit: the current titles are a bare, lowercase list of answer categories with no concept name at all — compare siblings `housing-type` ("Wohnform (Eigenheim, Mietwohnung, Sonstiges)") and `residence` ("Wohnortgröße (Stadt/Land)"), both "Concept name (category list)." This observation is missing the concept name entirely, and the vanishing dimension's own title ("Familienstand"/"Marital status") is exactly the missing piece.
- Proposed description-professional/laymen: no change (dimension empty). Proposed verified-health-links: none.

### Dimension: Living environment (living-environment) — 2 observations
Dimension completely empty — nothing to merge for either child; both titles already stand alone.

#### Observation: housing-type — unchanged.
#### Observation: residence (file: `residence-and-housing-type.json`) — unchanged.
- Notes: **PRE-EXISTING ISSUE, confirmed against source** — file is named `residence-and-housing-type.json` but `key`/`id_tech` = `"residence"`, breaking the "filename derived from key" convention. Likely a leftover from a rename/split. Doesn't affect this merge; worth a cleanup rename to `residence.json` separately.

---

## Category: Workability (work)

### Dimension: Workability (workability) — 4 observations — NEEDS YOUR DECISION

Dimension has DE definitions (Kloimüller quotes) + a stray unresolved TODO + 1 link. Only
`workability-worksoc-wai` has this merged in (with an inline URL dump); the other 3
(`impairment-of-employment`, `loss-of-income`, `work-absence-days`) are completely empty stubs.

Also note: the **category** itself is named "Workability" (EN) / "Arbeit" (DE), and this
**dimension** is also named "Workability" (EN) / "Arbeitsfähigkeit" (DE) — sharing the English
name. An observation also bare-titled "Workability" would sit directly under a category called
"Workability" — reads redundantly.

#### Observation: workability-worksoc-wai
- Current title: EN "Work ability (Work-SoC / WAI)" / DE "Arbeitsfähigkeit"
- Proposed title: DE **"Arbeitsfähigkeit (Work-SoC / WAI)"** — **PRE-EXISTING ISSUE**: EN already has the instrument suffix, DE doesn't; DE alone (bare "Arbeitsfähigkeit") is the one that most directly collides with the category/dimension name. **NEEDS YOUR DECISION** (separate from the fix above): given the category is also "Workability," is bare "Work ability" still too redundant now that the dimension layer is gone? Could consider "Work ability index (Work-SoC / WAI)" instead — flagging, not deciding.
- Proposed description-professional (DE): unchanged minus "Weiterführende Links:" + 1 URL (moved below); the "Illmarinen, J. – hier fehlt die Referenz" placeholder line kept as-is (an editorial content decision, not a formatting one — see note below).
- Proposed description-laymen (DE): unchanged (no URL dump present here).
- Proposed verified-health-links:
```json
[{"title":"Handbuch Betriebliche Gesundheitsförderung","url":"https://www.netzwerk-bgf.at/cdscontent/load?contentid=10008.773130&version=1673273440","audience":[],"note":""}]
```
- Notes: **PRE-EXISTING ISSUE, confirmed against source** — the professional description contains a literal unresolved TODO: `"Illmarinen, J. – hier fehlt die Referenz"` ("reference missing here") — an author's note-to-self still in production content, likely a misspelling of "Ilmarinen." Should be resolved (find the citation or remove the line) before publishing; left untouched here since that's a content call, not a merge-mechanics one.

#### Observation: impairment-of-employment
- Current title: unchanged — stands alone fine.
- Proposed description-professional/laymen: **NEEDS YOUR DECISION** — should the dimension's general "Arbeitsfähigkeit" definition be duplicated here? This reads as a *consequence* of low workability rather than a direct measure, so default is **drop as not applicable** — flagging since a reviewer with more context on the intended data model may see it differently.
- Proposed verified-health-links: none (default).

#### Observation: loss-of-income
- Current title: EN "loss of income" / DE "Einkommensverlust"
- Proposed title: EN **"Loss of income"** — **PRE-EXISTING ISSUE**: lowercase, inconsistent with sibling Title Case. DE unchanged.
- Proposed description-professional/laymen: **NEEDS YOUR DECISION** — same pattern as `impairment-of-employment`: default **drop as not applicable** (outcome measure, not a workability measure per se).
- Proposed verified-health-links: none (default).

#### Observation: work-absence-days
- Current title: unchanged — stands alone, consistent Title Case already.
- Proposed description-professional/laymen: **NEEDS YOUR DECISION** — same pattern as its two siblings: default **drop as not applicable**.
- Proposed verified-health-links: none (default).

**Dimension-level note (all 4 children):** the clearest "NEEDS YOUR DECISION" case in this
whole sheet — `workability-worksoc-wai` is a direct measurement, while the other three are
workability-*adjacent outcomes* (impairment, income loss, absence days), not equally-weighted
facets of one thing the way the sleep or SES observations are. Default across the board keeps
the shared "Arbeitsfähigkeit" definition scoped to the one observation that actually measures it,
and does not duplicate it into the three outcome observations — but the opposite call (duplicate
to all four, so nothing is lost when the "Workability" grouping vanishes) is equally defensible.

---

## Files read

All 12 categories, all 38 remaining dimensions (after Phase 1's deletion of the 2
zero-observation ones), and all 62 observations were read in full (both locale blocks) to
produce this sheet.

---

## Final decisions (recorded after interactive review)

**Global policies:**
- EN translation gap: defer entirely — leave EN description/citizen-info fields empty everywhere in this pass.
- Link audience inference: preserve the inferred professional/layman split when moving inline URLs into the structured `verified-health-links` field (applies to alcohol, emotional-distress, smoking-status).
- Questionnaire/instrument-name suffixes in titles (e.g. "(PSS-4 / PSS-10)", "(PHQ-2)", "(WHOQOL-BREF)", "(Work-SoC / WAI)"): drop these from titles catalogue-wide, both DE and EN.
- German-derived observation `key`/filename values: rename to English-derived slugs catalogue-wide (15 files, list below).

**Per-item decisions:**
- Alcohol "Handbuch..." reference (no URL exists): add as a `verified-health-links` placeholder entry with an empty `url`.
- Height/weight (BMI): fold dimension content into `body-height-weight-bmi` only; nothing added to `waist-circumference`/`waist-to-hip-ratio`.
- Dietary pattern: fold dimension content into `dietary-pattern-athis` only; nothing added to the other 6. Duplicate the "Ernährungsempfehlungen: Fleisch und Fisch" link into `fisch-fleisch-portionen-woche` too. General FBDG framing stays on `dietary-pattern-athis`, not moved to the category.
- Nutrition title format: use "(portions/day)"/"(portions/week)" bracket convention consistently across all 7 dietary-pattern observations' EN titles (not just the 3 originally flagged).
- Physical Activity category description: drop the dimension enumeration list entirely (DE `description-professional`), keep the rest of the text.
- Everyday activity: fold into `steps-per-day` only; `zeit-leichte-koerperliche-aktivitaet` stays a stub.
- `steps-per-day`'s `target-info` field: remove entirely — it's an orphaned field (not in `admin/config.yml`'s schema at all) with wrong content copy-pasted from a different dimension. Same treatment for the orphaned `id_tech` field found on this file and on `minutes-moderate-physical-activity.json`.
- `lessons-per-week` (flexibility-and-balance): rename to DE "Flexibilitäts- und Gleichgewichtstraining (Einheiten/Woche)" / EN "Flexibility and balance training (units/week)" — adopts the dimension's full name to cover the "balance" gap in the title itself.
- `potential-access-barriers`: fix `category` field from `"sociodemographic-data"` to `"psychosocial-factors"` (data bug, both locales).
- `sleep-quality`: rename to EN "Self-assessment of sleep quality" / DE "Selbstangegebene Einschätzung der Schlafqualität"; fold dimension content here only, not into `einschlafzeit`.
- `sleep-duration`'s "Empfehlung: ???" placeholder: left as-is for now (separate content gap).
- Self-monitoring dimension (3 obs): apply the author's own "strike Eigenständige/Independent documentation of" note to all 3 titles, both locales → `documentation-of-blood-glucose-level` "Blutzuckerwert (mmol/l?)"/"Blood glucose level (mmol/l?)", `documentation-of-blood-pressure` "Blutdruck (mmHg)"/"Blood pressure (mmHg?)", `documentation-of-heart-rate` "Herzfrequenz (bpm)"/"Heart rate (bpm?)".
- `smoking-status` WHO Tobacco link: tagged layman-only (per the inferred-split policy), not both audiences.
- Zigaretten dimension (4 obs: `entwoehnungsmotivation`, `entwoehnungsversuche`, `nikotinabhaengigkeit`, `pack-years`): **no title changes** — left exactly as they are, pending review by the project's partners. (Key rename still applies per the catalogue-wide policy, based on the current unchanged titles.)
- Socio-economic status: do **not** duplicate the SES definition into `employment-status-income` or `native-language` — both stay empty. `education-level-isced` renamed to DE "Höchste abgeschlossene Schulbildung" / EN "Highest completed education (ISCED level)" (fixes the bug where it duplicated the dimension's own title).
- `workability-worksoc-wai`'s "Illmarinen, J. – hier fehlt die Referenz" placeholder: left as-is for now (separate content gap). Dimension's shared "Arbeitsfähigkeit" definition not duplicated into `impairment-of-employment`/`loss-of-income`/`work-absence-days`.
- `ethnicity`: renamed to DE "Herkunft - Ethnische Zugehörigkeit" / EN "Origin (Ethnicity)" — broadens the title to acknowledge the parent dimension's wider scope while the content still only covers ethnicity.

**German-derived key/filename renames (15):**

| Old key | New key |
|---|---|
| alkoholfreie-ungesuesste-getraenke-glaeser-tag | non-alcoholic-unsweetened-drinks-glasses-day |
| e-zigaretten-tabakerhitzer-anzahl-pro-woche | e-cigarettes-or-tobacco-heaters-number-week |
| einschlafzeit | time-taken-to-fall-asleep |
| entwoehnungsmotivation | motivation-to-quit |
| entwoehnungsversuche | attempts-to-give-up |
| fisch-fleisch-portionen-woche | fish-and-meat-portions-week |
| getreide-erdaepfel-portionen-pro-tag | cereals-potatoes-rice-pasta-portions-day |
| haeufigkeit-einhaltung-schlaffoerdernder-routinen | adherence-to-sleep-promoting-routines |
| huelsenfruechte-portionen-pro-woche | legumes-portions-week |
| milchprodukte-oele-fette-nuesse-samen-portionen-pro-tag | dairy-products-oils-fats-nuts-seeds-portions-day |
| nikotinabhaengigkeit | nicotine-addiction |
| pfeife-wasserpfeife-anzahl-pro-woche | pipe-or-hookah-number-week |
| selbstberichteter-chronotyp | self-reported-chronotype |
| stark-verarbeitete-lebensmittel | highly-processed-foods-portions-day |
| zigarren-zigarillos-pro-woche | cigars-or-cigarillos-number-week |

Not renamed (pre-existing filename/key/id_tech mismatches, English already, out of scope for the "German key" policy): `hp-observations/minutes-moderate-physical-activity-per-week.json` (key `steps-per-day`) and `hp-observations/residence-and-housing-type.json` (key `residence`) — flagged only.


---

## Session 2 — Key re-check, dimension-info-preservation walkthrough, and content splits

Follow-up session after the Phase 4 execution above. Two parts: (1) a full re-check of every
observation's `key`/filename against its current title (several had drifted stale after Phase 4's
title edits), and (2) a category-by-category walkthrough to confirm no information that used to
live on a now-hidden indicator dimension was lost from its observation(s).

### Key/filename re-check (all 62 then-existing observations audited)

Found and fixed:
- `zeit-leichte-koerperliche-aktivitaet` — a German key missed entirely in the original Phase 4
  sweep -> renamed to `light-physical-activity-minutes-day` (later renamed again, see below).
- `lessons-per-week` — key had gone stale (bore no relation to its already-updated title) ->
  `flexibility-and-balance-training-units-week`.
- `quality-of-life-whoqol-bref` -> `quality-of-life-score`.
- `emotional-distress-phq2` -> `self-reported-emotional-burden`, with new titles DE "Selbstbericht
  über emotionale Belastung" / EN "Self-reported emotional burden" (dropped the PHQ-2 suffix
  policy applied to title, key updated to match).
- `perceived-stress-pss` -> `self-reported-stress`, new titles DE "Selbstbericht über Stress" / EN
  "Self-reported stress".
- `workability-worksoc-wai` -> `work-ability`.
- `documentation-of-blood-glucose-level` -> `blood-glucose-level`, `documentation-of-blood-pressure`
  -> `blood-pressure`, `documentation-of-heart-rate` -> `heart-rate`.
- `dietary-pattern-athis` -> `fruit-vegetable-consumption`, dropped "(ATHIS)" from the EN title too.
- Two pre-existing filename/key mismatches unrelated to this work, fixed while cleaning up:
  `minutes-moderate-physical-activity-per-week.json` -> `steps-per-day.json`,
  `residence-and-housing-type.json` -> `residence.json`.

Confirmed clean afterward: every observation file's `key` matches its filename, and DE/EN `key`
values match each other.

### Dimension-info-preservation walkthrough (category by category)

Went through every category to confirm each observation's title still conveys what its (now
hidden) parent dimension used to convey. Net changes:

**Physical Activity** (completed the set started in Phase 4):
- `minutes-moderate-physical-activity` -> `moderate-vigorous-endurance-oriented-activity-minutes-week`,
  DE "Moderate und intensive ausdauerorientierte Aktivität (Minuten/Woche)" / EN "Moderate and
  vigorous endurance-oriented activity (minutes/week)" — restores "endurance-oriented activity"
  from the dimension name; fixed a "vigouros" typo and a missing-space DE typo along the way;
  corrected the unit to /week after confirming the underlying data (150–300 min/week is the
  actual measured/recommended period, not daily).
- `steps-per-day` -> `everyday-activity-steps-day`, DE "Alltagsaktivität (Schritte/Tag)" / EN
  "Everyday activity (steps/day)" — restores "everyday activity" from the dimension name.
- `light-physical-activity-minutes-day` -> `light-everyday-physical-activity-minutes-day`, DE
  "Leichte körperliche Alltagsaktivität (Minuten/Tag)" / EN "Light everyday physical activity
  (minutes/day)" — same dimension ("everyday-activity"), same treatment as its sibling above.
- `muscle-strengthening-exercises-daysweek` -> `muscle-strengthening-exercises-units-week` — unit
  changed from days/week to units/week (DE "Einheiten/Woche", EN "units/week") per instruction.

**Alcohol**: `alcohol-consumption-frequency` — added a measurement clarifier since the underlying
instrument is a frequency scale, not a literal count: DE "(Tage/Woche oder Getränke/Tag)" / EN
"(days/week or drinks/day)".

**Anthropometry**: `body-height-weight-bmi` -> `body-mass-index`, retitled "Body-Mass-Index
(kg/m²)" — identical string for DE and EN, since BMI is the same term in both. `waist-circumference`
and `waist-to-hip-ratio` confirmed to stay standalone (they measure something distinct from
height/weight, so dimension-name context wouldn't fit).

**Nutrition**: found two observations whose own `discussion` field already flagged an unresolved
"needs to be split" author note (`dairy-products-oils-fats-nuts-seeds-portions-day`: "Milchprodukte
müssen noch getrennt werden."; `fish-and-meat-portions-week`: "Muss auf Fisch und Fleisch aufgeteilt
werden."). Resolved both by replacing each combined observation with two new ones (content copied
from the parent as a starting point, not yet differentiated — flagged as still needing real
editorial content per food group):
- `dairy-products-oils-fats-nuts-seeds-portions-day` -> removed, replaced by
  `dairy-products-portions-day` ("Milchprodukte (Portionen/Tag)") and
  `oils-fats-nuts-seeds-portions-day` ("Öle/Fette/Nüsse/Samen (Portionen/Tag)", currently no
  content — the copied dairy-specific text didn't apply here so it was left empty rather than
  copied wrongly).
- `fish-and-meat-portions-week` -> removed, replaced by `fish-portions-week` ("Fisch
  (Portionen/Woche)") and `meat-portions-week` ("Fleisch (Portionen/Woche)"), both currently
  carrying the same combined fish+meat portion guidance as a placeholder.
- Both original discussion notes carried over into all 4 new files with "--> erledigt" appended,
  marking the split itself as done (the content refinement is a separate follow-up).
- Total observation count: 62 -> 64.
- The other 5 dietary-pattern observations (cereals/potatoes, fruit/veg, highly processed foods,
  legumes, non-alcoholic drinks) confirmed fine standalone — no "Dietary pattern:" prefix needed.

**Psychosocial Factors**:
- `self-reported-resilience` — DE "Selbstbericht über Coping-Fähigkeit (Resilienz)" / EN
  "Self-reported coping ability (resilience)" — restores "coping ability" from the dimension name
  (key unchanged, "resilience" still present).
- `daily-energy-and-performance-capacity` -> `fatigue-daily-energy-performance-capacity`, DE
  "Müdigkeit und tägliche Energie/Leistungsfähigkeit" / EN "Fatigue and daily energy/performance
  capacity" — restores "fatigue" from the dimension name ("Fatigue / Decline in performance").
- `number-of-close-relationships` -> `loneliness-social-support-close-relationships`, DE
  "Einsamkeit/Soziale Unterstützung (Anzahl enger Bezugspersonen)" / EN "Loneliness/Social support
  (number of close relationships)" — restores the dimension name; its two siblings
  (`self-reported-social-integration`, `subjective-sense-of-support`) confirmed fine standalone.
- `potential-access-barriers` confirmed fine standalone (Access to care).

**Quality of Life**: `quality-of-life-score`'s DE title was still the raw, unedited dimension name
("Körperliche, mentale, soziale, umweltbezogene Lebensqualität") — a bug that only the EN side had
been fixed for back in Phase 4. Fixed to DE "Lebensqualität (0-100 Score)", matching the EN pattern
and the category's own short DE name.

**Self-management**: `health-literacy` and `reporting-symptoms-or-changes` confirmed fine
standalone (Communication/Understanding). `monitoring-of-medication-and-vaccination-status`
confirmed fine (already names "medication"). `blood-glucose-level`/`blood-pressure`/`heart-rate`
confirmed to intentionally stay bare — the original content author's own note said to strike
"Eigenständige Dokumentation"/"Independent documentation of" everywhere, and re-adding
"self-monitoring" context would contradict that.

**Sexuality**: `self-reported-sexual-satisfaction` confirmed fine standalone.

**Sleep**: `time-taken-to-fall-asleep` confirmed fine standalone (Sleep Quality dimension).
`adherence-to-sleep-promoting-routines` -> `sleep-hygiene-adherence-routines-week`, DE "Schlafhygiene
(Häufigkeit der Einhaltung schlaffördernder Routinen/Woche)" / EN "Sleep hygiene (frequency of
adherence to sleep-promoting routines/week)" — restores "sleep hygiene" explicitly.
`sleep-duration` — DE title gained the "(Stunden/Nacht)" unit suffix EN already had.

**Smoking**: `smoking-status` — added status-category suffix DE "(nie, ehemalig, aktuell)" / EN
"(never, former, current)". All other smoking-status/e-cigarette/cigar/pipe observations confirmed
fine standalone. The 4 Zigaretten-dimension observations remain deferred pending partner review,
per the earlier decision — not touched in this pass either.

**Sociodemographic Data**:
- `single-married-partnership-separated-widowed` -> `marital-status` — the fix decided back in
  Phase 3 but never actually applied; finally done: DE "Familienstand (ledig, verheiratet, in
  Partnerschaft, getrennt, verwitwet)" / EN "Marital status (single, married, in a partnership,
  separated, widowed)".
- `age` — added "(Jahre)"/"(years)" suffix.
- `gender` — added the full accurate answer-option suffix (verified against the actual data rather
  than a guessed simplification): DE "(weiblich, männlich, inter, divers, offen, keine Angabe)" /
  EN "(female, male, inter, diverse, open, no answer)".
- `education-level-isced` — DE title was missing the "(ISCED-Level)" suffix that EN already had;
  added for parity.
- `number-of-infections` -> `susceptibility-to-infection-number-period`, DE "Infektanfälligkeit
  (Anzahl innerhalb definierter Periode)" / EN "Susceptibility to infection (number within a
  defined period)" — restores the dimension name.
- `housing-type`, `residence` confirmed fine standalone (Living environment).

**Workability**: `work-ability` — added "(Score)" suffix (DE "Arbeitsfähigkeit (Score)" / EN "Work
ability (Score)") after confirming the instrument name itself ("Work-SoC") wasn't what was meant.
`impairment-of-employment`, `loss-of-income`, `work-absence-days` confirmed fine standalone (the
category is itself already called "Workability," so a dimension-name prefix would be redundant).

### Verified after every change in this session
- `scripts/validate.py --strict` — clean throughout, checked after essentially every edit.
- Filename/key/DE-EN-key consistency re-checked at the end: 64 observation files, 0 mismatches.
- Full rebuild (`consolidate.py` -> `render_html.py` -> `render_index.py`) confirms all titles
  render correctly in the browse table and Explore page.

### Outstanding for partner review
- The 4 Zigaretten-dimension observations (`motivation-to-quit`, `attempts-to-give-up`,
  `nicotine-addiction`, `pack-years`) — titles untouched, scope question (cigarette-specific vs.
  smoking-general wording) still open.
- The 2 new Nutrition split observations with no differentiated content yet
  (`oils-fats-nuts-seeds-portions-day` is currently empty; `fish-portions-week` /
  `meat-portions-week` currently share identical placeholder guidance covering both foods) — need
  real per-food-group content before publishing.
- Several EN `description`/`citizen-info` fields remain empty catalogue-wide (the "defer entirely"
  translation policy from Phase 4 still stands).
