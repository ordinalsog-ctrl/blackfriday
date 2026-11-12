"""Command-line interface for auditable catalogue and price evidence."""
import argparse, sqlite3
from pathlib import Path
from src.importer import prepare_database, import_catalog, stage_csv
from src.review import decide, identify_product
from src.coverage import export
ROOT=Path(__file__).parent
p=argparse.ArgumentParser(description='BF Intelligence data pipeline')
p.add_argument('action',choices=['init','stage','coverage','identify','review'])
p.add_argument('--file');p.add_argument('--db',default=str(ROOT/'blackfriday.sqlite'))
p.add_argument('--observation-id',type=int);p.add_argument('--decision',choices=['APPROVED','REJECTED'])
p.add_argument('--reviewer');p.add_argument('--rationale');p.add_argument('--identity-checked',action='store_true');p.add_argument('--evidence-checked',action='store_true')
p.add_argument('--product-id');p.add_argument('--model');p.add_argument('--mpn');p.add_argument('--gtin');p.add_argument('--source-url')
p.add_argument('--output',default=str(ROOT/'data'/'pilot20_abdeckungsbericht.csv'))
a=p.parse_args()
with sqlite3.connect(a.db) as db:
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    prepare_database(db,ROOT)
    if a.action=='init':
        n=import_catalog(db,ROOT/'data'/'produktstamm_500_kandidaten.csv');print(f'Initialized catalog: {n} candidates')
    elif a.action=='stage':
        if not a.file:p.error('stage requires --file')
        print(stage_csv(db,a.file))
    elif a.action=='coverage':
        items=export(db,ROOT/'data'/'pilot20_verifikationsregister.csv',a.output)
        print(f'Exported {len(items)} pilot rows to {a.output}; evaluable: {sum(x["assessment_status"]=="READY_FOR_EVALUATION" for x in items)}')
    elif a.action=='identify':
        if not all([a.product_id,a.model,a.mpn,a.reviewer,a.source_url,a.rationale]):p.error('identify requires --product-id --model --mpn --reviewer --source-url --rationale')
        print(identify_product(db,a.product_id,a.model,a.mpn,a.reviewer,a.source_url,a.rationale,a.gtin))
    elif a.action=='review':
        if not all([a.observation_id,a.decision,a.reviewer,a.rationale]):p.error('review requires --observation-id --decision --reviewer --rationale')
        print(decide(db,a.observation_id,a.decision,a.reviewer,a.rationale,a.identity_checked,a.evidence_checked))
