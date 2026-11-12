# ADR-0002: Keine Gleichsetzung von Marktbestpreis und Händler-Endpreis

**Status:** Accepted, 2026-11-12

**Kontext:** 120 echte API-Historienpunkte aus Nutzer-Log, Quelltyp `MARKET_BEST_UNVERIFIED_SHIPPING`, Identitätsstatus `UNVERIFIED`.

**Entscheidung:** Scrappa-Geizhals-Historie separat aufbewahren. Keine automatische Überführung in `approved_comparable_prices`; kein Deal-Score ohne vollständige Endpreise und identische Variante. Chart-Interpolation separat markieren, sobald technisch bestimmbar.

**Konsequenzen:** weniger spontane Rankings, aber wissenschaftlich vertretbare Aussagekraft. Historische Verläufe dürfen weiterhin als *ungeprüfte Trends* gezeigt werden.
