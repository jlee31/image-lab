from fastapi.testclient import TestClient
from api.main import app
import numpy as np
import cv2
import io



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
    img_bytes = make_test_image()
    response = client.post("/filters/blur", files={"file": ("test.png", io.BytesIO(img_bytes), "image/png")})
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    
    