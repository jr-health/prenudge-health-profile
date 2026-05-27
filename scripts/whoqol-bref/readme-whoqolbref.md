# WHOQOL-BREF Auswertungs-Script

Python-Script zur Berechnung der Domänen-Scores des **WHOQOL-BREF** (World Health Organization Quality of Life – kurze Version - https://www.who.int/tools/whoqol/whoqol-bref) nach dem offiziellen WHO-Scoring-Manual. Die Implementierung entspricht der publizierten SPSS-Syntax der WHO.

---

## Online Rechner liefern falsches Ergebnis

Online Rechner wie z.B. https://neurotoolkit.com/whoqol-bref/ oder https://orthopowertools.com/WHOQOLBREF haben einen Rundungsfehler.

Neurotoolkit rundet das Zwischenergebnis, unser Skript nicht.

Rechenweg im Detail

|                 Schritt                  |  Unser Skript (WHO-SPSS)   |         Neurotoolkit         |
|---|---|---|
| Rohdaten F3, F4, F10, F15, F16, F17, F18 | 2, 1, 4, 4, 4, 4, 4        | identisch                    |
| Nach Umkehrung F3/F4                     | 4, 5, 4, 4, 4, 4, 4        | identisch                    |
| Summe (Raw Score 7–35)                   | 29                         | 29 ✓                         |
| Mittelwert                               | 29 ÷ 7 = 4.1429            | 29 ÷ 7 = 4.1429              |
| dom (4–20) = Mittelwert × 4              | 16.571                     | 17 ← rundet auf Integer      |
| Score (0–100) = (dom − 4) × 100/16       | (16.571 − 4) × 6.25 = 78.6 | (17 − 4) × 6.25 = 81.25 → 81 |
      
                                                    
## SPSS Definition - Validierung

Es gibt ein SPSS-Script für die Berechnung von https://www.who.int/tools/whoqol/whoqol-bref unter `WHOQOL-BREF_Syntax_files`. Man kann es mit https://www.gnu.org/software/pspp/ laufen lassen. Das Skript filtert ungültige Fragebögen heraus. Dazu wurde das Skript um die Testdaten erweitert und RELIABILITY auskommentiert, weil nicht von PSPP unterstützt.,

```
COUNT TOTAL=F1 TO F26 (1 THRU 5).
SELECT IF (TOTAL>=21).
```

`SELECT IF` entfernt alle Fälle mit weniger als 21 gültigen Items aus der weiteren Analyse. Datensatz 20 hat nur 19 gültige Items → wird ausgeschlossen → 19 Ergebniszeilen.

Das entspricht der WHO-Vorgabe: Ein ungültiger Fragebogen soll nicht ausgewertet werden. Die berechneten Domänenwerte für Datensatz 20 existieren zwar im Speicher, werden aber nicht in die Ausgabe übernommen.

Unser Python-Skript verhält sich anders: es markiert den Fragebogen als ungültig, zeigt aber trotzdem die berechenbaren Domänenwerte an. Das ist eine bewusste Designentscheidung, die wir getroffen haben — beides ist vertretbar.

### Validierung der CSV Testdaten

Die CSV-Testdaten wurden manuell (TRT) mit den Berechnungsergebnissen aus dem SPSS verglichen - bis auf Rundungen in den Nachkommastellen passen die Ergebnisse im CSV.

## Dateien

| Datei | Beschreibung |
|---|---|
| `whoqol_bref.py` | Auswertungs-Script (Python ≥ 3.10) |
| `whoqol_bref_testdaten.csv` | 20 Testdatensätze mit erwarteten Ergebnissen |
| `test_whoqolbref.py` | Automatisierte Tests (unittest, kein extra Package nötig) |

---

## Fragebogen-Struktur

Der WHOQOL-BREF umfasst **26 Items (F1–F26)** mit einer 5-stufigen Antwortskala:

| Wert | Bedeutung |
|---|---|
| 1 | sehr schlecht / überhaupt nicht / nie |
| 2 | schlecht / wenig / selten |
| 3 | mittelmäßig / manchmal |
| 4 | gut / meistens / oft |
| 5 | sehr gut / äußerst / immer |

---

## Domänen und zugehörige Items

| Domäne | Items | Mindest-Items |
|---|---|---|
| **Allgemeine Lebensqualität** | F1 | – (Einzelitem) |
| **Allgemeine Gesundheit** | F2 | – (Einzelitem) |
| **Physische Gesundheit** | F3, F4, F10, F15, F16, F17, F18 | 6 von 7 |
| **Psychisches Wohlbefinden** | F5, F6, F7, F11, F19, F26 | 5 von 6 |
| **Soziale Beziehungen** | F20, F21, F22 | 2 von 3 |
| **Umwelt** | F8, F9, F12, F13, F14, F23, F24, F25 | 6 von 8 |

### Umkehr-Items (negativ formuliert)

Die Items **F3**, **F4** und **F26** sind negativ formuliert und werden vor der Berechnung umgekehrt:

```
Korrigierter Wert = 6 − Rohwert
```

Beispiel: F3 = 4 (starke Schmerzen) → korrigiert zu 2

---

## Scoring-Formel

Die Berechnung folgt exakt der offiziellen SPSS-Syntax der WHO:

### Schritt 1 – Rohwert (4–20-Skala)
```
dom = Mittelwert(Items) × 4
```

### Schritt 2 – Transformation auf 0–100
```
Score = (dom − 4) × (100 / 16)
```

**Kurzform:** `Score = ((Mittelwert − 1) / 4) × 100`

### F1 und F2 (Einzelitems)
```
Score = (Rohwert − 1) × (100 / 4)
```

### Referenzwerte
| Rohwert (Mittelwert) | Score 0–100 |
|---|---|
| 1 | 0 |
| 2 | 25 |
| 3 | 50 |
| 4 | 75 |
| 5 | 100 |

---

## Gültigkeitsregel

Ein Fragebogen ist nur auswertbar, wenn **mindestens 21 von 26 Items** beantwortet wurden (≤ 5 fehlende Werte). Wird die Mindestanzahl unterschritten, gibt das Script eine Warnung aus und verweigert die Auswertung.

Zusätzlich gilt pro Domäne eine Mindestanzahl (siehe Tabelle oben): Fehlen zu viele Items einer Domäne, wird deren Score als `---` (nicht berechenbar) ausgegeben.

---

## Interpretationsskala

| Score 0–100 | Bewertung |
|---|---|
| 0–24 | sehr niedrig |
| 25–49 | niedrig |
| 50–74 | mittel |
| 75–100 | hoch |

---

## Verwendung

### Inline-Modus (einzelner Datensatz)
26 kommagetrennte Antworten als Argument. Leeres Feld oder `.` = fehlend.

```
python whoqol_bref.py "4,4,2,1,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2"
```

### CSV-Batch-Modus (mehrere Datensätze)
Verarbeitet alle Zeilen einer CSV-Datei und gibt die Ergebnisse sequenziell aus.

```
python whoqol_bref.py --csv whoqol_bref_testdaten.csv
```

Ausgabe in Datei umleiten:

```
python whoqol_bref.py --csv whoqol_bref_testdaten.csv > ergebnisse.txt
```

---

## CSV-Format

Das CSV verwendet **Semikolon** als Trennzeichen (Excel-kompatibel, deutsches Gebietsschema). Das Script erkennt Semikolon- und Komma-getrennte Dateien automatisch.

### Pflicht-Spalten
`F1` bis `F26` — Rohwerte 1–5. Leeres Feld oder `.` wird als fehlender Wert behandelt.

### Optionale Spalten
`ID` und `Profil` — werden nur für die Ausgabe verwendet, nicht für die Berechnung.

`E_Gueltig`, `E_F1`, `E_F2`, `E_D1`–`E_D4` — erwartete Ergebnisse für automatisierte Tests (werden vom Script ignoriert, von `test_whoqolbref.py` gelesen).

### Beispiel-Header (Eingabe-Spalten)
```
ID;Profil;F1;F2;F3;F4;F5;F6;F7;F8;F9;F10;F11;F12;F13;F14;F15;F16;F17;F18;F19;F20;F21;F22;F23;F24;F25;F26
```

### Eigene Datensätze hinzufügen
1. CSV in einem Tabellenkalkulationsprogramm öffnen
2. Neue Zeile am Ende anfügen
3. ID vergeben, Profil beschreiben, F1–F26 ausfüllen
4. E_Gueltig und E_F1/F2/D1–D4 mit den erwarteten Werten befüllen (optional, aber empfohlen)
5. Als CSV (Semikolon-getrennt) speichern
6. Script mit `--csv` ausführen, Tests mit `python test_whoqolbref.py` prüfen

---

## Testdatensätze – Übersicht

| ID | Profil | Besonderheit |
|---|---|---|
| 1 | Maximale LQ | Alle Items optimal — Score 100 in allen Domänen |
| 2 | Gute LQ | Referenzprofil für Score ≈ 75 |
| 3 | Mittlere LQ | Alle Items = 3 — Score exakt 50 in allen Domänen |
| 4 | Schlechte LQ | Score ≈ 25 in allen Domänen |
| 5 | Minimale LQ | Alle Items negativ — Score 0 in allen Domänen |
| 6 | Körperliche Einschränkungen | Niedrige Physik, Rest mittel–gut |
| 7 | Psychische Belastung | Depression/Angst-Muster |
| 8 | Soziale Isolation | F20/F21/F22 = 1, Rest gut |
| 9 | Umweltprobleme | Niedrige Umwelt-Domäne, Rest gut |
| 10 | Chron. Erkrankung | Ältere Person, gemischt niedrig–mittel |
| 11 | Junger Erwachsener | Sozial gut integriert, hohe Werte |
| 12 | Burnout-Symptome | Niedrige Psyche und Physik |
| 13 | Aktive Seniorin | Mittel–hohe Werte in allen Domänen |
| 14 | Chron. Schmerzen, gute Psyche | Niedrige Physik, hohe Psyche |
| 15 | Sozial gut, finanziell arm | Niedrige Umwelt (F12=1), hohe Soziales |
| 16 | 1 fehlender Wert (F21) | Gültiger Fragebogen, eine Lücke |
| 17 | 3 fehlende Werte (F7, F19, F24) | Gültig (23/26), E_D2 leer (nur 4/6 Psych.-Items) |
| 18 | Gemischtes Profil | Varied, alle Domänen um 50–60 |
| 19 | Gute Physik, schlechte Psyche | Inverses Domänenprofil |
| 20 | **UNGÜLTIG** | 7 fehlende Werte (19/26) → Auswertung verweigert |

---

## Tests

### Ausführung

```
python test_whoqolbref.py
```

Kein zusätzliches Package nötig — verwendet das eingebaute `unittest`-Modul. Mit installiertem `pytest` alternativ:

```
python -m pytest test_whoqolbref.py -v
```

### Abdeckung (23 Tests)

| Testklasse | Was wird geprüft |
|---|---|
| `TestReverse` | Umkehr-Formel (`6 − Rohwert`) für alle Werte 1–5 |
| `TestIndividualScore` | F1/F2-Transformation: Min, Max, Mitte, Linearität, None-Input |
| `TestDomainScore` | Domänen-Score: Extremwerte, Mitte, fehlende Items (ausreichend / zu wenige) |
| `TestValidity` | Gültigkeitsschwelle: exakt 21 (gültig), exakt 20 (ungültig), alle fehlend |
| `TestReversedItemsApplied` | F3, F4, F26 werden korrekt in die Domänenberechnung eingesetzt |
| `TestCsvDatasets` | Alle 20 Datensätze: Gültigkeit + alle 6 Score-Spalten gegen E_-Werte |

### E_-Spalten im CSV

Die Spalten `E_Gueltig`, `E_F1`, `E_F2`, `E_D1`–`E_D4` in `whoqol_bref_testdaten.csv` enthalten die erwarteten Ergebnisse. `test_whoqolbref.py` liest diese und vergleicht sie mit den berechneten Werten (Toleranz ±0,05 durch `assertAlmostEqual(places=1)`).

Leere E_-Spalten bedeuten:
- Fragebogen ungültig (E_Gueltig=0) → keine Score-Prüfung
- Domäne nicht berechenbar (zu wenige Items) → Score muss `None` sein

---

## Quellen

- WHO (1996): *WHOQOL-BREF: Introduction, Administration, Scoring and Generic Version of the Assessment.* Geneva: World Health Organization.
- The WHOQOL Group (1998): Development of the World Health Organization WHOQOL-BREF Quality of Life Assessment. *Psychological Medicine*, 28(3), 551–558.
- Offizielle deutsche Adaptation: Universität Zürich / DIMDI.
