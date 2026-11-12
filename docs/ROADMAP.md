# Umsetzungsplan (priorisiert, keine erfundenen Deadlines)

## P0 – GitHub-Baseline und Identitätsschutz (vor dem nächsten Import)
- [x] Quellstand v0.7 übernommen, README und Status dokumentiert
- [x] `.gitignore`, Offline-CI, API-Kontrakt, ADRs und Prüfcheckliste angelegt
- [x] Neues `audit` + `revoke` gegen falsche Mapping-Freigabe
- [ ] Betreiber widerruft vorhandenen Platzhalter-Review **in seiner lokalen DB**
- [ ] Betreiber dokumentiert echten Geizhals-Artikel-/Herstellernachweis
- [ ] Keine lokalen Zugangsdaten oder Datenbanken nach GitHub pushen

**Abnahme:** `git status` enthält keine Datenbank/Secrets, Unit-Tests grün, `audit` zeigt ungültige Mapping-Freigabe nicht als vertrauenswürdig.

## P1 – Scrappa/Geizhals vollständig qualifizieren
- [x] Live-Suche und Historienabruf auf Nutzerrechner erfolgreich (USER-LOG)
- [ ] Product-ID/GTIN/MPN/Variante nachvollziehbar belegen, abweichende Enterprise-Edition ausschließen
- [ ] Preisfelddefinition und Versand inklusive Mehrwertsteuer / Lieferland beim Anbieter klären
- [ ] Herkunft: echte Daily Snapshots vs. Chart-Interpolation nachweisen
- [ ] Zeitserienqualität 90-Tage-Median und Tageabdeckung automatisiert je Produkt prüfen
- [ ] Nutzungs-/Veröffentlichungsrecht und API-Stabilität dokumentieren
- [ ] Negative Tests: falsche IDs, Link-Platzhalter, Ratelimit, Quota, Zeitstempel, Duplikate

**Abnahme:** Ein Artikel mit freigegebenem Endpreis und vollständiger Auditspur, oder bei ungeklärtem Versand ein sichtbar begrenzter *Marktpreis-Trend* ohne Rabattversprechen. Danach 20er-Pilot, dann 100.

## P2 – Multi-API-Gerüst
- [x] Provider-Interface + Datentypen als gemeinsame Form definiert
- [ ] Adapter-Registry, lokale rohe Response-Ablage, Quota-Verwaltung und Scheduler
- [ ] Getrennte Quellen-Zustände im Dashboard
- [ ] Datensatz- und ID-Deduplizierung über Provider hinweg
- [ ] Tests mit unabhängigen Preisbelegen

**Abnahme:** zwei unabhängige Provider laufen durch denselben Normalizer; keiner umgeht Prüf-Gates.

## P3 – Weitere Datenquellen (in dieser Reihenfolge prüfen)
1. Offene Produktidentitäten: Open Beauty Facts, Open Food Facts (wo Kategorie passend).
2. Aktuelle Händlerangebote: vertraglich erlaubte Affiliate-/Händler-Feeds und idealo-Zugang.
3. Historische Zweitquelle: Keepa oder anderer lizenzierter Anbieter.
4. Cross-Source-Ländervergleich DE/AT/EU mit Mehrwertsteuer, Versand und Verfügbarkeit.

**Abnahme:** unabhängige Produktzuordnung über ≥ 2 Quellen, Endpreise und Preiskurven nicht vermischt.

## P4 – Veröffentlichung / Skalierung
- [ ] 20 verifizierte Produkte, anschließend 100, dann 500 Kandidaten bearbeiten
- [ ] Deal-Score mit Konfidenz, Datenschutz-/Lizenzhinweisen, Quellenlinks
- [ ] optional PostgreSQL/Jobrunner erst bei Lastbedarf

## Arbeitsregel gegen Slop
Jeder PR hat genau einen fachlichen Zweck, einen messbaren Akzeptanztest und eine Dokumentationsänderung. Status nie allein wegen einer grünen Testanzeige auf `PRODUCTION` setzen. Keine generierten Produktnamen als verifizierte Artikel, keine geschätzten Preise als historische Messungen.
