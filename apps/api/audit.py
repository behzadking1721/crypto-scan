from datetime import datetime, timezone


def audit(event: str, actor: str | None = None, detail: str | None = None) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "actor": actor,
        "detail": detail,
    }
