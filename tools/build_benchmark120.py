#!/usr/bin/env python3
"""Deterministic provisional API benchmarking sample from the editorial 500 catalog.
Does not verify sellability, popularity, model identity or API availability.
"""
import argparse
import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

SEED = 'BFI-API-BENCHMARK-2026-11-12-v1'
QUOTAS = {'Elektronik': 30, 'Haushalt': 25, 'Küche': 25, 'Kosmetik': 20, 'Gesundheit': 20}
FIELDS = ['benchmark_id','product_id','category','subcategory','candidate_name','brand_hint',
          'gtin','manufacturer_part_number','exact_model','sample_method','sample_seed',
          'identity_status','benchmark_eligibility','provider_match_status','selection_note']


def build(source: Path):
    with source.open(newline='', encoding='utf-8-sig') as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 500 or len({r['product_id'] for r in rows}) != 500:
        raise ValueError('Expected 500 distinct catalog IDs; input changed; revise sampling plan explicitly')
    groups = defaultdict(list)
    for row in rows:
        if row['category'] not in QUOTAS:
            raise ValueError('Unexpected category: ' + row['category'])
        groups[(row['category'], row['subcategory'])].append(row)
    selected = []
    for category, quota in QUOTAS.items():
        subs = sorted(k[1] for k in groups if k[0] == category)
        if not subs:
            raise ValueError('Missing subcategories: ' + category)
        base, extra = divmod(quota, len(subs))
        for idx, sub in enumerate(subs):
            n = base + (idx < extra)
            available = groups[category, sub]
            if len(available) < n:
                raise ValueError(f'Not enough candidates: {category}/{sub}')
            ranked = sorted(available, key=lambda r: (hashlib.sha256((SEED + '|' + r['product_id']).encode()).hexdigest(),r['product_id']))
            for item in ranked[:n]:
                selected.append({
                    'benchmark_id': '', 'product_id': item['product_id'],
                    'category': category, 'subcategory': sub,
                    'candidate_name': item['candidate_name'], 'brand_hint': item['brand_hint'],
                    'gtin': item['gtin'], 'manufacturer_part_number': item['manufacturer_part_number'],
                    'exact_model': item['exact_model'],
                    'sample_method': 'DETERMINISTIC_STRATIFIED_SUBCATEGORY_HASH',
                    'sample_seed': SEED,
                    'identity_status': 'UNVERIFIED' if not (item['gtin'] and item['exact_model']) else 'REVIEW_REQUIRED',
                    'benchmark_eligibility': 'DISCOVERY_ONLY',
                    'provider_match_status': 'NOT_TESTED',
                    'selection_note': 'Editorial candidate; not a bestseller or verified exact SKU; confirm GTIN/MPN, variant and pack size before history comparison',
                })
    selected.sort(key=lambda r: (list(QUOTAS).index(r['category']), r['subcategory'], r['product_id']))
    for index, row in enumerate(selected, 1):
        row['benchmark_id'] = f'BM-{index:03d}'
    if len(selected) != 120 or Counter(r['category'] for r in selected) != Counter(QUOTAS):
        raise AssertionError('Quota mismatch')
    return selected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=Path('data/produktstamm_500_kandidaten.csv'))
    parser.add_argument('--output', type=Path, default=Path('data/api_benchmark_120_candidates.csv'))
    args = parser.parse_args()
    rows = build(args.source)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('w', newline='',encoding='utf-8') as out:
        writer = csv.DictWriter(out, fieldnames=FIELDS, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    print(f'Wrote {len(rows)} discovery-only candidates to {args.output}')

if __name__ == '__main__':
    main()
