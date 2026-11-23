"""Mock streaming connector."""

from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Sequence
from uuid import UUID

from connectors.base import BaseConnector
from connectors.protocols import StreamProvider, CredentialProvider
from connectors.types import Capabilities, ConnectContext, RawRecord, StreamMessage, StreamMeta, Subscription, Completeness, HealthState, HealthStatus, ConnectorState, ConnectorStatus
from connectors.errors import ConnectorError, TransientConnectorError, PermanentConnectorError


class MockStreamConnector(BaseConnector, StreamProvider):
    capabilities = Capabilities(rest=True, stream=True, subscribe=True)

    def __init__(self, credentials: CredentialProvider, delay: float = 0.0, fail_mode: str | None = None, count: int = 3) -> None:
        super().__init__(credentials)
        self._delay = delay
        self._fail_mode = fail_mode
        self._count = count
        self._subs: list[Subscription] = []

    async def _connect(self, ctx: ConnectContext) -> None:
        await asyncio.sleep(self._delay)
        if self._fail_mode == "transient":
            raise TransientConnectorError("transient failure")
        if self._fail_mode == "permanent":
            raise PermanentConnectorError("permanent failure")

    async def _disconnect(self) -> None:
        self._subs.clear()

    async def health_check(self) -> HealthStatus:
        from datetime import datetime, timezone
        return HealthStatus(state=HealthState.HEALTHY, checked_at=datetime.now(timezone.utc))

    async def get_status(self) -> ConnectorStatus:
        from datetime import datetime, timezone
        return ConnectorStatus(state=ConnectorState.CONNECTED, updated_at=datetime.now(timezone.utc))

    async def subscribe(self, channels: Sequence[Subscription]) -> None:
        self._subs.extend(channels)

    async def unsubscribe(self, channels: Sequence[Subscription]) -> None:
        for ch in channels:
            self._subs = [s for s in self._subs if s.channel != ch.channel]

    async def stream(self, req: Any) -> AsyncIterator[StreamMessage]:
        for i in range(self._count):
            await asyncio.sleep(self._delay)
            if self._fail_mode == "transient":
                raise TransientConnectorError("transient failure")
            if self._fail_mode == "permanent":
                raise PermanentConnectorError("permanent failure")
            record = RawRecord(source="mock", symbol="BTC", type="stream", ts_event=__import__("datetime").datetime.now(__import__("datetime").timezone.utc), payload={"seq": i}, idempotency_key=f"stream-{i}")
            yield StreamMessage(record=record, stream_meta=StreamMeta(channel="trades", seq=i, heartbeat=False))
        if self._subs:
            await asyncio.sleep(0)
