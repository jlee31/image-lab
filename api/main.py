import logging
import traceback
from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from api.routers import filters
from api.routers import ml


# Create Logger
logger = logging.getLogger(__name__)

# Files
THIS_FILE = Path(__file__).resolve()   # .../image-lab/api/main.py
API_DIR   = THIS_FILE.parent            # .../image-lab/api/
ROOT_DIR  = API_DIR.parent              # .../image-lab/
WEB_DIR   = ROOT_DIR / "web"            # .../image-lab/web/

# Main App here
app = FastAPI(
    title="Image Lab API",
    description="REST API for Image Lab photo processing.",
    version="1.0.0",
)

# The CORS thing is important since we can send requests from one domain to another
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "type": "http_error"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, _exc: Exception):
    logger.error(
        "Unhandled exception on %s %s\n%s",
        request.method,
        request.url.path,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "server_error"},
    )


# Giving the Static Data

if WEB_DIR.exists():
    static_files = StaticFiles(directory=WEB_DIR) 
    app.mount("/static", static_files, name="static")

# Routers

app.include_router(filters.router)
app.include_router(ml.router)

# Route 

@app.get("/", tags=["Health"])
def root():
    index = WEB_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"status": "ok", "message": "Image Lab API is running"}
