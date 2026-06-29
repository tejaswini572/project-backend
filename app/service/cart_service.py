from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.schema.order import OrderCreate


async def get_all_orders(db: AsyncSession) -> Sequence[Order]:
    result = await db.execute(select(Order))
    return result.scalars().all()


async def get_order_by_id(db: AsyncSession, order_id: int) -> Order | None:
    result = await db.execute(select(Order).where(Order.order_id == order_id))
    return result.scalars().first()


async def add_order(db: AsyncSession, order: OrderCreate) -> Order:
    new_order = Order(
        customer_id=order.customer_id,
        total_amount=order.total_amount,
        status=order.status
    )
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    return new_order


async def get_or_create_active_order(db: AsyncSession, customer_id: int) -> Order:
    result = await db.execute(
        select(Order).where(Order.customer_id == customer_id, Order.status == "pending")
    )
    existing_order = result.scalars().first()

    if existing_order:
        return existing_order

    new_order = Order(
        customer_id=customer_id,
        total_amount=0,
        status="pending"
    )
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    return new_order


async def update_order(db: AsyncSession, order_id: int, order: OrderCreate) -> Order:
    result = await db.execute(select(Order).where(Order.order_id == order_id))
    existing = result.scalars().first()
    if not existing:
        raise HTTPException(status_code=404, detail="Order not found")
    existing.customer_id = order.customer_id
    existing.total_amount = order.total_amount
    existing.status = order.status
    await db.commit()
    await db.refresh(existing)
    return existing


async def delete_order(db: AsyncSession, order_id: int) -> dict[str, str]:
    result = await db.execute(select(Order).where(Order.order_id == order_id))
    existing = result.scalars().first()
    if not existing:
        raise HTTPException(status_code=404, detail="Order not found")
    await db.delete(existing)
    await db.commit()
    return {"message": "Order deleted successfully"}
