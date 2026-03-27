# image lab

Desktop photo editor made with OpenCV, Pillow, and CustomTkinter.

### Features

- **Photo Editor tab**
  - Load, edit, and save images.
  - One-click effects: brightness, contrast, saturation, glitch, blur, sharpen, pixelate, invert, noise, vignette, retro filter, pencil sketch.
  - **Smart Enhance** preset: human-tuned combo of contrast/saturation boost and light sharpening.
  - Slider-based adjustments for brightness, contrast, saturation, blur radius, and noise intensity, with live preview for brightness and contrast.
  - Undo/redo and reset, plus a visible history list of applied operations.

- **Batch Tools tab**
  - Choose an input and output folder.
  - Apply a simple pipeline (retro / sharpen / blur) to all images in a folder.
  - See a list of recent files opened in the current session.

- **Settings tab**
  - Toggle success and error notifications.
  - Choose display mode (fit to width vs fit to window).
  - Placeholder toggle for future TTS/sound options.

- **Keyboard shortcuts**
  - Cmd/Ctrl+O: Open image
  - Cmd/Ctrl+S: Save image
  - Cmd/Ctrl+Z: Undo
  - Shift+Cmd+Z / Ctrl+Y: Redo
  - Cmd/Ctrl+R: Reset image
  - Cmd/Ctrl+B: Apply blur
  - Cmd/Ctrl+E: Smart Enhance

### How to run the app

**Desktop GUI:**

```bash
pip install -r requirements-gui.txt
python3 main.py
```

**Web / API:**

```bash
pip install -r requirements-api.txt
uvicorn api.main:app
# then open http://localhost:8000
```

**Or run with Docker:**

```bash
docker compose up
# then open http://localhost:8000
```

**Run tests:**

```bash
pip install -r requirements-api.txt
pytest
```

