import datetime as _dt
import json
import logging as _stdlib_logging
import time
import uuid
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

SENSITIVE_HEADERS = {
    "authorization",
    "api-key",
    "x-api-key",
    "proxy-authorization",
    "cookie",
    "set-cookie",
}

REQUEST_ID_HEADER = "x-request-id"
LOGGER_NAME = "crypto.api"

_RESERVED_LOGRECORD_ATTRS = {
    "name", "msg", "args", "levelname", "levelno", "pathname",
    "filename", "module", "exc_info", "exc_text", "stack_info",
    "lineno", "funcName", "created", "msecs", "relativeCreated",
    "thread", "threadName", "processName", "process",
}


def _is_valid_request_id(value: str | None) -> bool:
    if not value:
        return False
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def _generate_request_id() -> str:
    return str(uuid.uuid4())


from connectors.redaction import redact_mapping, redact_string, redact_value

ALLOWED_EXTRA_FIELDS = {
    "request_id",
    "method",
    "path",
    "process_time_ms",
    "status_code",
    "exception_type",
    "event",
    "level",
    "data_source_id",
    "error_code",
    "http_status",
    "latency_ms",
}

class JsonFormatter(_stdlib_logging.Formatter):
    def format(self, record: _stdlib_logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": _dt.datetime.fromtimestamp(
                record.created, tz=_dt.timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_string(record.getMessage()),
        }
        if record.exc_info:
            log_entry["exception"] = redact_string(self.formatException(record.exc_info))
        for key, value in record.__dict__.items():
            if key in _RESERVED_LOGRECORD_ATTRS:
                continue
            if key not in ALLOWED_EXTRA_FIELDS:
                continue
            if key not in log_entry:
                log_entry[key] = redact_value(value)
        return json.dumps(redact_mapping(log_entry), ensure_ascii=False)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        incoming_id = request.headers.get(REQUEST_ID_HEADER)
        request_id = (
            incoming_id if _is_valid_request_id(incoming_id)
            else _generate_request_id()
        )
        request.state.request_id = request_id

        start_time = time.perf_counter()
        logger = _stdlib_logging.getLogger(LOGGER_NAME)

        try:
            response = await call_next(request)
        except Exception as exc:
            process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                "unhandled_exception",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "process_time_ms": process_time_ms,
                    "exception_type": type(exc).__name__,
                },
            )
            raise

        process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            "http_request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": process_time_ms,
            },
        )
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


def setup_logging(log_level: str = "INFO") -> None:
    logger = _stdlib_logging.getLogger(LOGGER_NAME)
    logger.setLevel(
        getattr(_stdlib_logging, log_level.upper(), _stdlib_logging.INFO)
    )

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    handler = _stdlib_logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False


def get_logger() -> _stdlib_logging.Logger:
    return _stdlib_logging.getLogger(LOGGER_NAME)
