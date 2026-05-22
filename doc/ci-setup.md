# CI Setup — Gitea Actions

Der Workflow `.gitea/workflows/update-profile.yml` regeneriert bei jedem Push auf `main` automatisch `health-profile.json` und die Markdown-Reports.

## Voraussetzung: Gitea Runner

Gitea Actions benötigt einen konfigurierten Runner auf dem Server. Ohne Runner werden Workflows zwar erkannt, aber nicht ausgeführt.

### Runner installieren und registrieren

```bash
# Runner-Binary herunterladen (siehe https://gitea.com/gitea/act_runner/releases)
wget https://gitea.com/gitea/act_runner/releases/download/v0.2.11/act_runner-0.2.11-linux-amd64 -O act_runner
chmod +x act_runner

# Runner beim Gitea registrieren
# Token: Gitea → Repository → Einstellungen → Actions → Runner → Token erstellen
./act_runner register \
  --instance https://health.joanneum.at/git \
  --token <runner-token> \
  --name prenudge-runner \
  --labels ubuntu-latest

# Runner starten
./act_runner daemon
```

Für einen dauerhaften Betrieb empfiehlt sich ein systemd-Service:

```ini
# /etc/systemd/system/act_runner.service
[Unit]
Description=Gitea Actions Runner
After=network.target

[Service]
ExecStart=/opt/act_runner/act_runner daemon
WorkingDirectory=/opt/act_runner
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable --now act_runner
```

---

## Workflow-Verhalten

**Trigger:** Push auf `main`, aber nur wenn sich folgende Pfade ändern:
- `hp-categories/**`, `hp-dimensions/**`, `hp-observations/**`, `data-provider/**`
- `scripts/**`, `render/templates/**`

Änderungen an generierten Dateien (`health-profile.json`, `*.md`) triggern den Workflow **nicht**.

**Schritte:**

| Schritt | Was passiert |
|---|---|
| Checkout | Vollständiger Verlauf (`fetch-depth: 0`) für `git log` (Bearbeitungshistorie) |
| Validate | `validate.py --strict` — bricht ab bei kaputten Referenzen |
| Consolidate | `consolidate.py` mit aktueller Version aus JSON |
| Render | `render_doc.py` generiert DE- und EN-Markdown |
| Commit | Geänderte Dateien werden mit `[skip ci]` zurückgepusht |

**Loop-Prävention:** Der Commit-Rückschritt verwendet `[skip ci]` im Commit-Message — Gitea überspringt dadurch den nächsten Workflow-Run.

**Versionshandling:** Der Workflow liest die Version aus dem bestehenden `health-profile.json` und übernimmt sie unverändert. Die Version wird **nicht** automatisch erhöht — das bleibt Teil des manuellen Release-Prozesses (siehe `doc/release.md`).

---

## Workflow manuell triggern

Über die Gitea-UI unter **Repository → Actions → Update Health Profile → Run workflow**, oder per API:

```bash
curl -X POST https://health.joanneum.at/git/api/v1/repos/PreNudge/prenudge-health-profile/actions/workflows/update-profile.yml/dispatches \
  -H "Authorization: token <api-token>" \
  -H "Content-Type: application/json" \
  -d '{"ref": "main"}'
```
