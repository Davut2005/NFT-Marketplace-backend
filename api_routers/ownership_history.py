from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.database import get_db

router = APIRouter(
    prefix="/ownership_history",
    tags=["ownership_history"]
)

@router.get("/")
async def get_ownership_history(sort_by: str = "id", order: str = "asc", db: AsyncSession = Depends(get_db)):
    valid_sort_columns = ["id", "transfer_date"]
    if sort_by not in valid_sort_columns:
        sort_by = "id"
    if order not in ["asc", "desc"]:
        order = "asc"
        
    query = text(f"SELECT * FROM ownership_history ORDER BY {sort_by} {order}")
    result = await db.execute(query)
    return [dict(row._mapping) for row in result]

@router.get("/{history_id}")
async def get_ownership_history_entry(history_id: int, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM ownership_history WHERE id = :history_id")
    result = await db.execute(query, {"history_id": history_id})
    entry = result.fetchone()
    if not entry:
        raise HTTPException(status_code=404, detail="Ownership history entry not found")
    return dict(entry._mapping)

@router.post("/")
async def create_ownership_history_entry(entry: dict, db: AsyncSession = Depends(get_db)):
    columns = ", ".join(entry.keys())
    values = ", ".join([f":{key}" for key in entry.keys()])
    query = text(f"INSERT INTO ownership_history ({columns}) VALUES ({values}) RETURNING *")
    try:
        result = await db.execute(query, entry)
        await db.commit()
        new_entry = result.fetchone()
        return dict(new_entry._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
