"""Human-in-the-loop price evidence review. No automatic approvals."""
import sqlite3
from datetime import datetime, timezone
from urllib.parse import urlparse


def decide(conn, observation_id: int, decision: str, reviewer: str, rationale: str,
           identity_checked: bool = False, evidence_checked: bool = False):
    if decision not in ('APPROVED', 'REJECTED'):
        raise ValueError('decision must be APPROVED or REJECTED')
    if not reviewer.strip() or len(rationale.strip()) < 15:
        raise ValueError('reviewer and a substantive rationale (>=15 characters) required')
    conn.execute('PRAGMA foreign_keys=ON')
    current = conn.execute('''SELECT o.*, p.status as product_status FROM price_observations o
        JOIN products p ON p.product_id=o.product_id WHERE o.observation_id=?''', (observation_id,)).fetchone()
    if current is None:
        raise ValueError('Unknown observation')
    data = dict(current)
    if data['review_status'] != 'PENDING':
        raise ValueError('Only PENDING observations can be decided; prior decisions are immutable')
    if decision == 'APPROVED':
        reasons=[]
        if not identity_checked or data['product_status'] not in ('IDENTIFIED','VALIDATED'):
            reasons.append('verified identity and IDENTIFIED/VALIDATED product required')
        if not evidence_checked or urlparse(data['source_url']).scheme != 'https':
            reasons.append('reviewed HTTPS source evidence required')
        if data['shipping_known'] != 1 or data['shipping_cents'] is None:
            reasons.append('shipping and final price required')
        if data['availability'] != 'IN_STOCK' or data['condition'] != 'NEW':
            reasons.append('in-stock, new condition required')
        if data['currency'] != 'EUR' or data['country_code'] not in ('DE','AT','FR','IT','ES','NL','BE','LU','PL','CZ','DK','SE','FI','IE','PT','GR','SI','SK','EE','LV','LT','HR','HU','RO','BG','CY','MT'):
            reasons.append('supported EU country and EUR currency required')
        if data['price_kind'] not in ('OFFER','HISTORICAL_POINT'):
            reasons.append('claimed prior prices cannot be approved as market price')
        if reasons:
            raise ValueError('; '.join(reasons))
    conn.execute('''UPDATE price_observations SET review_status=?,identity_verified=?,evidence_verified=?,review_note=?
       WHERE observation_id=?''', (decision, int(decision=='APPROVED'), int(decision=='APPROVED'), rationale, observation_id))
    conn.execute('''INSERT INTO review_events(record_type,record_id,reviewer,action,rationale)
       VALUES ('price_observation',?,?,?,?)''',(str(observation_id),reviewer,decision,rationale))
    conn.commit()
    return {'observation_id':observation_id,'status':decision}


def identify_product(conn, product_id: str, exact_model: str, mpn: str, reviewer: str, source_url: str, rationale: str, gtin=None):
    if not all((exact_model.strip(), mpn.strip(), reviewer.strip(), rationale.strip())):
        raise ValueError('exact_model, MPN, reviewer and rationale mandatory')
    if len(rationale.strip()) < 15 or urlparse(source_url).scheme!='https':
        raise ValueError('evidence HTTPS URL and meaningful rationale required')
    if gtin and (not gtin.isdigit() or len(gtin) not in (8,12,13,14)):
        raise ValueError('GTIN must have valid length and numeric characters')
    if not conn.execute('SELECT 1 FROM products WHERE product_id=?',(product_id,)).fetchone():
        raise ValueError('unknown product')
    conn.execute('''UPDATE products SET exact_model=?,mpn=?,source_url=?,gtin=?,status='IDENTIFIED'
      WHERE product_id=?''',(exact_model,mpn,source_url,gtin,product_id))
    conn.execute('''INSERT INTO review_events(record_type,record_id,reviewer,action,rationale)
      VALUES ('product',?,?,'IDENTIFIED',?)''',(product_id,reviewer,rationale+' | '+source_url))
    conn.commit()
    return {'product_id':product_id,'status':'IDENTIFIED'}
