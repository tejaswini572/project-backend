from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.activity_log import ActivityLog
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/activity-log")
async def get_activity_log(
    db: Annotated[AsyncSession, Depends(get_db)],
    _admin: Annotated[User, Depends(require_admin)],
) -> JSONResponse:
    result = await db.execute(select(ActivityLog).order_by(ActivityLog.timestamp.desc()))
    logs = result.scalars().all()
    return JSONResponse(
        status_code=200,
        content=[
            {
                "log_id": log.log_id,
                "user_email": log.user_email,
                "action": log.action,
                "details": log.details,
                "timestamp": str(log.timestamp),
            }
            for log in logs
        ],
    )
