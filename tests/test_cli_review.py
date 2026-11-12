import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class TestCliReview(unittest.TestCase):
    def test_revoke_and_audit(self):
        with tempfile.TemporaryDirectory() as dirname:
            db=Path(dirname)/'pilot.sqlite'
            with sqlite3.connect(db) as conn:
                conn.executescript((ROOT/'schema.sql').read_text())
                conn.execute("INSERT INTO products(product_id,category,subcategory,candidate_name) VALUES('BF-0001','E','Mobile','Galaxy')")
                conn.executescript((ROOT/'src'/'scrappa_ingest.py').read_text().split("SCHEMA = '''",1)[1].split("'''",1)[0])
                conn.execute("INSERT INTO geizhals_candidates(product_id,geizhals_id,product_title,identity_status) VALUES('BF-0001',3430460,'Samsung Galaxy A56 (SM-A566BZKA)','VERIFIED')")
                conn.execute("INSERT INTO geizhals_history(product_id,geizhals_id,market,observed_at,price_cents,response_sha256,identity_status) VALUES('BF-0001',3430460,'de','2026-09-01',29900,'abc','VERIFIED')")
                conn.execute("INSERT INTO review_events(record_type,record_id,reviewer,action,rationale) VALUES('GEIZHALS_MAPPING','BF-0001:3430460','test','VERIFIED','https://HIER-DEN-GEPRUEFTEN-PRODUKTLINK-EINSETZEN')")
            def run(*args):
                return subprocess.run([sys.executable,str(ROOT/'scrappa_cli.py'),*args,'--db',str(db)],cwd=ROOT,capture_output=True,text=True)
            before=run('audit','--product-id','BF-0001')
            self.assertEqual(before.returncode,0,before.stderr)
            self.assertIn('placeholder evidence',before.stdout)
            revoke=run('revoke','--product-id','BF-0001','--geizhals-id','3430460','--reason','Invalid placeholder evidence')
            self.assertEqual(revoke.returncode,0,revoke.stderr)
            with sqlite3.connect(db) as conn:
                self.assertEqual(conn.execute('SELECT identity_status FROM geizhals_candidates').fetchone()[0],'UNVERIFIED')
                self.assertEqual(conn.execute('SELECT identity_status FROM geizhals_history').fetchone()[0],'UNVERIFIED')
                self.assertEqual(conn.execute("SELECT count(*) FROM review_events WHERE action='REVOKED'").fetchone()[0],1)
            bad=run('verify','--product-id','BF-0001','--geizhals-id','3430460','--confirmed-mpn','SM-A566BZKA','--identity-evidence','https://HIER-DEN-GEPRUEFTEN-PRODUKTLINK-EINSETZEN')
            self.assertNotEqual(bad.returncode,0)
