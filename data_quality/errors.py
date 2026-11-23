"""Data quality errors."""

from __future__ import annotations


class DataQualityError(Exception):
    pass


class InvalidConfigError(DataQualityError, ValueError):
    pass


class InvalidNormalizedRecordError(DataQualityError, ValueError):
    pass


class InvalidReferenceError(DataQualityError, ValueError):
    pass


class InvalidQualityIssueError(DataQualityError, ValueError):
    pass
