from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class Order(Base):
    __tablename__ = "order"
    order_id: Mapped[int] = mapped_column(index=True, autoincrement=True, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.customer_id"))
    order_date: Mapped[datetime] = mapped_column(server_default=func.now())
    total_amount: Mapped[float]
    status: Mapped[str]
