"""
processing/security/adversarial.py
-----------------------------------
Adversarial ML pen-testing: FGSM (Fast Gradient Sign Method).

Goodfellow, Shlens & Szegedy, "Explaining and Harnessing Adversarial Examples"
(ICLR 2015) — https://arxiv.org/abs/1412.6572

Idea: image classifiers can be fooled by a perturbation that's invisible to a
human. We compute the gradient of the model's loss w.r.t. the *input pixels*,
then nudge each pixel in the direction that increases that loss:

    x_adv = clip( x + epsilon * sign( grad_x L(model(x), y) ),  0, 1 )

`epsilon` is the L_inf budget — the max per-pixel change in [0, 1] space.
With epsilon ~ 0.01 the change is imperceptible to a human but routinely flips
ImageNet predictions.

This module is model-agnostic: pass any torch model that accepts a normalized
(B,3,H,W) tensor and returns class logits.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class AttackResult:
    adversarial_image: np.ndarray  # BGR uint8, same shape as input
    perturbation: np.ndarray       # float32 in [-epsilon, +epsilon], RGB order
    linf_distance: float           # actual achieved L_inf in [0,1] space
    original_label_index: int      # label the clean image was predicted as
    target_label_index: int        # label we used as the "true" label for the loss


def fgsm_attack(
    image: np.ndarray,
    model,
    preprocess,
    epsilon: float = 0.01,
    target_label_index: int | None = None,
) -> AttackResult:
    """
    Run an untargeted FGSM attack against `model` on a BGR uint8 image.

    `preprocess` is the torchvision Weights.transforms() callable — but we apply
    normalization manually so the gradient is taken w.r.t. raw [0,1] pixels,
    which is where the L_inf budget lives.

    If `target_label_index` is None we use the model's own top-1 prediction as
    the "true" label — a standard untargeted setup that pushes the prediction
    *away from* whatever the model currently thinks.
    """
    import torch
    from PIL import Image
    from torchvision import transforms

    if not (0.0 < epsilon < 1.0):
        raise ValueError(f"epsilon must be in (0, 1), got {epsilon}")

    # BGR uint8 -> RGB PIL -> resized [0,1] tensor (no normalization yet)
    pil_rgb = Image.fromarray(image[:, :, ::-1])
    # Match the preprocessing's resize/crop but stop before normalize. We pull
    # those dims off the supplied transforms() object so this stays generic.
    resize_size = getattr(preprocess, "resize_size", [256])[0]
    crop_size = getattr(preprocess, "crop_size", [224])[0]
    mean = getattr(preprocess, "mean", [0.485, 0.456, 0.406])
    std = getattr(preprocess, "std", [0.229, 0.224, 0.225])

    to_tensor = transforms.Compose([
        transforms.Resize(resize_size),
        transforms.CenterCrop(crop_size),
        transforms.ToTensor(),  # -> [0,1] float32, shape (3,H,W)
    ])
    normalize = transforms.Normalize(mean=mean, std=std)

    x = to_tensor(pil_rgb).unsqueeze(0)  # (1,3,H,W), in [0,1]
    x.requires_grad_(True)

    logits = model(normalize(x))
    pred_index = int(torch.argmax(logits, dim=1).item())
    label_index = pred_index if target_label_index is None else int(target_label_index)

    loss = torch.nn.functional.cross_entropy(
        logits, torch.tensor([label_index])
    )
    model.zero_grad()
    loss.backward()

    perturbation = epsilon * x.grad.sign()
    x_adv = torch.clamp(x + perturbation, 0.0, 1.0).detach()

    # back to BGR uint8 at the cropped resolution
    adv_np = (x_adv.squeeze(0).permute(1, 2, 0).numpy() * 255.0).astype(np.uint8)
    bgr_adv = adv_np[:, :, ::-1].copy()

    pert_np = perturbation.detach().squeeze(0).permute(1, 2, 0).numpy()
    linf = float(np.max(np.abs((x_adv - x).detach().numpy())))

    return AttackResult(
        adversarial_image=bgr_adv,
        perturbation=pert_np,
        linf_distance=linf,
        original_label_index=pred_index,
        target_label_index=label_index,
    )
