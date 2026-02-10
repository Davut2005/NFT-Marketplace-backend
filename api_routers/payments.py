from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.database import get_db

router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)

@router.get("/")
async def get_payments(sort_by: str = "id", order: str = "asc", db: AsyncSession = Depends(get_db)):
    valid_sort_columns = ["id", "amount", "created_at"]
    if sort_by not in valid_sort_columns:
        sort_by = "id"
    if order not in ["asc", "desc"]:
        order = "asc"
        
    query = text(f"SELECT * FROM payments ORDER BY {sort_by} {order}")
    result = await db.execute(query)
    return [dict(row._mapping) for row in result]

@router.get("/{payment_id}")
async def get_payment(payment_id: int, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM payments WHERE id = :payment_id")
    result = await db.execute(query, {"payment_id": payment_id})
    payment = result.fetchone()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return dict(payment._mapping)

@router.post("/")
async def create_payment(payment: dict, db: AsyncSession = Depends(get_db)):
    columns = ", ".join(payment.keys())
    values = ", ".join([f":{key}" for key in payment.keys()])
    query = text(f"INSERT INTO payments ({columns}) VALUES ({values}) RETURNING *")
    try:
        result = await db.execute(query, payment)
        await db.commit()
        new_payment = result.fetchone()
        return dict(new_payment._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{payment_id}")
async def delete_payment(payment_id: int, db: AsyncSession = Depends(get_db)):
    query = text("DELETE FROM payments WHERE id = :payment_id RETURNING id")
    result = await db.execute(query, {"payment_id": payment_id})
    await db.commit()
    deleted_payment = result.fetchone()
    if not deleted_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment deleted", "payment_id": payment_id}
