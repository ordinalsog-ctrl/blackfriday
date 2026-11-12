"""Strict CSV staging; no observation is approved automatically."""
import csv, hashlib, json, sqlite3
from pathlib import Path
from datetime import datetime

REQUIRED = ('product_id','source_name','source_url','observed_at','country_code','currency','item_price_cents','availability','price_kind')

def prepare_database(conn, root):
    conn.executescript(Path(root, 'schema.sql').read_text(encoding='utf-8'))

def import_catalog(conn, csv_file):
    with open(csv_file, encoding='utf-8-sig', newline='') as f:
        rows=list(csv.DictReader(f))
    for r in rows:
        conn.execute('''INSERT OR IGNORE INTO products
        (product_id,category,subcategory,candidate_name,brand_hint,gtin,mpn,exact_model,variant_attributes,
        quantity_value,quantity_unit,status,origin_method,selection_reason,popularity_evidence,source_url)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (r['product_id'],r['category'],r['subcategory'],r['candidate_name'],r.get('brand_hint'),r.get('gtin') or None,
        r.get('manufacturer_part_number') or None,r.get('exact_model') or None,r.get('variant_attributes') or None,
        r.get('quantity_value') or None,r.get('quantity_unit') or None,r.get('validation_status') or 'CANDIDATE_UNVERIFIED',
        'EDITORIAL_CANDIDATE','Initial editorial selection; sales volume not established',r.get('popularity_evidence') or None,
        r.get('product_source_url') or None))
    conn.commit()
    return len(rows)

def stage_csv(conn, file_path):
    data=Path(file_path).read_bytes(); digest=hashlib.sha256(data).hexdigest()
    if conn.execute('SELECT 1 FROM import_batches WHERE file_sha256=?',(digest,)).fetchone():
        return {'status':'ALREADY_IMPORTED','accepted':0,'rejected':0}
    with open(file_path, encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    conn.execute('INSERT INTO import_batches(file_sha256,filename,rows_received) VALUES (?,?,?)',
                 (digest,Path(file_path).name,len(rows)))
    batch_id=conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    accepted=rejected=0
    for row in rows:
        try:
            if any(not row.get(k) for k in REQUIRED): raise ValueError('Missing required column/value')
            datetime.fromisoformat(row['observed_at'].replace('Z','+00:00'))
            cents=int(row['item_price_cents']); assert cents>=0
            if row['availability'] not in ('IN_STOCK','OUT_OF_STOCK','UNKNOWN'): raise ValueError('Bad availability')
            if row['price_kind'] not in ('OFFER','HISTORICAL_POINT','CLAIMED_PRIOR'): raise ValueError('Bad price_kind')
            if not conn.execute('SELECT 1 FROM products WHERE product_id=?',(row['product_id'],)).fetchone():
                raise ValueError('Unknown product')
            source=row['source_name']
            conn.execute('INSERT OR IGNORE INTO sources(name,source_type,access_method) VALUES (?,?,?)',(source,'PRICE','MANUAL_CSV'))
            source_id=conn.execute('SELECT source_id FROM sources WHERE name=? AND source_type=?',(source,'PRICE')).fetchone()[0]
            shipping = int(row['shipping_cents']) if row.get('shipping_cents') not in (None,'') else None
            # An imported record remains PENDING until evidence, identity and landed costs are reviewed.
            conn.execute('''INSERT INTO price_observations(product_id,source_id,batch_id,source_url,observed_at,
            country_code,currency,item_price_cents,shipping_cents,shipping_known,availability,price_kind,raw_record)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (row['product_id'],source_id,batch_id,row['source_url'],row['observed_at'],row['country_code'],row['currency'],
             cents,shipping,int(shipping is not None),row['availability'],row['price_kind'],json.dumps(row,ensure_ascii=False)))
            accepted+=1
        except (ValueError, TypeError, AssertionError, sqlite3.IntegrityError):
            rejected+=1
    conn.execute('UPDATE import_batches SET rows_accepted=?,rows_rejected=? WHERE batch_id=?',
                 (accepted,rejected,batch_id))
    conn.commit()
    return {'status':'STAGED_FOR_REVIEW','accepted':accepted,'rejected':rejected,'batch_id':batch_id}
