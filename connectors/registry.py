"""Connector registry."""

from __future__ import annotations

from typing import Callable
from uuid import UUID

from connectors.base import BaseConnector
from connectors.errors import ConnectorError


class ConnectorRegistry:
    """Registry intended for use within a single event loop and thread.

    Synchronous registry operations do not yield control. Registry data
    structures are not thread-safe or multi-event-loop safe.
    """

    def __init__(self) -> None:
        self._connectors: dict[UUID, BaseConnector] = {}

    def register(self, source_id: UUID, connector: BaseConnector) -> None:
        if source_id in self._connectors:
            raise ConnectorError("connector already registered", error_code="duplicate_registration")
        if not isinstance(connector, BaseConnector):
            raise TypeError("connector must be a BaseConnector")
        self._connectors[source_id] = connector

    def get(self, source_id: UUID) -> BaseConnector:
        try:
            return self._connectors[source_id]
        except KeyError as exc:
            raise ConnectorError("connector not found", error_code="not_found") from exc

    def unregister(self, source_id: UUID) -> None:
        self._connectors.pop(source_id, None)

    def list(self) -> list[tuple[UUID, BaseConnector]]:
        return list(self._connectors.items())

    def filter_by_capability(self, predicate: Callable[[object], bool]) -> list[tuple[UUID, BaseConnector]]:
        return [(sid, c) for sid, c in self._connectors.items() if predicate(c.capabilities)]

    def has_capability(self, source_id: UUID, name: str) -> bool:
        connector = self.get(source_id)
        return bool(getattr(connector.capabilities, name, False))
