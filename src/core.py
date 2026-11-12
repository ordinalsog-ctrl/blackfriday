"""Price analytics with conservative data quality gates. Standard library only."""
from datetime import datetime, timedelta, timezone
from statistics import median


def iso_date(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def evaluate(offer, history, competitors=(), now=None, min_days=21, min_points=15):
    """Return no discount when observed history fails independent coverage checks.

    history must be approved identity-verified observations for the SAME product,
    COUNTRY, currency and compatible condition, with known delivered prices.
    A single merchant is permitted but coverage warnings flag the limitation.
    """
    now = iso_date(now) if isinstance(now, str) else (now or datetime.now(timezone.utc))
    required = ('product_id', 'country_code', 'currency', 'landed_price_cents')
    if any(offer.get(k) is None for k in required):
        raise ValueError('Offer lacks comparison keys or landed price')
    if not offer.get('identity_verified') or not offer.get('evidence_verified') or offer.get('review_status') != 'APPROVED':
        return {'status':'NOT_ASSESSABLE','reason':'Offer identity or evidence not approved'}
    if offer.get('availability') != 'IN_STOCK':
        return {'status':'NOT_ASSESSABLE','reason':'Offer not in stock'}
    start = now - timedelta(days=90)
    valid = []
    for p in history:
        try:
            d = iso_date(p['observed_at'])
        except (ValueError, KeyError, TypeError):
            continue
        if not start <= d < now:
            continue
        if any(p.get(k) != offer[k] for k in ('product_id', 'country_code', 'currency')):
            continue
        if p.get('review_status') != 'APPROVED' or not p.get('identity_verified') or not p.get('evidence_verified'):
            continue
        if p.get('availability') != 'IN_STOCK' or p.get('condition','NEW') != 'NEW':
            continue
        if p.get('landed_price_cents') is None:
            continue
        valid.append(p)
    unique_days = len({iso_date(p['observed_at']).date() for p in valid})
    if len(valid) < min_points or unique_days < min_days:
        return {'status':'NOT_ASSESSABLE','reason':'Insufficient independent historical coverage',
                'observations':len(valid),'unique_days':unique_days}
    # Avoid overweighting periods with many snapshots by using one daily minimum.
    daily = {}
    for p in valid:
        day = iso_date(p['observed_at']).date()
        daily[day] = min(daily.get(day, 10**15), p['landed_price_cents'])
    normal = median(daily.values())
    current = offer['landed_price_cents']
    other = [p['landed_price_cents'] for p in competitors if p.get('product_id')==offer['product_id']
             and p.get('country_code')==offer['country_code'] and p.get('currency')==offer['currency']
             and p.get('review_status')=='APPROVED' and p.get('identity_verified') and p.get('evidence_verified')
             and p.get('availability')=='IN_STOCK' and p.get('landed_price_cents') is not None]
    return {'status':'ASSESSABLE','normal_price_cents':round(normal),
            'historical_min_cents':min(daily.values()),'deal_price_cents':current,
            'discount_pct':round((normal-current)/normal*100,2) if normal else None,
            'competitor_min_cents':min(other) if other else None,
            'observations':len(valid),'unique_days':unique_days,
            'merchant_count':len({p.get('merchant_id') for p in valid if p.get('merchant_id') is not None}),
            'confidence':'MEDIUM' if unique_days >= 30 else 'LIMITED',
            'note':'Historical market median is not the statutory 30-day seller reference price.'}
