# Image Lab — Plan

## Completed: 
- FastAPI backend with all filter endpoints
- Web frontend (HTML/CSS/JS, split into 3 files)
- Docker + docker-compose
- Desktop GUI (CustomTkinter, mixin architecture)
- Background removal processing function (rembg)

---

## Todo

- [ ] Wire up the ML router — add POST /ml/remove-background endpoint in api/routers/ml.py and include it in api/main.py
- [ ] Enable the Remove Background button in the web UI once the endpoint exists
- [ ] Add global error handler in api/main.py so unexpected exceptions return clean JSON instead of a raw 500
- [ ] Fix web slider bug — sliders apply to currentBlob (already edited image) instead of the original, so dragging brightness twice compounds. Should apply to a saved base image like the desktop does with preview_base_image

## Testing

- [ ] Add API integration tests using FastAPI TestClient — upload a real image, assert you get a PNG back
- [ ] Add unit tests for the untested filters: noise, glitch, vignette, pixelate, retro, pencil, invert

## Features (MAIN TO-DO)

- [ ] Image classification / auto-tagging — use a pretrained CNN (ResNet or EfficientNet) via torchvision to predict top-5 labels with confidence scores for any uploaded image. Applies transfer learning concepts from Hands-On ML Ch 14.
- [ ] Depth-based bokeh (portrait mode) — use Depth Anything V2 (HuggingFace), same thread pattern as background removal
- [ ] Super-resolution 4x — Real-ESRGAN, download weights to ~/.imagelab/models/ on first use
- Add like a PDF compression feature or convert formats (part of pdf_tools)


## Web UI

- [ ] fix some front end things (not really interested in this so ill probably just vibe code this) > responsive layout : sidebar and right panel have fixed px widths, breaks on smaller screens, add a media query to stack them vertically

## Misc / Polish

- [ ] Update README with before/after screenshots for each filter
- [ ] Add API rate limiting to ML endpoints if deploying publicly
- learn how to do like basic ci/cd just to know how the basics
