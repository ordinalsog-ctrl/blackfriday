# API Discovery & Cross-Provider Benchmark — 2026-11-12

**Decision:** API-first. The existing Geizhals BF-0001 deep-dive is paused, not accepted. No deal score or publication clearance follows from this benchmark.

## What exists and what does not

- Existing `data/produktstamm_500_kandidaten.csv`: 500 **editorial candidates**, not market shares or bestsellers, often not exact SKU/GTIN.
- Prior pilot: 20 **product candidates**, four per category, for technical workflow testing.
- Existing 120 Geizhals history rows: **120 dates for one Samsung product**, **not 120 products**. Historical market-best values have unverified shipping and are NOT approved for scoring.
- `data/api_benchmark_120_candidates.csv` in this package: **120 distinct, reproducibly selected candidate rows** for discovery and API coverage assessment; **zero provider matches asserted**.

## Methodology and reproducibility

Run from repository root:

```bash
python3 tools/build_benchmark120.py
python3 -m unittest discover -s tests -v
```

The script uses only Python stdlib. It fails if the input does not contain exactly 500 unique IDs. Per category it distributes the quota across the ten existing subcategories (alphabetical order, remainder assigned to first subcategories) and chooses candidates using SHA-256 of `BFI-API-BENCHMARK-2026-11-12-v1|product_id`. Stable output columns and order; no random API calls.

| Editorial category | Discovery sample |
|---|---:|
| Elektronik | 30 |
| Haushalt | 25 |
| Küche | 25 |
| Kosmetik | 20 |
| Gesundheit | 20 |
| **Total** | **120** |

**Limitation:** The sample deliberately reflects the existing editorial candidate catalog and its equal ten-subcategory structure. It is stratified **within that catalog**, not representative of Germany's unit sales, deal frequency or consumer spending. For an unbiased measure of API coverage, a separately drawn market sample is required. No provider is queried until ambiguous candidates are resolved to exact SKUs or recorded as unmatched.

## Provider distinctions (do not merge by brand)

1. **Scrappa Geizhals**: third-party access to Geizhals. Search/GTIN, product/offers, 1–3650-day history are documented. Price semantics, interpolation, seller, shipping and republication rights remain unknown; up to 3650 days is a request limit, not a coverage guarantee.
2. **Keepa**: distinct original data source for Amazon; API subscription and tokens required. Keepa's Amazon offer or Buy Box statistics must not be presented as cross-market merchant minima.
3. **idealo MCP**: idealo's separate MCP guide documents a 30-day price history tool, contingent on accessible tools, credentials and terms. Do not infer a public unrestricted historical-data license from the guide.
4. **Scrappa idealo**: third-party search/offers from idealo; its FAQ explicitly says **no price-history endpoint**. Current shipping may be unknown. Both idealo routes share an underlying data origin and must not be counted as independent confirmations.
5. **Official idealo PWS 2.0 merchant API**: intended for merchants to submit/manage their own offers; NOT a general public competitor-price history API. Deliberately excluded from the actual benchmark provider candidates.

## Shared test protocol and metrics

1. **Readiness gate**: record subscription/account access, intended endpoints, expected credits, rate limits, rights to store, reuse and publicly display data. No secrets in repos or logs. Abort paid calls until budget approved.
2. **Discovery pass**: each of the 120 catalog rows against available sources, log `MATCH_EXACT_GTIN`, `MATCH_EXACT_MPN_VARIANT`, `AMBIGUOUS`, `NOT_FOUND`, `ERROR`, or `NOT_RUN`. Matching by title alone is not a verified identity. Do not silently substitute Enterprise, bundles, refurbished, pack sizes, colors or storage variants.
3. **History pass**: ONLY confirmed identities. Record origin, source endpoint, timestamp timezone, currency, price type (Amazon/new/used/Buy Box, market-best, seller-specific), VAT, shipping status/amount, availability, response digest and acquisition time. Preserve all raw distinctions.
4. **Coverage**: distinct verified products per provider; exact-match share; covered unique dates in past 30/90/180 days, not count of chart points; observed vs interpolated vs unknown; last-observation freshness, no synthetic fill pretending daily observations.
5. **Reliability/cost**: attempts, HTTP category, rate-limit/429, timeouts, retries with bounded backoff, spend/credits per match and per usable product history. Redact credentials.
6. **Cross-source comparison**: compare only exact same SKU, market, condition and comparable delivered price. Preserve source families; do not double-count Scrappa idealo and idealo MCP as independent.
7. **Decision**: `DISCOVERY_READY` / `HISTORY_READY` / `PUBLICATION_READY` separate. A provider may support discovery and current price without history, and may support history without publishing rights. All actual acceptance thresholds and remaining uncertainties documented.

## Preliminary experiment budget (planning, not purchased)

- Start with 5 products per category (25 total), not all 120, to validate response shape and avoid unnecessary credits.
- If matching, legal, technical and billing gates pass, expand to remaining 95. Use exactly the same catalog IDs across providers.
- Block public deal scores until shipping, product identity, rights and history provenance gates are met.
- On 27 Nov 2026, a 90-day comparison can only use legitimately obtained retrospective histories; the tool cannot build 90 days of new observations in the remaining 15 days.

## Documentation sources (checked 2026-11-12)

- Scrappa Geizhals overview: https://scrappa.co/apis/geizhals-api
- Scrappa Geizhals history: https://scrappa.co/docs/geizhals-api/geizhals_price_history
- Keepa official API: https://keepa.com/api-docs/
- idealo MCP history: https://github.com/idealo/mcp-server-guide/blob/main/docs/tools.md
- Scrappa idealo FAQ: https://scrappa.co/apis/idealo-api
- idealo merchant interface: https://partner.idealo.com/partner-idealo-com/de/idealo-academy/faqs/faq-technische-anbindung

## Integration into existing repo

Copy these patch folders into the repository **root** (not another nested `blackfriday` folder). This patch creates only `docs/API_DISCOVERY_AND_BENCHMARK.md`, `data/provider_matrix.csv`, `data/api_benchmark_120_candidates.csv`, `tools/build_benchmark120.py`, and `tests/test_benchmark120.py`; existing code is untouched. Use a PR from `feature/geizhals-qualification`, optionally rename branch to `feature/api-discovery-benchmark` later. Update `docs/STATUS.md` when changes are merged; don't mark provider qualifications as done.
