from __future__ import annotations

import unittest
from datetime import datetime, timezone
from decimal import Decimal

from connectors.types import Completeness
from normalizers.types import MarketDataType, NormalizedRecord, OHLCV

from data_quality.config import QualityConfig
from data_quality.engine import DataQualityEngine
from data_quality.types import QualityStatus


def make_record(data_type, **kwargs):
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


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.cfg = QualityConfig()
        self.checked = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def test_valid_no_issues(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("100"), quantity=Decimal("10"))
        res = DataQualityEngine.evaluate(rec, checked_at=self.checked)
        self.assertEqual(res.score, Decimal("100"))
        self.assertEqual(res.status, QualityStatus.PASS)
        self.assertEqual(res.issues, ())

    def test_missing_checked_raises(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("100"), quantity=Decimal("10"))
        with self.assertRaises(ValueError):
            DataQualityEngine.evaluate(rec)

    def test_naive_checked_raises(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("100"), quantity=Decimal("10"))
        with self.assertRaises(ValueError):
            DataQualityEngine.evaluate(rec, checked_at=datetime(2026, 1, 1))

    def test_each_issue(self):
        # ohlcv violation
        from normalizers.types import OHLCV
        rec = make_record(MarketDataType.OHLCV, ohlcv=OHLCV(open=Decimal("1"), high=Decimal("0.5"), low=Decimal("2"), close=Decimal("1.5"), volume=Decimal("10"), interval="1m"))
        res = DataQualityEngine.evaluate(rec, checked_at=self.checked)
        self.assertIn("ohlcv_violation", [i.code for i in res.issues])

    def test_determinism(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("100"), quantity=Decimal("10"))
        r1 = DataQualityEngine.evaluate(rec, checked_at=self.checked)
        r2 = DataQualityEngine.evaluate(rec, checked_at=self.checked)
        self.assertEqual(r1, r2)

    def test_reference_present(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("120"), quantity=Decimal("10"))
        ref = make_record(MarketDataType.TRADE, price=Decimal("100"), quantity=Decimal("10"))
        res = DataQualityEngine.evaluate(rec, reference=ref, checked_at=self.checked)
        self.assertIn("price_anomaly", [i.code for i in res.issues])

    def test_invalid_reference_raises(self):
        rec = make_record(MarketDataType.TRADE, price=Decimal("100"), quantity=Decimal("10"))
        ref = make_record(MarketDataType.TRADE, price=Decimal("0"), quantity=Decimal("10"))
        with self.assertRaises(Exception):
            DataQualityEngine.evaluate(rec, reference=ref, checked_at=self.checked)
