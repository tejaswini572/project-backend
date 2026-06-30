from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityAction
from app.models.product import Product
from app.schema.product import ProductCreate
from app.service.activity_log_service import log_activity


async def get_all_product(db: AsyncSession) -> Sequence[Product]:
    result = await db.execute(select(Product))
    return result.scalars().all()


async def get_product_by_id(db: AsyncSession, product_id: int) -> Product | None:
    result = await db.execute(select(Product).where(Product.product_id == product_id))
    return result.scalars().first()


async def add_product(db: AsyncSession, product: ProductCreate, user_email: str) -> Product:
    new_product = Product(
        product_name=product.product_name,
        category=product.category,
        price=product.price,
        stock_quantity=product.stock_quantity,
    )
    db.add(new_product)
    log_activity(db, user_email, ActivityAction.ADD_PRODUCT)
    await db.commit()
    await db.refresh(new_product)

    return new_product


async def update_product(
        db: AsyncSession,
        product_id: int,
        product: ProductCreate,
        user_email: str,
) -> Product:
    result = await db.execute(
        select(Product).where(Product.product_id == product_id)
    )
    existing = result.scalars().first()
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    existing.product_name = product.product_name
    existing.category = product.category
    existing.price = product.price
    existing.stock_quantity = product.stock_quantity
    log_activity(db, user_email, ActivityAction.UPDATE_PRODUCT)
    await db.commit()
    await db.refresh(existing)

    return existing


async def delete_product(db: AsyncSession, product_id: int, user_email: str) -> dict[str, str]:
    result = await db.execute(select(Product).where(Product.product_id == product_id))
    existing = result.scalars().first()
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    log_activity(db, user_email, ActivityAction.DELETE_PRODUCT)
    await db.delete(existing)
    await db.commit()

    return {"message": "Product deleted successfully"}
