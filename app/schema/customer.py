from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer


class CustomerCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    first_name: str
    last_name: str
    email: str
    phone: str


class Customer(CustomerCreate):
    customer_id: int
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str | None:
        return value.isoformat() if value else None
