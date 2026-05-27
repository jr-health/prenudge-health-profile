"""
Tests für whoqol_bref.py

Unit-Tests:   Kernfunktionen einzeln (Umkehrung, Einzel-Score, Domänen-Score, Gültigkeit)
Integrations: Alle 20 CSV-Datensätze gegen hinterlegte E_-Spalten geprüft

Ausführung:
    python -m pytest test_whoqolbref.py -v
    python test_whoqolbref.py          (unittest-Fallback)
"""

import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from whoqol_bref import (
    _reverse,
    individual_score,
    domain_score,
    compute_all,
    MIN_TOTAL_VALID,
    TOTAL_ITEMS,
    DOMAINS,
)

CSV_PATH = Path(__file__).parent / "whoqol_bref_testdaten.csv"

# Mapping E_-Spalte → Domänenname
DOMAIN_COLS: dict[str, str] = {
    "Physische Gesundheit":     "E_D1",
    "Psychisches Wohlbefinden": "E_D2",
    "Soziale Beziehungen":      "E_D3",
    "Umwelt":                   "E_D4",
}


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _load_csv() -> list[dict]:
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def _parse_answers(row: dict) -> dict[int, int | None]:
    answers: dict[int, int | None] = {}
    for i in range(1, TOTAL_ITEMS + 1):
        raw = row.get(f"F{i}", "").strip()
        if raw in ("", "."):
            answers[i] = None
        else:
            v = int(raw)
            answers[i] = v if 1 <= v <= 5 else None
    return answers


# ---------------------------------------------------------------------------
# Unit-Tests: Kernfunktionen
# ---------------------------------------------------------------------------

class TestReverse(unittest.TestCase):

    def test_all_values(self):
        for v in range(1, 6):
            self.assertEqual(_reverse(v), 6 - v)

    def test_midpoint(self):
        self.assertEqual(_reverse(3), 3)


class TestIndividualScore(unittest.TestCase):

    def test_minimum(self):
        self.assertAlmostEqual(individual_score(1), 0.0)

    def test_maximum(self):
        self.assertAlmostEqual(individual_score(5), 100.0)

    def test_midpoint(self):
        self.assertAlmostEqual(individual_score(3), 50.0)

    def test_none_input(self):
        self.assertIsNone(individual_score(None))

    def test_linear_steps(self):
        scores = [individual_score(v) for v in range(1, 6)]
        for s1, s2 in zip(scores, scores[1:]):
            self.assertAlmostEqual(s2 - s1, 25.0)


class TestDomainScore(unittest.TestCase):

    def _corrected(self, values: list[int]) -> dict[int, int | None]:
        return {i + 1: v for i, v in enumerate(values)}

    def test_all_maximum(self):
        c = self._corrected([5, 5, 5])
        self.assertAlmostEqual(domain_score([1, 2, 3], 3, c), 100.0)

    def test_all_minimum(self):
        c = self._corrected([1, 1, 1])
        self.assertAlmostEqual(domain_score([1, 2, 3], 3, c), 0.0)

    def test_all_midpoint(self):
        c = self._corrected([3, 3, 3])
        self.assertAlmostEqual(domain_score([1, 2, 3], 3, c), 50.0)

    def test_score_75(self):
        c = self._corrected([4, 4, 4])
        self.assertAlmostEqual(domain_score([1, 2, 3], 3, c), 75.0)

    def test_insufficient_items_returns_none(self):
        c = {1: 3, 2: None, 3: None}   # 1 valid, min=2
        self.assertIsNone(domain_score([1, 2, 3], 2, c))

    def test_exactly_min_valid(self):
        c = {1: 4, 2: 4, 3: None}      # 2 valid, min=2 → OK
        self.assertIsNotNone(domain_score([1, 2, 3], 2, c))
        self.assertAlmostEqual(domain_score([1, 2, 3], 2, c), 75.0)

    def test_all_none_returns_none(self):
        c = {1: None, 2: None, 3: None}
        self.assertIsNone(domain_score([1, 2, 3], 1, c))


class TestValidity(unittest.TestCase):

    def _answers(self, n_missing: int) -> dict[int, int | None]:
        a = {i: 3 for i in range(1, TOTAL_ITEMS + 1)}
        for i in range(1, n_missing + 1):
            a[i] = None
        return a

    def test_all_answered_valid(self):
        self.assertTrue(compute_all(self._answers(0))["is_valid"])

    def test_5_missing_valid(self):
        r = compute_all(self._answers(5))
        self.assertTrue(r["is_valid"])
        self.assertEqual(r["n_valid"], 21)

    def test_6_missing_invalid(self):
        r = compute_all(self._answers(6))
        self.assertFalse(r["is_valid"])
        self.assertEqual(r["n_valid"], 20)

    def test_all_missing_invalid(self):
        a = {i: None for i in range(1, TOTAL_ITEMS + 1)}
        self.assertFalse(compute_all(a)["is_valid"])


class TestReversedItemsApplied(unittest.TestCase):
    """Stellt sicher, dass F3, F4, F26 tatsächlich umgekehrt werden."""

    def test_f3_reversed_in_physical(self):
        # F3=1 → korrigiert zu 5 → physische Gesundheit muss maximal sein (wenn Rest=5)
        answers = {i: 5 for i in range(1, TOTAL_ITEMS + 1)}
        answers[3]  = 1   # negativ formuliert, 1=am besten
        answers[4]  = 1
        answers[26] = 1
        r = compute_all(answers)
        self.assertAlmostEqual(r["domains"]["Physische Gesundheit"]["score"], 100.0)

    def test_f26_reversed_in_psychological(self):
        answers = {i: 5 for i in range(1, TOTAL_ITEMS + 1)}
        answers[3]  = 1
        answers[4]  = 1
        answers[26] = 1
        r = compute_all(answers)
        self.assertAlmostEqual(r["domains"]["Psychisches Wohlbefinden"]["score"], 100.0)


# ---------------------------------------------------------------------------
# Integrations-Tests: alle 20 CSV-Datensätze
# ---------------------------------------------------------------------------

class TestCsvDatasets(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rows = _load_csv()

    def test_csv_row_count(self):
        self.assertEqual(len(self.rows), 20)

    def test_csv_has_expected_columns(self):
        required = {f"F{i}" for i in range(1, 27)} | {"E_Gueltig", "E_F1", "E_F2",
                                                        "E_D1", "E_D2", "E_D3", "E_D4"}
        actual = set(self.rows[0].keys())
        self.assertTrue(required.issubset(actual),
                        f"Fehlende CSV-Spalten: {required - actual}")

    def test_all_datasets(self):
        for row in self.rows:
            row_id = row["ID"]
            profil = row.get("Profil", "")
            answers = _parse_answers(row)
            result  = compute_all(answers)

            with self.subTest(id=row_id, profil=profil):
                expected_valid = row["E_Gueltig"].strip() == "1"
                self.assertEqual(
                    result["is_valid"], expected_valid,
                    f"Gültigkeit: erwartet {'gültig' if expected_valid else 'ungültig'}")

                # F1 / F2
                for key, col in [("f1_score", "E_F1"), ("f2_score", "E_F2")]:
                    exp = row.get(col, "").strip()
                    got = result[key]
                    if exp:
                        self.assertIsNotNone(got, f"{col} sollte nicht None sein")
                        self.assertAlmostEqual(got, float(exp), places=1,
                                               msg=f"{col}: erwartet {exp}, erhalten {got}")
                    else:
                        self.assertIsNone(got, f"{col} sollte None sein")

                # Domänen
                for domain_name, e_col in DOMAIN_COLS.items():
                    exp = row.get(e_col, "").strip()
                    got = result["domains"][domain_name]["score"]
                    if exp:
                        self.assertIsNotNone(got,
                            f"{domain_name}: Score sollte nicht None sein")
                        self.assertAlmostEqual(got, float(exp), places=1,
                            msg=f"{domain_name}: erwartet {exp}, erhalten {got}")
                    else:
                        self.assertIsNone(got,
                            f"{domain_name}: Score sollte None sein (zu wenige Items)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
