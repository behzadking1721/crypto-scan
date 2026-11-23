"""Mock REST connector."""

from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator
from uuid import UUID

from connectors.base import BaseConnector
from connectors.protocols import HistoricalFetcher, LatestFetcher, CredentialProvider
from connectors.types import Capabilities, Completeness, ConnectContext, HealthState, HealthStatus, RawRecord, Timeouts, ConnectorState, ConnectorStatus
from connectors.errors import ConnectorError, TransientConnectorError, PermanentConnectorError


class MockRestConnector(BaseConnector, HistoricalFetcher, LatestFetcher):
    capabilities = Capabilities(rest=True, historical=True, latest=True)

    def __init__(self, credentials: CredentialProvider, assets: list[dict[str, Any]] | None = None, delay: float = 0.0, fail_mode: str | None = None) -> None:
        super().__init__(credentials)
        self._assets = assets if assets is not None else [{"id": "bitcoin", "symbol": "BTC", "price": 64000.0}]
        self._delay = delay
        self._fail_mode = fail_mode

    async def _connect(self, ctx: ConnectContext) -> None:
        await asyncio.sleep(self._delay)
        if self._fail_mode == "transient":
            raise TransientConnectorError("transient failure")
        if self._fail_mode == "permanent":
            raise PermanentConnectorError("permanent failure")

    async def _disconnect(self) -> None:
        pass

    async def health_check(self) -> HealthStatus:
        from datetime import datetime, timezone
        return HealthStatus(state=HealthState.HEALTHY, checked_at=datetime.now(timezone.utc))

    async def get_status(self) -> ConnectorStatus:
        from datetime import datetime, timezone
        return ConnectorStatus(state=ConnectorState.CONNECTED, updated_at=datetime.now(timezone.utc))

    def _find_assets(self, req: Any) -> list[dict[str, Any]]:
        if req is None:
            return list(self._assets)
        symbol = getattr(req, "symbol", None)
        if symbol:
            found = [a for a in self._assets if a["symbol"] == symbol]
            if not found:
                raise PermanentConnectorError("asset not found", error_code="not_found")
            return found
        return list(self._assets)

    async def fetch_latest(self, req: Any) -> AsyncIterator[RawRecord]:
        await asyncio.sleep(self._delay)
        if self._fail_mode == "transient":
            raise TransientConnectorError("transient failure")
        if self._fail_mode == "permanent":
            raise PermanentConnectorError("permanent failure")
        assets = self._find_assets(req)
        for a in assets:
            yield RawRecord(source="mock", symbol=a["symbol"], type="latest", ts_event=__import__("datetime").datetime.now(__import__("datetime").timezone.utc), payload={"price": a["price"]}, idempotency_key=f"latest-{a['id']}")

    async def fetch_historical(self, req: Any) -> AsyncIterator[RawRecord]:
        await asyncio.sleep(self._delay)
        if self._fail_mode == "transient":
            raise TransientConnectorError("transient failure")
        if self._fail_mode == "permanent":
            raise PermanentConnectorError("permanent failure")
        assets = self._find_assets(req)
        for a in assets:
            for i in range(3):
                yield RawRecord(source="mock", symbol=a["symbol"], type="historical", ts_event=__import__("datetime").datetime.now(__import__("datetime").timezone.utc), payload={"price": a["price"] + i}, idempotency_key=f"hist-{a['id']}-{i}")
