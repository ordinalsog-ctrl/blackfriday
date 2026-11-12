import tempfile, sqlite3, csv, unittest
from pathlib import Path
from src.evidence_pipeline import build_report
class TestEvidencePipeline(unittest.TestCase):
  def test_no_history_does_not_claim_readiness(self):
    with tempfile.TemporaryDirectory() as d:
      db=Path(d)/'d.sqlite'; catalog=Path(d)/'p.csv';out=Path(d)/'o.csv'
      with sqlite3.connect(db) as conn:
        conn.execute('CREATE TABLE price_observations(product_id TEXT,observed_at TEXT,review_status TEXT)')
        conn.execute("INSERT INTO price_observations VALUES('P1','2026-09-01','PENDING')")
      with open(catalog,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['catalog_id','product_name_from_pilot']);w.writeheader();w.writerow({'catalog_id':'P1','product_name_from_pilot':'Sample'})
      x=build_report(db,catalog,out)
      self.assertEqual(x[0]['normal_price_ready'],'NO')
      self.assertEqual(x[0]['missing_observation_days'],20)
if __name__=='__main__': unittest.main()
