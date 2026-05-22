# Release-Workflow

Releases basieren auf **Git Tags** (`v1.2.0`) auf Gitea. Das `health-profile.json` enthält immer ein `version`-Feld, damit Konsumenten die Version ohne Git-Kenntnisse erkennen können.

## SemVer-Definition

| | Änderungstyp | Beispiele |
|---|---|---|
| **MAJOR** | Breaking — Konsumenten müssen angepasst werden | Key umbenannt; Feld entfernt; Feldtyp geändert (String → Liste); Collection-Struktur grundlegend geändert |
| **MINOR** | Additiv — bestehende Konsumenten funktionieren weiter | Neue Category / Dimension / Observation; neues optionales Feld; neue Collection aktiviert |
| **PATCH** | Inhaltliche Korrektur — kein Struktureinfluss | Tipp-/Inhaltsfehler; falscher FHIR-Code; Link aktualisiert; leeres Pflichtfeld befüllt; kaputte Referenz repariert |

---

## Release-Schritte

### 1. Validierung

Vor jedem Release Referenzintegrität prüfen — Fehler müssen vor dem Release behoben werden:

```
py scripts/validate.py --strict
```

### 2. Konsolidierung mit Versionsnummer

```
py scripts/consolidate.py --version 1.2.0
```

Das erzeugt `health-profile.json` mit `"version": "1.2.0"` im Header.

### 3. Committen

```
git add health-profile.json
git commit -m "Release v1.2.0"
```

### 4. Tag setzen und pushen

```
git tag v1.2.0
git push origin main
git push origin v1.2.0
```

Gitea erzeugt aus dem Tag automatisch einen Release-Eintrag mit Download-Link für das Repository-Archiv.

### 5. Gitea Release vervollständigen (optional)

Unter **Releases → Draft a new release** auf Gitea:
- Tag `v1.2.0` auswählen
- Release Notes eintragen (was hat sich geändert, welche SemVer-Kategorie)
- `health-profile.json` als zusätzliches Artefakt anhängen

---

## Versionsnummer bestimmen

Die aktuelle Version ist im `health-profile.json` unter `"version"` ablesbar oder per Tag-Liste:

```
git tag --sort=-version:refname | head -5
```

Nächste Version ableiten:
- Gab es einen Key-Rename oder Feld-Entfernung? → **MAJOR** erhöhen, MINOR und PATCH auf 0
- Nur neue Einträge oder Felder hinzugekommen? → **MINOR** erhöhen, PATCH auf 0
- Nur Inhaltskorrekturen? → **PATCH** erhöhen
