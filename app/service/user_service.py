from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.schema.customer import CustomerCreate


async def get_all_users(db: AsyncSession) -> Sequence[Customer]:
    result = await db.execute(select(Customer))
    return result.scalars().all()


async def get_user_by_id(db: AsyncSession, customer_id: int) -> Customer | None:
    result = await db.execute(select(Customer).where(Customer.customer_id == customer_id))
    return result.scalars().first()


async def add_user(db: AsyncSession, customer: CustomerCreate) -> Customer:
    new_user = Customer(
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        phone=customer.phone
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_user(db: AsyncSession, customer_id: int, customer: CustomerCreate) -> Customer:
    result = await db.execute(select(Customer).where(Customer.customer_id == customer_id))
    existing = result.scalars().first()
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    existing.first_name = customer.first_name
    existing.last_name = customer.last_name
    existing.email = customer.email
    existing.phone = customer.phone
    await db.commit()
    await db.refresh(existing)
    return existing


async def delete_user(db: AsyncSession, customer_id: int) -> dict[str, str]:
    result = await db.execute(select(Customer).where(Customer.customer_id == customer_id))
    existing = result.scalars().first()
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(existing)
    await db.commit()
    return {"message": "User deleted successfully"}
