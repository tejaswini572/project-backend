from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.order_item import OrderItem
from app.schema.order_item import OrderItemCreate


async def add_order_item(db: AsyncSession, order_item: OrderItemCreate) -> OrderItem:
    new_item = OrderItem(
        order_id=order_item.order_id,
        product_id=order_item.product_id,
        quantity=order_item.quantity,
        unit_price=order_item.unit_price
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    await recalculate_order_total(db, new_item.order_id)
    await db.refresh(new_item)
    return new_item


async def get_items_by_order(db: AsyncSession, order_id: int) -> Sequence[OrderItem]:
    result = await db.execute(select(OrderItem).where(OrderItem.order_id == order_id))
    return result.scalars().all()


async def update_order_item(db: AsyncSession, order_item_id: int, order_item: OrderItemCreate) -> OrderItem:
    result = await db.execute(select(OrderItem).where(OrderItem.order_item_id == order_item_id))
    existing = result.scalars().first()
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")
    existing.order_id = order_item.order_id
    existing.product_id = order_item.product_id
    existing.quantity = order_item.quantity
    existing.unit_price = order_item.unit_price
    await db.commit()
    await db.refresh(existing)
    await recalculate_order_total(db, existing.order_id)
    await db.refresh(existing)
    return existing


async def delete_order_item(db: AsyncSession, order_item_id: int) -> dict[str, str]:
    result = await db.execute(select(OrderItem).where(OrderItem.order_item_id == order_item_id))
    existing = result.scalars().first()
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")
    order_id = existing.order_id
    await db.delete(existing)
    await db.commit()
    await recalculate_order_total(db, order_id)
    return {"message": "Order item deleted successfully"}


async def recalculate_order_total(db: AsyncSession, order_id: int) -> None:
    result = await db.execute(select(OrderItem).where(OrderItem.order_id == order_id))
    items = result.scalars().all()

    total = sum(item.quantity * item.unit_price for item in items)

    order_result = await db.execute(select(Order).where(Order.order_id == order_id))
    order = order_result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.total_amount = total

    await db.commit()
