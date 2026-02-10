from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.database import get_db

router = APIRouter(
    prefix="/collections",
    tags=["collections"]
)

@router.get("/")
async def get_collections(db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM collections")
    result = await db.execute(query)
    return [dict(row._mapping) for row in result]

@router.get("/{collection_id}")
async def get_collection(collection_id: int, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM collections WHERE id = :collection_id")
    result = await db.execute(query, {"collection_id": collection_id})
    collection = result.fetchone()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return dict(collection._mapping)

@router.post("/")
async def create_collection(collection: dict, db: AsyncSession = Depends(get_db)):
    columns = ", ".join(collection.keys())
    values = ", ".join([f":{key}" for key in collection.keys()])
    query = text(f"INSERT INTO collections ({columns}) VALUES ({values}) RETURNING *")
    try:
        result = await db.execute(query, collection)
        await db.commit()
        new_collection = result.fetchone()
        return dict(new_collection._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{collection_id}")
async def update_collection(collection_id: int, collection: dict, db: AsyncSession = Depends(get_db)):
    set_clause = ", ".join([f"{key} = :{key}" for key in collection.keys()])
    query = text(f"UPDATE collections SET {set_clause} WHERE id = :collection_id RETURNING *")
    try:
        result = await db.execute(query, {**collection, "collection_id": collection_id})
        await db.commit()
        updated_collection = result.fetchone()
        if not updated_collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        return dict(updated_collection._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{collection_id}")
async def delete_collection(collection_id: int, db: AsyncSession = Depends(get_db)):
    query = text("DELETE FROM collections WHERE id = :collection_id RETURNING id")
    result = await db.execute(query, {"collection_id": collection_id})
    await db.commit()
    deleted = result.fetchone()
    if not deleted:
        raise HTTPException(status_code=404, detail="Collection not found")
    return {"message": "Collection deleted", "collection_id": collection_id}
