from fastapi import FastAPI
from api.routers import filters

app = FastAPI(
    title="Image Lab API",
    description="REST API for Image Lab photo processing.",
    version="1.0.0",
)

app.include_router(filters.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Image Lab API is running"}
