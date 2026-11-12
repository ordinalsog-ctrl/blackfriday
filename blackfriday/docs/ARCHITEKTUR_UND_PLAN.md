# Black Friday Intelligence v0.3 – Architektur und Ausführungsplan

Stand: 12.11.2026 | Zielmarkt: DE/EU | Budget: bevorzugt kostenlos

## Verbindliche Produktregeln

1. Die 500 Kandidaten stammen aus redaktioneller Vorselektion und sind **keine nachgewiesenen Top-Seller**.
2. Ein Produkt gilt erst nach eindeutiger Variantenprüfung als IDENTIFIED; VALIDATED braucht nachvollziehbare Identitäts- und Produktnachweise.
3. Eine Preisbeobachtung braucht Originalquelle, Beobachtungszeit, Händler-/Lieferland, Zustand, Versandkosten und Währung.
4. CSV-Import ist standardmäßig PENDING; Review erfolgt getrennt. Nur ausdrücklich freigegebene Beobachtungen fließen in Kennzahlen ein.
5. Der 90-Tage-Marktmedian ist eine *eigene Analysekennzahl*. Gesetzliche Händler-30-Tage-Referenzen werden separat erfasst.
6. EU-Angebote nicht allein aufgrund eines EUR-Preises miteinander vergleichen; Zielland, Steuern, Versand und Verfügbarkeit müssen stimmen.
7. Historische Einzelpunkte niemals als lückenlose Preiszeitreihe ausgeben.

## Komponenten

- `schema.sql`: Produkt-, Quellen-, Händler-, Listing-, Batch-, Preis-, Nachfrage- und Audit-Tabellen.
- `src/importer.py`: idempotenter CSV-Batchimport (SHA-256), Vorprüfung, Staging zur manuellen Freigabe.
- `src/core.py`: konservative Preislogik; tägliche Aggregation verhindert Verzerrung durch mehrfaches Abfragen eines Tages.
- `app.py`: Dashboard für Produktstamm, Beobachtungen und Quellen; noch keine fingierten Deal-Scores.
- `tests/`: Kernregeln für Preisberechnung und Qualitätsgates.

## Aktuelle Datenlage

- 500 redaktionelle Kandidaten vorhanden, davon 0 systematisch GTIN-validiert.
- Pilot-20-Quellenregister vorhanden; keine automatisch geprüfte historische Zeitreihe.
- `data/price_import_template.csv` ist leer; **keine Live-Schnittstelle ist angebunden**.
- Keepa bietet historische Daten per kostenpflichtiger, tokenbasierter API: https://keepa.com/api-docs/
- idealo/Geizhals-Preishistorien ggf. öffentlich einsehbar, aber automatischer Export und Rechte sind getrennt zu prüfen.
- Unter kostenlosem Ansatz zunächst manueller, dokumentierter Nachweisimport oder ausdrücklich erlaubte Händlerfeeds.

## Zeitplan bis zum 27.11.2026

| Datum | Phase | Output | Abnahmebedingung |
|---|---|---|---|
| 12.–13.11. | P0 Datenmodell & Audit | Schema, importer, Tests, Katalogstatus | 500 Kandidaten, 0 erfundene Identitätsdaten, Tests grün |
| 13.–15.11. | P1 Artikelidentität | 20 Pilotartikel verifizieren | Produktvariante + Quelle, eindeutige ID je Artikel |
| 15.–18.11. | P2 Historien-Backfill | 20 Preisserien oder explizite Datenlücken | Historien mit Quellen, mindestens 21 unterschiedliche Tage für Bewertung |
| 18.–20.11. | P3 Händlerimport | Aktuelle Preisbelege, Import-Review | Deduplizierung, Versand/Verfügbarkeit kontrolliert |
| 20.–23.11. | P4 Deal-Engine | Vergleich & Qualitätslabel | Keine Bewertung bei lückenhafter Historie |
| 23.–26.11. | P5 Ausbau | 50–100 valide Artikel sofern Daten verfügbar | Stichproben und Regressionstests |
| 27.11. | P6 Black Friday | Dashboard-Export mit Quellen | Jeder ausgewiesene Deal ist rückverfolgbar |

**Stop-/Go-Gate am 18.11.:** Wenn keine legale, hinreichend dichte Preisgeschichte beschafft werden kann, wird nur ein transparentes Momentpreis-Ranking und 'historisch nicht bewertbar' gezeigt. Keine fingierten Rabatte.

## Nächste Arbeitspakete

- A1: 20 Quellen aus Pilot-CSV einzeln prüfen (Modell, Variante, Beobachtungsdatum, Preis inkl. Versand).
- A2: Historischen Importvertrag definieren: Datenformat, Nutzungserlaubnis, Erhebungsmethode, maximale Abfragerate.
- A3: Review-Workflow für Produkte und Beobachtungen bauen, inklusive Nutzer- und Freigabeprotokoll.
- A4: Händlervergleich mit Lieferung nach DE zuerst; FR/AT/NL später je Zielland getrennt.
- A5: Anzeigen von Marktmedian, Marktminimum, Wettbewerberpreis und Händler-30-Tage-Tief nur bei hinreichender Datenlage.

## Betriebliche Risiken

- Rechte an Preis-/Historien-APIs; kein eigenmächtiges Scraping entgegen Nutzungsbedingungen.
- Geringe Datenabdeckung bis 19.11.; teilweise bereits laufende Black-Friday-Aktionen.
- Hersteller-/Varianten-Mismatch, Bundles, Verkäuferqualität, Coupons, Prime-/Clubpreise.
- Historischer Preis einer Amazon-ASIN ≠ europaweiter Marktmedian.
