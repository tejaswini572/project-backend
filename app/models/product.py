from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class Product(Base):
    __tablename__ = "product"
    product_id: Mapped[int] = mapped_column(index=True, primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(unique=True)
    category: Mapped[str] = mapped_column()
    price: Mapped[float]
    stock_quantity: Mapped[int]
