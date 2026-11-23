"""Connector protocols."""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol, runtime_checkable
from uuid import UUID

from connectors.types import RawRecord, StreamMessage, Subscription


@dataclass
class HistoricalRequest:
    source_id: UUID
    symbol: str
    start: datetime
    end: datetime
    limit: int | None = None


@dataclass
class LatestRequest:
    source_id: UUID
    symbol: str
    limit: int | None = None


@dataclass
class StreamRequest:
    source_id: UUID
    channels: Sequence[Subscription]


@runtime_checkable
class HistoricalFetcher(Protocol):
    def fetch_historical(self, req: HistoricalRequest) -> AsyncIterator[RawRecord]: ...


@runtime_checkable
class LatestFetcher(Protocol):
    def fetch_latest(self, req: LatestRequest) -> AsyncIterator[RawRecord]: ...


@runtime_checkable
class StreamProvider(Protocol):
    def stream(self, req: StreamRequest) -> AsyncIterator[StreamMessage]: ...
    async def subscribe(self, channels: Sequence[Subscription]) -> None: ...
    async def unsubscribe(self, channels: Sequence[Subscription]) -> None: ...


@runtime_checkable
class CredentialProvider(Protocol):
    async def auth_headers(self, method: str, path: str, body: bytes) -> dict[str, str]: ...
    async def sign(self, payload: bytes) -> bytes: ...
    def lease(self) -> Any: ...
