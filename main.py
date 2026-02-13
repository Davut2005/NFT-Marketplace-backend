from api_routers import users, collections, nfts, listings, sales, payments, activity_logs, analytics, ownership_history
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(collections.router)
app.include_router(nfts.router)
app.include_router(listings.router)
app.include_router(sales.router)
app.include_router(payments.router)
app.include_router(activity_logs.router)
app.include_router(analytics.router)
app.include_router(ownership_history.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
