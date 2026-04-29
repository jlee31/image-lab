# ML Papers and Models

This directory contains ML-backed image processing features.
Each section lists the paper, the model used, and what the implementation does.

---

## Background Removal

**Paper:** Qin, X., Zhang, Z., Huang, C., Dehghan, M., Zaiane, O., Jagersand, M.
"U2-Net: Going Deeper with Nested U-Structure for Salient Object Detection."
Pattern Recognition, 2020.
https://arxiv.org/abs/2005.09007

**Model:** rembg (wraps U2-Net / IS-Net via ONNX Runtime)
Install: `pip install rembg onnxruntime`

**What it does:**
Takes a BGR image, runs U2-Net to produce a foreground mask, and returns a
BGRA image where the background pixels are set to fully transparent (alpha = 0).
The model weights are downloaded automatically on first use by rembg.

**File:** `background_removal.py`

---

## Depth-Based Bokeh (Portrait Mode) -- not yet implemented

**Paper:** Yang, L. et al. "Depth Anything V2." arXiv, 2024.
https://arxiv.org/abs/2406.09414
in
Also see: Ranftl, R. et al. "Towards Robust Monocular Depth Estimation:
Mixing Datasets for Zero-Shot Cross-Dataset Transfer." TPAMI, 2020.
https://arxiv.org/abs/1907.01341

**Model:** depth-anything/Depth-Anything-V2-Small-hf (Hugging Face)
Install: `pip install transformers torch`

**What it does:**
Runs a monocular depth estimation model to produce a per-pixel depth map.
Uses the depth map to apply variable-radius Gaussian blur: far pixels receive
heavy blur, near pixels stay sharp, simulating a camera bokeh effect.

---

## Super-Resolution (4x Upscaling) -- not yet implemented

**Paper:** Wang, X. et al. "Real-ESRGAN: Training Real-World Blind
Super-Resolution with Pure Synthetic Data." ICCV Workshops, 2021.
https://arxiv.org/abs/2107.10833

Also see: Wang, X. et al. "ESRGAN: Enhanced Super-Resolution Generative
Adversarial Networks." ECCV Workshops, 2018.
https://arxiv.org/abs/1809.00219

**Model:** xinntao/Real-ESRGAN
Install: `pip install realesrgan basicsr`

**What it does:**
Runs a GAN-based super-resolution model to upscale images by 4x while
reconstructing fine details that simple interpolation cannot recover.
Model weights are downloaded to ~/.imagelab/models/ on first use.

---

## Object Removal via Inpainting -- not yet implemented

**Paper:** Suvorov, R. et al. "Resolution-robust Large Mask Inpainting
with Fourier Convolutions." WACV, 2022.
https://arxiv.org/abs/2109.07161

**Model:** lama-cleaner (wraps LaMa)
Install: `pip install lama-cleaner`

**What it does:**
User paints a mask over an object in the canvas. The LaMa model fills
the masked region with plausible background content by using Fourier
convolutions to capture long-range spatial context across the image.

---

## B&W Photo Colorization -- not yet implemented

**Paper:** Zhang, R., Isola, P., Efros, A. "Colorful Image Colorization."
ECCV, 2016.
https://arxiv.org/abs/1603.08511

Also see: Antic, J. "DeOldify." 2018.
https://github.com/jantic/DeOldify

**Model:** piddnad/ddcolor-artistic (Hugging Face)
Install: `pip install transformers`

**What it does:**
Converts a grayscale image to color by predicting the AB channels in
LAB color space. If the input image is already in color, a warning is shown.
