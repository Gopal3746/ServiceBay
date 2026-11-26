from fastapi import FastAPI

from app.routes.repairs import router as repairs_router

app = FastAPI(
    title="ServiceBay",
    description="Automotive repair data ingestion API",
    version="0.1.0",
)

app.include_router(repairs_router)


@app.get("/health")
def health():
    return {"status": "ok"}
