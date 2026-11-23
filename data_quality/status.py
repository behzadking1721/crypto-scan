"""Data quality status resolver."""

from __future__ import annotations

from decimal import Decimal

from data_quality.config import QualityConfig
from data_quality.errors import InvalidQualityIssueError
from data_quality.types import QualityIssue, QualityStatus


class StatusResolver:
    @staticmethod
    def _validate_issue(issue: QualityIssue, config: QualityConfig) -> None:
        if not isinstance(issue, QualityIssue):
            raise InvalidQualityIssueError("issue must be a QualityIssue")
        if issue.code not in config.issue_penalties:
            raise InvalidQualityIssueError(f"unknown issue code: {issue.code}")
        if issue.penalty != config.issue_penalties[issue.code]:
            raise InvalidQualityIssueError("penalty mismatch")
        if not issue.penalty.is_finite() or issue.penalty < 0:
            raise InvalidQualityIssueError("penalty must be finite and non-negative")
        if issue.severity.value != config.issue_severities[issue.code]:
            raise InvalidQualityIssueError("severity mismatch")

    @staticmethod
    def resolve(issues, score, config: QualityConfig) -> QualityStatus:
        if not isinstance(config, QualityConfig):
            raise TypeError("config must be a QualityConfig")
        if not isinstance(score, Decimal) or isinstance(score, bool):
            raise TypeError("score must be a Decimal")
        if not score.is_finite():
            raise ValueError("score must be finite")
        if score < 0 or score > 100:
            raise ValueError("score must be between 0 and 100")
        if not isinstance(issues, (list, tuple)):
            raise TypeError("issues must be a list or tuple")
        for issue in issues:
            StatusResolver._validate_issue(issue, config)

        has_critical = any(i.severity.value == "critical" for i in issues)
        has_warning = any(i.severity.value == "warning" for i in issues)

        if has_critical:
            return QualityStatus.FAIL
        if has_warning:
            return QualityStatus.WARNING
        if score >= config.pass_threshold:
            return QualityStatus.PASS
        if score >= config.warning_threshold:
            return QualityStatus.WARNING
        return QualityStatus.FAIL
