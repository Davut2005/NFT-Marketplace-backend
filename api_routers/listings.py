from fastapi import APIRouter

router = APIRouter(
    prefix="/listings",
    tags=["listings"]
)

@router.get("/")
def get_listings():
    return [{"price": 100.00}]

@router.get("/{listing_id}")
def get_listing(listing_id: int):
    return {"listing_id": listing_id, "price": 100.00}

@router.post("/")
def create_listing(listing: dict):
    return {"message": "Listing created", "listing": listing}
