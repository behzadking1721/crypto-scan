from __future__ import annotations

import unittest
from datetime import datetime, timezone
from decimal import Decimal

from connectors.types import Completeness, RawRecord
from normalizers.errors import (
    InvalidNumericValueError,
    InvalidTimestampError,
    MissingFieldError,
    UnknownAssetError,
    UnsupportedDataTypeError,
)
from normalizers.mapping import NormalizerMapping
from normalizers.normalizer import NormalizerEngine
from normalizers.types import MarketDataType


class TestNormalizerEngine(unittest.TestCase):
    def setUp(self):
        self.mappings = [
            NormalizerMapping(
                source="mock",
                provider_symbol="BTC",
                canonical_asset_id="btc",
                canonical_symbol="BTC",
                data_type=MarketDataType.TRADE,
                field_map={"price": "price", "quantity": "qty"},
            ),
            NormalizerMapping(
                source="mock",
                provider_symbol="BTC",
                canonical_asset_id="btc",
                canonical_symbol="BTC",
                data_type=MarketDataType.OHLCV,
                field_map={"open": "o", "high": "h", "low": "l", "close": "c", "volume": "v", "interval": "iv"},
            ),
        ]
        self.engine = NormalizerEngine(self.mappings)

    def test_price_valid(self):
        raw = RawRecord(source="mock", symbol="BTC", type="trade", ts_event=datetime(2026,1,1,tzinfo=timezone.utc), payload={"price": "64000.5", "qty": 2}, idempotency_key="k")
        rec = self.engine.normalize(raw)
        self.assertEqual(rec.price, Decimal("64000.5"))
        self.assertEqual(rec.quantity, Decimal(2))

    def test_ohlcv_valid(self):
        raw = RawRecord(source="mock", symbol="BTC", type="ohlcv", ts_event=datetime(2026,1,1,tzinfo=timezone.utc), payload={"o":"1","h":"2","l":"0.5","c":"1.5","v":"10","iv":"1m"}, idempotency_key="k")
        rec = self.engine.normalize(raw)
        self.assertEqual(rec.ohlcv.close, Decimal("1.5"))

    def test_unknown_asset(self):
        raw = RawRecord(source="mock", symbol="ETH", type="trade", ts_event=datetime(2026,1,1,tzinfo=timezone.utc), payload={"price":"1"}, idempotency_key="k")
        with self.assertRaises(UnknownAssetError):
            self.engine.normalize(raw)

    def test_unsupported_type(self):
        raw = RawRecord(source="mock", symbol="BTC", type="foo", ts_event=datetime(2026,1,1,tzinfo=timezone.utc), payload={"price":"1"}, idempotency_key="k")
        with self.assertRaises(UnsupportedDataTypeError):
            self.engine.normalize(raw)

    def test_missing_field(self):
        raw = RawRecord(source="mock", symbol="BTC", type="trade", ts_event=datetime(2026,1,1,tzinfo=timezone.utc), payload={"qty":2}, idempotency_key="k")
        with self.assertRaises(MissingFieldError):
            self.engine.normalize(raw)

    def test_float_rejected(self):
        raw = RawRecord(source="mock", symbol="BTC", type="trade", ts_event=datetime(2026,1,1,tzinfo=timezone.utc), payload={"price": 1.5, "qty":2}, idempotency_key="k")
        with self.assertRaises(InvalidNumericValueError):
            self.engine.normalize(raw)

    def test_nan_rejected(self):
        raw = RawRecord(source="mock", symbol="BTC", type="trade", ts_event=datetime(2026,1,1,tzinfo=timezone.utc), payload={"price": "NaN", "qty":2}, idempotency_key="k")
        with self.assertRaises(InvalidNumericValueError):
            self.engine.normalize(raw)

    def test_naive_timestamp(self):
        # RawRecord itself rejects naive timestamps; engine relies on this invariant.
        with self.assertRaises(ValueError):
            RawRecord(source="mock", symbol="BTC", type="trade", ts_event=datetime(2026,1,1), payload={"price":"1","qty":2}, idempotency_key="k")

    def test_non_utc_conversion(self):
        from datetime import timedelta
        tz = timezone(timedelta(hours=2))
        raw = RawRecord(source="mock", symbol="BTC", type="trade", ts_event=datetime(2026,1,1,tzinfo=tz), payload={"price":"1","qty":2}, idempotency_key="k")
        rec = self.engine.normalize(raw)
        self.assertEqual(rec.ts_event, datetime(2026,1,1,tzinfo=timezone.utc) - timedelta(hours=2) if False else datetime(2025,12,31,22,0,tzinfo=timezone.utc))

    def test_immutability(self):
        raw = RawRecord(source="mock", symbol="BTC", type="trade", ts_event=datetime(2026,1,1,tzinfo=timezone.utc), payload={"price":"1","qty":2}, idempotency_key="k")
        before = dict(raw.payload)
        self.engine.normalize(raw)
        self.assertEqual(raw.payload, before)

    def test_provenance(self):
        raw = RawRecord(source="mock", symbol="BTC", type="trade", ts_event=datetime(2026,1,1,tzinfo=timezone.utc), payload={"price":"1","qty":2}, idempotency_key="k", completeness=Completeness.PARTIAL, trace_id="t")
        rec = self.engine.normalize(raw)
        self.assertEqual(rec.source, "mock")
        self.assertEqual(rec.idempotency_key, "k")
        self.assertEqual(rec.completeness, Completeness.PARTIAL)
        self.assertEqual(rec.trace_id, "t")
