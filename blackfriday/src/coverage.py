"""Evidence coverage report. Avoids conflating single points with price history."""
import csv
from pathlib import Path


def rows(conn, pilot_file):
    with open(pilot_file,encoding='utf-8-sig',newline='') as f:
        pilot=list(csv.DictReader(f))
    result=[]
    for r in pilot:
        pid=r['catalog_id']
        p=conn.execute('SELECT status,gtin,mpn,exact_model FROM products WHERE product_id=?',(pid,)).fetchone()
        raw=conn.execute('''SELECT COUNT(*),COUNT(DISTINCT substr(observed_at,1,10)),MIN(observed_at),MAX(observed_at),
           SUM(CASE WHEN review_status='APPROVED' AND evidence_verified=1 AND identity_verified=1 AND shipping_known=1 AND availability='IN_STOCK' THEN 1 ELSE 0 END)
           FROM price_observations WHERE product_id=?''',(pid,)).fetchone()
        approved=conn.execute('''SELECT COUNT(DISTINCT substr(observed_at,1,10)),COUNT(DISTINCT merchant_id)
           FROM approved_comparable_prices WHERE product_id=?''',(pid,)).fetchone()
        result.append(dict(product_id=pid,product_name=r['product_name_from_pilot'],product_status=p[0] if p else 'MISSING',
            gtin_present=int(bool(p and p[1])),exact_model_present=int(bool(p and p[3])),
            reference_identity_status=r['identity_status'],raw_price_points=raw[0],raw_unique_days=raw[1],
            earliest_point=raw[2] or '',latest_point=raw[3] or '',approved_price_points=raw[4] or 0,
            approved_unique_days=approved[0],approved_merchants=approved[1],
            assessment_status='PENDING_HISTORY' if (approved[0] or 0)<21 or (raw[4] or 0)<15 else 'READY_FOR_EVALUATION'))
    return result


def export(conn, pilot_file, destination):
    data=rows(conn,pilot_file)
    with open(destination,'w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(data[0].keys()));writer.writeheader();writer.writerows(data)
    return data
