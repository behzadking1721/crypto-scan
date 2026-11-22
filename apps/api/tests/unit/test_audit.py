import pytest
from unittest.mock import patch
from datetime import datetime, timezone

import audit
from audit import audit as audit_func
from models import AuditLog


class FakeSession:
    def __init__(self, should_fail=False):
        self._should_fail = should_fail
        self.added = None
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def add(self, obj):
        self.added = obj

    async def commit(self):
        self.committed = True
        if self._should_fail:
            raise Exception("DB write failed")


async def _make_async_gen(session):
    yield session


@pytest.mark.asyncio
async def test_audit_creates_record_dict():
    with patch.object(audit, "get_session") as mock_get_session:
        mock_get_session.return_value = _make_async_gen(FakeSession())
        result = await audit_func("test_event", actor="user1", detail="test detail")

    assert result["event"] == "test_event"
    assert result["actor"] == "user1"
    assert result["detail"] == "test detail"
    assert "timestamp" in result


@pytest.mark.asyncio
async def test_audit_persists_to_database():
    with patch.object(audit, "get_session") as mock_get_session:
        session = FakeSession()
        mock_get_session.return_value = _make_async_gen(session)

        await audit_func("health_check", actor="system", detail="health check")

    assert session.added is not None
    assert isinstance(session.added, AuditLog)
    assert session.added.event_type == "health_check"
    assert session.added.actor == "system"
    assert session.added.detail == "health check"
    assert session.committed is True


@pytest.mark.asyncio
async def test_audit_db_write_failure_logged_and_does_not_crash():
    with patch.object(audit, "get_session") as mock_get_session:
        mock_get_session.return_value = _make_async_gen(FakeSession(should_fail=True))

        result = await audit_func("test_event")

    assert result["event"] == "test_event"


@pytest.mark.asyncio
async def test_audit_no_sensitive_data_in_model():
    log = AuditLog(
        event_type="login",
        actor="user1",
        timestamp=datetime.now(timezone.utc),
        detail="user logged in",
    )
    assert not hasattr(log, "password")
    assert not hasattr(log, "api_key")
    assert not hasattr(log, "token")
    assert not hasattr(log, "request_body")
    assert not hasattr(log, "authorization_header")


@pytest.mark.asyncio
async def test_audit_default_actor_and_detail_none():
    with patch.object(audit, "get_session") as mock_get_session:
        session = FakeSession()
        mock_get_session.return_value = _make_async_gen(session)

        result = await audit_func("bare_event")

    assert result["actor"] is None
    assert result["detail"] is None
    assert session.added.actor is None
    assert session.added.detail is None
