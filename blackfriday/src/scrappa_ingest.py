"""Keep price comparison history distinct from seller quotes.

Market-best history MAY omit shipping: never insert it into approved_comparable_prices.
"""
import datetime as dt
import hashlib
import json
import sqlite3
from pathlib import Path

SCHEMA = '''
CREATE TABLE IF NOT EXISTS geizhals_candidates (
 candidate_id INTEGER PRIMARY KEY, product_id TEXT REFERENCES products(product_id),
 geizhals_id INTEGER NOT NULL, product_title TEXT NOT NULL, gtins_json TEXT NOT NULL DEFAULT '[]',
 fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 identity_status TEXT NOT NULL DEFAULT 'UNVERIFIED',
 UNIQUE(product_id, geizhals_id)
);
CREATE TABLE IF NOT EXISTS geizhals_history (
 history_id INTEGER PRIMARY KEY,
 product_id TEXT NOT NULL REFERENCES products(product_id),
 geizhals_id INTEGER NOT NULL,
 market TEXT NOT NULL,
 observed_at TEXT NOT NULL,
 price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
 source_kind TEXT NOT NULL DEFAULT 'MARKET_BEST_UNVERIFIED_SHIPPING',
 imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 response_sha256 TEXT NOT NULL,
 identity_status TEXT NOT NULL DEFAULT 'UNVERIFIED',
 UNIQUE(product_id, geizhals_id, market, observed_at, price_cents)
);
'''

def setup(db):
    db.executescript(SCHEMA)

def store_candidates(db, product_id, payload):
    if not db.execute('SELECT 1 FROM products WHERE product_id=?',(product_id,)).fetchone():
        raise ValueError('Unbekannte Produkt-ID')
    count=0
    for item in payload.get('products',[]):
        gid=item.get('gzhid')
        if not str(gid).isdigit() or not item.get('product'):
            continue
        db.execute('''INSERT OR IGNORE INTO geizhals_candidates
          (product_id,geizhals_id,product_title,gtins_json) VALUES(?,?,?,?)''',
          (product_id,int(gid),str(item['product']),json.dumps(item.get('gtin') or [])))
        count+=1
    db.commit()
    return count

def _parse_point(p):
    raw_ts=p.get('timestamp_ms')
    if raw_ts is None:
        raw_ts=p.get('timestamp')
        if raw_ts is None: return None
        seconds=float(raw_ts)
    else:
        seconds=float(raw_ts)/1000
    if seconds <= 0 or seconds > 4102444800: return None
    price=p.get('price')
    if isinstance(price,bool) or price is None: return None
    from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
    try:
        value=Decimal(str(price))
        if not value.is_finite() or value < 0: return None
        cents=int((value*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
    except (InvalidOperation, ValueError, OverflowError):
        return None
    date=dt.datetime.fromtimestamp(seconds,dt.timezone.utc).isoformat(timespec='seconds')
    return date,cents

def store_history(db, product_id, geizhals_id, payload, market='de'):
    if not db.execute('SELECT 1 FROM products WHERE product_id=?',(product_id,)).fetchone():
        raise ValueError('Unbekannte Produkt-ID')
    if int(payload.get('product_id',-1)) != int(geizhals_id):
        raise ValueError('Die Antwort gehört zu einer anderen Geizhals-ID')
    if payload.get('loc',market) != market: raise ValueError('Der Markt weicht ab')
    points=payload.get('history',[])
    if not isinstance(points,list): raise ValueError('Keine Zeitreihe')
    digest=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    count=0
    for point in points:
        if not isinstance(point,dict):continue
        parsed=_parse_point(point)
        if not parsed:continue
        observed, cents=parsed
        cur=db.execute('''INSERT OR IGNORE INTO geizhals_history
          (product_id,geizhals_id,market,observed_at,price_cents,response_sha256)
          VALUES(?,?,?,?,?,?)''', (product_id,int(geizhals_id),market,observed,cents,digest))
        count+=cur.rowcount
    db.commit()
    return count

def report(db):
    return db.execute('''SELECT p.product_id, p.candidate_name,
      count(h.history_id) AS history_points, count(DISTINCT substr(h.observed_at,1,10)) AS observed_days,
      min(h.observed_at) AS first_point, max(h.observed_at) AS last_point
      FROM products p LEFT JOIN geizhals_history h ON h.product_id=p.product_id
      WHERE p.product_id IN (SELECT DISTINCT catalog_id FROM pilot20_ids)
      GROUP BY p.product_id ORDER BY p.product_id''').fetchall()
