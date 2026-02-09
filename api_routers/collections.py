from fastapi import APIRouter

router = APIRouter(
    prefix="/collections",
    tags=["collections"]
)

@router.get("/")
def get_collections():
    return [{"name": "CryptoPunks 2.0"}]

@router.get("/{collection_id}")
def get_collection(collection_id: int):
    return {"collection_id": collection_id, "name": "CryptoPunks 2.0"}

@router.post("/")
def create_collection(collection: dict):
    return {"message": "Collection created", "collection": collection}
