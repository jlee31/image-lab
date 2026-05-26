"""
processing/ml/classification.py
--------------------------------
Image classification via ResNet50 pretrained on ImageNet (1000 classes).

How it works (Hands-On ML, Ch. 14):
A pretrained CNN learned to extract visual features layer-by-layer — edges →
textures → shapes → objects — from ImageNet's 1.2M labeled images. We load
those weights, preprocess the image into the format the network expects, run
inference, softmax the logits into probabilities, and return the top-k labels.

This is transfer learning by reuse: no training step, just inference.

Returns a list of {"label": str, "confidence": float}, sorted high → low.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np


@lru_cache(maxsize=1)
def _load_model() -> tuple[Any, Any, list[str]]:
    """Load ResNet50 + IMAGENET1K_V2 weights once and cache."""
    try:
        import torch  # noqa: F401  — surfaces a clear ImportError if missing
        from torchvision.models import ResNet50_Weights, resnet50
    except ImportError as e:
        raise ImportError(
            "torch/torchvision are required for classification.\n"
            "Run: pip install torch torchvision"
        ) from e

    weights = ResNet50_Weights.IMAGENET1K_V2
    model = resnet50(weights=weights)
    model.eval()
    categories = list(weights.meta["categories"])
    return model, weights, categories


def classify(image: np.ndarray, top_k: int = 5) -> list[dict]:
    """
    Classify a BGR uint8 image (OpenCV convention) and return top-k labels.
    """
    import torch
    from PIL import Image

    model, weights, categories = _load_model()
    preprocess = weights.transforms()

    # BGR uint8 -> RGB PIL -> preprocessed tensor batch
    pil_rgb = Image.fromarray(image[:, :, ::-1])
    batch = preprocess(pil_rgb).unsqueeze(0)

    with torch.no_grad():
        logits = model(batch)
    probs = torch.nn.functional.softmax(logits[0], dim=0)
    top_probs, top_idx = torch.topk(probs, top_k)

    return [
        {"label": categories[int(idx)], "confidence": float(prob)}
        for idx, prob in zip(top_idx, top_probs)
    ]
