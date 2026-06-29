from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class ActivityAction(StrEnum):
    LOGIN = "login"
    ADD_PRODUCT = "add_product"
    UPDATE_PRODUCT = "update_product"
    DELETE_PRODUCT = "delete_product"


class ActivityLog(Base):
    __tablename__ = "activity_log"

    log_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    user_email: Mapped[str]
    action: Mapped[str]
    details: Mapped[str | None] = mapped_column(nullable=True)
    timestamp: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
