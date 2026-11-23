"""Normalizer engine."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from connectors.types import RawRecord

from normalizers.errors import (
    InvalidNumericValueError,
    InvalidTimestampError,
    MissingFieldError,
    NormalizationError,
    UnknownAssetError,
    UnsupportedDataTypeError,
)
from normalizers.mapping import NormalizerMapping
from normalizers.types import MarketDataType, NormalizedRecord, OHLCV


def _to_market_data_type(value: str) -> MarketDataType:
    try:
        return MarketDataType(value)
    except ValueError as exc:
        raise UnsupportedDataTypeError(f"unsupported data type: {value!r}") from exc


def _to_decimal(value: Any, field_name: str) -> Decimal:
    if isinstance(value, bool):
        raise InvalidNumericValueError(f"{field_name} must not be bool")
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise InvalidNumericValueError(f"{field_name} must be finite")
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        try:
            result = Decimal(value)
        except (InvalidOperation, ValueError) as exc:
            raise InvalidNumericValueError(f"{field_name} is not a valid decimal") from exc
        if not result.is_finite():
            raise InvalidNumericValueError(f"{field_name} must be finite")
        return result
    raise InvalidNumericValueError(f"{field_name} must be Decimal, int or str")


def _require_utc(dt: Any) -> datetime:
    if not isinstance(dt, datetime):
        raise InvalidTimestampError("timestamp must be a datetime")
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise InvalidTimestampError("timestamp must be timezone-aware")
    return dt.astimezone(timezone.utc)


class NormalizerEngine:
    def __init__(self, mappings: list[NormalizerMapping]) -> None:
        NormalizerMapping.validate_unique(mappings)
        self._mappings = list(mappings)

    def _resolve_mapping(self, raw: RawRecord) -> NormalizerMapping:
        data_type = _to_market_data_type(raw.type)
        for mapping in self._mappings:
            if mapping.source == raw.source and mapping.provider_symbol == raw.symbol and mapping.data_type == data_type:
                return mapping
        raise UnknownAssetError(f"no mapping for source={raw.source!r}, symbol={raw.symbol!r}, type={raw.type!r}")

    def _get_field(self, payload: dict[str, Any], mapping: NormalizerMapping, target: str) -> Any:
        source_field = mapping.field_map.get(target)
        if source_field is None:
            raise MissingFieldError(f"missing field mapping for {target!r}")
        if source_field not in payload:
            raise MissingFieldError(f"missing payload field {source_field!r}")
        return payload[source_field]

    def normalize(self, raw: RawRecord) -> NormalizedRecord:
        if not isinstance(raw, RawRecord):
            raise TypeError("raw must be a RawRecord")
        mapping = self._resolve_mapping(raw)
        payload = raw.payload
        ts_event = _require_utc(raw.ts_event)

        kwargs: dict[str, Any] = {
            "source": raw.source,
            "canonical_asset_id": mapping.canonical_asset_id,
            "canonical_symbol": mapping.canonical_symbol,
            "data_type": mapping.data_type,
            "ts_event": ts_event,
            "idempotency_key": raw.idempotency_key,
            "completeness": raw.completeness,
            "trace_id": raw.trace_id,
        }

        if mapping.data_type == MarketDataType.OHLCV:
            open_v = _to_decimal(self._get_field(payload, mapping, "open"), "open")
            high_v = _to_decimal(self._get_field(payload, mapping, "high"), "high")
            low_v = _to_decimal(self._get_field(payload, mapping, "low"), "low")
            close_v = _to_decimal(self._get_field(payload, mapping, "close"), "close")
            volume_v = _to_decimal(self._get_field(payload, mapping, "volume"), "volume")
            interval_raw = self._get_field(payload, mapping, "interval")
            if not isinstance(interval_raw, str) or not interval_raw.strip():
                raise MissingFieldError("interval must be a non-empty string")
            kwargs["ohlcv"] = OHLCV(open=open_v, high=high_v, low=low_v, close=close_v, volume=volume_v, interval=interval_raw)
        else:
            if "price" in mapping.field_map:
                kwargs["price"] = _to_decimal(self._get_field(payload, mapping, "price"), "price")
            if "quantity" in mapping.field_map:
                kwargs["quantity"] = _to_decimal(self._get_field(payload, mapping, "quantity"), "quantity")
            if "bid" in mapping.field_map:
                kwargs["bid"] = _to_decimal(self._get_field(payload, mapping, "bid"), "bid")
            if "ask" in mapping.field_map:
                kwargs["ask"] = _to_decimal(self._get_field(payload, mapping, "ask"), "ask")
            if "side" in mapping.field_map:
                side_val = self._get_field(payload, mapping, "side")
                if not isinstance(side_val, str):
                    raise MissingFieldError("side must be a string")
                kwargs["side"] = side_val

        return NormalizedRecord(**kwargs)
