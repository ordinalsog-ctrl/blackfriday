# Meilenstein 20: Prüfbericht vom 12.11.2026

## Ergebnis

Die **20 Pilotkandidaten** wurden als feste Stichprobe übernommen. In dieser Prüfrunde wurden **12 zugehörige öffentliche Produkt-/Varianten-Preisvergleichsseiten erneut inhaltlich überprüft**. Die übrigen **8** behalten den Status `NOT_RECHECKED`; das bedeutet **nicht**, dass ihr Produkt falsch oder unauffindbar ist. Auf allen 20 Einträgen bleiben GTIN-Nachweis und belegter Absatz/Bestsellerstatus offen. Bei 2 der 12 geprüften Seiten bestehen konkrete Varianten-/Setrisiken (Roborock Qrevo S und Oral-B iO Series 3).

**Keine der 20 Positionen erfüllt derzeit die Regel für einen verifizierten 90-Tage-Normalpreis.** Ein öffentlicher September-Snapshot ist nur eine historische Einzelbeobachtung; die interaktiven Preisverlaufsgrafiken liefern keine automatisch frei exportierbare Rohdatenreihe. Deshalb sind alle Deals ausdrücklich `NOT_ASSESSABLE`.

## Quellen und Reproduzierbarkeit

- `data/pilot20_verifikationsregister.csv`: alle 20 mit Matchstatus, historischem Einzelpunkt und Quell-URL.
- `build_milestone20.py`: explizites, wiederholbares Erzeugen des Prüfregisters (inkl. konservativer Prüfregeln).
- `data/pilot20_historische_belege_staging.csv`: vier bereits überprüfte Einzelangebote mit **exaktem Zeitstempel im sichtbaren Seitentext**, nur zur manuellen Freigabe eingespielt. Sie sind noch `PENDING`, `identity_verified=0`, `evidence_verified=0`.
- `price_observations` und `import_batches` in SQLite: vollständiger Importvorgang, Ablehnung oder Freigabe nur nach Review.

Prüffundstellen der zwölf Seiten (Quellbelege: öffentlich aufrufbare Preisseiten; beim erneuten Prüfen können sich Live-Preise geändert haben):

- BF-0001: https://www.idealo.de/preisvergleich/OffersOfProduct/206022816_-galaxy-a56-128gb-awesome-graphite-samsung.html
- BF-0011: https://www.idealo.de/preisvergleich/OffersOfProduct/206023474_-ipad-128gb-wifi-silber-2025-apple.html
- BF-0021: https://www.idealo.de/preisvergleich/OffersOfProduct/204771908_-airpods-4-anc-apple.html
- BF-0024: https://www.idealo.de/preisvergleich/OffersOfProduct/201952086_-wh-1000xm5-black-sony.html
- BF-0109: https://www.idealo.de/preisvergleich/OffersOfProduct/204405361_-qrevo-s-roborock.html
- BF-0202: https://www.idealo.de/preisvergleich/OffersOfProduct/200749470_-af300eu-ninja.html
- BF-0203: https://www.idealo.de/preisvergleich/OffersOfProduct/204449576_-hd9252-90-schwarz-philips.html
- BF-0211: https://www.idealo.de/preisvergleich/OffersOfProduct/4811448_-magnifica-s-ecam-22-110-b-delonghi.html
- BF-0221: https://www.idealo.de/preisvergleich/OffersOfProduct/5707400_-essenza-mini-en85-delonghi.html
- BF-0303: https://www.idealo.de/preisvergleich/OffersOfProduct/6375656_-moisturising-cream-177-ml-cerave.html
- BF-0321: https://www.idealo.de/preisvergleich/OffersOfProduct/200727706_-niacinamide-10-zinc-1-30-ml-the-ordinary.html
- BF-0403: https://www.idealo.de/preisvergleich/OffersOfProduct/202896527_-io-series-3-oral-b.html

## Methodische Vorsicht

1. **Publikationszeit ist nicht Beobachtungszeit.** Ein Suchindex aus September kann den Seitentext einer damaligen Momentaufnahme enthalten. Wir übernehmen nur einen einzelnen, belegten Snapshot, keine angebliche vollständige Historie.
2. **Varianten strikt trennen.** Unterschiedliche Farben, Kapazitäten, Bundles, Einzel- oder Mehrfachpackungen werden nicht zusammengeführt.
3. **Versandkosten sind obligatorisch** für eine Bewertung des tatsächlichen Kaufpreises. Der niedrigste Artikelpreis ist nicht unbedingt das günstigste Gesamtangebot.
4. **Beweis für häufig gekauft fehlt.** Nutzerbewertungen, Suchtrend oder Produktmeinungen sind kein Absatznachweis.
5. **EU-Preise länderspezifisch** halten, Lieferbarkeit nach Deutschland und Versandland berücksichtigen.
6. **Quelle und Datennutzungsrecht beachten.** Keine unautorisierte Massenerfassung von Vergleichsportal-Daten.

## Nächste Arbeitspakete (priorisiert)

- P0: **GTIN und exakte Variante** der 20 Artikel über Herstellerdaten/seriöse Datenquellen ergänzen, 2 Bundle-Risiken separat erfassen.
- P0: Historische CSV/API-Rechte klären, mindestens 21 unterschiedliche Tage innerhalb von 90 Tagen mit dokumentiertem Gesamtpreis sammeln oder bereitgestellte Rohdaten importieren.
- P0: Review-Workflow zur **manuellen** Freigabe einzelner Beobachtungen inklusive Evidenz-Screenshot oder revisionssicherem Nachweis ergänzen.
- P1: Händler-Liveangebote täglich erfassen; Rechts- und Nutzungsrechte je Quelle prüfen.
- P1: Erst bei ausreichender Zeitreihenabdeckung den Deal-Score freischalten.

Bei weiterhin fehlenden historischen Rohdaten wird der Meilenstein nicht als abgeschlossen ausgegeben: "20 vollständig verifiziert mit Preisgeschichte" ist ein Ziel, kein vorgetäuschter Ist-Zustand.
