"""Connector error hierarchy."""

from __future__ import annotations

__all__ = [
    "ConnectorError",
    "TransientConnectorError",
    "PermanentConnectorError",
    "AuthError",
    "RateLimitError",
    "IncompleteDataError",
]


class ConnectorError(Exception):
    def __init__(
        self,
        message: str = "connector error",
        *,
        error_code: str | None = None,
        http_status: int | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.http_status = http_status

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(message={self.args[0]!r}, "
            f"error_code={self.error_code!r}, http_status={self.http_status!r})"
        )

    def __str__(self) -> str:
        return self.args[0] if self.args else type(self).__name__


class TransientConnectorError(ConnectorError):
    pass


class PermanentConnectorError(ConnectorError):
    pass


class AuthError(PermanentConnectorError):
    pass


class RateLimitError(TransientConnectorError):
    def __init__(
        self,
        message: str = "rate limited",
        *,
        retry_after: float | None = None,
        error_code: str | None = "rate_limited",
        http_status: int | None = 429,
    ) -> None:
        super().__init__(message, error_code=error_code, http_status=http_status)
        if retry_after is not None:
            if not isinstance(retry_after, (int, float)) or isinstance(retry_after, bool):
                raise TypeError("retry_after must be a number or None")
            if retry_after < 0:
                raise ValueError("retry_after must be >= 0")
        self.retry_after = float(retry_after) if retry_after is not None else None

    def __repr__(self) -> str:
        return (
            f"RateLimitError(message={self.args[0]!r}, retry_after={self.retry_after!r}, "
            f"error_code={self.error_code!r}, http_status={self.http_status!r})"
        )


class IncompleteDataError(ConnectorError):
    pass
