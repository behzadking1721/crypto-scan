"""Normalizer core types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any

from connectors.types import Completeness

__all__ = ["MarketDataType", "NormalizedRecord", "OHLCV"]


class MarketDataType(str, Enum):
    TRADE = "trade"
    QUOTE = "quote"
    OHLCV = "ohlcv"
    ORDER_BOOK = "order_book"


def _require_utc(dt: datetime, name: str) -> datetime:
    if not isinstance(dt, datetime):
        raise TypeError(f"{name} must be a datetime")
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"{name} must be UTC-aware")
    return dt.astimezone(timezone.utc)


def _require_decimal(value: Any, name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, Decimal):
        raise TypeError(f"{name} must be a Decimal")
    return value


@dataclass(frozen=True)
class OHLCV:
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    interval: str

    def __post_init__(self) -> None:
        for name in ("open", "high", "low", "close", "volume"):
            _require_decimal(getattr(self, name), name)
        if not isinstance(self.interval, str) or not self.interval.strip():
            raise ValueError("interval must be a non-empty string")


@dataclass(frozen=True)
class NormalizedRecord:
    source: str
    canonical_asset_id: str
    canonical_symbol: str
    data_type: MarketDataType
    ts_event: datetime
    idempotency_key: str
    completeness: Completeness = Completeness.UNKNOWN
    trace_id: str | None = None
    price: Decimal | None = None
    quantity: Decimal | None = None
    side: str | None = None
    bid: Decimal | None = None
    ask: Decimal | None = None
    ohlcv: OHLCV | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be a non-empty string")
        if not isinstance(self.canonical_asset_id, str) or not self.canonical_asset_id.strip():
            raise ValueError("canonical_asset_id must be a non-empty string")
        if not isinstance(self.canonical_symbol, str) or not self.canonical_symbol.strip():
            raise ValueError("canonical_symbol must be a non-empty string")
        if not isinstance(self.data_type, MarketDataType):
            raise TypeError("data_type must be a MarketDataType")
        if not isinstance(self.idempotency_key, str) or not self.idempotency_key.strip():
            raise ValueError("idempotency_key must be a non-empty string")
        if not isinstance(self.completeness, Completeness):
            raise TypeError("completeness must be a Completeness")
        if self.trace_id is not None and not isinstance(self.trace_id, str):
            raise TypeError("trace_id must be str or None")
        if self.price is not None:
            _require_decimal(self.price, "price")
        if self.quantity is not None:
            _require_decimal(self.quantity, "quantity")
        if self.bid is not None:
            _require_decimal(self.bid, "bid")
        if self.ask is not None:
            _require_decimal(self.ask, "ask")
        if self.side is not None and not isinstance(self.side, str):
            raise TypeError("side must be str or None")
        if self.ohlcv is not None and not isinstance(self.ohlcv, OHLCV):
            raise TypeError("ohlcv must be OHLCV or None")
        if not isinstance(self.extra, dict):
            raise TypeError("extra must be a dict")
        object.__setattr__(self, "ts_event", _require_utc(self.ts_event, "ts_event"))
