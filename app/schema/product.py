from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_name: str
    category: str
    price: float
    stock_quantity: int


class Product(ProductCreate):
    product_id: int
