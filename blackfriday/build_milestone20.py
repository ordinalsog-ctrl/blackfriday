"""Create a conservative, reproducible evidence review from the existing pilot.

Curated evidence references correspond to individually inspected public result pages on
2026-11-12. Never imply that a comparison-site listing authenticates a GTIN or
establishes a historical price series.
"""
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'data/pilot_20_preisquellen_2026-11-12.csv'
DEST=ROOT/'data/pilot20_verifikationsregister.csv'
# Explicit result-level page and variant checks. Snapshot date is recorded only if visible.
CHECKED={
'BF-0001':('MODEL_VARIANT_PAGE','2026-09-11','Samsung Galaxy A56 128 GB Awesome Graphite','Auf Preisvergleichsseite ist die 128-GB-Graphite-Variante sichtbar; GTIN fehlt.'),
'BF-0011':('MODEL_VARIANT_PAGE','2026-11-03','Apple iPad 2025 128 GB Wi-Fi Silber','Variante auf Seite bestätigt; Händler-Einzelangebot noch nicht erneut geprüft.'),
'BF-0021':('MODEL_VARIANT_PAGE','2026-11-12','Apple AirPods 4 ANC','ANC-Version auf Seite; Snapshot 12.11.03:39; keine historische Zeitreihe.'),
'BF-0024':('MODEL_VARIANT_PAGE','2026-09-11','Sony WH-1000XM5 Black','Schwarze Variante; September-Snapshot mit Versandaufschlag; GTIN fehlt.'),
'BF-0109':('PRODUCT_PAGE_VARIANT_RISK','2026-09-11','Roborock Qrevo S','Angebotsseite zeigt weiß + 2 Wischmops; Setidentität und Vergleichbarkeit offen.'),
'BF-0202':('MODEL_VARIANT_PAGE','2026-09-11','Ninja AF300EU 7,6 l','Modell AF300EU und Füllmenge auf September-Snapshot sichtbar.'),
'BF-0203':('MODEL_VARIANT_PAGE','2026-09-02','Philips HD9252/90 schwarz','Preisseite benennt /90 getrennt von /70 und /91; Original-Datensatz datierte 11.09., Quellensnapshot 02.09.'),
'BF-0211':('MODEL_VARIANT_PAGE','2026-09-11','DeLonghi ECAM22.110.B schwarz','Variante ECAM22.110.B auf Angebotsseite; kein GTIN-Nachweis.'),
'BF-0221':('MODEL_VARIANT_PAGE','2026-09-11','DeLonghi Essenza Mini EN85.B','EN85.B getrennt von EN85.R, EN85.BAE etc.; Set/Variante genau beachten.'),
'BF-0303':('MODEL_VARIANT_PAGE','2026-09-11','CeraVe Moisturising Cream 177 ml','177-ml-Variante auf Preisvergleichsseite; Verkäuferverpackung und Versand beachten.'),
'BF-0321':('MODEL_VARIANT_PAGE','2026-09-11','The Ordinary Niacinamide 10% + Zinc 1% 30 ml','30 ml nachgewiesen; Quellenpreise mit und ohne Versand unterscheiden.'),
'BF-0403':('PRODUCT_PAGE_VARIANT_RISK','2026-09-11','Oral-B iO Series 3 Matte Black','Aggregierte Seite enthält auch Blush Pink und Set mit Reiseetui; Preisvergleichsrisiko.'),
}
# Re-checkable totals, deliberately only a *single offer*, not a 90d median.
LANDED={
'BF-0021':(12899,0,'2026-11-12T03:39:00','Gelistetes Angebot 128,99 € inkl. Versand'),
'BF-0024':(19900,499,'2026-09-11T12:00:00','199,00 € + 4,99 €; Datum aus Quellensnapshot, Uhrzeit nicht verifiziert'),
'BF-0109':(34797,0,'2026-09-11T09:59:00','347,97 € inkl. Versand; Setabweichung beachten'),
'BF-0202':(12998,599,'2026-09-11T12:00:00','129,98 € + 5,99 €; Uhrzeit nur Platzhalter, nicht verwenden'),
'BF-0203':(9990,495,'2026-09-02T20:48:00','99,90 € + 4,95 €, Quellenstand 02.09.'),
'BF-0211':(27400,0,'2026-09-11T12:00:00','Anderer Händler als Artikelpreisminimum: 274,00 € inkl. Versand'),
'BF-0221':(6590,0,'2026-09-11T14:05:00','Günstigster Gesamtpreis 65,90 €, Artikelpreis-Minimum 63,99 € bei anderem Händler'),
'BF-0303':(799,490,'2026-09-11T12:00:00','7,99 € + 4,90 €, nicht billigster Artikelpreis 7,95 €'),
'BF-0321':(520,390,'2026-09-11T12:00:00','5,20 € + 3,90 €, günstigster Gesamtpreis 9,10 €'),
}
with SRC.open(encoding='utf-8-sig',newline='') as f: old=list(csv.DictReader(f))
output=[]
for r in old:
    pid=r['catalog_id']; hit=CHECKED.get(pid)
    page_status,date,variant,note=hit if hit else ('NOT_RECHECKED','','','Quellenverweis aus Pilot vorhanden, aber in dieser Prüfrunde keine eigenständige Bestätigung.')
    r2={
       'catalog_id':pid,'product_name_from_pilot':r['exact_product'],'model_from_pilot':r['manufacturer_model_or_variant'],
       'model_variant_on_source':variant,'identity_status':page_status,'gtin_verified':'NO',
       'price_evidence_status':'SINGLE_POINT_RECHECKED' if (pid in LANDED or pid in CHECKED) and r['observed_min_item_price_eur'] else ('NOT_RECHECKED' if r['observed_min_item_price_eur'] else 'NO_PRICE'),
       'source_snapshot_date_confirmed':date,'pilot_item_price_eur':r['observed_min_item_price_eur'],
       'source_url':r['source_url'],'history_points_90d_confirmed':'1' if hit and r['observed_min_item_price_eur'] else '0',
       '90d_median_eur':'','deal_status':'NOT_ASSESSABLE',
       'popularity_verified':'NO','review_note':note+' Keine vollständige 90-Tage-Preishistorie.'
    }
    output.append(r2)
with DEST.open('w',encoding='utf-8-sig',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(output[0]));wr.writeheader();wr.writerows(output)
# Stage only observations with confirmed SOURCE timestamp (no invented noon!).
rows=[]
for r in old:
    pid=r['catalog_id']
    if pid not in LANDED:continue
    price,ship,stamp,desc=LANDED[pid]
    if '12:00:00' in stamp: continue
    rows.append(dict(product_id=pid,source_name='idealo.de (manuell geprüfter Snapshot)',source_url=r['source_url'],
       observed_at=stamp,country_code='DE',currency='EUR',item_price_cents=str(price),
       shipping_cents=str(ship),availability='IN_STOCK',price_kind='HISTORICAL_POINT',
       evidence_comment=desc))
stage=ROOT/'data/pilot20_historische_belege_staging.csv'
with stage.open('w',encoding='utf-8-sig',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
print(f'audit: {len(output)} records; pages checked: {len(CHECKED)}; stage with exact timestamps: {len(rows)}')
