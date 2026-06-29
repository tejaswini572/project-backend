from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityAction, ActivityLog


def log_activity(
        db: AsyncSession,
        user_email: str,
        action: ActivityAction,
        details: str | None = None,
) -> None:
    log_entry = ActivityLog(
        user_email=user_email,
        action=action,
        details=details,
        timestamp=datetime.now(UTC)
    )
    db.add(log_entry)
