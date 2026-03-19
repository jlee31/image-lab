import io
import cv2
import numpy as np
from PIL import Image
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from processing.filters import apply_blur_with_radius
from processing.filters import apply_sharpen

router = APIRouter(prefix="/filters", tags=["Filters"])

def _decode_image(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Could not decode image. Send a valid PNG or JPEG.")
    return image


def _encode_image(image: np.ndarray) -> StreamingResponse:
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    buf = io.BytesIO()
    image_pil.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@router.post("/blur", summary="Apply Gaussian blur", response_description="Blurred image as PNG")
async def blur(
    file: UploadFile = File(..., description="Image to blur (PNG or JPEG)"),
    radius: float = Query(default=2.0, ge=1.0, le=10.0, description="Blur radius (1–10)"),
):
    image = _decode_image(await file.read())
    result = apply_blur_with_radius(image, radius)
    return _encode_image(result)

@router.post("/sharpen")
async def sharpen(
    file: UploadFile = File(...)
):
    image = _decode_image(await file.read())
    result = apply_sharpen(image)
    return _encode_image(result)