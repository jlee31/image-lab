import io
import cv2
import numpy as np
from PIL import Image
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from processing.filters import (
    adjust_brightness_with_factor,
    adjust_contrast_with_factor,
    adjust_saturation_with_factor,
    apply_blur_with_radius,
    apply_noise_with_intensity,
    apply_glitch,
    apply_sharpen,
    apply_pixels,
    apply_invert,
    apply_vignette,
    apply_retro_filter,
    apply_pencil,
    apply_smart_enhance,
)

router = APIRouter(prefix="/filters", tags=["Filters"])


# Encoding and Decoding Images

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


# ── Slider-based filters (take a parameter) ─────────────────────────────────

@router.post("/blur")
async def blur(
    file: UploadFile = File(...),
    radius: float = Query(default=2.0, ge=1.0, le=10.0),
):
    image = _decode_image(await file.read())
    return _encode_image(apply_blur_with_radius(image, radius))


@router.post("/brightness")
async def brightness(
    file: UploadFile = File(...),
    factor: float = Query(default=1.0, ge=0.0, le=2.0),
):
    image = _decode_image(await file.read())
    return _encode_image(adjust_brightness_with_factor(image, factor))


@router.post("/contrast")
async def contrast(
    file: UploadFile = File(...),
    factor: float = Query(default=1.0, ge=0.0, le=2.0),
):
    image = _decode_image(await file.read())
    return _encode_image(adjust_contrast_with_factor(image, factor))


@router.post("/saturation")
async def saturation(
    file: UploadFile = File(...),
    factor: float = Query(default=1.0, ge=0.0, le=2.0),
):
    image = _decode_image(await file.read())
    return _encode_image(adjust_saturation_with_factor(image, factor))


@router.post("/noise")
async def noise(
    file: UploadFile = File(...),
    intensity: float = Query(default=0.3, ge=0.0, le=1.0),
):
    image = _decode_image(await file.read())
    return _encode_image(apply_noise_with_intensity(image, intensity))


# ── One-click filters (no parameters) ───────────────────────────────────────

@router.post("/sharpen")
async def sharpen(file: UploadFile = File(...)):
    image = _decode_image(await file.read())
    return _encode_image(apply_sharpen(image))


@router.post("/glitch")
async def glitch(file: UploadFile = File(...)):
    image = _decode_image(await file.read())
    return _encode_image(apply_glitch(image))


@router.post("/invert")
async def invert(file: UploadFile = File(...)):
    image = _decode_image(await file.read())
    return _encode_image(apply_invert(image))


@router.post("/vignette")
async def vignette(file: UploadFile = File(...)):
    image = _decode_image(await file.read())
    return _encode_image(apply_vignette(image))


@router.post("/pixelate")
async def pixelate(file: UploadFile = File(...)):
    image = _decode_image(await file.read())
    return _encode_image(apply_pixels(image))


@router.post("/retro")
async def retro(file: UploadFile = File(...)):
    image = _decode_image(await file.read())
    return _encode_image(apply_retro_filter(image))


@router.post("/pencil")
async def pencil(file: UploadFile = File(...)):
    image = _decode_image(await file.read())
    return _encode_image(apply_pencil(image))


@router.post("/smart-enhance")
async def smart_enhance(file: UploadFile = File(...)):
    image = _decode_image(await file.read())
    return _encode_image(apply_smart_enhance(image))