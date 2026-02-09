from fastapi import APIRouter

router = APIRouter(
    prefix="/sales",
    tags=["sales"]
)

@router.get("/")
def get_sales():
    return [{"sale_price": 100.00}]

@router.get("/{sale_id}")
def get_sale(sale_id: int):
    return {"sale_id": sale_id, "sale_price": 100.00}

@router.post("/")
def create_sale(sale: dict):
    return {"message": "Sale created", "sale": sale}
