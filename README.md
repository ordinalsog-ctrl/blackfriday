# Black Friday Intelligence — GitHub-Baseline v0.8

**Modularer Preisbeobachtungs-Prototyp, kein produktives Deal-Portal.** Markt: Deutschland zuerst, EU-Länder geplant. 500 redaktionelle Kandidaten sind **keine** validierten Bestseller. Die vom Betreiber gemeldeten 120 Samsung-Historienpunkte befinden sich **nur in dessen lokaler SQLite-Datei**, nicht im Repository und nicht im Bewertungs-View.

**Einstieg:** [Ist-Stand](docs/STATUS.md) · [Architektur](docs/ARCHITECTURE.md) · [Roadmap](docs/ROADMAP.md) · [API-Adaptervertrag](docs/PROVIDER_CONTRACT.md) · [Sicherheit](docs/SECURITY.md) · [ADRs](docs/DECISIONS/ADR-0001-modular-monolith.md)

## Lokal starten (Python 3.12/3.13)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py init
python -m unittest discover -s tests -v
streamlit run app.py
```

`python main.py init` erstellt eine **neue lokale** `blackfriday.sqlite`, ohne Live-Historie. Eine bestehende Datenbank **vorher sichern**, nicht versehentlich überschreiben. In GitHub ist die Datenbank ausgeschlossen.

## Scrappa-CLI mit gesicherter Identität

```bash
# Schlüssel lokal setzen (nicht ins Repo committen)
read -rs SCRAPPA_API_KEY; echo; export SCRAPPA_API_KEY
python scrappa_cli.py search --product-id BF-0001 --query 'Samsung Galaxy A56 128GB Graphite'
python scrappa_cli.py audit --product-id BF-0001
# Alte ungültige Freigabe im bestehenden lokalen DB-Bestand zurücknehmen:
python scrappa_cli.py revoke --product-id BF-0001 --geizhals-id 3430460 --reason 'Platzhalter-Link ist kein Identitätsnachweis'
# Nach tatsächlich geprüftem Geizhals-Link und MPN:
python scrappa_cli.py verify --product-id BF-0001 --geizhals-id 3430460 --confirmed-mpn SM-A566BZKA --identity-evidence 'DEINE_TATSAECHLICH_GEPRUEFTE_GEIZHALS_URL'
python scrappa_cli.py history --product-id BF-0001 --geizhals-id 3430460 --days 120 --market de
```

**Hinweis:** `verify` prüft URL-Form und Modellnummern-Konsistenz, nicht den externen Seiteninhalt. Die konkrete Adresse im Beispiel ist **nur ein Platzhalter**; eine echte URL verwenden. Die manuelle Freigabe bleibt eine menschliche Behauptung, bis der Nachweis unabhängig geprüft wurde. Historien werden selbst nach Verifizierung **nicht** automatisch zum Deal-Score zugelassen.

## GitHub-Anbindung

Es ist kein vorhandenes Ziel-Repository bekannt; daher wird ein **GitHub-fertiger lokaler Snapshot** geliefert, aber noch kein Remote-Push behauptet. [Schritte](docs/GITHUB_SETUP.md). `.github/workflows/ci.yml` testet offline; keine echten API-Keys in GitHub Actions.

## Arbeitsprinzipien

- Klarer `IST`/`SOLL`-Status, keine fiktive Freigabe, keine erfundenen historischen Preise.
- Datenquellen müssen Rechte, Preisart, Produktidentität und Quota offenlegen.
- Kleine PRs mit Tests, Review und ADR bei Architekturänderungen.
- Weitere APIs erst nach P1-Qualifikation, über gemeinsamen Adaptervertrag (siehe Roadmap).
