# PreNUDGE Gesundheitsprofil — Katalog

_Version: 0.1.0 | Generiert: 2026-07-27_

---

## Inhaltsverzeichnis

- [Alkohol](#alkohol)
  - [Konsumhäufigkeit](#konsumhäufigkeit)
- [Anthropometrie](#anthropometrie)
- [Ernährung](#ernährung)
- [Körperliche Aktivität](#körperliche-aktivität)
  - [Ausdauerorientierte Aktivität](#ausdauerorientierte-aktivität)
    - [Minuten in moderater und intensiver körperlichen Aktivität](#minuten-in-moderater-und-intensiver-körperlichen-aktivität)
  - [Alltagsaktivität](#alltagsaktivität)
    - [Schrittzahl (pro Tag)](#schrittzahl-pro-tag)
  - [Muskelkräftigende Übungen](#muskelkräftigende-übungen)
  - [Sitzen](#sitzen)
- [Psychosoziale Faktoren](#psychosoziale-faktoren)
- [Lebensqualität](#lebensqualität)
- [Schlaf](#schlaf)
  - [Schlafdauer](#schlafdauer)
  - [Schlafqualität](#schlafqualität)
- [Rauchen](#rauchen)
  - [Raucherstatus](#raucherstatus)
- [Soziodemografische Daten](#soziodemografische-daten)
- [Arbeit](#arbeit)
- [Bearbeitungshistorie](#bearbeitungshistorie)

---

## Alkohol

<img src="media/wine_white.png" alt="Alkohol" width="48" style="background-color: #00a256; padding: 6px; border-radius: 6px;">

### Konsumhäufigkeit

_Keine Beobachtungen erfasst._

---

## Anthropometrie

<img src="media/ruler-dimension-line.png" alt="Anthropometrie" width="48" style="background-color: #e0d3de; padding: 6px; border-radius: 6px;">

_Keine Dimensionen erfasst._

---

## Ernährung

<img src="media/apple.png" alt="Ernährung" width="48" style="background-color: #f2c57c; padding: 6px; border-radius: 6px;">

_Keine Dimensionen erfasst._

---

## Körperliche Aktivität

<img src="media/dumbbell.png" alt="Körperliche Aktivität" width="48" style="background-color: #9bc6a0; padding: 6px; border-radius: 6px;">

### Ausdauerorientierte Aktivität

#### Minuten in moderater und intensiver körperlichen Aktivität

**Beschreibung für Fachpersonal:**

Die dimensionsbasierte Ausdauer-Indikatorvariable für körperliche Aktivität umfasst die gesamte wöchentliche Dauer moderater und intensiver aerober Aktivität sowie die Einhaltung der empfohlenen Grenzwerte (≥150 Minuten moderate oder ≥75 Minuten intensive Aktivität pro Woche).

**Information für Bevölkerung:**

Regelmäßige evidenzbasierte körperliche Aktivität, wie zügiges Gehen oder Radfahren, stärkt Herz und Lunge, verbessert den Stoffwechsel und hilft, Krankheiten wie Type 2 Diabetes und Cardiovascular Disease vorzubeugen. Sie unterstützt außerdem das psychische Wohlbefinden und trägt dazu bei, Mobilität und Selbstständigkeit im Alter zu erhalten.

##### Messinstrumente

**Messinstrument 1** — Wearable device / sensor · automated
- **Einheit:** min/week
- **Datenformat:** min
- **Datentyp:** integer
- **Wertebereich:** min: 0 max: >48h/day
- **Erfassungsfrequenz:** Von 7 Tagen brauche ich mindestens 4 valide Tage um genommen. Pro Tag muss es mindestens 10 Stunden getragen werden.
- **Empfohlene Monitoringfrequenz:** pro Tag/täglich
- **FHIR IG Link:** -
- **FHIR IG Status:** planned
- **Sunburst-Chart Status:** published

**Spezifische Normen:**
- adults >=18 years: >=150 min /week

**Scoring-Algorithmus:** vigorous Intensitätsminuten x2

**Quellen:**
- [Norm?](Finger et al. 2015 https://pubmed.ncbi.nlm.nih.gov/26634120/)

**Messinstrument 2** — Questionnaire · manual (self-reported)
- **Einheit:** -
- **Datenformat:** -
- **Datentyp:** categorial
- **Wertebereich:** -
- **Erfassungsfrequenz:** Alle 3 Monate
- **Empfohlene Monitoringfrequenz:** Alle 6 Monate = 2x im Jahr
- **FHIR IG Link:** -
- **FHIR IG Status:** planned
- **Sunburst-Chart Status:** published

**Fragebögen:**
- **EHIS-PAQ (Q4-Q7)**: Q4: An wie vielen Tagen in einer typischen Woche fahren Sie mindestens 10 Minuten ohne Unterbrechung mit dem Fahrrad, um von Ort zu Ort zu gelangen?  

Antwortmöglichkeit: Nie oder seltener als einmal pro Woche; 1 Tag pro Woche; 2 Tage pro Woche  

3 Tage pro Woche;  4 Tage pro Woche; 5 Tage pro Woche; 6 Tage pro Woche; 7 Tage pro Woche 

Q5: Wie lange fahren Sie an einem typischen Tag mit dem Fahrrad, um von Ort zu Ort zu gelangen? 

Antwortmöglichkeit: 10 – 29 Minuten pro Tag;  30 – 59 Minuten pro Tag;  1 Stunde bis unter 2 Stunden pro Tag  

2 Stunden bis unter 3 Stunden pro Tag;  3 Stunden pro Tag oder mehr 

Q6: An wie vielen Tagen in einer typischen Woche üben Sie mindestens 10 Minuten ohne  Unterbrechung Sport, Fitness oder körperliche Aktivität in der Freizeit aus?  Zum Beispiel (Nordic-)Walking, Ballsport, Joggen, Fahrradfahren, Schwimmen, Aerobic, Rudern  oder Badminton  

Antwortmöglichkeiten: Nie oder seltener als einmal pro Woche; 1 Tag pro Woche; 2 Tage pro Woche; 3 Tage pro Woche; 4 Tage pro Woche; 5 Tage pro Woche; 6 Tage pro Woche; 7 Tage pro Woche 

Q7: Wie viel Zeit verbringen Sie insgesamt in einer typischen Woche mit Sport, Fitness oder  körperlicher Aktivität in der Freizeit?   

Antwortmöglichkeit:  \_\_\_ Stunden und \_\_\_ Minuten pro Woche

**Quellen:**
- [EHIS-PAQ Fragebogen](Finger et al. 2015 https://pubmed.ncbi.nlm.nih.gov/26634120/)

##### Terminologiecodes

| System | Code | Bezeichnung |
|---|---|---|
| http://loinc.org | 77593-2 | Physical activity - minutes per week at vigorous intensity |
| http://loinc.org | 77592-4 | Moderate physical activity [IPAQ] |

### Alltagsaktivität

#### Schrittzahl (pro Tag)

### Muskelkräftigende Übungen

_Keine Beobachtungen erfasst._

### Sitzen

_Keine Beobachtungen erfasst._

---

## Psychosoziale Faktoren

<img src="media/brain-circuit-white.png" alt="Psychosoziale Faktoren" width="48" style="background-color: #6e4e69; padding: 6px; border-radius: 6px;">

_Keine Dimensionen erfasst._

---

## Lebensqualität

<img src="media/heart-plus.png" alt="Lebensqualität" width="48" style="background-color: #f8e4bf; padding: 6px; border-radius: 6px;">

_Keine Dimensionen erfasst._

---

## Schlaf

<img src="media/bed_white.png" alt="Schlaf" width="48" style="background-color: #007ba7; padding: 6px; border-radius: 6px;">

### Schlafdauer

_Keine Beobachtungen erfasst._

### Schlafqualität

_Keine Beobachtungen erfasst._

---

## Rauchen

<img src="media/cigarette-off.png" alt="Rauchen" width="48" style="background-color: #004e64; padding: 6px; border-radius: 6px;">

### Raucherstatus

_Keine Beobachtungen erfasst._

---

## Soziodemografische Daten

<img src="media/person-standing-white.png" alt="Soziodemografische Daten" width="48" style="background-color: #e28913; padding: 6px; border-radius: 6px;">

_Keine Dimensionen erfasst._

---

## Arbeit

<img src="media/briefcase-business.png" alt="Arbeit" width="48" style="background-color: #9bc6a0; padding: 6px; border-radius: 6px;">

_Keine Dimensionen erfasst._

---

## Bearbeitungshistorie

_Änderungen seit Version v0.0.1-test:_

| Datum | Bearbeiter |
|---|---|
| 2026-07-27 | Theresa.Weitlaner |
