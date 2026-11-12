# Verträge für mehrere Preis-/Produkt-APIs

Jeder neue Provider liefert **eigene Adaptertypen**, aber normalisierte gemeinsame Datenobjekte. Kein Provider schreibt direkt in freigegebene Analytics-Views.

## Provider-Metadaten

`provider_id`, `provider_name`, `category_coverage`, `countries`, `auth_type`, `quota_cost_model`, `terms_url`, `legal_review`, `historical_coverage`, `shipping_semantics`, `redistribution_allowed`, `last_verified_at`.

Status: `RESEARCH` → `SANDBOX` → `IDENTITY_TESTED` → `HISTORY_TESTED` → `COST_SHIPPING_TESTED` → `LEGAL_APPROVED` → `PRODUCTION` (jeder Status widerrufbar).

## NormalizedProductCandidate

- `provider`, `provider_product_id`, `name`, `manufacturer`, `gtins[]`, `mpn`, `variant` (size/color/bundle/quantity), `source_url`, `fetched_at`, `raw_sha256`.

## NormalizedPricePoint

- `provider`, `provider_product_id`, `observed_at` mit Zeitzone, `collected_at`, `country`, `currency`, `item_price_cents`, `shipping_cents?`, `shipping_known`, `tax_included?`, `availability`, `condition`, `price_kind` (`MARKET_BEST`, `MERCHANT_OFFER`, `CLAIMED_PRIOR`), `merchant_id?`, `provenance_url`, `raw_sha256`, `derived_or_interpolated?`, `licence_class`.

Pflichtregeln: fehlende Versandkosten ≠ 0; fehlender Händler ≠ Marktbestpreis eines konkreten Händlers; interpolierte Tageswerte nicht als gemessene Tagespreise ausgeben; bei Mengenartikel Grundpreis über Menge/Einheit berechnen; alle Währungen und EU-Lieferländer explizit.

## Connector-Methoden

```python
search_products(query, country) -> list[ProductCandidate]
get_product(product_ref, country) -> ProductCandidate | None
get_price_history(product_ref, country, start, end) -> list[PricePoint]
get_current_offers(product_ref, country) -> list[PricePoint]
capabilities() -> ProviderCapabilities
```

Ein Provider kann einzelne Funktionen als `not_supported` deklarieren; **keine** leeren Ergebnisse als erfolgreich vorgespielte Antworten. Prüffelder für 401, 403, 404, 429, Retry-After, Netzwerkfehler, Quota, Pagination, Idempotenz, Zeitstempel, Cent-Rundung.

## Testpyramide für neue APIs

1. **Unit/contract**: vollständig offline mit sanitisierter JSON-Fixture, keine Secrets, deutsche und EU-Varianten, negative Fälle.
2. **Sandbox smoke**: 1–3 dokumentierte Beispielartikel, API-Credits budgetieren, echte IDs/GTINs prüfen.
3. **History quality**: min/max Datum, Tageabdeckung, interpolierte Werte, Quelltyp; stichprobenweise gegen originale Portalseite.
4. **Shipping/legal**: mindestens ein tatsächlich lieferbares Endpreisangebot für Deutschland, Nutzungsrecht schriftlich festhalten.
5. **Release gate**: PR, Review, CI grün, Status und ADR aktualisiert; erst dann produktiv schalten.

## Quellen-Portfolio (keine Zusage über nutzbare APIs)

| Kandidat | Fokus | möglicher Mehrwert | Eintrittsbedingung |
|---|---|---|---|
| Scrappa Geizhals | DE/AT Elektronik/Geräte | Historische Marktbestpreise | Identität, Versand, Lizenz, API-Semantik klären |
| Scrappa idealo | DE/EU aktuelle Händlerangebote | Anbieterdiversifikation | Endpoint, AGB, Preisart, Quota verifizieren |
| Keepa | Amazon Historie | Händler-/Marketplace-Sicht | Kosten / API-Zugang / rechtliche Nutzung |
| Open Prices (Open Food Facts) | Lebensmittel/Alltag | Datierte Beobachtungen | Datenabdeckung, ODbL, Länder-/GTIN-Fit |
| Open Beauty Facts | Kosmetik | GTIN, Menge, Produktidentität | Lizenz, Modell/Packungspräzision |
| Offizielle Händler-/Affiliate-Feeds | mehrere Kategorien | aktuelle lieferbare Angebote | Vertrags-/Feedberechtigung, Versand |
| Alternative Preisvergleichsportale | Geizhals-Unabhängigkeit | Cross-Source-Kontrollpreise | erlaubte API/Feed vor Implementierung prüfen |

Mindestens **zwei voneinander unabhängige Quellen** pro priorisiertem Artikel sind Ziel, nicht bereits erreicht. Zwei Drittanbieter-Endpunkte mit identischem zugrunde liegendem Portal sind nicht zwingend unabhängige Quellen.
