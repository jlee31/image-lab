import io
import cv2
import numpy as np
from PIL import Image
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from processing.ml import background_removal

router = APIRouter(prefix="/ml", tags=["ML"])


def _decode_image(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Could not decode image. Send a valid PNG or JPEG.")
    return image


def _encode_image(image: np.ndarray) -> StreamingResponse:
    if image.ndim == 3 and image.shape[2] == 4:
        rgba = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        image_pil = Image.fromarray(rgba, mode="RGBA")
    else:
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    buf = io.BytesIO()
    image_pil.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@router.post("/remove-background")
async def remove_background(file: UploadFile = File(...)):
    image = _decode_image(await file.read())
    return _encode_image(background_removal.remove_background(image))
