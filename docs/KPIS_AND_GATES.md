# Messbare Kennzahlen und Quality Gates

## Quelle / API

| Marker | Definition | Abnahmewert im Pilot |
|---|---|---|
| Search hit rate | Treffer für bekannte exakte MPN/GTIN / getestete Artikel | berichten, kein erfundener Sollwert |
| Identity match precision | manuell korrekte Top-1-Zuordnungen / geprüfte Top-1-Zuordnungen | 100 % bei freigegebenen 20 |
| Source legal readiness | Quellen mit dokumentierter Nutzung-/Publikationsfreigabe / produktive Quellen | 100 % für produktiven Betrieb |
| Data freshness | Abrufzeit minus letzter beobachteter Zeitpunkt | täglich messen |
| Daily coverage | einzigartige echte Beobachtungstage / Tage im betrachteten Fenster | ≥ 21 Tage und ≥ 15 Punkte als heutiger Code-Mindestwert; Ziel >= 75/90 Tage |
| Identity completeness | Anteil mit belastbarer GTIN/MPN + Variante | 100 % freigegebener Produkte |
| Shipping completeness | Anteil aktueller Angebote mit bekannten Versandkosten | 100 % bewerteter Angebote |
| Error rate | technische Fehlversuche / API-Requests | täglich messen, 429 separat |
| Quota cost | Credits pro eindeutig identifiziertem Artikel / importierter Tag | laufend ausweisen |
| Cross-source agreement | Abweichung des lieferbaren Endpreises über unabhängige Quellen für gleiche GTIN | dokumentieren, keine automatische Gleichsetzung |
| Interpolation rate | als interpoliert erkennbare Punkte / historische Punkte | 0 % für behauptete *beobachtete* Tagespreise |

## Prüfung historischer Reihen

- `points` ist **nicht** gleich `unique_days`; gleiche Tage deduplizieren, historische Preise als `MARKET_BEST` separat betrachten.
- `unique_days` ist **nicht** notwendigerweise Anzahl tatsächlich erfasster Tagespreise: bei Diagrammauflösung kann der Dienst Zwischenwerte erzeugen.
- 120-Tage-Median ist nicht 90-Tage-Median; beide getrennt berechnen und mit exaktem Fenster ausgeben.
- Ohne bestätigte Versandsemantik nur **Trendmetrik**, keine rechts-/handelsverbindliche Ersparnis.
- Seller-30-Day-Low erfordert Händlerhistorie, nicht den Marktbestpreis.

## Definition of Done für Geizhals/Scrappa

1. Gleiche Variante (Standard vs Enterprise) identifiziert und Beleg überprüfbar.
2. Historien-Preisart, Zeitstempel und interpolationsbedingte Grenzen dokumentiert.
3. Historie über 90 Tage mit QA-Kennzahlen und Quellverweisen.
4. Versandkosten-/Steuersemantik und DE-Verfügbarkeit gesichert — falls nicht, explizite Sperre für den Deal-Score.
5. Rechteprüfung und Credits geklärt.
6. Negative Tests, Unit-/CLI-/CI-Prüfungen grün.
7. `docs/STATUS.md` aktualisiert und PR reviewt.

**Kein Gate kann durch einen grünen CI-Test ersetzt werden**, wenn das Gate einen externen Lizenznachweis oder Produktbeleg erfordert.
