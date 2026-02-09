from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/")
def get_users():
    return [{"username": "test_user"}]

@router.get("/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "username": "test_user"}

@router.post("/")
def create_user(user: dict):
    return {"message": "User created", "user": user}
