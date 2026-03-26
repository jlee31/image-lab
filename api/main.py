from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routers import filters

app = FastAPI(
    title="Image Lab API",
    description="REST API for Image Lab photo processing.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(filters.router)

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.get("/", tags=["Health"])
def root():
    index = WEB_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"status": "ok", "message": "Image Lab API is running"}
