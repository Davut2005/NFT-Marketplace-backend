from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.database import get_db

router = APIRouter(
    prefix="/listings",
    tags=["listings"]
)

@router.get("/")
async def get_listings(sort_by: str = "id", order: str = "asc", db: AsyncSession = Depends(get_db)):
    valid_sort_columns = ["id", "price", "status", "listed_at"]
    if sort_by not in valid_sort_columns:
        sort_by = "id"
    if order not in ["asc", "desc"]:
        order = "asc"
        
    query = text(f"SELECT * FROM listings ORDER BY {sort_by} {order}")
    result = await db.execute(query)
    return [dict(row._mapping) for row in result]

@router.get("/{listing_id}")
async def get_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM listings WHERE id = :listing_id")
    result = await db.execute(query, {"listing_id": listing_id})
    listing = result.fetchone()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return dict(listing._mapping)

@router.post("/")
async def create_listing(listing: dict, db: AsyncSession = Depends(get_db)):
    columns = ", ".join(listing.keys())
    values = ", ".join([f":{key}" for key in listing.keys()])
    query = text(f"INSERT INTO listings ({columns}) VALUES ({values}) RETURNING *")
    try:
        result = await db.execute(query, listing)
        await db.commit()
        new_listing = result.fetchone()
        return dict(new_listing._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{listing_id}")
async def update_listing(listing_id: int, listing: dict, db: AsyncSession = Depends(get_db)):
    set_clause = ", ".join([f"{key} = :{key}" for key in listing.keys()])
    query = text(f"UPDATE listings SET {set_clause} WHERE id = :listing_id RETURNING *")
    try:
        result = await db.execute(query, {**listing, "listing_id": listing_id})
        await db.commit()
        updated_listing = result.fetchone()
        if not updated_listing:
            raise HTTPException(status_code=404, detail="Listing not found")
        return dict(updated_listing._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{listing_id}")
async def delete_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
    query = text("DELETE FROM listings WHERE id = :listing_id RETURNING id")
    result = await db.execute(query, {"listing_id": listing_id})
    await db.commit()
    deleted_listing = result.fetchone()
    if not deleted_listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"message": "Listing deleted", "listing_id": listing_id}
