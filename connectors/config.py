"""Connector configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from connectors.types import Timeouts


@dataclass
class HttpRetryConfig:
    max_attempts: int = 3
    max_total_wait_seconds: float = 30.0
    base_backoff_seconds: float = 0.5
    backoff_cap_seconds: float = 8.0
    jitter_ratio: float = 0.20

    def __post_init__(self) -> None:
        if not isinstance(self.max_attempts, int) or isinstance(self.max_attempts, bool) or self.max_attempts < 1:
            raise ValueError("max_attempts must be a positive int")
        for name in ("max_total_wait_seconds", "base_backoff_seconds", "backoff_cap_seconds"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive number")
        if not isinstance(self.jitter_ratio, (int, float)) or isinstance(self.jitter_ratio, bool):
            raise ValueError("jitter_ratio must be a number")
        if self.jitter_ratio < 0 or self.jitter_ratio > 1:
            raise ValueError("jitter_ratio must be between 0 and 1")


@dataclass
class RetryProfiles:
    historical: HttpRetryConfig = field(default_factory=HttpRetryConfig)
    realtime: HttpRetryConfig = field(default_factory=HttpRetryConfig)


@dataclass
class WebSocketReconnectConfig:
    base_backoff_seconds: float | None = None
    backoff_cap_seconds: float | None = None
    jitter_ratio: float | None = None
    max_attempts: int | None = None

    def __post_init__(self) -> None:
        for name in ("base_backoff_seconds", "backoff_cap_seconds"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0):
                raise ValueError(f"{name} must be a positive number or None")
        if self.jitter_ratio is not None:
            if not isinstance(self.jitter_ratio, (int, float)) or isinstance(self.jitter_ratio, bool):
                raise ValueError("jitter_ratio must be a number or None")
            if self.jitter_ratio < 0 or self.jitter_ratio > 1:
                raise ValueError("jitter_ratio must be between 0 and 1 or None")
        if self.max_attempts is not None:
            if not isinstance(self.max_attempts, int) or isinstance(self.max_attempts, bool) or self.max_attempts < 1:
                raise ValueError("max_attempts must be a positive int or None")


@dataclass
class WebSocketHeartbeatConfig:
    interval_seconds: float | None = None
    timeout_seconds: float | None = None

    def __post_init__(self) -> None:
        for name in ("interval_seconds", "timeout_seconds"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0):
                raise ValueError(f"{name} must be a positive number or None")


@dataclass
class ConnectorConfig:
    timeouts: Timeouts = field(default_factory=Timeouts)
    retry_profiles: RetryProfiles = field(default_factory=RetryProfiles)
    websocket_reconnect: WebSocketReconnectConfig = field(default_factory=WebSocketReconnectConfig)
    websocket_heartbeat: WebSocketHeartbeatConfig = field(default_factory=WebSocketHeartbeatConfig)
    extra: dict[str, Any] = field(default_factory=dict)
