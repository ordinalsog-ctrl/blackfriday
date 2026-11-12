# Datenversorgung und Prüfgates – 12.11.2026

## Aktueller Stand

20 Pilotkandidaten, keine freigegebene belastbare 90-Tage-Historie. 4 historische Einzelbeobachtungen aus dem bisherigen Projekt sind im Staging; die übrigen früheren Recherche-Treffer sind nicht als geprüfte Preiszeitreihen übernommen. Keine Deal- oder Rabattbehauptungen ableiten.

## Datenquellen: Zugangs- und Lizenzrealität

1. **Keepa**: Offizielle API bietet vollständige Amazon-Preisgeschichten gegen abonnementbasierten Zugang. Dokumentation: https://keepa.com/api-docs/ und https://keepa.com/api-docs/plans-tokens.html. Kostenfrei ist der maschinelle Zugriff nicht gesichert.
2. **idealo**: Öffentliche Preisverläufe können bei der manuellen Einzelfallprüfung helfen. Ein kostenloser, ausdrücklich erlaubter automatisierter Massenexport historischer Reihen wurde nicht nachgewiesen.
3. **Geizhals**: Produktseiten und Preisentwicklung sind Recherchequellen; keine unbestätigte Erlaubnis zum automatischen Scraping unterstellen.
4. **Händler**: Eigenes Tracking ab 12.11. starten, nur mit rechtmäßig zugänglichen Feeds, erlaubten APIs, Exporten oder dokumentierter manueller Sichtung. Keine rückwirkenden Beobachtungen erfinden.
5. **Andere öffentliche Preisreihen**: Nur auf Produktebene übernehmen, wenn Identität, Beobachtungsdatum, historische Originalquelle, Preis inkl. Versand und erlaubte Weiterverwendung nachweisbar sind. Drittseiten, die Geizhals/idealo weiterverwenden, sind nicht automatisch lizenzierbar.

## Freigabekette

`products.status = IDENTIFIED` nach dokumentierter Prüfung einer exakten Variante (GTIN optional, MPN verpflichtend); anschließend manuell dokumentierter Preisbeleg mit expliziter Identitäts- und Quellprüfung, verfügbarer Ware und bekanntem Versand. Beim Freigeben erzeugt die Anwendung einen Audit-Eintrag; abgelehnte Belege bleiben zu Prüfzwecken erhalten. Der Review-CLI akzeptiert keine automatischen Freigaben beim Import.

Bei Ländern mit anderer Währung **keinen künstlichen EUR-Preis angeben**. Wechselkurs, Mehrwertsteuer, grenzüberschreitende Lieferbarkeit und Endpreislogik müssen später gesondert implementiert werden. Der Pilot beschränkt den auswertbaren Preisvergleich auf EUR.

## Ausführbare Schritte

```bash
python main.py init
python main.py coverage
python main.py stage --file data/price_import_template.csv
python main.py identify --product-id BF-0001 --model 'EXAKTE VARIANTE' --mpn 'HERSTELLERNUMMER' --source-url 'https://...' --reviewer 'Name' --rationale 'Pruefung anhand eines konkreten Herstellerdokuments'
python main.py review --observation-id 1 --decision REJECTED --reviewer 'Name' --rationale 'Nicht sicher einer genauen Produktvariante zuordenbar'
python -m unittest discover -s tests -v
streamlit run app.py
```

Freigabe eines tatsächlichen Belegs ist nur möglich, wenn alle Vorbedingungen erfüllt sind; zusätzlich `--identity-checked --evidence-checked` verwenden. **Die Beispiele sind Bedienhilfe, keine faktische Produktbestätigung.**

## Arbeitsprioritäten

- **Sofort**: 20 Pilotartikel mit eindeutiger MPN/GTIN auf Original-Herstellerseiten abgleichen; Quellenbelege mit Datum sichern.
- **Vor 19.11.**: Historische Daten-Zugriffsrechte klären und eigene erlaubte Preis-Snapshots starten. Kurzfristig nur Angebote mit einem belegbaren historischen Vergleich auszeichnen; Verfügbarkeit der Reihen bleibt ungewiss.
- **19.–26.11.**: Tägliche Händlerpreise mit Datum, Lieferbarkeit, Versandkosten, Quellenlink und Artikelvariante erfassen; Qualitätsprüfungen durchführen.
- **27.11.**: Nur bei ausreichender Historie historischen Rabatt berechnen; ansonsten Status `NOT_ASSESSABLE` und ggf. reinen aktuellen Marktvergleich zeigen.

## Statistik-Konvention

Der experimentelle Bewertungsalgorithmus `src/core.py` setzt 15 zugelassene Beobachtungen an 21 unterschiedlichen Tagen in 90 Tagen voraus. Dies ist ein Mindestgate, kein empirischer Vollständigkeitsnachweis. Mit Einzelbelegen kann der normale 90-Tage-Preis nicht berechnet werden. Preisverläufe verschiedener Märkte/Länder, Varianten, Zustände oder Währungen dürfen nicht vermischt werden. Händlerreferenzpreis nach §11 PAngV ist separat zu behandeln.
