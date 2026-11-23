from __future__ import annotations

import unittest
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from connectors.types import Completeness, RawRecord
from normalizers.normalizer import NormalizerEngine
from normalizers.mapping import NormalizerMapping
from normalizers.types import MarketDataType

from data_quality.config import QualityConfig
from data_quality.errors import InvalidNormalizedRecordError, InvalidReferenceError
from data_quality.types import QualityIssue, QualityStatus
from data_quality.validators import (
    OHLCVValidator,
    PriceAnomalyValidator,
    VolumeAnomalyValidator,
    FreshnessValidator,
    CompletenessValidator,
)


def make_record(data_type, **kwargs):
    from normalizers.types import NormalizedRecord, OHLCV
    base = dict(
        source="s",
        canonical_asset_id="a",
        canonical_symbol="BTC",
        data_type=data_type,
        ts_event=datetime(2026, 1, 1, tzinfo=timezone.utc),
        idempotency_key="k",
        completeness=Completeness.COMPLETE,
    )
    base.update(kwargs)
    return NormalizedRecord(**base)


class TestValidators(unittest.TestCase):
    def setUp(self):
        self.cfg = QualityConfig()

    def test_ohlcv_valid(self):
        rec = make_record(MarketDataType.OHLCV, ohlcv=__import__("normalizers.types", fromlist=["OHLCV"]).OHLCV(open=Decimal("1"), high=Decimal("2"), low=Decimal("0.5"), close=Decimal("1.5"), volume=Decimal("10"), interval="1m"))
        self.assertEqual(OHLCVValidator.validate(rec, self.cfg), [])

    def test_ohlcv_violation_single(self):
        from normalizers.types import OHLCV
        rec = make_record(MarketDataType.OHLCV, ohlcv=OHLCV(open=Decimal("1"), high=Decimal("0.5"), low=Decimal("2"), close=Decimal("1.5"), volume=Decimal("10"), interval="1m"))
        issues = OHLCVValidator.validate(rec, self.cfg)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "ohlcv_violation")

    def test_ohlcv_missing_raises(self):
        rec = make_record(MarketDataType.OHLCV)
        with self.assertRaises(InvalidNormalizedRecordError):
            OHLCVValidator.validate(rec, self.cfg)

    def test_price_missing_required(self):
        rec = make_record(MarketDataType.TRADE, price=None)
        issues = PriceAnomalyValidator.validate(rec, None, self.cfg)
        self.assertEqual(issues[0].code, "missing_price")

    def test_price_optional_skip(self):
        rec = make_record(MarketDataType.OHLCV, price=None, ohlcv=__import__("normalizers.types", fromlist=["OHLCV"]).OHLCV(open=Decimal("1"), high=Decimal("2"), low=Decimal("0.5"), close=Decimal("1.5"), volume=Decimal("10"), interval="1m"))
        issues = PriceAnomalyValidator.validate(rec, None, self.cfg)
        self.assertEqual(issues, [])

    def test_price_invalid(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("0"))
        issues = PriceAnomalyValidator.validate(rec, None, self.cfg)
        self.assertEqual(issues[0].code, "invalid_price")

    def test_price_anomaly(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("120"))
        ref = make_record(MarketDataType.TRADE, price=Decimal("100"))
        issues = PriceAnomalyValidator.validate(rec, ref, self.cfg)
        self.assertEqual(issues[0].code, "price_anomaly")

    def test_price_threshold_equality_no_issue(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("110"))
        ref = make_record(MarketDataType.TRADE, price=Decimal("100"))
        issues = PriceAnomalyValidator.validate(rec, ref, self.cfg)
        self.assertEqual(issues, [])

    def test_price_no_reference_skip(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("100"))
        issues = PriceAnomalyValidator.validate(rec, None, self.cfg)
        self.assertEqual(issues, [])

    def test_price_invalid_reference_raises(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("100"))
        ref = make_record(MarketDataType.TRADE, price=Decimal("0"))
        with self.assertRaises(InvalidReferenceError):
            PriceAnomalyValidator.validate(rec, ref, self.cfg)

    def test_volume_trade_missing_raises(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("1"), quantity=None)
        with self.assertRaises(InvalidNormalizedRecordError):
            VolumeAnomalyValidator.validate(rec, None, self.cfg)

    def test_volume_negative_current(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("1"), quantity=Decimal("-1"))
        issues = VolumeAnomalyValidator.validate(rec, None, self.cfg)
        self.assertEqual(issues[0].code, "invalid_volume")

    def test_volume_anomaly(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("1"), quantity=Decimal("200"))
        ref = make_record(MarketDataType.TRADE, price=Decimal("1"), quantity=Decimal("100"))
        issues = VolumeAnomalyValidator.validate(rec, ref, self.cfg)
        self.assertEqual(issues[0].code, "volume_anomaly")

    def test_volume_zero_reference_skip(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("1"), quantity=Decimal("10"))
        ref = make_record(MarketDataType.TRADE, price=Decimal("1"), quantity=Decimal("0"))
        issues = VolumeAnomalyValidator.validate(rec, ref, self.cfg)
        self.assertEqual(issues, [])

    def test_volume_zero_current_compared(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("1"), quantity=Decimal("0"))
        ref = make_record(MarketDataType.TRADE, price=Decimal("1"), quantity=Decimal("100"))
        issues = VolumeAnomalyValidator.validate(rec, ref, self.cfg)
        self.assertEqual(issues[0].code, "volume_anomaly")

    def test_volume_different_dtype_raises(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("1"), quantity=Decimal("10"))
        ref = make_record(MarketDataType.QUOTE, price=Decimal("1"), quantity=Decimal("10"))
        with self.assertRaises(InvalidReferenceError):
            VolumeAnomalyValidator.validate(rec, ref, self.cfg)

    def test_freshness_stale(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("1"), quantity=Decimal("1"))
        checked = datetime(2026, 1, 1, 0, 10, tzinfo=timezone.utc)
        issues = FreshnessValidator.validate(rec, checked, self.cfg)
        self.assertEqual(issues[0].code, "stale_record")

    def test_freshness_boundary_pass(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("1"), quantity=Decimal("1"))
        checked = datetime(2026, 1, 1, 0, 5, tzinfo=timezone.utc)
        issues = FreshnessValidator.validate(rec, checked, self.cfg)
        self.assertEqual(issues, [])

    def test_freshness_future(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("1"), quantity=Decimal("1"), ts_event=datetime(2026, 1, 1, 0, 0, 10, tzinfo=timezone.utc))
        checked = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
        issues = FreshnessValidator.validate(rec, checked, self.cfg)
        self.assertEqual(issues[0].code, "future_timestamp")

    def test_completeness_states(self):
        for comp, expected in [(Completeness.COMPLETE, []), (Completeness.PARTIAL, ["completeness_partial"]), (Completeness.UNKNOWN, ["completeness_unknown"])]:
            rec = make_record(MarketDataType.TRADE, price=Decimal("1"), quantity=Decimal("1"), completeness=comp)
            issues = CompletenessValidator.validate(rec, self.cfg)
            self.assertEqual([i.code for i in issues], expected)
