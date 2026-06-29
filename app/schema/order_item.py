from pydantic import BaseModel, ConfigDict


class OrderItemCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    order_id: int
    product_id: int
    quantity: int
    unit_price: float


class OrderItem(OrderItemCreate):
    order_item_id: int
