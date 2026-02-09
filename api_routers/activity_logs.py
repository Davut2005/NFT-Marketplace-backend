from fastapi import APIRouter

router = APIRouter(
    prefix="/activity_logs",
    tags=["activity_logs"]
)

@router.get("/")
def get_activity_logs():
    return [{"action": "minted"}]

@router.get("/{log_id}")
def get_activity_log(log_id: int):
    return {"log_id": log_id, "action": "minted"}

@router.post("/")
def create_activity_log(log: dict):
    return {"message": "Activity log created", "log": log}
