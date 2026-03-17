# Dev Notes

## Things I Want to Have

- Some type of text to speech
- Some kind of notification

### TTS Ideas

- Add tutorial mode with TTS
- Add action feedback (e.x add a button that describes what the tool does)

### Notification Ideas

- Pop up that happens when the filter is successful
- Errors or warnings
- Let the user enable or disable TTS/notifications via a Settings panel.

---

## ML Feature Roadmap

### Priority 1 — Background Removal

**Paper:** Qin, X. et al. "U²-Net: Going Deeper with Nested U-Structure for Salient Object Detection." *Pattern Recognition*, 2020. [arxiv.org/abs/2005.09007](https://arxiv.org/abs/2005.09007)

**Model:** `rembg` library (wraps U²-Net / IS-Net under the hood)

**Install:** `pip install rembg onnxruntime`

**What to change:**

1. Add `remove_background()` function in `processing/image_filters.py` — takes a BGR numpy array, converts to PIL RGBA via `rembg.remove()`, converts back
2. Add "Remove Background" button in the effects panel in `gui/app_window.py`
3. After removal, show a checkerboard pattern on the canvas to represent transparency
4. Add a "Replace Background" option: solid color picker or load a second image
5. Add "Apply filter to foreground only" / "Apply filter to background only" toggle using the alpha mask

---

### Priority 2 — Depth-Based Bokeh (Portrait Mode)

**Paper:** Yang, L. et al. "Depth Anything V2." *arXiv*, 2024. [arxiv.org/abs/2406.09414](https://arxiv.org/abs/2406.09414)

**Also see:** Ranftl, R. et al. "Towards Robust Monocular Depth Estimation: Mixing Datasets for Zero-Shot Cross-Dataset Transfer." *TPAMI*, 2020 (MiDaS). [arxiv.org/abs/1907.01341](https://arxiv.org/abs/1907.01341)

**Model:** `depth-anything/Depth-Anything-V2-Small-hf` on Hugging Face

**Install:** `pip install transformers torch`

**What to change:**

1. Add `estimate_depth(image)` in `processing/image_filters.py` — runs HF depth estimation pipeline, returns a normalized grayscale depth map as numpy array
2. Add `apply_depth_bokeh(image, blur_strength)` — uses the depth map to apply variable-radius Gaussian blur: far pixels get heavy blur, near pixels stay sharp
3. Add "Portrait Mode (Bokeh)" button in the effects panel in `gui/app_window.py`
4. Add a "Blur Strength" slider (0–20) scoped to this effect
5. Show a "Generating depth map..." progress indicator while the model runs (in a background thread)

---

### Priority 3 — Image Super-Resolution (4× Upscaling)

**Paper:** Wang, X. et al. "Real-ESRGAN: Training Real-World Blind Super-Resolution with Pure Synthetic Data." *ICCV Workshops*, 2021. [arxiv.org/abs/2107.10833](https://arxiv.org/abs/2107.10833)

**Also see:** Wang, X. et al. "ESRGAN: Enhanced Super-Resolution Generative Adversarial Networks." *ECCV Workshops*, 2018. [arxiv.org/abs/1809.00219](https://arxiv.org/abs/1809.00219)

**Model:** `xinntao/Real-ESRGAN` or ONNX version for faster CPU inference

**Install:** `pip install realesrgan basicsr`

**What to change:**

1. Add `apply_super_resolution(image, scale=4)` in `processing/image_filters.py` — loads RealESRGANer, runs enhance, returns upscaled BGR array
2. Download model weights on first use to `~/.imagelab/models/`, show download progress
3. Add "Super Resolution 4×" button in the effects panel in `gui/app_window.py`
4. Run inference in a background thread — show a CTk progress bar during processing
5. After upscaling, update the canvas with the new larger image and show "4× upscaled" in the history panel

---

### Priority 4 — Object Removal via Inpainting

**Paper:** Suvorov, R. et al. "Resolution-robust Large Mask Inpainting with Fourier Convolutions." *WACV*, 2022. [arxiv.org/abs/2109.07161](https://arxiv.org/abs/2109.07161)

**Model:** `lama-cleaner` library (wraps LaMa) or `Samsung/LaMa` on Hugging Face

**Install:** `pip install lama-cleaner`

**What to change:**

1. Add a "Paint Mask" toggle button in `gui/app_window.py` — when active, mouse drag on canvas draws a red brush stroke overlay
2. Store the drawn mask as a separate numpy array (same size as image, binary)
3. Add `apply_inpainting(image, mask)` in `processing/image_filters.py` — passes image + mask to LaMa, returns inpainted result
4. Add "Remove Object" button that runs inpainting on the current mask, then clears the mask
5. Add "Clear Mask" button to reset the painted region

---

### Priority 5 — Before/After Comparison Slider (UX)

**No ML required — pure UX improvement.**

**What to change:**

1. Add a "Compare" toggle button in `gui/app_window.py`
2. When active, render the canvas as two halves: left = original image, right = current processed image
3. Draw a vertical white divider line at the midpoint
4. Bind mouse drag on the canvas to move the divider left/right
5. Update on `<B1-Motion>` and redraw both halves clipped to their respective sides

---

### Priority 6 — B&W Photo Colorization

**Paper:** Zhang, R. et al. "Colorful Image Colorization." *ECCV*, 2016. [arxiv.org/abs/1603.08511](https://arxiv.org/abs/1603.08511)

**Also see:** Antic, J. "DeOldify" (2018). [github.com/jantic/DeOldify](https://github.com/jantic/DeOldify)

**Model:** `piddnad/ddcolor-artistic` on Hugging Face (or official Zhang et al. model via OpenCV DNN)

**Install:** `pip install transformers`

**What to change:**

1. Add `apply_colorization(image)` in `processing/image_filters.py` — detects if image is grayscale, converts to LAB color space, runs model on L channel, outputs predicted AB channels, merges back
2. Add "Colorize" button in the effects panel in `gui/app_window.py`
3. Show a before/after comparison automatically after colorization runs
4. If image is already in color, show a warning dialog

---

## Architecture Improvements

### Async Inference + Progress Bar

- All ML operations should run in a `threading.Thread`
- While running: disable all buttons, show a `CTkProgressBar` in indeterminate mode below the canvas
- On completion: re-enable buttons, update canvas, push to undo stack

### On-Demand Model Downloading

- Create `utils/model_manager.py`
- On first use of any ML feature, download model weights to `~/.imagelab/models/<model_name>/`
- Show download progress in a dialog
- Cache check on subsequent uses — skip download if file exists

### ONNX Runtime for Inference

- Where possible, prefer ONNX model variants over full PyTorch
- Faster CPU inference, no CUDA required, smaller install size
- Relevant for: U²-Net (rembg already does this), Real-ESRGAN has ONNX exports

---

## Random / Other

- Host code on GitHub with a README showing before/after screenshots for each ML feature
- Include visual comparisons (original vs. processed side-by-side)
- Add "AI processing in progress" progress indicator for UX polish
- Write a short blog post or demo video showcasing the AI-powered features
- Consider packaging the app with PyInstaller for distribution
- Performance benchmarks for ML-enhanced filters (CPU vs. GPU timing)
