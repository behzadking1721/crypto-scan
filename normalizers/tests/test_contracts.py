from __future__ import annotations

import unittest
from datetime import datetime, timezone
from decimal import Decimal

from connectors.types import Completeness
from normalizers.base import Normalizer
from normalizers.errors import (
    InvalidMappingError,
    InvalidNumericValueError,
    InvalidTimestampError,
    MissingFieldError,
    NormalizationError,
    UnknownAssetError,
    UnsupportedDataTypeError,
)
from normalizers.mapping import NormalizerMapping
from normalizers.types import MarketDataType, NormalizedRecord, OHLCV


class TestContracts(unittest.TestCase):
    def test_market_data_type_values(self):
        self.assertEqual(MarketDataType.TRADE.value, "trade")

    def test_normalized_record_decimal_and_utc(self):
        dt = datetime(2026, 1, 1, tzinfo=timezone.utc)
        rec = NormalizedRecord(
            source="s",
            canonical_asset_id="a",
            canonical_symbol="BTC",
            data_type=MarketDataType.TRADE,
            ts_event=dt,
            idempotency_key="k",
            price=Decimal("1"),
        )
        self.assertEqual(rec.price, Decimal("1"))
        self.assertIsNotNone(rec.ts_event.tzinfo)

    def test_decimal_type_required(self):
        with self.assertRaises(TypeError):
            NormalizedRecord(
                source="s",
                canonical_asset_id="a",
                canonical_symbol="BTC",
                data_type=MarketDataType.TRADE,
                ts_event=datetime(2026, 1, 1, tzinfo=timezone.utc),
                idempotency_key="k",
                price=1,
            )

    def test_utc_required(self):
        with self.assertRaises(ValueError):
            NormalizedRecord(
                source="s",
                canonical_asset_id="a",
                canonical_symbol="BTC",
                data_type=MarketDataType.TRADE,
                ts_event=datetime(2026, 1, 1),
                idempotency_key="k",
            )

    def test_ohlcv_decimal(self):
        ohlcv = OHLCV(open=Decimal("1"), high=Decimal("2"), low=Decimal("0.5"), close=Decimal("1.5"), volume=Decimal("10"), interval="1m")
        self.assertEqual(ohlcv.open, Decimal("1"))

    def test_mapping_validation(self):
        m = NormalizerMapping(
            source="src",
            provider_symbol="BTCUSDT",
            canonical_asset_id="btc",
            canonical_symbol="BTC",
            data_type=MarketDataType.TRADE,
            field_map={"p": "price"},
        )
        self.assertEqual(m.source, "src")

    def test_mapping_empty_field_map(self):
        with self.assertRaises(ValueError):
            NormalizerMapping(
                source="src",
                provider_symbol="BTCUSDT",
                canonical_asset_id="btc",
                canonical_symbol="BTC",
                data_type=MarketDataType.TRADE,
                field_map={},
            )

    def test_duplicate_mapping(self):
        m1 = NormalizerMapping(
            source="src",
            provider_symbol="BTCUSDT",
            canonical_asset_id="btc",
            canonical_symbol="BTC",
            data_type=MarketDataType.TRADE,
            field_map={"p": "price"},
        )
        m2 = NormalizerMapping(
            source="src",
            provider_symbol="BTCUSDT",
            canonical_asset_id="btc2",
            canonical_symbol="BTC2",
            data_type=MarketDataType.TRADE,
            field_map={"p": "price"},
        )
        with self.assertRaises(ValueError):
            NormalizerMapping.validate_unique([m1, m2])

    def test_ambiguous_mapping(self):
        m1 = NormalizerMapping(
            source="src",
            provider_symbol="BTCUSDT",
            canonical_asset_id="btc",
            canonical_symbol="BTC",
            data_type=MarketDataType.TRADE,
            field_map={"p": "price"},
        )
        m2 = NormalizerMapping(
            source="src",
            provider_symbol="BTCUSDT",
            canonical_asset_id="btc2",
            canonical_symbol="BTC2",
            data_type=MarketDataType.TRADE,
            field_map={"p": "price"},
        )
        with self.assertRaises(ValueError):
            NormalizerMapping.validate_unique([m1, m2])

    def test_error_hierarchy(self):
        self.assertTrue(issubclass(UnsupportedDataTypeError, NormalizationError))
        self.assertTrue(issubclass(UnknownAssetError, NormalizationError))
        self.assertTrue(issubclass(MissingFieldError, NormalizationError))
        self.assertTrue(issubclass(InvalidNumericValueError, NormalizationError))
        self.assertTrue(issubclass(InvalidTimestampError, NormalizationError))
        self.assertTrue(issubclass(InvalidMappingError, NormalizationError))

    def test_protocol_compatibility(self):
        class N:
            def normalize(self, raw):
                return NormalizedRecord(
                    source="s",
                    canonical_asset_id="a",
                    canonical_symbol="BTC",
                    data_type=MarketDataType.TRADE,
                    ts_event=datetime(2026, 1, 1, tzinfo=timezone.utc),
                    idempotency_key="k",
                )

        self.assertTrue(isinstance(N(), Normalizer))
