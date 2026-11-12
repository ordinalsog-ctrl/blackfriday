PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS products (
 product_id TEXT PRIMARY KEY, category TEXT NOT NULL, subcategory TEXT NOT NULL,
 candidate_name TEXT NOT NULL, brand_hint TEXT, gtin TEXT, mpn TEXT,
 exact_model TEXT, variant_attributes TEXT, quantity_value REAL, quantity_unit TEXT,
 status TEXT NOT NULL DEFAULT 'CANDIDATE_UNVERIFIED'
 CHECK(status IN ('CANDIDATE_UNVERIFIED','IDENTIFIED','VALIDATED','REJECTED')),
 origin_method TEXT NOT NULL DEFAULT 'EDITORIAL_CANDIDATE',
 selection_reason TEXT, popularity_evidence TEXT, source_url TEXT,
 CHECK(gtin IS NULL OR length(gtin) IN (8,12,13,14))
);
CREATE TABLE IF NOT EXISTS sources (
 source_id INTEGER PRIMARY KEY, name TEXT NOT NULL, source_type TEXT NOT NULL,
 url TEXT, access_method TEXT NOT NULL,
 legal_basis_note TEXT, automated_access_approved INTEGER NOT NULL DEFAULT 0,
 UNIQUE(name,source_type)
);
CREATE TABLE IF NOT EXISTS merchants (
 merchant_id INTEGER PRIMARY KEY, name TEXT NOT NULL, country_code TEXT NOT NULL,
 UNIQUE(name,country_code)
);
CREATE TABLE IF NOT EXISTS listings (
 listing_id INTEGER PRIMARY KEY, product_id TEXT NOT NULL REFERENCES products(product_id),
 merchant_id INTEGER NOT NULL REFERENCES merchants(merchant_id), listing_url TEXT NOT NULL,
 listing_sku TEXT, identity_method TEXT CHECK(identity_method IN ('GTIN','MPN','MANUAL')),
 identity_verified INTEGER NOT NULL DEFAULT 0 CHECK(identity_verified IN (0,1)),
 UNIQUE(merchant_id,listing_url)
);
CREATE TABLE IF NOT EXISTS import_batches (
 batch_id INTEGER PRIMARY KEY, file_sha256 TEXT NOT NULL UNIQUE, filename TEXT NOT NULL,
 source_id INTEGER REFERENCES sources(source_id), imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 rows_received INTEGER NOT NULL DEFAULT 0, rows_accepted INTEGER NOT NULL DEFAULT 0,
 rows_rejected INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS price_observations (
 observation_id INTEGER PRIMARY KEY, product_id TEXT NOT NULL REFERENCES products(product_id),
 listing_id INTEGER REFERENCES listings(listing_id), merchant_id INTEGER REFERENCES merchants(merchant_id),
 source_id INTEGER NOT NULL REFERENCES sources(source_id), batch_id INTEGER REFERENCES import_batches(batch_id),
 source_url TEXT NOT NULL, observed_at TEXT NOT NULL, collected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 country_code TEXT NOT NULL, currency TEXT NOT NULL DEFAULT 'EUR',
 item_price_cents INTEGER NOT NULL CHECK(item_price_cents>=0),
 shipping_cents INTEGER CHECK(shipping_cents>=0), shipping_known INTEGER NOT NULL DEFAULT 0,
 availability TEXT NOT NULL CHECK(availability IN ('IN_STOCK','OUT_OF_STOCK','UNKNOWN')),
 condition TEXT NOT NULL DEFAULT 'NEW',
 price_kind TEXT NOT NULL CHECK(price_kind IN ('OFFER','HISTORICAL_POINT','CLAIMED_PRIOR')),
 historical_series_id TEXT, identity_verified INTEGER NOT NULL DEFAULT 0,
 evidence_verified INTEGER NOT NULL DEFAULT 0,
 review_status TEXT NOT NULL DEFAULT 'PENDING' CHECK(review_status IN ('PENDING','APPROVED','REJECTED')),
 review_note TEXT, raw_record TEXT,
 CHECK(shipping_known=0 OR shipping_cents IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS idx_price_product_date ON price_observations(product_id,observed_at);
CREATE INDEX IF NOT EXISTS idx_price_country ON price_observations(country_code,currency);
CREATE TABLE IF NOT EXISTS demand_signals (
 signal_id INTEGER PRIMARY KEY, product_id TEXT NOT NULL REFERENCES products(product_id),
 date TEXT NOT NULL, country_code TEXT NOT NULL, signal_type TEXT NOT NULL,
 value REAL, source_id INTEGER REFERENCES sources(source_id), source_url TEXT,
 evidence_verified INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS review_events (
 event_id INTEGER PRIMARY KEY, record_type TEXT NOT NULL, record_id TEXT NOT NULL,
 event_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, reviewer TEXT NOT NULL,
 action TEXT NOT NULL, rationale TEXT
);
CREATE VIEW IF NOT EXISTS approved_comparable_prices AS
 SELECT o.*, (o.item_price_cents + o.shipping_cents) AS landed_price_cents
 FROM price_observations o
 WHERE o.review_status='APPROVED' AND o.evidence_verified=1 AND o.identity_verified=1
 AND o.shipping_known=1 AND o.availability='IN_STOCK' AND o.condition='NEW'
 AND o.currency='EUR' AND o.price_kind IN ('OFFER','HISTORICAL_POINT');
