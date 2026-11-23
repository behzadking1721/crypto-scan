"""Data quality validators."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from normalizers.types import MarketDataType, NormalizedRecord

from data_quality.config import QualityConfig
from data_quality.errors import (
    InvalidNormalizedRecordError,
    InvalidReferenceError,
)
from data_quality.types import QualityIssue, Severity


def _issue(code: str, config: QualityConfig, field: str | None = None) -> QualityIssue:
    severity_str = config.issue_severities[code]
    severity = Severity(severity_str)
    penalty = config.issue_penalties[code]
    return QualityIssue(code=code, severity=severity, message=code, penalty=penalty, field=field)


def _require_utc(dt: datetime, name: str) -> datetime:
    if not isinstance(dt, datetime):
        raise TypeError(f"{name} must be a datetime")
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"{name} must be UTC-aware")
    return dt.astimezone(timezone.utc)


class OHLCVValidator:
    @staticmethod
    def validate(record: NormalizedRecord, config: QualityConfig) -> list[QualityIssue]:
        if record.data_type != MarketDataType.OHLCV:
            return []
        ohlcv = record.ohlcv
        if ohlcv is None:
            raise InvalidNormalizedRecordError("OHLCV data missing")
        violations = False
        if ohlcv.high < ohlcv.low:
            violations = True
        if ohlcv.high < ohlcv.open:
            violations = True
        if ohlcv.high < ohlcv.close:
            violations = True
        if ohlcv.low > ohlcv.open:
            violations = True
        if ohlcv.low > ohlcv.close:
            violations = True
        if ohlcv.volume < 0:
            violations = True
        if violations:
            return [_issue("ohlcv_violation", config)]
        return []


class PriceAnomalyValidator:
    @staticmethod
    def _price_required(data_type: MarketDataType) -> bool:
        return data_type in (MarketDataType.TRADE, MarketDataType.QUOTE)

    @staticmethod
    def validate(record: NormalizedRecord, reference: NormalizedRecord | None, config: QualityConfig) -> list[QualityIssue]:
        price = record.price
        required = PriceAnomalyValidator._price_required(record.data_type)
        if price is None:
            if required:
                return [_issue("missing_price", config, "price")]
            return []
        if price <= 0:
            return [_issue("invalid_price", config, "price")]
        # invalid suppresses anomaly
        if reference is None:
            return []
        # validate reference
        if not isinstance(reference, NormalizedRecord):
            raise InvalidReferenceError("reference must be NormalizedRecord")
        if reference.canonical_asset_id != record.canonical_asset_id:
            raise InvalidReferenceError("asset mismatch")
        if reference.data_type != record.data_type:
            raise InvalidReferenceError("data type mismatch")
        # interval compatibility
        ref_interval = getattr(reference.ohlcv, "interval", None) if reference.ohlcv else None
        rec_interval = getattr(record.ohlcv, "interval", None) if record.ohlcv else None
        if ref_interval is not None and rec_interval is not None and ref_interval != rec_interval:
            raise InvalidReferenceError("interval mismatch")
        # timestamps
        rec_ts = _require_utc(record.ts_event, "ts_event")
        ref_ts = _require_utc(reference.ts_event, "ts_event")
        if ref_ts > rec_ts:
            raise InvalidReferenceError("reference timestamp after record")
        if reference.price is None or reference.price <= 0:
            raise InvalidReferenceError("reference price invalid")
        pct = (abs(price - reference.price) / reference.price) * Decimal("100")
        if pct > config.price_change_threshold:
            return [_issue("price_anomaly", config, "price")]
        return []


class VolumeAnomalyValidator:
    @staticmethod
    def _volume_source(record: NormalizedRecord) -> Decimal | None:
        if record.data_type == MarketDataType.OHLCV:
            if record.ohlcv is None:
                raise InvalidNormalizedRecordError("OHLCV data missing")
            return record.ohlcv.volume
        return record.quantity

    @staticmethod
    def _ref_volume_source(reference: NormalizedRecord) -> Decimal | None:
        if reference.data_type == MarketDataType.OHLCV:
            if reference.ohlcv is None:
                raise InvalidReferenceError("reference OHLCV data missing")
            return reference.ohlcv.volume
        return reference.quantity

    @staticmethod
    def _volume_required(data_type: MarketDataType) -> bool:
        return data_type in (MarketDataType.TRADE, MarketDataType.OHLCV)

    @staticmethod
    def validate(record: NormalizedRecord, reference: NormalizedRecord | None, config: QualityConfig) -> list[QualityIssue]:
        vol = VolumeAnomalyValidator._volume_source(record)
        required = VolumeAnomalyValidator._volume_required(record.data_type)
        if vol is None:
            if required:
                raise InvalidNormalizedRecordError("volume missing")
            return []
        if vol < 0:
            return [_issue("invalid_volume", config, "volume")]
        if reference is None:
            return []
        if not isinstance(reference, NormalizedRecord):
            raise InvalidReferenceError("reference must be NormalizedRecord")
        if reference.canonical_asset_id != record.canonical_asset_id:
            raise InvalidReferenceError("asset mismatch")
        if reference.data_type != record.data_type:
            raise InvalidReferenceError("data type mismatch")
        ref_vol = VolumeAnomalyValidator._ref_volume_source(reference)
        if ref_vol is None:
            return []
        if ref_vol < 0:
            raise InvalidReferenceError("reference volume invalid")
        if ref_vol == 0:
            return []
        rec_ts = _require_utc(record.ts_event, "ts_event")
        ref_ts = _require_utc(reference.ts_event, "ts_event")
        if ref_ts > rec_ts:
            raise InvalidReferenceError("reference timestamp after record")
        pct = (abs(vol - ref_vol) / ref_vol) * Decimal("100")
        if pct > config.volume_change_threshold:
            return [_issue("volume_anomaly", config, "volume")]
        return []


class FreshnessValidator:
    @staticmethod
    def validate(record: NormalizedRecord, checked_at: datetime, config: QualityConfig) -> list[QualityIssue]:
        rec_ts = _require_utc(record.ts_event, "ts_event")
        chk = _require_utc(checked_at, "checked_at")
        issues: list[QualityIssue] = []
        age_seconds = (chk - rec_ts).total_seconds()
        if age_seconds > config.max_age_seconds:
            issues.append(_issue("stale_record", config))
        future_seconds = (rec_ts - chk).total_seconds()
        if future_seconds > config.future_tolerance_seconds:
            issues.append(_issue("future_timestamp", config))
        return issues


class CompletenessValidator:
    @staticmethod
    def validate(record: NormalizedRecord, config: QualityConfig) -> list[QualityIssue]:
        from connectors.types import Completeness

        if record.completeness == Completeness.COMPLETE:
            return []
        if record.completeness == Completeness.PARTIAL:
            return [_issue("completeness_partial", config)]
        return [_issue("completeness_unknown", config)]
