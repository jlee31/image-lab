"""
api/routers/security.py
------------------------
Pen-testing the image classifier with adversarial examples.

POST /security/fgsm-attack
    multipart form-data:
        file:    image (PNG/JPEG)
        epsilon: float in (0, 1), default 0.01 — L_inf budget

    Returns JSON:
        {
          "epsilon": 0.01,
          "linf_distance": 0.0098,
          "fooled": true,
          "original_prediction": [{"label": "...", "confidence": ...}, ...],
          "adversarial_prediction": [{"label": "...", "confidence": ...}, ...],
          "adversarial_image_base64": "iVBOR..."  # PNG, base64-encoded
        }
"""

from __future__ import annotations

import base64
import io

import cv2
import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from PIL import Image

from processing.security.adversarial import fgsm_attack


router = APIRouter(prefix="/security", tags=["Security"])


def _decode_image(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(
            status_code=400,
            detail="Could not decode image. Send a valid PNG or JPEG.",
        )
    return image


def _png_b64(bgr: np.ndarray) -> str:
    pil = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


@router.post("/fgsm-attack")
async def fgsm_attack_endpoint(
    file: UploadFile = File(...),
    epsilon: float = Form(0.01),
):
    """Run an untargeted FGSM attack against the ResNet50 classifier."""
    image = _decode_image(await file.read())

    # Loaded lazily so the import cost is paid on first hit, not at app boot,
    # and so unit tests that don't touch this endpoint stay fast.
    from processing.ml.classification import _load_model, classify

    model, weights, categories = _load_model()
    preprocess = weights.transforms()

    original_prediction = classify(image, top_k=5)

    try:
        result = fgsm_attack(
            image=image,
            model=model,
            preprocess=preprocess,
            epsilon=epsilon,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    adversarial_prediction = classify(result.adversarial_image, top_k=5)

    fooled = (
        original_prediction[0]["label"] != adversarial_prediction[0]["label"]
    )

    return {
        "epsilon": epsilon,
        "linf_distance": result.linf_distance,
        "fooled": fooled,
        "original_prediction": original_prediction,
        "adversarial_prediction": adversarial_prediction,
        "adversarial_image_base64": _png_b64(result.adversarial_image),
    }
