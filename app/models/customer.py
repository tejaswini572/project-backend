from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class Customer(Base):
    __tablename__ = "customer"
    customer_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(index=True, unique=True)
    phone: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
