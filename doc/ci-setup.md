# CI Setup — GitHub Actions

Der Workflow `.github/workflows/update-profile.yml` regeneriert bei jedem Push auf `main`
automatisch `health-profile.json` und die Markdown-Reports. Er läuft auf GitHub-gehosteten
Runnern — es ist kein eigener Runner zu installieren oder zu betreiben.

## Workflow-Verhalten

**Trigger:** Push auf `main`, aber nur wenn sich folgende Pfade ändern:
- `hp-categories/**`, `hp-dimensions/**`, `hp-observations/**`, `data-provider/**`
- `scripts/**`, `render/templates/**`

Zusätzlich manuell auslösbar über **Actions → Update Health Profile → Run workflow**
(`workflow_dispatch`).

Änderungen an generierten Dateien (`health-profile.json`, `*.md`) triggern den Workflow
**nicht**.

**Schritte:**

| Schritt | Was passiert |
|---|---|
| Checkout | Vollständiger Verlauf (`fetch-depth: 0`) für `git log` (Bearbeitungshistorie) |
| Validate | `validate.py --strict` — bricht ab bei kaputten Referenzen |
| Consolidate | `consolidate.py` mit aktueller Version aus JSON |
| Render | `render_doc.py` generiert DE- und EN-Markdown |
| Commit | Geänderte Dateien werden mit `[skip ci]` zurückgepusht (Committer: `github-actions[bot]`) |

**Berechtigungen:** Der Workflow setzt `permissions: contents: write` explizit, damit der
Commit-back mit dem Standard-`GITHUB_TOKEN` funktioniert. Voraussetzung ist, dass auf `main`
keine Branch-Protection-Regel aktiv ist, die das verhindert (aktuell nicht der Fall, siehe
`doc/github-actions-plan.md`, Phase 2, Schritt 9).

**Loop-Prävention:** Der Commit-Rückschritt verwendet `[skip ci]` im Commit-Message — GitHub
Actions überspringt dadurch den nächsten Workflow-Run für diesen Commit. Zusätzlich sind
`health-profile.json`/`*.md` ohnehin nicht Teil der Pfad-Filter, lösen also auch ohne
`[skip ci]` keinen erneuten Lauf aus.

**Versionshandling:** Der Workflow liest die Version aus dem bestehenden `health-profile.json`
und übernimmt sie unverändert. Die Version wird **nicht** automatisch erhöht — das bleibt Teil
des manuellen Release-Prozesses (siehe `doc/release.md`).

---

Die Pipeline lief vor der GitHub-Migration als `.gitea/workflows/update-profile.yml` auf einem
selbst betriebenen Gitea-Runner unter `health.joanneum.at/git`. Das Gitea-Repository ist
aktuell eingefroren und wird nicht weiter bearbeitet; der historische Runner-Setup ist dort
weiterhin nachvollziehbar und wird hier nicht dupliziert.
