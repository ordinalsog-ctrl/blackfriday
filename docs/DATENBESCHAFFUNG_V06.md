# Datenbeschaffung v0.6 – Stand 12.11.2026

## Nachweisart
- Produktreferenz: Eine URL kann die Produktidentität unterstützen, ist aber keine GTIN-Prüfung.
- Historischer Seitenstand: Einzelner öffentlich indexierter Preis-Snapshot mit Zeitstempel des Seiteninhalts.
- Historische Zeitreihe: Mehrere unabhängige Beobachtungstage; im Pilot noch **nicht** verfügbar.

## Reproduzierbarkeit
`data/historische_quellenpunkte_v06_staging.csv` enthält zwei September-Snapshots (Samsung A56 und Sony WH-1000XM5). Sie wurden aus jeweils datierten idealo-Angebotsseiten übernommen und blieben **PENDING**. Der ursprüngliche Pilot enthält weitere vier gestagte Einzelpunkte. Für nachträgliche Prüfbarkeit sind Seiten-URL, beobachteter Zeitstempel, Artikelpreis und Versandkosten getrennt dokumentiert. Eine heute aufrufbare Produktseite kann inzwischen neue Angebote zeigen; ihr alter Stand ist nur über die indexierte historische Ansicht belegt.

## Keine erfundenen Historien
Die vorhandenen archivierten Webseiten sind **keine** 90-Tage-Reihen. Ein 90-Tage-Median bleibt für alle 20 Produkte unberechnet. Angebote aus verschiedenen Quellen oder Händlern werden nicht als tägliche Marktdaten zusammengezählt.

## Datenbeschaffung, Priorität
1. GTIN und Variantenmodell der 20 Produkte anhand Hersteller- und Handelshändlerangaben bestätigen.
2. Historische Datenexporte bei Preisquellen ausdrücklich anfragen oder rechtmäßig bereitgestellte Downloads importieren. Keepa hat eine kostenpflichtige API; kein kostenloser API-Zugang wird behauptet.
3. Für aktuelle Händlerpreise offizielle erlaubte CSV-Feeds oder manuell erfasste Quellen mit Original-Zeitpunkt speichern. Ohne bestätigte Schnittstelle keine automatisierte Abfrage in Produktion.
4. Je Produkt Tage/Abdeckung messen; nur freigegebene und vergleichbare Endpreise für quantitative Auswertung verwenden.
5. Bis genügend Historie vorliegt, nur klare Momentpreisvergleiche getrennt ausweisen.

## Qualitätssperren
Kein automatisches Freigeben; kein Import ohne Quell-URL; unbekannte Versandkosten bleiben unbekannt; keine angeblichen 90-Tage-Mediane; kein Score ohne Datendichte. Manuell dokumentierte Quellen ersetzen kein vollständiges Händler- oder Preishistorienarchiv.
