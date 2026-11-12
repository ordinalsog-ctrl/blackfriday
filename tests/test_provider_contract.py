import unittest
from src.providers.contract import PricePoint, PriceKind

class TestProviderContract(unittest.TestCase):
    def test_cannot_claim_shipping_without_amount(self):
        with self.assertRaises(ValueError):
            PricePoint('s','p','2026-11-12','DE','EUR',1000,None,True,PriceKind.MARKET_BEST,None,'UNKNOWN',None)

    def test_missing_shipping_is_not_zero(self):
        p=PricePoint('s','p','2026-11-12','DE','EUR',1000,None,False,PriceKind.MARKET_BEST,None,'UNKNOWN',None)
        self.assertIsNone(p.shipping_cents)
