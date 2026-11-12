## Zweck und begrenzter Scope
- Was ändert sich und warum?
- Welche Datenquellen / Länder / Produktarten sind betroffen?

## Evidenz und Datenrechte
- [ ] Echte Quellenbelege oder explizit als Mock gekennzeichnet
- [ ] Zugang / Lizenz / Nutzungs- und Veröffentlichungsbedingungen dokumentiert
- [ ] Keine Schlüssel, Rohdaten mit sensiblen Feldern oder persönliche Daten committed

## Qualität
- [ ] `python -m unittest discover -s tests -v` erfolgreich
- [ ] Mapping aus GTIN/MPN/Variante geprüft
- [ ] Shipping, Land, Währung und Preisart berücksichtigt
- [ ] Historische Zeitpunkte sind keine interpolierten Kurvenpunkte (oder klar markiert)
- [ ] Nicht freigegebene Daten können keinen Deal-Score erzeugen

## Dokumentationsänderungen
- [ ] STATUS.md aktualisiert, falls Reifegrad geändert
- [ ] ADR ergänzt, wenn Architekturentscheidungen geändert
- [ ] Adapter-Vertrag aktualisiert, falls API-Schema verändert
