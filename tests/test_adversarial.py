"""
Unit tests for the FGSM attack.

We deliberately avoid downloading ResNet50 (~100MB) on every `pytest` run by
building a tiny CNN with random weights and the same input contract
(normalized 3-channel tensor, logits out). The FGSM math doesn't care about
the model's quality — only that gradients flow.
"""

import numpy as np
import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("torchvision")

import torch.nn as nn  # noqa: E402

from processing.security.adversarial import fgsm_attack  # noqa: E402


class _TinyClassifier(nn.Module):
    """A 10-class CNN small enough to run in milliseconds."""

    def __init__(self, num_classes: int = 10):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(3, 8, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(8, num_classes),
        )

    def forward(self, x):
        return self.net(x)


class _FakeWeightsTransforms:
    """Mimics the shape of torchvision Weights.transforms() for our attack."""

    resize_size = [64]
    crop_size = [64]
    mean = [0.5, 0.5, 0.5]
    std = [0.5, 0.5, 0.5]


def _dummy_bgr_image(size: int = 96) -> np.ndarray:
    rng = np.random.default_rng(seed=42)
    return rng.integers(0, 256, size=(size, size, 3), dtype=np.uint8)


def test_fgsm_returns_correct_shape_and_dtype():
    model = _TinyClassifier().eval()
    image = _dummy_bgr_image()

    result = fgsm_attack(
        image=image,
        model=model,
        preprocess=_FakeWeightsTransforms(),
        epsilon=0.05,
    )

    # adversarial image is at the cropped size, BGR uint8
    assert result.adversarial_image.shape == (64, 64, 3)
    assert result.adversarial_image.dtype == np.uint8


def test_fgsm_respects_linf_budget():
    """The achieved L_inf distance should never exceed epsilon."""
    model = _TinyClassifier().eval()
    image = _dummy_bgr_image()
    epsilon = 0.03

    result = fgsm_attack(
        image=image,
        model=model,
        preprocess=_FakeWeightsTransforms(),
        epsilon=epsilon,
    )

    # Allow a tiny floating-point slop. The clamp to [0,1] can only *reduce*
    # the achieved distance vs epsilon, never grow it.
    assert result.linf_distance <= epsilon + 1e-6


def test_fgsm_rejects_invalid_epsilon():
    model = _TinyClassifier().eval()
    image = _dummy_bgr_image()

    with pytest.raises(ValueError):
        fgsm_attack(
            image=image,
            model=model,
            preprocess=_FakeWeightsTransforms(),
            epsilon=0.0,
        )

    with pytest.raises(ValueError):
        fgsm_attack(
            image=image,
            model=model,
            preprocess=_FakeWeightsTransforms(),
            epsilon=1.5,
        )


def test_fgsm_perturbation_is_signed_epsilon():
    """The perturbation should be exactly ±epsilon at every pixel (FGSM sign step)."""
    model = _TinyClassifier().eval()
    image = _dummy_bgr_image()
    epsilon = 0.02

    result = fgsm_attack(
        image=image,
        model=model,
        preprocess=_FakeWeightsTransforms(),
        epsilon=epsilon,
    )

    unique_vals = np.unique(np.round(result.perturbation, 6))
    # Every entry is +epsilon or -epsilon (or 0 if gradient was exactly 0,
    # which shouldn't happen here but we don't assert against it).
    for v in unique_vals:
        assert v in (epsilon, -epsilon, 0.0), f"unexpected perturbation value: {v}"
