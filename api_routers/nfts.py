from fastapi import APIRouter

router = APIRouter(
    prefix="/nfts",
    tags=["nfts"]
)

@router.get("/")
def get_nfts():
    return [{"name": "Punk #001"}]

@router.get("/{nft_id}")
def get_nft(nft_id: int):
    return {"nft_id": nft_id, "name": "Punk #001"}

@router.post("/")
def create_nft(nft: dict):
    return {"message": "NFT created", "nft": nft}
