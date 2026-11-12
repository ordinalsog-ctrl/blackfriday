import unittest, sqlite3, tempfile
from pathlib import Path
from src.importer import prepare_database, import_catalog, stage_csv
from src.review import decide, identify_product
from src.coverage import rows
ROOT=Path(__file__).resolve().parents[1]
class TestReview(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:');self.db.row_factory=sqlite3.Row
        prepare_database(self.db,ROOT);import_catalog(self.db,ROOT/'data'/'produktstamm_500_kandidaten.csv')
        with tempfile.TemporaryDirectory() as d:
            csv_file=Path(d)/'price.csv'
            csv_file.write_text('product_id,source_name,source_url,observed_at,country_code,currency,item_price_cents,shipping_cents,availability,price_kind\nBF-0001,Example,https://example.com/offer,2026-09-12T12:00:00+00:00,DE,EUR,29900,,IN_STOCK,HISTORICAL_POINT\n',encoding='utf-8')
            stage_csv(self.db,csv_file)
    def tearDown(self):self.db.close()
    def test_cannot_approve_unidentified_product(self):
        with self.assertRaisesRegex(ValueError,'identity'):
            decide(self.db,1,'APPROVED','Auditor','Checked 2026 source and product',True,True)
    def test_cannot_approve_missing_shipping(self):
        identify_product(self.db,'BF-0001','A56 128 GB graphite','SM-A566BZKA','Auditor','https://example.com/model','Checked model with manufacturer catalogue')
        with self.assertRaisesRegex(ValueError,'shipping'):
            decide(self.db,1,'APPROVED','Auditor','Checked dated listing source details',True,True)
    def test_reject_is_auditable(self):
        decide(self.db,1,'REJECTED','Auditor','Historical price not sufficiently documented')
        events=self.db.execute('SELECT count(*) FROM review_events').fetchone()[0]
        self.assertEqual(events,1)
        with self.assertRaisesRegex(ValueError,'PENDING'):
            decide(self.db,1,'REJECTED','Auditor','Another decision attempt is invalid')
    def test_coverage_never_assumes_historical_series(self):
        report=rows(self.db,ROOT/'data'/'pilot20_verifikationsregister.csv')
        self.assertEqual(len(report),20)
        self.assertEqual(sum(x['assessment_status']=='READY_FOR_EVALUATION' for x in report),0)
    def test_approval_with_all_gates(self):
        identify_product(self.db,'BF-0001','A56 128GB graphite','SM-A566BZKA','Auditor','https://example.com/model','Verified exact manufacturer number')
        self.db.execute('UPDATE price_observations SET shipping_cents=0,shipping_known=1 WHERE observation_id=1')
        self.assertEqual(decide(self.db,1,'APPROVED','Auditor','Confirmed official archived listing',True,True)['status'],'APPROVED')
if __name__=='__main__':unittest.main()
