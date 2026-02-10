from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.database import get_db

router = APIRouter(
    prefix="/nfts",
    tags=["nfts"]
)

@router.get("/")
async def get_nfts(sort_by: str = "id", order: str = "asc", db: AsyncSession = Depends(get_db)):
    valid_sort_columns = ["id", "name", "price", "created_at"]
    if sort_by not in valid_sort_columns:
        sort_by = "id"
    if order not in ["asc", "desc"]:
        order = "asc"
        
    query = text(f"SELECT * FROM nfts ORDER BY {sort_by} {order}")
    result = await db.execute(query)
    return [dict(row._mapping) for row in result]

@router.get("/{nft_id}")
async def get_nft(nft_id: int, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM nfts WHERE id = :nft_id")
    result = await db.execute(query, {"nft_id": nft_id})
    nft = result.fetchone()
    if not nft:
        raise HTTPException(status_code=404, detail="NFT not found")
    return dict(nft._mapping)

@router.post("/")
async def create_nft(nft: dict, db: AsyncSession = Depends(get_db)):
    columns = ", ".join(nft.keys())
    values = ", ".join([f":{key}" for key in nft.keys()])
    query = text(f"INSERT INTO nfts ({columns}) VALUES ({values}) RETURNING *")
    try:
        result = await db.execute(query, nft)
        await db.commit()
        new_nft = result.fetchone()
        return dict(new_nft._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{nft_id}")
async def update_nft(nft_id: int, nft: dict, db: AsyncSession = Depends(get_db)):
    set_clause = ", ".join([f"{key} = :{key}" for key in nft.keys()])
    query = text(f"UPDATE nfts SET {set_clause} WHERE id = :nft_id RETURNING *")
    try:
        result = await db.execute(query, {**nft, "nft_id": nft_id})
        await db.commit()
        updated_nft = result.fetchone()
        if not updated_nft:
            raise HTTPException(status_code=404, detail="NFT not found")
        return dict(updated_nft._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{nft_id}")
async def delete_nft(nft_id: int, db: AsyncSession = Depends(get_db)):
    query = text("DELETE FROM nfts WHERE id = :nft_id RETURNING id")
    result = await db.execute(query, {"nft_id": nft_id})
    await db.commit()
    deleted_nft = result.fetchone()
    if not deleted_nft:
        raise HTTPException(status_code=404, detail="NFT not found")
    return {"message": "NFT deleted", "nft_id": nft_id}
