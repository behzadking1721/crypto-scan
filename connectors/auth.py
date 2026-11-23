"""Authentication abstractions."""

from __future__ import annotations

from enum import Enum


class AuthMode(str, Enum):
    VAULT_SIGNING = "vault_signing"
    LEASE = "lease"
