from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer


class OrderCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    customer_id: int
    total_amount: float
    status: str


class Order(OrderCreate):
    order_id: int
    order_date: datetime

    @field_serializer("order_date")
    def serialize_order_date(self, value: datetime) -> str | None:
        return value.isoformat() if value else None
