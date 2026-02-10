from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/")
async def get_users(sort_by: str = "id", order: str = "asc", db: AsyncSession = Depends(get_db)):
    # Prevent SQL Injection by validating sort_by
    valid_sort_columns = ["id", "username", "email", "created_at"]
    if sort_by not in valid_sort_columns:
        sort_by = "id"
    if order not in ["asc", "desc"]:
        order = "asc"
        
    query = text(f"SELECT * FROM users ORDER BY {sort_by} {order}")
    result = await db.execute(query)
    return [dict(row._mapping) for row in result]

@router.get("/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM users WHERE id = :user_id")
    result = await db.execute(query, {"user_id": user_id})
    user = result.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(user._mapping)

@router.post("/")
async def create_user(user: dict, db: AsyncSession = Depends(get_db)):
    query = text("INSERT INTO users (username, email) VALUES (:username, :email) RETURNING *")
    try:
        result = await db.execute(query, user)
        await db.commit()
        new_user = result.fetchone()
        return dict(new_user._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}")
async def update_user(user_id: int, user: dict, db: AsyncSession = Depends(get_db)):
    query = text("UPDATE users SET username = :username, email = :email WHERE id = :user_id RETURNING *")
    try:
        result = await db.execute(query, {**user, "user_id": user_id})
        await db.commit()
        updated_user = result.fetchone()
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(updated_user._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    # This demonstrates On Delete Cascade if user has collections
    query = text("DELETE FROM users WHERE id = :user_id RETURNING id")
    result = await db.execute(query, {"user_id": user_id})
    await db.commit()
    deleted_user = result.fetchone()
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted", "user_id": user_id}
