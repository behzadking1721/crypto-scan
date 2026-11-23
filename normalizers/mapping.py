"""Normalizer mapping."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from normalizers.types import MarketDataType

__all__ = ["FieldMapping", "NormalizerMapping"]


@dataclass(frozen=True)
class FieldMapping:
    source_field: str
    target_field: str
    required: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.source_field, str) or not self.source_field.strip():
            raise ValueError("source_field must be a non-empty string")
        if not isinstance(self.target_field, str) or not self.target_field.strip():
            raise ValueError("target_field must be a non-empty string")


@dataclass(frozen=True)
class NormalizerMapping:
    source: str
    provider_symbol: str
    canonical_asset_id: str
    canonical_symbol: str
    data_type: MarketDataType
    field_map: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be a non-empty string")
        if not isinstance(self.provider_symbol, str) or not self.provider_symbol.strip():
            raise ValueError("provider_symbol must be a non-empty string")
        if not isinstance(self.canonical_asset_id, str) or not self.canonical_asset_id.strip():
            raise ValueError("canonical_asset_id must be a non-empty string")
        if not isinstance(self.canonical_symbol, str) or not self.canonical_symbol.strip():
            raise ValueError("canonical_symbol must be a non-empty string")
        if not isinstance(self.data_type, MarketDataType):
            raise TypeError("data_type must be a MarketDataType")
        if not isinstance(self.field_map, dict):
            raise TypeError("field_map must be a dict")
        for k, v in self.field_map.items():
            if not isinstance(k, str) or not k.strip():
                raise ValueError("field_map keys must be non-empty strings")
            if not isinstance(v, str) or not v.strip():
                raise ValueError("field_map values must be non-empty strings")
        if not self.field_map:
            raise ValueError("field_map must be non-empty")

    @staticmethod
    def validate_unique(mappings: list["NormalizerMapping"]) -> None:
        seen: set[tuple[str, str, MarketDataType]] = set()
        for m in mappings:
            key = (m.source, m.provider_symbol, m.data_type)
            if key in seen:
                raise ValueError("duplicate mapping")
            seen.add(key)
        prov_map: dict[tuple[str, str], set[str]] = {}
        for m in mappings:
            prov_map.setdefault((m.source, m.provider_symbol), set()).add(m.canonical_asset_id)
        for v in prov_map.values():
            if len(v) > 1:
                raise ValueError("ambiguous mapping")
