from fastapi import APIRouter

router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)

@router.get("/")
def get_payments():
    return [{"amount": 100.00}]

@router.get("/{payment_id}")
def get_payment(payment_id: int):
    return {"payment_id": payment_id, "amount": 100.00}

@router.post("/")
def create_payment(payment: dict):
    return {"message": "Payment created", "payment": payment}
