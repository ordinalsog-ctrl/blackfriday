"""Scrappa Geizhals connector. Never persists or logs authentication secrets.

Public documented endpoints:
 /api/geizhals/search?query=...&loc=de&pagesize=...
 /api/geizhals/price-history?product_id=...&days=...&loc=de
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

BASE = 'https://scrappa.co'
MARKETS = {'de','at','eu','pl','uk'}

class ApiProblem(RuntimeError):
    pass


def _request(path, params, key=None, opener=None):
    api_key = key or os.environ.get('SCRAPPA_API_KEY', '')
    if not api_key.strip():
        raise ApiProblem('SCRAPPA_API_KEY ist nicht gesetzt.')
    if not path.startswith('/api/geizhals/'):
        raise ApiProblem('Unzulässiger API-Pfad.')
    url = BASE + path + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'x-api-key': api_key, 'Accept':'application/json'}, method='GET')
    try:
        with (opener or urllib.request.urlopen)(req, timeout=20) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        # Never disclose error body: it may contain request details or credentials.
        raise ApiProblem(f'HTTP {exc.code} von Scrappa. Zugang, Credits oder Parameter prüfen.') from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ApiProblem('Netzwerkverbindung zur Scrappa-API nicht möglich.') from None
    except (ValueError, UnicodeDecodeError):
        raise ApiProblem('API lieferte keine gültige JSON-Antwort.') from None
    if not isinstance(payload, dict) or payload.get('success') is False:
        raise ApiProblem('API-Antwort meldet keinen erfolgreichen Abruf.')
    return payload


def search(query, market='de', pagesize=10, key=None, opener=None):
    if market not in MARKETS or not (1 <= pagesize <= 100):
        raise ValueError('Unzulässiger Markt oder pagesize.')
    if not query or len(query) > 200:
        raise ValueError('Suchbegriff fehlt oder ist zu lang.')
    return _request('/api/geizhals/search', {'query':query,'loc':market,'pagesize':pagesize},key,opener)


def history(product_id, days=120, market='de', key=None, opener=None):
    if not str(product_id).isdigit() or int(product_id) <= 0 or days < 1 or days > 3650 or market not in MARKETS:
        raise ValueError('Ungültige Produkt-ID, Zeitraum oder Markt.')
    return _request('/api/geizhals/price-history', {'product_id':int(product_id),'days':days,'loc':market},key,opener)
