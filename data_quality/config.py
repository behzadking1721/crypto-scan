"""Data quality configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from types import MappingProxyType
from typing import Any

from data_quality.errors import InvalidConfigError
from data_quality.types import QualityStatus

__all__ = ["QualityConfig", "ISSUE_PENALTIES", "ISSUE_SEVERITIES"]


ISSUE_PENALTIES: dict[str, Decimal] = {
    "ohlcv_violation": Decimal("25"),
    "invalid_price": Decimal("25"),
    "invalid_volume": Decimal("25"),
    "price_anomaly": Decimal("20"),
    "stale_record": Decimal("20"),
    "future_timestamp": Decimal("15"),
    "volume_anomaly": Decimal("15"),
    "missing_price": Decimal("10"),
    "completeness_partial": Decimal("10"),
    "completeness_unknown": Decimal("0"),
}

ISSUE_SEVERITIES: dict[str, str] = {
    "ohlcv_violation": "critical",
    "invalid_price": "critical",
    "invalid_volume": "critical",
    "price_anomaly": "critical",
    "stale_record": "warning",
    "future_timestamp": "warning",
    "volume_anomaly": "warning",
    "missing_price": "warning",
    "completeness_partial": "warning",
    "completeness_unknown": "info",
}


def _is_decimal(value: Any) -> bool:
    return isinstance(value, Decimal) and not isinstance(value, bool)


@dataclass(frozen=True)
class QualityConfig:
    price_change_threshold: Decimal = Decimal("10.0")
    volume_change_threshold: Decimal = Decimal("50.0")
    max_age_seconds: int = 300
    future_tolerance_seconds: int = 5
    pass_threshold: Decimal = Decimal("80")
    warning_threshold: Decimal = Decimal("50")
    issue_penalties: dict[str, Decimal] = field(default_factory=lambda: dict(ISSUE_PENALTIES))
    issue_severities: dict[str, str] = field(default_factory=lambda: dict(ISSUE_SEVERITIES))

    def __post_init__(self) -> None:
        if not _is_decimal(self.price_change_threshold) or not self.price_change_threshold.is_finite() or self.price_change_threshold <= 0:
            raise InvalidConfigError("price_change_threshold must be a positive finite Decimal")
        if not _is_decimal(self.volume_change_threshold) or not self.volume_change_threshold.is_finite() or self.volume_change_threshold <= 0:
            raise InvalidConfigError("volume_change_threshold must be a positive finite Decimal")
        if not isinstance(self.max_age_seconds, int) or isinstance(self.max_age_seconds, bool) or self.max_age_seconds < 0:
            raise InvalidConfigError("max_age_seconds must be a non-negative int")
        if not isinstance(self.future_tolerance_seconds, int) or isinstance(self.future_tolerance_seconds, bool) or self.future_tolerance_seconds < 0:
            raise InvalidConfigError("future_tolerance_seconds must be a non-negative int")
        if not _is_decimal(self.pass_threshold) or not self.pass_threshold.is_finite():
            raise InvalidConfigError("pass_threshold must be a finite Decimal")
        if not _is_decimal(self.warning_threshold) or not self.warning_threshold.is_finite():
            raise InvalidConfigError("warning_threshold must be a finite Decimal")
        if not (0 <= self.warning_threshold <= self.pass_threshold <= 100):
            raise InvalidConfigError("status thresholds must satisfy 0 <= warning <= pass <= 100")
        if not isinstance(self.issue_penalties, dict):
            raise InvalidConfigError("issue_penalties must be a dict")
        if not isinstance(self.issue_severities, dict):
            raise InvalidConfigError("issue_severities must be a dict")
        for code, penalty in self.issue_penalties.items():
            if not isinstance(code, str) or not code.strip():
                raise InvalidConfigError("issue code must be a non-empty string")
            if not _is_decimal(penalty) or not penalty.is_finite() or penalty < 0:
                raise InvalidConfigError(f"penalty for {code} must be a non-negative finite Decimal")
        # freeze nested dicts
        object.__setattr__(self, "issue_penalties", MappingProxyType(dict(self.issue_penalties)))
        object.__setattr__(self, "issue_severities", MappingProxyType(dict(self.issue_severities)))
