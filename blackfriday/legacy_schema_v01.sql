PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS products (
 product_id TEXT PRIMARY KEY, category TEXT NOT NULL, subcategory TEXT NOT NULL,
 candidate_name TEXT NOT NULL, brand_hint TEXT, gtin TEXT, manufacturer_part_number TEXT,
 exact_model TEXT, quantity_value REAL, quantity_unit TEXT, variant_attributes TEXT,
 popularity_evidence TEXT, product_source_url TEXT,
 validation_status TEXT NOT NULL DEFAULT 'CANDIDATE_UNVERIFIED'
  CHECK(validation_status IN ('CANDIDATE_UNVERIFIED','IDENTIFIED','VALIDATED','REJECTED')),
 validation_notes TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(category, subcategory, candidate_name)
);
CREATE TABLE IF NOT EXISTS merchants (
 merchant_id INTEGER PRIMARY KEY, merchant_name TEXT NOT NULL,
 country_code TEXT NOT NULL, website TEXT, UNIQUE(merchant_name, country_code)
);
CREATE TABLE IF NOT EXISTS merchant_listings (
 listing_id INTEGER PRIMARY KEY, merchant_id INTEGER NOT NULL REFERENCES merchants(merchant_id),
 product_id TEXT NOT NULL REFERENCES products(product_id), listing_url TEXT NOT NULL,
 merchant_sku TEXT, match_method TEXT NOT NULL CHECK(match_method IN ('GTIN','MPN','MANUAL')),
 match_verified INTEGER NOT NULL DEFAULT 0 CHECK(match_verified IN (0,1)),
 UNIQUE(merchant_id,listing_url)
);
CREATE TABLE IF NOT EXISTS collection_runs (
 run_id INTEGER PRIMARY KEY, source_name TEXT NOT NULL, started_at TEXT NOT NULL,
 finished_at TEXT, status TEXT NOT NULL, error_message TEXT, records_seen INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS price_snapshots (
 snapshot_id INTEGER PRIMARY KEY, listing_id INTEGER NOT NULL REFERENCES merchant_listings(listing_id),
 run_id INTEGER REFERENCES collection_runs(run_id), observed_at TEXT NOT NULL,
 currency TEXT NOT NULL DEFAULT 'EUR', product_price_cents INTEGER NOT NULL CHECK(product_price_cents >= 0),
 shipping_cents INTEGER CHECK(shipping_cents >= 0),
 total_price_cents INTEGER GENERATED ALWAYS AS (product_price_cents + COALESCE(shipping_cents,0)) VIRTUAL,
 shipping_known INTEGER NOT NULL DEFAULT 0 CHECK(shipping_known IN (0,1)),
 availability TEXT NOT NULL CHECK(availability IN ('IN_STOCK','OUT_OF_STOCK','UNKNOWN')),
 delivery_country TEXT NOT NULL, seller_type TEXT NOT NULL DEFAULT 'RETAILER',
 coupon_requirements TEXT, membership_required INTEGER NOT NULL DEFAULT 0,
 original_claim_cents INTEGER, claimed_reference_type TEXT, claimed_reference_cents INTEGER,
 raw_source_reference TEXT, UNIQUE(listing_id,observed_at)
);
CREATE TABLE IF NOT EXISTS demand_signals (
 signal_id INTEGER PRIMARY KEY, product_id TEXT NOT NULL REFERENCES products(product_id),
 observed_at TEXT NOT NULL, country_code TEXT NOT NULL, metric TEXT NOT NULL,
 metric_value REAL, metric_unit TEXT, source_name TEXT NOT NULL, source_url TEXT,
 interpretation_note TEXT
);
CREATE TABLE IF NOT EXISTS deal_evaluations (
 evaluation_id INTEGER PRIMARY KEY, product_id TEXT NOT NULL REFERENCES products(product_id),
 evaluated_at TEXT NOT NULL, country_code TEXT NOT NULL,
 offer_snapshot_id INTEGER NOT NULL REFERENCES price_snapshots(snapshot_id),
 market_median_90d_cents INTEGER, market_min_90d_cents INTEGER,
 merchant_min_preceding_30d_cents INTEGER, current_competitor_min_cents INTEGER,
 actual_discount_pct REAL, advertised_discount_pct REAL, score REAL,
 history_days INTEGER NOT NULL DEFAULT 0, confidence TEXT NOT NULL,
 notes TEXT, UNIQUE(product_id, offer_snapshot_id, evaluated_at)
);
CREATE INDEX IF NOT EXISTS ix_snapshots_listing_date ON price_snapshots(listing_id, observed_at);
CREATE INDEX IF NOT EXISTS ix_listing_product ON merchant_listings(product_id);
CREATE INDEX IF NOT EXISTS ix_demand_product_date ON demand_signals(product_id, observed_at);
CREATE INDEX IF NOT EXISTS ix_evaluation_product_date ON deal_evaluations(product_id, evaluated_at);
CREATE VIEW IF NOT EXISTS latest_prices AS
 SELECT p.*, l.product_id, l.merchant_id, l.match_verified
 FROM price_snapshots p JOIN merchant_listings l ON l.listing_id=p.listing_id
 WHERE p.snapshot_id = (SELECT p2.snapshot_id FROM price_snapshots p2 WHERE p2.listing_id=p.listing_id ORDER BY p2.observed_at DESC,p2.snapshot_id DESC LIMIT 1);
