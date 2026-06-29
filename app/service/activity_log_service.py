from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityAction, ActivityLog


async def log_activity(
        db: AsyncSession,
        user_email: str,
        action: ActivityAction,
        details: str | None = None,
) -> None:
    log_entry = ActivityLog(
        user_email=user_email,
        action=action,
        details=details,
        timestamp=datetime.utcnow()
    )
    db.add(log_entry)
