from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class OrderItem(Base):
    __tablename__ = "order_item"
    order_item_id: Mapped[int] = mapped_column(autoincrement=True, index=True, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.order_id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("product.product_id"))
    quantity: Mapped[int]
    unit_price: Mapped[float]
