from __future__ import annotations

import unittest
from decimal import Decimal
from data_quality.config import QualityConfig
from data_quality.errors import InvalidQualityIssueError
from data_quality.status import StatusResolver
from data_quality.types import QualityIssue, QualityStatus, Severity


class TestStatus(unittest.TestCase):
    def setUp(self):
        self.cfg = QualityConfig()

    def test_critical_score_100(self):
        issue = QualityIssue(code="invalid_price", severity=Severity.CRITICAL, message="m", penalty=Decimal("25"))
        self.assertEqual(StatusResolver.resolve([issue], Decimal("100"), self.cfg), QualityStatus.FAIL)

    def test_warning_score_100(self):
        issue = QualityIssue(code="stale_record", severity=Severity.WARNING, message="m", penalty=Decimal("20"))
        self.assertEqual(StatusResolver.resolve([issue], Decimal("100"), self.cfg), QualityStatus.WARNING)

    def test_info_only(self):
        issue = QualityIssue(code="completeness_unknown", severity=Severity.INFO, message="m", penalty=Decimal("0"))
        self.assertEqual(StatusResolver.resolve([issue], Decimal("100"), self.cfg), QualityStatus.PASS)

    def test_empty(self):
        self.assertEqual(StatusResolver.resolve([], Decimal("100"), self.cfg), QualityStatus.PASS)

    def test_boundary_80(self):
        self.assertEqual(StatusResolver.resolve([], Decimal("80"), self.cfg), QualityStatus.PASS)

    def test_just_below_80(self):
        self.assertEqual(StatusResolver.resolve([], Decimal("79.99"), self.cfg), QualityStatus.WARNING)

    def test_boundary_50(self):
        self.assertEqual(StatusResolver.resolve([], Decimal("50"), self.cfg), QualityStatus.WARNING)

    def test_just_below_50(self):
        self.assertEqual(StatusResolver.resolve([], Decimal("49.99"), self.cfg), QualityStatus.FAIL)

    def test_zero(self):
        self.assertEqual(StatusResolver.resolve([], Decimal("0"), self.cfg), QualityStatus.FAIL)

    def test_hundred(self):
        self.assertEqual(StatusResolver.resolve([], Decimal("100"), self.cfg), QualityStatus.PASS)

    def test_invalid_score_type(self):
        with self.assertRaises(TypeError):
            StatusResolver.resolve([], 100, self.cfg)

    def test_invalid_score_range(self):
        with self.assertRaises(ValueError):
            StatusResolver.resolve([], Decimal("101"), self.cfg)

    def test_invalid_issue_metadata(self):
        bad = QualityIssue(code="stale_record", severity=Severity.CRITICAL, message="m", penalty=Decimal("20"))
        with self.assertRaises(InvalidQualityIssueError):
            StatusResolver.resolve([bad], Decimal("100"), self.cfg)

    def test_order_independence(self):
        i1 = QualityIssue(code="stale_record", severity=Severity.WARNING, message="m", penalty=Decimal("20"))
        i2 = QualityIssue(code="future_timestamp", severity=Severity.WARNING, message="m", penalty=Decimal("15"))
        a = StatusResolver.resolve([i1, i2], Decimal("100"), self.cfg)
        b = StatusResolver.resolve([i2, i1], Decimal("100"), self.cfg)
        self.assertEqual(a, b)
