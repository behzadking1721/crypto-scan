"""Credential security foundation."""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncIterator
from uuid import UUID

from connectors.protocols import CredentialProvider


@dataclass(frozen=True)
class CredentialMetadata:
    credential_version: str
    encryption_key_version: str
    status: str = "active"
    last4_hint: str | None = None


@dataclass
class CredentialBundle:
    api_key: str = ""
    api_secret: str = ""
    passphrase: str = ""

    def __repr__(self) -> str:
        return "CredentialBundle([REDACTED])"

    def __str__(self) -> str:
        return "CredentialBundle([REDACTED])"


class CredentialLease:
    def __init__(self, bundle: CredentialBundle) -> None:
        self._bundle = bundle

    async def __aenter__(self) -> CredentialBundle:
        return self._bundle

    async def __aexit__(self, *exc: Any) -> None:
        return None


class CredentialVault:
    def __init__(self) -> None:
        self._providers: dict[UUID, CredentialProvider] = {}

    def register(self, source_id: UUID, provider: CredentialProvider) -> None:
        self._providers[source_id] = provider

    def provider_for(self, source_id: UUID) -> CredentialProvider:
        return self._providers[source_id]
