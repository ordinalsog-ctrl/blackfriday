import unittest
from datetime import datetime,timedelta,timezone
from src.core import evaluate
NOW=datetime(2026,11,12,tzinfo=timezone.utc)
def row(days, price=15000):
    return dict(product_id='P1',country_code='DE',currency='EUR',landed_price_cents=price,
                observed_at=(NOW-timedelta(days=days)).isoformat(),review_status='APPROVED',
                evidence_verified=1,identity_verified=1,availability='IN_STOCK',condition='NEW',merchant_id=1)
class TestPricing(unittest.TestCase):
    def test_undersampled_not_assessable(self):
        self.assertEqual(evaluate(row(0,10000),[row(5)],now=NOW)['status'],'NOT_ASSESSABLE')
    def test_verified_coverage(self):
        hist=[row(i) for i in range(1,35)]
        r=evaluate(row(0,12000),hist,now=NOW)
        self.assertEqual(r['status'],'ASSESSABLE');self.assertEqual(r['discount_pct'],20)
    def test_mismatch_excluded(self):
        hist=[dict(row(i),country_code='FR') for i in range(1,35)]
        self.assertEqual(evaluate(row(0,12000),hist,now=NOW)['status'],'NOT_ASSESSABLE')
    def test_offer_unverified(self):
        self.assertEqual(evaluate(dict(row(0,12000),evidence_verified=0),[row(i) for i in range(1,35)],now=NOW)['status'],'NOT_ASSESSABLE')
if __name__=='__main__':unittest.main()
