"""Normalizer errors."""

from __future__ import annotations


class NormalizationError(Exception):
    """Base normalizer error."""


class UnsupportedDataTypeError(NormalizationError, ValueError):
    pass


class UnknownAssetError(NormalizationError, ValueError):
    pass


class MissingFieldError(NormalizationError, ValueError):
    pass


class InvalidNumericValueError(NormalizationError, ValueError):
    pass


class InvalidTimestampError(NormalizationError, ValueError):
    pass


class InvalidMappingError(NormalizationError, ValueError):
    pass
