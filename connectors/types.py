"""Shared connector types."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

__all__ = [
    "Completeness",
    "HealthState",
    "ConnectorState",
    "RawRecord",
    "StreamMeta",
    "StreamMessage",
    "HealthStatus",
    "ConnectorStatus",
    "ConnectContext",
    "Capabilities",
    "Timeouts",
    "Subscription",
]


class Completeness(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class HealthState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ConnectorState(str, Enum):
    CONNECTED = "connected"
    DEGRADED = "degraded"
    ERROR = "error"
    DISCONNECTED = "disconnected"


def _require_utc(dt: datetime, name: str) -> datetime:
    if not isinstance(dt, datetime):
        raise TypeError(f"{name} must be a datetime")
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"{name} must be UTC-aware")
    return dt.astimezone(timezone.utc)


@dataclass(frozen=True)
class Capabilities:
    rest: bool = False
    historical: bool = False
    latest: bool = False
    stream: bool = False
    subscribe: bool = False


@dataclass(frozen=True)
class Timeouts:
    connect_timeout: float = 10.0
    read_timeout: float = 30.0
    ws_timeout: float = 30.0

    def __post_init__(self) -> None:
        for field_name in ("connect_timeout", "read_timeout", "ws_timeout"):
            value = getattr(self, field_name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{field_name} must be a number")
            if value <= 0:
                raise ValueError(f"{field_name} must be > 0")


@dataclass(frozen=True)
class Subscription:
    channel: str
    symbol: str | None = None
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.channel, str) or not self.channel.strip():
            raise ValueError("channel must be a non-empty string")
        if self.symbol is not None and not isinstance(self.symbol, str):
            raise TypeError("symbol must be str or None")
        if not isinstance(self.params, dict):
            raise TypeError("params must be a dict")


@dataclass(frozen=True)
class RawRecord:
    source: str
    symbol: str
    type: str
    ts_event: datetime
    payload: dict[str, Any]
    idempotency_key: str
    completeness: Completeness = Completeness.UNKNOWN
    trace_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be a non-empty string")
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError("symbol must be a non-empty string")
        if not isinstance(self.type, str) or not self.type.strip():
            raise ValueError("type must be a non-empty string")
        if not isinstance(self.payload, dict):
            raise TypeError("payload must be a dict")
        if not isinstance(self.idempotency_key, str) or not self.idempotency_key.strip():
            raise ValueError("idempotency_key must be a non-empty string")
        if not isinstance(self.completeness, Completeness):
            raise TypeError("completeness must be a Completeness")
        if self.trace_id is not None and not isinstance(self.trace_id, str):
            raise TypeError("trace_id must be str or None")
        object.__setattr__(self, "ts_event", _require_utc(self.ts_event, "ts_event"))


@dataclass(frozen=True)
class StreamMeta:
    channel: str
    seq: int | None = None
    ts_event: datetime | None = None
    completeness: Completeness = Completeness.UNKNOWN
    heartbeat: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.channel, str) or not self.channel.strip():
            raise ValueError("channel must be a non-empty string")
        if self.seq is not None and (not isinstance(self.seq, int) or isinstance(self.seq, bool)):
            raise TypeError("seq must be int or None")
        if self.seq is not None and self.seq < 0:
            raise ValueError("seq must be >= 0")
        if self.ts_event is not None:
            object.__setattr__(self, "ts_event", _require_utc(self.ts_event, "ts_event"))
        if not isinstance(self.completeness, Completeness):
            raise TypeError("completeness must be a Completeness")
        if not isinstance(self.heartbeat, bool):
            raise TypeError("heartbeat must be bool")


@dataclass(frozen=True)
class StreamMessage:
    record: RawRecord
    stream_meta: StreamMeta

    def __post_init__(self) -> None:
        if not isinstance(self.record, RawRecord):
            raise TypeError("record must be a RawRecord")
        if not isinstance(self.stream_meta, StreamMeta):
            raise TypeError("stream_meta must be a StreamMeta")


@dataclass(frozen=True)
class HealthStatus:
    state: HealthState
    checked_at: datetime
    latency_ms: int | None = None
    consecutive_failures: int = 0
    message: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.state, HealthState):
            raise TypeError("state must be a HealthState")
        object.__setattr__(self, "checked_at", _require_utc(self.checked_at, "checked_at"))
        if self.latency_ms is not None:
            if not isinstance(self.latency_ms, int) or isinstance(self.latency_ms, bool) or self.latency_ms < 0:
                raise ValueError("latency_ms must be a non-negative int or None")
        if not isinstance(self.consecutive_failures, int) or isinstance(self.consecutive_failures, bool) or self.consecutive_failures < 0:
            raise ValueError("consecutive_failures must be a non-negative int")
        if self.message is not None and not isinstance(self.message, str):
            raise TypeError("message must be str or None")


@dataclass(frozen=True)
class ConnectorStatus:
    state: ConnectorState
    updated_at: datetime
    last_heartbeat: datetime | None = None
    last_success_at: datetime | None = None
    last_error_code: str | None = None
    latency_ms: int | None = None
    consecutive_failures: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.state, ConnectorState):
            raise TypeError("state must be a ConnectorState")
        object.__setattr__(self, "updated_at", _require_utc(self.updated_at, "updated_at"))
        if self.last_heartbeat is not None:
            object.__setattr__(self, "last_heartbeat", _require_utc(self.last_heartbeat, "last_heartbeat"))
        if self.last_success_at is not None:
            object.__setattr__(self, "last_success_at", _require_utc(self.last_success_at, "last_success_at"))
        if self.last_error_code is not None and not isinstance(self.last_error_code, str):
            raise TypeError("last_error_code must be str or None")
        if self.latency_ms is not None:
            if not isinstance(self.latency_ms, int) or isinstance(self.latency_ms, bool) or self.latency_ms < 0:
                raise ValueError("latency_ms must be a non-negative int or None")
        if not isinstance(self.consecutive_failures, int) or isinstance(self.consecutive_failures, bool) or self.consecutive_failures < 0:
            raise ValueError("consecutive_failures must be a non-negative int")


@dataclass(frozen=True)
class ConnectContext:
    source_id: uuid.UUID
    base_url: str
    environment: str
    timeouts: Timeouts

    def __post_init__(self) -> None:
        if not isinstance(self.source_id, uuid.UUID):
            raise TypeError("source_id must be a UUID")
        if not isinstance(self.base_url, str) or not self.base_url.strip():
            raise ValueError("base_url must be a non-empty string")
        if not isinstance(self.environment, str) or not self.environment.strip():
            raise ValueError("environment must be a non-empty string")
        if not isinstance(self.timeouts, Timeouts):
            raise TypeError("timeouts must be a Timeouts")

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": str(self.source_id),
            "base_url": self.base_url,
            "environment": self.environment,
            "timeouts": {
                "connect_timeout": self.timeouts.connect_timeout,
                "read_timeout": self.timeouts.read_timeout,
                "ws_timeout": self.timeouts.ws_timeout,
            },
        }
