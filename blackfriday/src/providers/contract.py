"""Minimal standard-library-only multi-provider contract (not a live integration)."""
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

class PriceKind(str, Enum):
    MARKET_BEST = 'MARKET_BEST'
    MERCHANT_OFFER = 'MERCHANT_OFFER'
    CLAIMED_PRIOR = 'CLAIMED_PRIOR'

@dataclass(frozen=True)
class Capabilities:
    provider_id: str
    countries: tuple[str, ...]
    supports_search: bool
    supports_history: bool
    supports_offers: bool
    license_reviewed: bool = False

@dataclass(frozen=True)
class ProductCandidate:
    provider_id: str
    provider_product_id: str
    title: str
    manufacturer: str | None
    gtins: tuple[str, ...]
    mpn: str | None
    variant: str | None
    source_url: str | None

@dataclass(frozen=True)
class PricePoint:
    provider_id: str
    provider_product_id: str
    observed_at: str
    country: str
    currency: str
    item_price_cents: int
    shipping_cents: int | None
    shipping_known: bool
    kind: PriceKind
    merchant_id: str | None
    availability: str
    source_url: str | None
    interpolated: bool | None = None

    def __post_init__(self):
        if self.shipping_known and self.shipping_cents is None:
            raise ValueError('shipping_known requires explicit shipping_cents')
        if self.item_price_cents < 0 or (self.shipping_cents is not None and self.shipping_cents < 0):
            raise ValueError('Negative price')

class PriceProvider(Protocol):
    def capabilities(self) -> Capabilities: ...
    def search_products(self, query: str, country: str) -> list[ProductCandidate]: ...
    def get_product(self, product_ref: str, country: str) -> ProductCandidate | None: ...
    def get_price_history(self, product_ref: str, country: str, start: str, end: str) -> list[PricePoint]: ...
    def get_current_offers(self, product_ref: str, country: str) -> list[PricePoint]: ...
