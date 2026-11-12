"""Scrappa price data CLI, requiring API key via environment only."""
import argparse
import csv
import json
import sqlite3
from pathlib import Path
from src.scrappa_client import ApiProblem, history, search
from src.scrappa_ingest import setup, store_candidates, store_history
from src.identity_validation import valid_product_evidence, confirmed_mpn_matches

ROOT=Path(__file__).parent
p=argparse.ArgumentParser(description='Scrappa-Geizhals-Import ohne API-Key-Speicherung')
p.add_argument('action',choices=['search','verify','history','status','audit','revoke'])
p.add_argument('--product-id',help='interne Kennung, z.B. BF-0001')
p.add_argument('--query',help='Produktsuche für ein Pilotprodukt')
p.add_argument('--geizhals-id',type=int)
p.add_argument('--days',type=int,default=120)
p.add_argument('--identity-evidence',help='Echter geprüfter Geizhals-Produktlink')
p.add_argument('--confirmed-mpn',help='Mit dem Kandidatentitel verglichene Herstellernummer')
p.add_argument('--reason',help='Begründung eines Widerrufs')
p.add_argument('--market',choices=['de','at','eu','pl','uk'],default='de')
p.add_argument('--db',default=str(ROOT/'blackfriday.sqlite'))
a=p.parse_args()
try:
    with sqlite3.connect(a.db) as db:
        db.row_factory=sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        setup(db)
        if a.action=='search':
            if not a.product_id or not a.query:p.error('search requires --product-id and --query')
            data=search(a.query,market=a.market)
            n=store_candidates(db,a.product_id,data)
            print(f'{n} Kandidaten gespeichert (Identität: UNVERIFIED).')
            for x in data.get('products',[])[:10]:
                print(f"{x.get('gzhid')}: {str(x.get('product',''))[:120]} | GTINs {x.get('gtin',[])}")
        elif a.action=='verify':
            if not a.product_id or not a.geizhals_id or not a.identity_evidence or not a.confirmed_mpn:
                p.error('verify requires --product-id --geizhals-id --confirmed-mpn --identity-evidence')
            item=db.execute('''SELECT product_title FROM geizhals_candidates
                 WHERE product_id=? AND geizhals_id=?''',(a.product_id,a.geizhals_id)).fetchone()
            if not item:
                p.error('Keine Zuordnung gefunden: erst search ausführen')
            if not valid_product_evidence(a.identity_evidence, a.geizhals_id):
                p.error('Keine plausible echte Geizhals-Produkt-URL mit übereinstimmender Artikel-ID')
            if not confirmed_mpn_matches(item['product_title'],a.confirmed_mpn):
                p.error('Die bestätigte MPN passt nicht exakt zum Kandidatentitel')
            db.execute('''UPDATE geizhals_candidates SET identity_status='VERIFIED'
                WHERE product_id=? AND geizhals_id=?''',(a.product_id,a.geizhals_id))
            db.execute('''INSERT INTO review_events(record_type,record_id,reviewer,action,rationale)
                VALUES('GEIZHALS_MAPPING',?,'manual-cli','VERIFIED',?)''',
                (f'{a.product_id}:{a.geizhals_id}',f'MPN={a.confirmed_mpn}; URL={a.identity_evidence}; manual attestation'))
            db.commit()
            print('Zuordnung manuell bestätigt (syntaktische Prüfungen bestanden). Externer Seiteninhalt nicht maschinell verifiziert.')
        elif a.action=='revoke':
            if not a.product_id or not a.geizhals_id or not a.reason:
                p.error('revoke requires --product-id --geizhals-id --reason')
            cur=db.execute('''UPDATE geizhals_candidates SET identity_status='UNVERIFIED'
                 WHERE product_id=? AND geizhals_id=?''',(a.product_id,a.geizhals_id))
            if not cur.rowcount:p.error('Keine Zuordnung zum Widerrufen gefunden')
            db.execute('''UPDATE geizhals_history SET identity_status='UNVERIFIED'
                 WHERE product_id=? AND geizhals_id=?''',(a.product_id,a.geizhals_id))
            db.execute('''INSERT INTO review_events(record_type,record_id,reviewer,action,rationale)
                VALUES('GEIZHALS_MAPPING',?,'manual-cli','REVOKED',?)''',
                (f'{a.product_id}:{a.geizhals_id}',a.reason))
            db.commit()
            print('Zuordnung widerrufen. Zugehörige Historie verbleibt UNVERIFIED im Staging.')
        elif a.action=='audit':
            if not a.product_id:p.error('audit requires --product-id')
            candidates=db.execute('''SELECT geizhals_id, product_title, identity_status FROM geizhals_candidates
                   WHERE product_id=? ORDER BY geizhals_id''',(a.product_id,)).fetchall()
            for item in candidates:
                gid=item['geizhals_id']
                print(f'Geizhals {gid}: {item["product_title"]} | Mapping: {item["identity_status"]}')
                events=db.execute('''SELECT action,rationale,event_time FROM review_events
                   WHERE record_type='GEIZHALS_MAPPING' AND record_id=? ORDER BY event_id''',
                    (f'{a.product_id}:{gid}',)).fetchall()
                for event in events:
                    rationale=event['rationale'] or ''
                    known_bad=any(x in rationale.lower() for x in ('hier-den-geprueften', 'einsetzen', 'placeholder'))
                    print(f'  {event["event_time"]}: {event["action"]}' + (' [PLAUSIBILITY WARNING: placeholder evidence]' if known_bad else ''))
                count=db.execute('''SELECT count(*) FROM geizhals_history WHERE product_id=? AND geizhals_id=?''',
                    (a.product_id,gid)).fetchone()[0]
                print(f'  Historienpunkte: {count} (separate Prüfung erforderlich)')
        elif a.action=='history':
            if not a.product_id or not a.geizhals_id:p.error('history requires --product-id and --geizhals-id')
            # Hard gate: no history requests for a product before its manually confirmed mapping.
            match=db.execute('''SELECT identity_status FROM geizhals_candidates
                 WHERE product_id=? AND geizhals_id=?''',(a.product_id,a.geizhals_id)).fetchone()
            if not match or match['identity_status']!='VERIFIED':
                p.error('Geizhals-Zuordnung zunächst verifizieren (siehe docs/SCRAPPA_INTEGRATION.md)')
            data=history(a.geizhals_id,a.days,a.market)
            n=store_history(db,a.product_id,a.geizhals_id,data,a.market)
            print(f'{n} neue Historienpunkte importiert (nicht für Deal-Score freigegeben).')
        else:
            if a.product_id:
                print('Kandidaten:',db.execute('SELECT count(*) FROM geizhals_candidates WHERE product_id=?',(a.product_id,)).fetchone()[0])
                print('Historienpunkte:',db.execute('SELECT count(*) FROM geizhals_history WHERE product_id=?',(a.product_id,)).fetchone()[0])
                print('Verifizierte Zuordnungen:',db.execute("SELECT count(*) FROM geizhals_candidates WHERE product_id=? AND identity_status='VERIFIED'",(a.product_id,)).fetchone()[0])
            else:
                print('Kandidaten:',db.execute('SELECT count(*) FROM geizhals_candidates').fetchone()[0])
                print('Historienpunkte:',db.execute('SELECT count(*) FROM geizhals_history').fetchone()[0])
                print('Verifizierte Zuordnungen:',db.execute("SELECT count(*) FROM geizhals_candidates WHERE identity_status='VERIFIED'").fetchone()[0])
except ApiProblem as exc:
    p.exit(2,f'API-Fehler: {exc}\n')
