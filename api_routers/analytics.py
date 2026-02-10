from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.database import get_db

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)

@router.get("/high-value-sales")
async def get_high_value_sales(min_price: float = 100.0, collection_id: int = 1, db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT s.id as sale_id, n.name as nft_name, s.sale_price, u.username as buyer_username
        FROM sales s
        JOIN listings l ON s.listing_id = l.id
        JOIN nfts n ON l.nft_id = n.id
        JOIN users u ON s.buyer_id = u.id
        WHERE s.sale_price > :min_price AND n.collection_id = :collection_id
    """)
    result = await db.execute(query, {"min_price": min_price, "collection_id": collection_id})
    return [dict(row._mapping) for row in result]

@router.get("/top-sellers")
async def get_top_sellers(min_total_sales: float = 500.0, db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT u.id as seller_id, u.username, SUM(s.sale_price) as total_sales_volume, COUNT(s.id) as sales_count
        FROM users u
        JOIN listings l ON u.id = l.seller_id
        JOIN sales s ON l.id = s.listing_id
        GROUP BY u.id, u.username
        HAVING SUM(s.sale_price) > :min_total_sales
    """)
    result = await db.execute(query, {"min_total_sales": min_total_sales})
    return [dict(row._mapping) for row in result]
