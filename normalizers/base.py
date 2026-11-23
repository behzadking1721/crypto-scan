"""Normalizer base interface."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from normalizers.types import NormalizedRecord


@runtime_checkable
class Normalizer(Protocol):
    def normalize(self, raw: Any) -> NormalizedRecord:
        ...
