# Sicherheit / Datenrechte

- `SCRAPPA_API_KEY` ausschließlich als lokale Umgebungsvariable; keine Commits, Screenshots oder CI-Secrets ohne kontrollierte Freigabe.
- Bereits in Chat/Kontext geteilter Schlüssel sollte bei Bedarf über den Anbieter **rotiert** werden, besonders vor einem öffentlichen Repository.
- Keine mit echten Schlüsseln signierten API-Antworten in `tests/fixtures` committen. Antworten nur als sanitierte Mock-Fixtures.
- SQLite-Datei, Logdateien und Rohantworten sind `.gitignore`-geschützt. **Gitignore schützt nicht rückwirkend bereits getrackte Dateien:** `git ls-files` prüfen.
- Der Standard-Client sendet den Key in Headern, nicht in der URL; Ausnahmen niemals mit `print(request.headers)` debuggen.
- Dokumentiere Lizenz/Nutzungsbedingungen pro Provider vor automatisierter Speicherung oder öffentlicher Preisveröffentlichung.
- Produktidentität erfordert überprüfbare Artikelnummer und expliziten menschlichen Review; keine künstliche Evidenz.
- Ein kompromittierter, irrtümlich freigegebener Link muss widerrufbar und auditierbar sein. Alte Historien bleiben quarantänisiert.
