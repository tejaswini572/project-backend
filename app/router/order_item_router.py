from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schema.order_item import OrderItem as OrderItemSchema
from app.schema.order_item import OrderItemCreate
from app.service import order_item_service

router = APIRouter(prefix="/api/order_item", tags=["order_item"])


@router.post("/")
async def add_order_item(
    order_item: OrderItemCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JSONResponse:
    result = await order_item_service.add_order_item(db, order_item)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=OrderItemSchema.model_validate(result).model_dump(),
    )


@router.get("/order/{order_id}")
async def get_items_by_order(order_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> JSONResponse:
    result = await order_item_service.get_items_by_order(db, order_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[OrderItemSchema.model_validate(i).model_dump() for i in result],
    )


@router.put("/{order_item_id}")
async def update_order_item(
    order_item_id: int,
    order_item: OrderItemCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JSONResponse:
    result = await order_item_service.update_order_item(db, order_item_id, order_item)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=OrderItemSchema.model_validate(result).model_dump(),
    )


@router.delete("/{order_item_id}")
async def delete_order_item(order_item_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> JSONResponse:
    result = await order_item_service.delete_order_item(db, order_item_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
