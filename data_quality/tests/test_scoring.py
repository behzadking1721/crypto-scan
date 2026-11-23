from __future__ import annotations

import unittest
from decimal import Decimal
from data_quality.config import QualityConfig
from data_quality.errors import InvalidQualityIssueError
from data_quality.types import QualityIssue, Severity
from data_quality.scoring import ScoringEngine


class TestScoring(unittest.TestCase):
    def setUp(self):
        self.cfg = QualityConfig()

    def test_empty(self):
        self.assertEqual(ScoringEngine.score([], self.cfg), Decimal("100"))

    def test_single(self):
        issue = QualityIssue(code="stale_record", severity=Severity.WARNING, message="m", penalty=Decimal("20"))
        self.assertEqual(ScoringEngine.score([issue], self.cfg), Decimal("80"))

    def test_cumulative(self):
        i1 = QualityIssue(code="stale_record", severity=Severity.WARNING, message="m", penalty=Decimal("20"))
        i2 = QualityIssue(code="future_timestamp", severity=Severity.WARNING, message="m", penalty=Decimal("15"))
        self.assertEqual(ScoringEngine.score([i1, i2], self.cfg), Decimal("65"))

    def test_clamp_zero(self):
        issues = [
            QualityIssue(code="ohlcv_violation", severity=Severity.CRITICAL, message="m", penalty=Decimal("25")),
            QualityIssue(code="invalid_price", severity=Severity.CRITICAL, message="m", penalty=Decimal("25"), field="a"),
            QualityIssue(code="invalid_volume", severity=Severity.CRITICAL, message="m", penalty=Decimal("25"), field="b"),
            QualityIssue(code="price_anomaly", severity=Severity.CRITICAL, message="m", penalty=Decimal("20"), field="c"),
            QualityIssue(code="stale_record", severity=Severity.WARNING, message="m", penalty=Decimal("20"), field="d"),
        ]
        self.assertEqual(ScoringEngine.score(issues, self.cfg), Decimal("0"))

    def test_boundary(self):
        issue = QualityIssue(code="stale_record", severity=Severity.WARNING, message="m", penalty=Decimal("20"))
        self.assertEqual(ScoringEngine.score([issue], self.cfg), Decimal("80"))

    def test_duplicate_same_field(self):
        i1 = QualityIssue(code="stale_record", severity=Severity.WARNING, message="m", penalty=Decimal("20"), field="x")
        i2 = QualityIssue(code="stale_record", severity=Severity.WARNING, message="m", penalty=Decimal("20"), field="x")
        self.assertEqual(ScoringEngine.score([i1, i2], self.cfg), Decimal("80"))

    def test_independent_different_fields(self):
        i1 = QualityIssue(code="stale_record", severity=Severity.WARNING, message="m", penalty=Decimal("20"), field="a")
        i2 = QualityIssue(code="stale_record", severity=Severity.WARNING, message="m", penalty=Decimal("20"), field="b")
        self.assertEqual(ScoringEngine.score([i1, i2], self.cfg), Decimal("60"))

    def test_none_fields_duplicate(self):
        i1 = QualityIssue(code="stale_record", severity=Severity.WARNING, message="m", penalty=Decimal("20"))
        i2 = QualityIssue(code="stale_record", severity=Severity.WARNING, message="m", penalty=Decimal("20"))
        self.assertEqual(ScoringEngine.score([i1, i2], self.cfg), Decimal("80"))

    def test_invalid_metadata_raises(self):
        issue = QualityIssue(code="stale_record", severity=Severity.WARNING, message="m", penalty=Decimal("20"))
        # tamper severity by constructing mismatched
        bad = QualityIssue(code="stale_record", severity=Severity.CRITICAL, message="m", penalty=Decimal("20"))
        with self.assertRaises(InvalidQualityIssueError):
            ScoringEngine.score([bad], self.cfg)

    def test_unknown_code_raises(self):
        issue = QualityIssue(code="foo", severity=Severity.WARNING, message="m", penalty=Decimal("1"))
        with self.assertRaises(InvalidQualityIssueError):
            ScoringEngine.score([issue], self.cfg)

    def test_decimal_precision(self):
        issue = QualityIssue(code="completeness_unknown", severity=Severity.INFO, message="m", penalty=Decimal("0"))
        self.assertEqual(ScoringEngine.score([issue], self.cfg), Decimal("100"))
