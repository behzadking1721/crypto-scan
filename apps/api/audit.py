from datetime import datetime, timezone
from uuid import uuid4

from database import get_session
from logger import get_logger
from models import AuditLog

logger = get_logger()


async def audit(event: str, actor: str | None = None, detail: str | None = None) -> dict:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "actor": actor,
        "detail": detail,
    }

    try:
        async for session in get_session():
            session.add(
                AuditLog(
                    id=uuid4(),
                    event_type=event,
                    actor=actor,
                    timestamp=datetime.now(timezone.utc),
                    detail=detail,
                )
            )
            await session.commit()
    except Exception as exc:
        logger.error(
            "audit_persistence_failed",
            extra={"exception_type": type(exc).__name__, "event": event},
        )

    return record
