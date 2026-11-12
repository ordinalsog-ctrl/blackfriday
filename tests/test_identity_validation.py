import unittest
from src.identity_validation import valid_product_evidence, confirmed_mpn_matches

class TestIdentityValidation(unittest.TestCase):
    def test_bad_domains_or_placeholders(self):
        for u in ('https://HIER-DEN-GEPRUEFTEN-PRODUKTLINK-EINSETZEN',
                  'https://evil-geizhals.de/foo-a3430460.html',
                  'https://geizhals.de/',
                  'http://geizhals.de/samsung-a3430460.html',
                  'https://geizhals.de/samsung-a3432673.html',
                  'https://geizhals.de/ERSETZEN-a3430460.html'):
            self.assertFalse(valid_product_evidence(u,3430460),u)
    def test_plausible_real_url_format(self):
        self.assertTrue(valid_product_evidence('https://geizhals.de/samsung-a3430460.html',3430460))
    def test_mpn_exact(self):
        title='Samsung Galaxy A56 5G 128GB Awesome Graphite (SM-A566BZKA)'
        self.assertTrue(confirmed_mpn_matches(title,'SM-A566BZKA'))
        self.assertFalse(confirmed_mpn_matches(title,'SM-A566BZKAEE'))
        self.assertFalse(confirmed_mpn_matches(title,'A566'))
