from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.database import get_db

router = APIRouter(
    prefix="/activity_logs",
    tags=["activity_logs"]
)

@router.get("/")
async def get_activity_logs(sort_by: str = "id", order: str = "asc", db: AsyncSession = Depends(get_db)):
    valid_sort_columns = ["id", "action", "created_at"]
    if sort_by not in valid_sort_columns:
        sort_by = "id"
    if order not in ["asc", "desc"]:
        order = "asc"
        
    query = text(f"SELECT * FROM activity_logs ORDER BY {sort_by} {order}")
    result = await db.execute(query)
    return [dict(row._mapping) for row in result]

@router.get("/{log_id}")
async def get_activity_log(log_id: int, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM activity_logs WHERE id = :log_id")
    result = await db.execute(query, {"log_id": log_id})
    log = result.fetchone()
    if not log:
        raise HTTPException(status_code=404, detail="Activity log not found")
    return dict(log._mapping)

@router.post("/")
async def create_activity_log(log: dict, db: AsyncSession = Depends(get_db)):
    columns = ", ".join(log.keys())
    values = ", ".join([f":{key}" for key in log.keys()])
    query = text(f"INSERT INTO activity_logs ({columns}) VALUES ({values}) RETURNING *")
    try:
        result = await db.execute(query, log)
        await db.commit()
        new_log = result.fetchone()
        return dict(new_log._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
