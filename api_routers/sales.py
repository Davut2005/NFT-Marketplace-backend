from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.database import get_db

router = APIRouter(
    prefix="/sales",
    tags=["sales"]
)

@router.get("/")
async def get_sales(sort_by: str = "id", order: str = "asc", db: AsyncSession = Depends(get_db)):
    valid_sort_columns = ["id", "sale_price", "sold_at"]
    if sort_by not in valid_sort_columns:
        sort_by = "id"
    if order not in ["asc", "desc"]:
        order = "asc"
        
    query = text(f"SELECT * FROM sales ORDER BY {sort_by} {order}")
    result = await db.execute(query)
    return [dict(row._mapping) for row in result]

@router.get("/{sale_id}")
async def get_sale(sale_id: int, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM sales WHERE id = :sale_id")
    result = await db.execute(query, {"sale_id": sale_id})
    sale = result.fetchone()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return dict(sale._mapping)

@router.post("/")
async def create_sale(sale: dict, db: AsyncSession = Depends(get_db)):
    columns = ", ".join(sale.keys())
    values = ", ".join([f":{key}" for key in sale.keys()])
    query = text(f"INSERT INTO sales ({columns}) VALUES ({values}) RETURNING *")
    try:
        result = await db.execute(query, sale)
        await db.commit()
        new_sale = result.fetchone()
        return dict(new_sale._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{sale_id}")
async def update_sale(sale_id: int, sale: dict, db: AsyncSession = Depends(get_db)):
    set_clause = ", ".join([f"{key} = :{key}" for key in sale.keys()])
    query = text(f"UPDATE sales SET {set_clause} WHERE id = :sale_id RETURNING *")
    try:
        result = await db.execute(query, {**sale, "sale_id": sale_id})
        await db.commit()
        updated_sale = result.fetchone()
        if not updated_sale:
            raise HTTPException(status_code=404, detail="Sale not found")
        return dict(updated_sale._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{sale_id}")
async def delete_sale(sale_id: int, db: AsyncSession = Depends(get_db)):
    query = text("DELETE FROM sales WHERE id = :sale_id RETURNING id")
    result = await db.execute(query, {"sale_id": sale_id})
    await db.commit()
    deleted_sale = result.fetchone()
    if not deleted_sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return {"message": "Sale deleted", "sale_id": sale_id}
