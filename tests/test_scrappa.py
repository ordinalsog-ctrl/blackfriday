import io
import json
import sqlite3
import unittest
from src.scrappa_client import search, history, ApiProblem
from src.scrappa_ingest import setup, store_candidates, store_history
class FakeResponse:
 def __init__(self,content):self.content=content
 def read(self,*a):return json.dumps(self.content).encode()
 def __enter__(self):return self
 def __exit__(self,*a):return False
class TestScrappa(unittest.TestCase):
 def test_headers_and_no_embedded_key(self):
  def open_req(req,timeout):
   self.assertEqual(req.get_header('X-api-key'),'dummy-test-only')
   self.assertNotIn('dummy-test-only',req.full_url)
   return FakeResponse({'success':True,'products':[{'gzhid':55,'product':'Test'}]})
  self.assertEqual(search('Test',key='dummy-test-only',opener=open_req)['products'][0]['gzhid'],55)
 def test_history_market(self):
  with self.assertRaises(ValueError):history(123,days=5000,key='fake')
 def test_store_no_review_bypass(self):
  db=sqlite3.connect(':memory:')
  db.executescript('CREATE TABLE products (product_id TEXT PRIMARY KEY); CREATE TABLE approved_comparable_prices (id INT);')
  db.execute("INSERT INTO products VALUES('BF-0001')")
  setup(db)
  store_candidates(db,'BF-0001',{'products':[{'gzhid':77,'product':'Test','gtin':['123']}]})
  n=store_history(db,'BF-0001',77,{'product_id':77,'loc':'de','history':[{'timestamp':1780000000,'price':99.99}]})
  self.assertEqual(n,1)
  self.assertEqual(db.execute('SELECT count(*) FROM approved_comparable_prices').fetchone()[0],0)
  self.assertEqual(store_history(db,'BF-0001',77,{'product_id':77,'loc':'de','history':[{'timestamp':1780000000,'price':99.99}]}),0)
  db.close()
if __name__=='__main__':unittest.main()
