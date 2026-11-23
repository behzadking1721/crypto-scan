"""Base connector ABC."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from connectors.auth import AuthMode
from typing import Any

from connectors.protocols import CredentialProvider
from connectors.types import Capabilities, ConnectContext, ConnectorState, ConnectorStatus, HealthStatus


class BaseConnector(ABC):
    capabilities: Capabilities = Capabilities()
    auth_mode: AuthMode = AuthMode.VAULT_SIGNING

    def __init__(self, credentials: CredentialProvider) -> None:
        self._credentials = credentials
        self._connected = False
        self._state = ConnectorState.DISCONNECTED
        self._lifecycle_lock = asyncio.Lock()

    @property
    def credentials(self) -> CredentialProvider:
        return self._credentials

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def state(self) -> ConnectorState:
        return self._state

    async def connect(self, ctx: ConnectContext) -> None:
        async with self._lifecycle_lock:
            if self._connected:
                return
            try:
                await self._connect(ctx)
            except BaseException as exc:
                self._state = ConnectorState.ERROR
                self._connected = False
                try:
                    await self._disconnect()
                except asyncio.CancelledError as cleanup_cancelled:
                    raise cleanup_cancelled from exc
                except Exception:
                    pass
                raise exc
            self._connected = True
            self._state = ConnectorState.CONNECTED

    async def disconnect(self) -> None:
        async with self._lifecycle_lock:
            if not self._connected:
                self._state = ConnectorState.DISCONNECTED
                return
            try:
                await self._disconnect()
            except BaseException as exc:
                self._state = ConnectorState.ERROR
                raise
            self._connected = False
            self._state = ConnectorState.DISCONNECTED

    @abstractmethod
    async def _connect(self, ctx: ConnectContext) -> None:
        ...

    @abstractmethod
    async def _disconnect(self) -> None:
        ...

    @abstractmethod
    async def health_check(self) -> HealthStatus:
        ...

    @abstractmethod
    async def get_status(self) -> ConnectorStatus:
        ...

    async def reconnect(self) -> None:
        raise NotImplementedError

    async def heartbeat(self) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{type(self).__name__}(state={self._state.value!r}, connected={self._connected!r})"
