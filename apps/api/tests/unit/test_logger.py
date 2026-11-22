import json
import logging
import uuid
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

import logger
from logger import (
    JsonFormatter,
    REQUEST_ID_HEADER,
    _generate_request_id,
    _is_valid_request_id,
    get_logger,
    setup_logging,
)


class LogCaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)


@pytest.fixture(autouse=True)
def isolate_crypto_logger():
    """Snapshot and restore the shared ``crypto.api`` logger around each test.

    ``migrations/env.py`` calls ``logging.config.fileConfig`` during the
    integration migration tests, which defaults to
    ``disable_existing_loggers=True`` and disables any logger that already
    exists (such as ``crypto.api``). Because the whole suite shares one
    process, that global ``disabled`` flag leaks into these tests and prevents
    log records from ever reaching the capture handler. Re-enabling the logger
    for the test and restoring its full prior state afterwards keeps each test
    isolated without altering production logging behaviour.
    """

    lg = get_logger()
    saved_handlers = lg.handlers[:]
    saved_level = lg.level
    saved_propagate = lg.propagate
    saved_disabled = lg.disabled

    lg.disabled = False
    try:
        yield
    finally:
        lg.handlers[:] = saved_handlers
        lg.setLevel(saved_level)
        lg.propagate = saved_propagate
        lg.disabled = saved_disabled


@pytest.fixture
def capture_handler():
    lg = get_logger()
    for h in lg.handlers[:]:
        lg.removeHandler(h)
    lg.setLevel(logging.DEBUG)
    handler = LogCaptureHandler()
    lg.addHandler(handler)
    handler.records.clear()
    yield handler
    for h in lg.handlers[:]:
        lg.removeHandler(h)


def _formatted_json(record):
    return json.loads(JsonFormatter().format(record))


def test_json_output_valid(capture_handler):
    lg = get_logger()
    lg.info("test message", extra={"request_id": "abc", "method": "GET"})
    record = capture_handler.records[-1]
    parsed = _formatted_json(record)
    assert parsed["message"] == "test message"
    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "crypto.api"
    assert parsed["request_id"] == "abc"
    assert parsed["method"] == "GET"


def test_timestamp_is_utc(capture_handler):
    lg = get_logger()
    lg.info("utc test")
    record = capture_handler.records[-1]
    parsed = _formatted_json(record)
    dt = datetime.fromisoformat(parsed["timestamp"])
    assert dt.tzinfo is not None
    assert dt.utcoffset().total_seconds() == 0


def test_different_log_levels(capture_handler):
    lg = get_logger()
    lg.debug("debug msg")
    lg.info("info msg")
    lg.warning("warning msg")
    lg.error("error msg")
    lg.critical("critical msg")

    levels = [r.levelname for r in capture_handler.records]
    assert "DEBUG" in levels
    assert "INFO" in levels
    assert "WARNING" in levels
    assert "ERROR" in levels
    assert "CRITICAL" in levels


def test_is_valid_request_id():
    assert _is_valid_request_id(str(uuid.uuid4())) is True
    assert _is_valid_request_id("not-a-uuid") is False
    assert _is_valid_request_id("") is False
    assert _is_valid_request_id(None) is False


def test_generate_request_id_is_uuid():
    rid = _generate_request_id()
    parsed = uuid.UUID(rid)
    assert str(parsed) == rid


def test_request_id_in_response_header():
    app = FastAPI()
    app.add_middleware(__import__("logger").LoggingMiddleware)

    @app.get("/test")
    def test_endpoint():
        return {"ok": True}

    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 200
    assert REQUEST_ID_HEADER in response.headers
    assert uuid.UUID(response.headers[REQUEST_ID_HEADER])


def test_incoming_valid_request_id_used():
    app = FastAPI()
    app.add_middleware(__import__("logger").LoggingMiddleware)

    @app.get("/test")
    def test_endpoint(request: Request):
        return {"request_id": request.state.request_id}

    client = TestClient(app)
    valid_id = str(uuid.uuid4())
    response = client.get("/test", headers={"x-request-id": valid_id})
    assert response.headers[REQUEST_ID_HEADER] == valid_id


def test_invalid_incoming_request_id_regenerated():
    app = FastAPI()
    app.add_middleware(__import__("logger").LoggingMiddleware)

    @app.get("/test")
    def test_endpoint(request: Request):
        return {"request_id": request.state.request_id}

    client = TestClient(app)
    response = client.get("/test", headers={"x-request-id": "not-a-uuid"})
    assert response.headers[REQUEST_ID_HEADER] != "not-a-uuid"
    assert uuid.UUID(response.headers[REQUEST_ID_HEADER])


def test_http_request_log_contains_status_and_time(capture_handler):
    app = FastAPI()
    app.add_middleware(__import__("logger").LoggingMiddleware)

    @app.get("/test")
    def test_endpoint():
        return {"ok": True}

    client = TestClient(app)
    client.get("/test")

    http_records = [
        r for r in capture_handler.records if r.getMessage() == "http_request"
    ]
    assert len(http_records) >= 1
    parsed = _formatted_json(http_records[-1])
    assert parsed["status_code"] == 200
    assert "process_time_ms" in parsed
    assert isinstance(parsed["process_time_ms"], (int, float))


def test_no_sensitive_headers_in_logs(capture_handler):
    app = FastAPI()
    app.add_middleware(__import__("logger").LoggingMiddleware)

    @app.get("/test")
    def test_endpoint():
        return {"ok": True}

    client = TestClient(app)
    client.get(
        "/test",
        headers={"authorization": "Bearer secret-token", "x-api-key": "secret-key"},
    )

    for record in capture_handler.records:
        formatted = capture_handler.format(record)
        assert "secret-token" not in formatted
        assert "secret-key" not in formatted


def test_unhandled_exception_logged(capture_handler):
    app = FastAPI()
    app.add_middleware(__import__("logger").LoggingMiddleware)

    @app.get("/crash")
    def crash():
        raise RuntimeError("boom")

    client = TestClient(app)
    with pytest.raises(RuntimeError):
        client.get("/crash")

    error_records = [
        r for r in capture_handler.records if r.getMessage() == "unhandled_exception"
    ]
    assert len(error_records) >= 1
    parsed = _formatted_json(error_records[-1])
    assert parsed["level"] == "ERROR"
    assert "exception_type" in parsed
    assert parsed["exception_type"] == "RuntimeError"
    # sensitive data must not leak into the log message
    formatted = capture_handler.format(error_records[-1])
    assert "boom" not in formatted
    assert "DATABASE_URL" not in formatted
    assert "password" not in formatted.lower()
    assert "token" not in formatted.lower()
    assert "api-key" not in formatted.lower()


def test_no_duplicate_handler_on_setup_logging():
    lg = get_logger()
    setup_logging("INFO")
    setup_logging("INFO")
    assert len(lg.handlers) == 1
    assert isinstance(lg.handlers[0], logging.StreamHandler)


def test_setup_logging_respects_env_level(capture_handler):
    setup_logging("WARNING")
    lg = get_logger()
    assert lg.level == logging.WARNING
