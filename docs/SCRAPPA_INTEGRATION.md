# Scrappa Geizhals – Betreiberhandbuch (Baseline v0.8)

## Faktenlage

Der lokale Mac hat laut übermittelten Ausgaben erfolgreich Geizhals-Suche und einen 120-Tage-Historienimport ausgeführt. 120 Punkte für `BF-0001` / `3430460`, vom 15.07. bis 11.11.2026, jedoch weiterhin `UNVERIFIED`; Quelle `MARKET_BEST_UNVERIFIED_SHIPPING`. Die Datenbank des Macs wurde **nicht** in GitHub übernommen.

Die v0.7-CLI ließ eine Platzhalter-URL zur manuellen Verifizierung zu. Das wurde in v0.8 korrigiert: eine passende Geizhals-Hostname-/Artikel-ID-Kombination und exakt zur Suchantwort passende MPN sind erforderlich. **Dies ist nur eine Plausibilitäts- und menschliche Attestierungsprüfung, keine unabhängige Prüfung des Seiteninhalts.**

## Sicherer Betrieb

1. Bestehende lokale Datenbank sichern (`cp blackfriday.sqlite blackfriday_backup.sqlite`, Backup nicht committen).
2. Projektdateien upgraden, **lokale SQLite-Datei behalten**.
3. Mapping prüfen: `python scrappa_cli.py audit --product-id BF-0001`.
4. Alte ungültige Freigabe widerrufen:

```bash
python scrappa_cli.py revoke --product-id BF-0001 --geizhals-id 3430460 --reason 'Platzhalter-Nachweis der v0.7-CLI'
```

5. Offizielle Geizhals-Artikelkarte manuell öffnen und Produkt-/Herstellernummer/Farbe/Speicher abgleichen; erst danach echten Produktlink angeben. Beispiel für **syntaktische Form, nicht verifizierte reale URL**:

```bash
python scrappa_cli.py verify --product-id BF-0001 --geizhals-id 3430460 --confirmed-mpn SM-A566BZKA --identity-evidence 'DEINE_TATSAECHLICH_GEPRUEFTE_GEIZHALS_URL'
```

6. Unter dem bereits gesetzten API-Key `SCRAPPA_API_KEY` Import ausführen und Status prüfen. Passwort niemals in Tickets oder Logs kopieren.

```bash
python scrappa_cli.py history --product-id BF-0001 --geizhals-id 3430460 --days 120 --market de
python scrappa_cli.py status --product-id BF-0001
```

**Vor Deal-Freigabe:** Versand, Preisart, Zeitreihenherkunft, Marktländer, Rechte. Es gibt keinen automatischen Übergang von `geizhals_history` in die freigegebene View. Quelle des API-Designs: https://scrappa.co/docs/geizhals-api/geizhals_price_history (externer Drittanbieter).
