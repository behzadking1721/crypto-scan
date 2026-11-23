"""Data quality scoring engine."""

from __future__ import annotations

from decimal import Decimal

from data_quality.config import QualityConfig
from data_quality.errors import InvalidQualityIssueError
from data_quality.types import QualityIssue


class ScoringEngine:
    @staticmethod
    def score(issues, config: QualityConfig) -> Decimal:
        if not isinstance(config, QualityConfig):
            raise TypeError("config must be a QualityConfig")
        if not isinstance(issues, (list, tuple)):
            raise TypeError("issues must be a list or tuple")
        validated: list[QualityIssue] = []
        seen: set[tuple[str, str | None]] = set()
        for issue in issues:
            if not isinstance(issue, QualityIssue):
                raise InvalidQualityIssueError("issue must be a QualityIssue")
            if issue.code not in config.issue_penalties:
                raise InvalidQualityIssueError(f"unknown issue code: {issue.code}")
            expected_penalty = config.issue_penalties[issue.code]
            if issue.penalty != expected_penalty:
                raise InvalidQualityIssueError("penalty mismatch")
            if not issue.penalty.is_finite() or issue.penalty < 0:
                raise InvalidQualityIssueError("penalty must be finite and non-negative")
            expected_severity = config.issue_severities[issue.code]
            if issue.severity.value != expected_severity:
                raise InvalidQualityIssueError("severity mismatch")
            key = (issue.code, issue.field)
            if key in seen:
                continue
            seen.add(key)
            validated.append(issue)
        total = sum((i.penalty for i in validated), Decimal("0"))
        score = Decimal("100") - total
        if score < 0:
            score = Decimal("0")
        if score > 100:
            score = Decimal("100")
        return score
