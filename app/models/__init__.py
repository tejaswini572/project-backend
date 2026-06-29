from sqlalchemy.orm import DeclarativeBase


# Modern approach (SQLAlchemy 2.0+)
class Base(DeclarativeBase):
    pass


# Register the models for Migration
from . import activity_log, customer, order, order_item, product, user  # noqa: E402, F401
