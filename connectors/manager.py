"""Connector lifecycle manager."""

from __future__ import annotations

from typing import Callable
from uuid import UUID

from connectors.base import BaseConnector
from connectors.errors import ConnectorError
from connectors.protocols import CredentialProvider
from connectors.registry import ConnectorRegistry
from connectors.types import ConnectContext, ConnectorStatus, HealthStatus


class ConnectorManager:
    """Manage connector lifecycle within a single event loop and thread.

    Registry and Manager operations are not thread-safe and are not safe
    across multiple event loops. Connector lifecycle transitions are
    serialized by BaseConnector's asyncio.Lock.
    """

    def __init__(self, registry: ConnectorRegistry | None = None) -> None:
        self.registry = registry or ConnectorRegistry()

    def register(self, source_id: UUID, factory: Callable[[CredentialProvider], BaseConnector], credentials: CredentialProvider) -> BaseConnector:
        connector = factory(credentials)
        self.registry.register(source_id, connector)
        return connector

    def get(self, source_id: UUID) -> BaseConnector:
        return self.registry.get(source_id)

    def require_capability(self, source_id: UUID, name: str) -> None:
        connector = self.get(source_id)
        if not getattr(connector.capabilities, name, False):
            raise ConnectorError(f"capability '{name}' not supported", error_code="capability_not_supported")

    async def connect(self, source_id: UUID, ctx: ConnectContext) -> None:
        self.get(source_id)
        await self.get(source_id).connect(ctx)

    async def disconnect(self, source_id: UUID) -> None:
        self.get(source_id)
        await self.get(source_id).disconnect()

    async def health_check(self, source_id: UUID) -> HealthStatus:
        return await self.get(source_id).health_check()

    async def get_status(self, source_id: UUID) -> ConnectorStatus:
        return await self.get(source_id).get_status()
