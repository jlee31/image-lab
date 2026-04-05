from fastapi.testclient import TestClient
from api.main import app
import numpy as np
import cv2
import io

from processing.filters import (
    adjust_brightness_with_factor,
    adjust_contrast_with_factor,
    apply_blur_with_radius,
    apply_smart_enhance,
)

from test_image_filters import _dummy_image

client = TestClient(app)

def test_root_returns_200():
    response = client.get("/")
    assert response.status_code == 200

# Testing Endpoints

def make_test_image() -> bytes:
    img = np.zeros((100,100,3), dtype=np.uint8)
    _, buffer = cv2.imencode(".png", img)
    return buffer.tobytes()


def test_filter():
    response = client.post("/filters/blur", files={"file": ("test.png", io.BytesIO(img_bytes), "image/png")})
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    
    