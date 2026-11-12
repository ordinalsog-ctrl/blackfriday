# Ist-Stand / Baseline 2026-11-12

**Bedeutung der Angaben:** `CODE` = aus dem v0.7-Quellstand ablesbar; `TEST` = lokal hier ausgeführter Test; `USER-LOG` = vom Betreiber des Mac im Chat übermittelter Live-Log, nicht durch CI oder diese Entwicklungsumgebung repliziert; `OPEN` = unbewiesen / nicht umgesetzt.

| Sachverhalt | Stand | Evidenz | Konsequenz |
|---|---|---|---|
| Kandidatenkatalog: 500 Einträge | vorhanden, redaktionell | CODE / CSV | keine Verkaufsrangliste |
| SQLite + Streamlit + Python | vorhanden | CODE | lokale MVP-Architektur |
| Scrappa Geizhals Suche | 2 Treffer für Samsung A56 | USER-LOG | authentifizierte Suche funktionierte auf Nutzerrechner |
| Geizhals-Kandidaten 3430460 Standard, 3432673 Enterprise | API-Rückgabe | USER-LOG | Standard gewählt; GTIN/MPN unabhängig verifizieren |
| 120 Marktbestpreis-Historienpunkte für BF-0001 | importiert | USER-LOG | 2026-07-15 bis 2026-11-11, 120 einzigartige Kalendertage |
| 120-Tage-Median 298,99 €, Min. 267,00 €, Max. 321,90 € | deskriptiv | USER-LOG | **kein freigegebener Normalpreis** |
| 90-Tage-Median | nicht gesondert berechnet | OPEN | nicht mit 120-Tage-Median verwechseln |
| `source_kind` | `MARKET_BEST_UNVERIFIED_SHIPPING` | USER-LOG | keine Endpreis-Freigabe |
| Historien-Identitätsstatus | `UNVERIFIED` | USER-LOG | keine Deal-Freigabe |
| Manuelle Zuordnung als VERIFIED markiert | ja, mit Platzhalter-URL | USER-LOG / CODE | **falsch-positiv; muss widerrufen werden** |
| 13 Unit-Tests in v0.7 | bestanden | USER-LOG | Tests sind überwiegend offline; kein End-to-End-Nachweis |
| Scrappa-Lizenz / Re-Publishing | offen | OPEN | nicht ohne Rechtsprüfung öffentlich veröffentlichen |
| Andere APIs | nur geplante Adapter | OPEN | nicht als integriert bezeichnen |
| CI | neu in dieser Baseline | CODE | auf GitHub erst nach Push ausführbar |

## Unmittelbar notwendige Korrektur auf dem Mac

Im existierenden **lokalen** Datenbestand wurde `BF-0001` / `3430460` mit einem Platzhalter-Link freigegeben. Mit der neuen CLI:

```bash
python scrappa_cli.py revoke --product-id BF-0001 --geizhals-id 3430460 --reason "Alte Platzhalter-URL war kein Beleg"
python scrappa_cli.py audit --product-id BF-0001
```

Dadurch werden Mapping und gespeicherte Historie wieder ausdrücklich `UNVERIFIED` (die 120 Punkte bleiben erhalten). **Erst danach** den echten Link und Herstellerkennungen belegen und neu manuell bestätigen. Ein Link allein ist keine technische Identitätsgarantie.

**Wichtig:** Der GitHub-Snapshot enthält keine lokale SQLite-Datenbank. Der Nutzer importiert/geprüfte Live-Daten bleiben ausschließlich auf seinem Rechner. Weiterführende Quelle: `docs/ARCHITECTURE.md`.
