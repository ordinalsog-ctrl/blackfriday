# GitHub-Initialisierung

**Vorbedingungen:** ein **privates** leeres Repository auf GitHub erstellen, z. B. `blackfriday-intelligence`. Dieser Snapshot wurde **noch nicht** auf GitHub hochgeladen. GitHub-Secrets sind für den Offline-CI-Workflow nicht erforderlich.

```bash
cd ~/Downloads/blackfriday_intelligence_github_baseline
python3 -m venv .venv
source .venv/bin/activate
python -m unittest discover -s tests -v
git init -b main
git add .
git status --short
# Check: kein *.sqlite, kein .env, kein API-Key!
git commit -m "chore: baseline architecture, provenance and provider contracts"
git remote add origin https://github.com/DEIN-ACCOUNT/blackfriday-intelligence.git
git push -u origin main
```

Bei bereits existierendem Repository **nicht** blind `git init` oder `git push --force` verwenden. Änderungen auf Branch/Pull Request übernehmen. Ein lokaler Bestand mit den 120 Historienpunkten bleibt separat; bei Upgrades lokale DB nicht durch leere Repositoriumsdateien ersetzen.

## Empfohlene Repository-Einstellungen

- Repository privat bis Lizenz-/Datennutzungsrechte geklärt.
- Branch Protection für `main`: PR + CI erforderlich.
- Issues und Pull-Requests nutzen; Templates in `.github/`.
- Vor jedem Release: `docs/STATUS.md` und `docs/ROADMAP.md` aktualisieren.
- Bei Verdacht auf versehentlich veröffentlichten Schlüssel: Provider-Schlüssel rotieren, Git-History separat bereinigen.
