"""Data quality types and contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any

__all__ = ["QualityStatus", "Severity", "QualityIssue", "QualityResult"]


class QualityStatus(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


def _require_utc(dt: datetime, name: str) -> datetime:
    if not isinstance(dt, datetime):
        raise TypeError(f"{name} must be a datetime")
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"{name} must be UTC-aware")
    return dt.astimezone(timezone.utc)


@dataclass(frozen=True)
class QualityIssue:
    code: str
    severity: Severity
    message: str
    penalty: Decimal
    field: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.code, str) or not self.code.strip():
            raise ValueError("code must be a non-empty string")
        if not isinstance(self.severity, Severity):
            raise TypeError("severity must be a Severity")
        if not isinstance(self.message, str):
            raise TypeError("message must be a str")
        if isinstance(self.penalty, bool) or not isinstance(self.penalty, Decimal):
            raise TypeError("penalty must be a Decimal")
        if not self.penalty.is_finite() or self.penalty < 0:
            raise ValueError("penalty must be finite and >= 0")
        if self.field is not None and not isinstance(self.field, str):
            raise TypeError("field must be str or None")


@dataclass(frozen=True)
class QualityResult:
    score: Decimal
    status: QualityStatus
    issues: tuple[QualityIssue, ...]
    checked_at: datetime

    def __post_init__(self) -> None:
        if isinstance(self.score, bool) or not isinstance(self.score, Decimal):
            raise TypeError("score must be a Decimal")
        if not self.score.is_finite():
            raise ValueError("score must be finite")
        if self.score < 0 or self.score > 100:
            raise ValueError("score must be between 0 and 100")
        if not isinstance(self.status, QualityStatus):
            raise TypeError("status must be a QualityStatus")
        if not isinstance(self.issues, tuple):
            raise TypeError("issues must be a tuple")
        for issue in self.issues:
            if not isinstance(issue, QualityIssue):
                raise TypeError("issues must contain QualityIssue")
        object.__setattr__(self, "checked_at", _require_utc(self.checked_at, "checked_at"))
