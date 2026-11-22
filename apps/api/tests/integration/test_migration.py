import asyncio

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text

import database

pytestmark = pytest.mark.integration

ALEMBIC_CFG = Config("alembic.ini")


def _clear_all_caches():
    database.get_engine.cache_clear()
    database.get_sessionmaker.cache_clear()


def _check_table_exists() -> bool:
    engine = database.get_engine()

    async def _check():
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT to_regclass(:table_name)"),
                {"table_name": "audit_logs"},
            )
            return result.scalar() is not None

    return asyncio.run(_check())


def _dispose():
    asyncio.run(database.dispose_engine())


def test_migration_upgrade_creates_audit_logs_table():
    _clear_all_caches()

    command.upgrade(ALEMBIC_CFG, "head")

    assert _check_table_exists() is True

    _dispose()


def test_migration_downgrade_removes_audit_logs_table():
    _clear_all_caches()

    command.upgrade(ALEMBIC_CFG, "head")
    command.downgrade(ALEMBIC_CFG, "-1")

    assert _check_table_exists() is False

    _dispose()


def test_migration_upgrade_idempotent():
    _clear_all_caches()

    command.upgrade(ALEMBIC_CFG, "head")
    command.upgrade(ALEMBIC_CFG, "head")

    assert _check_table_exists() is True

    _dispose()
