#!/usr/bin/env python3
"""
WHOQOL-BREF Auswertung nach offiziellem WHO-Scoring (entspricht der SPSS-Syntax der WHO).

Fragebogen:  F1-F26, Antworten 1-5 (leer oder '.' = fehlend)
Domänen:     Allgemeine Lebensqualität (F1), Allgemeine Gesundheit (F2),
             Physische Gesundheit (D1), Psychisches Wohlbefinden (D2),
             Soziale Beziehungen (D3), Umwelt (D4)
Skala:       0-100 (transformierte WHO-Skala)
Validität:   mind. 21 von 26 Items beantwortet

Umkehr-Items (negativ formuliert, werden vor Berechnung korrigiert): F3, F4, F26

SPSS-Äquivalent:
  dom  = mean(items) * 4          Rohwert 4-20
  domB = (dom - 4) * (100/16)     Score 0-100
  f1b  = (f1 - 1) * (100/4)       F1/F2 einzeln transformiert

Aufruf:
  python whoqol_bref.py "3,4,2,1,5,..."          # 26 kommagetrennte Werte
  python whoqol_bref.py --csv datei.csv           # CSV-Batch
"""

from __future__ import annotations
import csv
import sys
import re

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

REVERSED_ITEMS: set[int] = {3, 4, 26}

DOMAINS: dict[str, tuple[list[int], int]] = {
    "Allgemein":                ([1, 2],                         1),
    "Physische Gesundheit":     ([3, 4, 10, 15, 16, 17, 18],     6),
    "Psychisches Wohlbefinden": ([5, 6, 7, 11, 19, 26],          5),
    "Soziale Beziehungen":      ([20, 21, 22],                   2),
    "Umwelt":                   ([8, 9, 12, 13, 14, 23, 24, 25], 6),
}

MIN_TOTAL_VALID = 21
TOTAL_ITEMS     = 26


# ---------------------------------------------------------------------------
# Eingabe-Parser
# ---------------------------------------------------------------------------

def parse_inline(raw: str) -> dict[int, int | None]:
    """Komma- oder semikolongetrennte Antwortzeile: '3;4,2;1,...' (leer oder '.' = fehlend)"""
    # Splittet bei jedem Komma ODER Semikolon
    parts = [p.strip() for p in re.split(r"[,;]", raw)]
    if len(parts) != TOTAL_ITEMS:
        raise ValueError(f"Erwartet {TOTAL_ITEMS} Werte, erhalten: {len(parts)}")
    answers: dict[int, int | None] = {}
    for i, part in enumerate(parts, start=1):
        if part in ("", "."):
            answers[i] = None
        else:
            val = int(part)
            if not (1 <= val <= 5):
                raise ValueError(f"F{i}: Wert {val!r} ausserhalb 1-5")
            answers[i] = val
    return answers


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _reverse(v: int) -> int:
    return 6 - v


def individual_score(value: int | None) -> float | None:
    """F1 / F2 direkt auf 0-100: (v - 1) * (100/4)"""
    return None if value is None else (value - 1) * 25.0


def domain_score(items: list[int], min_valid: int,
                 corrected: dict[int, int | None]) -> float | None:
    """
    Domänen-Score 0-100 nach SPSS-Formel:
      dom  = mean(items) * 4
      score = (dom - 4) * (100/16)
    Gibt None zurück, wenn zu wenige Items beantwortet.
    """
    valid = [corrected[i] for i in items if corrected.get(i) is not None]
    if len(valid) < min_valid:
        return None
    mean = sum(valid) / len(valid)
    dom  = mean * 4
    return (dom - 4) * (100.0 / 16.0)


def compute_all(answers: dict[int, int | None]) -> dict:
    corrected = {
        f: (_reverse(v) if f in REVERSED_ITEMS and v is not None else v)
        for f, v in answers.items()
    }
    n_valid = sum(1 for v in answers.values() if v is not None)
    result: dict = {
        "n_valid":   n_valid,
        "is_valid":  n_valid >= MIN_TOTAL_VALID,
        "f1_value":  answers.get(1),
        "f2_value":  answers.get(2),
        "f1_score":  individual_score(answers.get(1)),
        "f2_score":  individual_score(answers.get(2)),
        "domains":   {},
    }
    for name, (items, min_valid) in DOMAINS.items():
        score = domain_score(items, min_valid, corrected)
        item_values = {i: corrected.get(i) for i in items}
        valid_vals  = [v for v in item_values.values() if v is not None]
        result["domains"][name] = {
            "items":       items,
            "min_valid":   min_valid,
            "item_values": item_values,
            "n_valid":     len(valid_vals),
            "sum_points":  sum(valid_vals) if valid_vals else None,
            "score":       round(score, 1) if score is not None else None,
        }
    return result


# ---------------------------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------------------------

def _label(score: float) -> str:
    if score < 25:  return "sehr niedrig"
    if score < 50:  return "niedrig"
    if score < 75:  return "mittel"
    return "hoch"


def print_results(result: dict, header: str = "") -> None:
    print("\n" + "=" * 62)
    if header:
        print(f"  {header}")
    print("  ERGEBNISSE  -  WHOQOL-BREF")
    print("=" * 62)

    n, ok = result["n_valid"], result["is_valid"]
    if ok:
        print(f"\nFragebogen-Status: gueltig  ({n}/{TOTAL_ITEMS} Items)")
    else:
        print(f"\nFragebogen-Status: UNGUELTIG ({n}/{TOTAL_ITEMS} beantwortet, "
              f"Minimum: {MIN_TOTAL_VALID})")
        print("Achtung: Domänenscores werden dennoch ausgewiesen (wo berechenbar).")

    print(f"\n{'Bereich':<30}  {'Score':>6}  Bewertung")
    print("-" * 62)
    for label, val_key, score_key in [
        ("Allgemeine Lebensqualitaet (F1)", "f1_value", "f1_score"),
        ("Allgemeine Gesundheit (F2)",      "f2_value", "f2_score"),
    ]:
        s = result[score_key]
        v = result[val_key]
        if s is None:
            print(f"  {label:<28}     ---  (fehlend)")
        else:
            print(f"  {label:<28}  {s:>5.1f}  {_label(s)}  [Antwort: {v}]")
    print()
    for name, data in result["domains"].items():
        s      = data["score"]
        nv     = data["n_valid"]
        ntotal = len(data["items"])
        sp     = data["sum_points"]
        if s is None:
            print(f"  {name:<28}     ---  (nur {nv}/{ntotal} Items)")
        else:
            print(f"  {name:<28}  {s:>5.1f}  {_label(s)}")
            vals_parts = []
            for i in data["items"]:
                v = data["item_values"].get(i)
                rev = "*" if i in REVERSED_ITEMS else ""
                vals_parts.append(f"F{i}{rev}={v if v is not None else '?'}")
            print(f"    Punkte: {', '.join(vals_parts)}")
            print(f"    Summe: {sp}  ({nv}/{ntotal} Items)")

    print("\n" + "-" * 62)
    print("Skala: 0-24=sehr niedrig | 25-49=niedrig | 50-74=mittel | 75-100=hoch")
    print("Umkehr-Items (korrigiert): F3, F4, F26")
    print("=" * 62)


# ---------------------------------------------------------------------------
# CSV-Batch
# ---------------------------------------------------------------------------

def process_csv(filepath: str) -> None:
    with open(filepath, newline="", encoding="utf-8-sig") as fh:
        sample = fh.read(2048); fh.seek(0)
        delim = ";" if sample.count(";") >= sample.count(",") else ","
        reader = csv.DictReader(fh, delimiter=delim)
        for row in reader:
            row_id = row.get("ID", "").strip()
            profil = row.get("Profil", "").strip()
            header = f"ID {row_id}" + (f" - {profil}" if profil else "")

            answers: dict[int, int | None] = {}
            for i in range(1, TOTAL_ITEMS + 1):
                raw = row.get(f"F{i}", "").strip()
                if raw in ("", "."):
                    answers[i] = None
                else:
                    try:
                        val = int(raw)
                        answers[i] = val if 1 <= val <= 5 else None
                    except ValueError:
                        answers[i] = None

            print_results(compute_all(answers), header)


# ---------------------------------------------------------------------------
# Einstiegspunkt
# ---------------------------------------------------------------------------

USAGE = """
Verwendung:
  python whoqol_bref.py "v1,v2,...,v26"      Einzelauswertung (26 Werte 1-5, leer=fehlend)
  python whoqol_bref.py --csv datei.csv      Batch-Auswertung einer CSV-Datei

CSV-Format (Semikolon- oder Komma-getrennt):
  Pflichtfelder: F1 bis F26
  Optional:      ID, Profil
"""


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(USAGE)
        sys.exit(0)

    if sys.argv[1] == "--csv":
        if len(sys.argv) < 3:
            print("Fehler: --csv benoetigt einen Dateipfad.")
            sys.exit(1)
        process_csv(sys.argv[2])
        return

    try:
        answers = parse_inline(sys.argv[1])
    except ValueError as e:
        print(f"Fehler: {e}")
        sys.exit(1)
    print_results(compute_all(answers))


if __name__ == "__main__":
    main()
