"""Conservative, offline syntactic evidence checks; not a substitute for page review."""
import re
from urllib.parse import urlparse

HOSTS = {'geizhals.de', 'www.geizhals.de', 'geizhals.at', 'www.geizhals.at',
         'geizhals.eu', 'www.geizhals.eu'}


def valid_product_evidence(url: str, geizhals_id: int) -> bool:
    if not url or not isinstance(geizhals_id, int) or geizhals_id <= 0:
        return False
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or '').lower()
        if parsed.scheme != 'https' or host not in HOSTS:
            return False
        if parsed.username or parsed.password or parsed.port:
            return False
        lowered = (parsed.path + '?' + parsed.query).lower()
        if any(marker in lowered for marker in ('ersetzen', 'placeholder', 'example', 'dummy', 'hier-den', 'einsetzen')):
            return False
        # Geizhals item pages contain e.g. ...-a3430460.html, or ?...=a3430460.
        # Mere placeholder or homepage does NOT count as plausible evidence.
        return bool(re.search(r'(?<!\d)a' + str(geizhals_id) + r'(?!\d)', parsed.path + '?' + parsed.query))
    except (ValueError, TypeError):
        return False


def confirmed_mpn_matches(title: str, mpn: str) -> bool:
    if not mpn or len(mpn) < 5 or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]{4,59}', mpn):
        return False
    # Exact token-like MPN only; blocks accidentally confirming the Enterprise SKU
    return bool(re.search(r'(?<![A-Za-z0-9])' + re.escape(mpn) + r'(?![A-Za-z0-9])', title, re.I))
