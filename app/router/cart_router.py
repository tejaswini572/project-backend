from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schema.order import Order as OrderSchema
from app.schema.order import OrderCreate
from app.service import cart_service

router = APIRouter(prefix="/api/carts", tags=["carts"])


@router.get("/")
async def get_all_orders(db: Annotated[AsyncSession, Depends(get_db)]) -> JSONResponse:
    result = await cart_service.get_all_orders(db)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[OrderSchema.model_validate(o).model_dump() for o in result],
    )


@router.get("/active/{customer_id}")
async def get_active_order(customer_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> JSONResponse:
    result = await cart_service.get_or_create_active_order(db, customer_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=OrderSchema.model_validate(result).model_dump(),
    )


@router.get("/{order_id}")
async def get_order_by_id(order_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> JSONResponse:
    result = await cart_service.get_order_by_id(db, order_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=OrderSchema.model_validate(result).model_dump(),
    )


@router.post("/")
async def add_order(order: OrderCreate, db: Annotated[AsyncSession, Depends(get_db)]) -> JSONResponse:
    result = await cart_service.add_order(db, order)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=OrderSchema.model_validate(result).model_dump(),
    )


@router.put("/{order_id}")
async def update_order(
    order_id: int,
    order: OrderCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JSONResponse:
    result = await cart_service.update_order(db, order_id, order)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=OrderSchema.model_validate(result).model_dump(),
    )


@router.delete("/{order_id}")
async def delete_order(order_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> JSONResponse:
    result = await cart_service.delete_order(db, order_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
