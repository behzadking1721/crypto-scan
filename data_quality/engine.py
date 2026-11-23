"""Data quality engine."""

from __future__ import annotations

from datetime import datetime, timezone

from data_quality.config import QualityConfig
from data_quality.config import QualityConfig
from data_quality.scoring import ScoringEngine
from data_quality.status import StatusResolver
from data_quality.types import QualityResult
from data_quality.validators import (
    CompletenessValidator,
    FreshnessValidator,
    OHLCVValidator,
    PriceAnomalyValidator,
    VolumeAnomalyValidator,
)


def _require_utc(dt: datetime, name: str) -> datetime:
    if not isinstance(dt, datetime):
        raise TypeError(f"{name} must be a datetime")
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"{name} must be UTC-aware")
    return dt.astimezone(timezone.utc)


class DataQualityEngine:
    @staticmethod
    def evaluate(record, reference=None, config=None, checked_at=None) -> QualityResult:
        if config is None:
            config = QualityConfig()
        if checked_at is None:
            raise ValueError("checked_at is required")
        checked_at = _require_utc(checked_at, "checked_at")

        issues = []
        issues.extend(OHLCVValidator.validate(record, config))
        issues.extend(PriceAnomalyValidator.validate(record, reference, config))
        issues.extend(VolumeAnomalyValidator.validate(record, reference, config))
        issues.extend(FreshnessValidator.validate(record, checked_at, config))
        issues.extend(CompletenessValidator.validate(record, config))

        score = ScoringEngine.score(issues, config)
        status = StatusResolver.resolve(issues, score, config)
        return QualityResult(score=score, status=status, issues=tuple(issues), checked_at=checked_at)
