from __future__ import annotations

import unittest
from decimal import Decimal

from data_quality.config import QualityConfig, ISSUE_PENALTIES, ISSUE_SEVERITIES
from data_quality.errors import InvalidConfigError
from data_quality.types import QualityIssue, QualityResult, QualityStatus, Severity


class TestDataQualityStage1(unittest.TestCase):
    def test_enums(self):
        self.assertEqual(QualityStatus.PASS.value, "pass")
        self.assertEqual(Severity.CRITICAL.value, "critical")

    def test_quality_issue_construction(self):
        issue = QualityIssue(code="x", severity=Severity.WARNING, message="m", penalty=Decimal("5"))
        self.assertEqual(issue.penalty, Decimal("5"))

    def test_quality_result_construction(self):
        from datetime import datetime, timezone
        r = QualityResult(score=Decimal("80"), status=QualityStatus.PASS, issues=(), checked_at=datetime(2026,1,1,tzinfo=timezone.utc))
        self.assertEqual(r.score, Decimal("80"))

    def test_default_config(self):
        cfg = QualityConfig()
        self.assertEqual(cfg.price_change_threshold, Decimal("10.0"))
        self.assertEqual(cfg.volume_change_threshold, Decimal("50.0"))
        self.assertEqual(cfg.max_age_seconds, 300)
        self.assertEqual(cfg.future_tolerance_seconds, 5)
        self.assertEqual(cfg.pass_threshold, Decimal("80"))
        self.assertEqual(cfg.warning_threshold, Decimal("50"))

    def test_invalid_config_threshold(self):
        with self.assertRaises(InvalidConfigError):
            QualityConfig(price_change_threshold=Decimal("0"))

    def test_nan_rejected(self):
        with self.assertRaises(InvalidConfigError):
            QualityConfig(price_change_threshold=Decimal("NaN"))

    def test_status_threshold_ordering(self):
        with self.assertRaises(InvalidConfigError):
            QualityConfig(pass_threshold=Decimal("40"), warning_threshold=Decimal("50"))

    def test_immutability(self):
        cfg = QualityConfig()
        with self.assertRaises(Exception):
            cfg.max_age_seconds = 10
        issue = QualityIssue(code="x", severity=Severity.WARNING, message="m", penalty=Decimal("5"))
        with self.assertRaises(Exception):
            issue.penalty = Decimal("6")

    def test_penalty_mapping(self):
        self.assertEqual(ISSUE_PENALTIES["invalid_price"], Decimal("25"))
        self.assertEqual(ISSUE_SEVERITIES["invalid_price"], "critical")

    def test_infinity_rejected(self):
        with self.assertRaises(InvalidConfigError):
            QualityConfig(price_change_threshold=Decimal("Infinity"))
        with self.assertRaises(InvalidConfigError):
            QualityConfig(price_change_threshold=Decimal("-Infinity"))

    def test_zero_penalty_accepted(self):
        issue = QualityIssue(code="completeness_unknown", severity=Severity.INFO, message="m", penalty=Decimal("0"))
        self.assertEqual(issue.penalty, Decimal("0"))

    def test_invalid_decimal_rejected(self):
        with self.assertRaises(InvalidConfigError):
            QualityConfig(price_change_threshold="10")

    def test_nested_mutation_prevented(self):
        cfg = QualityConfig()
        with self.assertRaises(Exception):
            cfg.issue_penalties["x"] = Decimal("1")

    def test_utc_enforcement(self):
        from datetime import datetime
        with self.assertRaises(ValueError):
            QualityResult(score=Decimal("10"), status=QualityStatus.PASS, issues=(), checked_at=datetime(2026,1,1))

    def test_score_boundaries(self):
        from datetime import datetime, timezone
        r0 = QualityResult(score=Decimal("0"), status=QualityStatus.FAIL, issues=(), checked_at=datetime(2026,1,1,tzinfo=timezone.utc))
        r100 = QualityResult(score=Decimal("100"), status=QualityStatus.PASS, issues=(), checked_at=datetime(2026,1,1,tzinfo=timezone.utc))
        self.assertEqual(r0.score, Decimal("0"))
        self.assertEqual(r100.score, Decimal("100"))
        with self.assertRaises(ValueError):
            QualityResult(score=Decimal("-1"), status=QualityStatus.FAIL, issues=(), checked_at=datetime(2026,1,1,tzinfo=timezone.utc))
        with self.assertRaises(ValueError):
            QualityResult(score=Decimal("101"), status=QualityStatus.PASS, issues=(), checked_at=datetime(2026,1,1,tzinfo=timezone.utc))

