"""Centralized redaction utilities."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit

SENSITIVE_KEYS = {
    "authorization",
    "api-key",
    "x-api-key",
    "proxy-authorization",
    "cookie",
    "set-cookie",
    "token",
    "access_token",
    "refresh_token",
    "password",
    "secret",
    "api_secret",
    "passphrase",
}

_SENSITIVE_QUERY_KEYS = {"token", "access_token", "refresh_token", "api_key", "password", "secret"}

_SECRET_PATTERNS = [
    re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|authorization)\s*[:=]\s*([^\s,;]+)"),
    re.compile(r"(?i)bearer\s+([A-Za-z0-9._\-]+)"),
]


def _is_sensitive_key(key: Any) -> bool:
    if not isinstance(key, str):
        return False
    normalized = key.lower().replace("_", "-")
    return (
        normalized in SENSITIVE_KEYS
        or "secret" in normalized
        or "token" in normalized
        or "password" in normalized
        or "passwd" in normalized
    )


def redact_string(value: str) -> str:
    result = value
    # URL credentials
    try:
        parts = urlsplit(result)
        if parts.username or parts.password:
            netloc = parts.hostname or ""
            if parts.port:
                netloc = f"{netloc}:{parts.port}"
            parts = parts._replace(netloc=netloc)
            result = urlunsplit(parts)
    except Exception:
        pass
    # query params
    try:
        parts = urlsplit(result)
        if parts.query:
            pairs = []
            for pair in parts.query.split("&"):
                if "=" in pair:
                    k, _ = pair.split("=", 1)
                    if k.lower() in _SENSITIVE_QUERY_KEYS:
                        pairs.append(f"{k}=[REDACTED]")
                    else:
                        pairs.append(pair)
                else:
                    pairs.append(pair)
            result = urlunsplit(parts._replace(query="&".join(pairs)))
    except Exception:
        pass
    # URL credentials embedded in arbitrary text
    result = re.sub(r"(?i)(https?://)[^/\s:@]+:[^/\s@]+@", r"\1[REDACTED]@", result)
    for pattern in _SECRET_PATTERNS:
        result = pattern.sub(lambda m: f"{m.group(1)}=[REDACTED]", result)
    return result


def redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        return redact_mapping(value)
    if isinstance(value, list):
        return [redact_value(v) for v in value]
    if isinstance(value, tuple):
        return tuple(redact_value(v) for v in value)
    if isinstance(value, str):
        return redact_string(value)
    return value


def redact_mapping(data: dict[Any, Any]) -> dict[Any, Any]:
    result: dict[Any, Any] = {}
    for key, value in data.items():
        if _is_sensitive_key(key):
            result[key] = "[REDACTED]"
        else:
            result[key] = redact_value(value)
    return result
