# Image Lab — API + Multi-Frontend Refactor Plan

## Vision
Turn the project into a FastAPI REST backend with a shared `processing/` layer,
keeping the existing CustomTkinter desktop app and adding a web UI frontend.

---

## Phase 1 — FastAPI Backend

- [ ] Add `fastapi` and `uvicorn` to `requirements.txt`
- [ ] Add `python-multipart` for file upload support
- [ ] Create `api/` directory with:
  - [ ] `api/main.py` — FastAPI app entry point, mounts routers
  - [ ] `api/routers/filters.py` — filter endpoints (`/api/filters/*`)
  - [ ] `api/routers/ml.py` — ML endpoints (`/api/ml/*`)
  - [ ] `api/schemas.py` — Pydantic request/response models
- [ ] Define image transport format: multipart file upload → base64 JSON response
- [ ] Implement filter endpoints (thin wrappers around existing `processing/filters/`):
  - [ ] `POST /api/filters/brightness`
  - [ ] `POST /api/filters/contrast`
  - [ ] `POST /api/filters/saturation`
  - [ ] `POST /api/filters/blur`
  - [ ] `POST /api/filters/sharpen`
  - [ ] `POST /api/filters/invert`
  - [ ] `POST /api/filters/vignette`
  - [ ] `POST /api/filters/pixelate`
  - [ ] `POST /api/filters/glitch`
  - [ ] `POST /api/filters/retro`
  - [ ] `POST /api/filters/pencil`
  - [ ] `POST /api/filters/smart-enhance`
- [ ] Implement ML endpoints:
  - [ ] `POST /api/ml/remove-background`
- [ ] Add response metadata: `{ image, width, height, processing_time_ms }`
- [ ] Verify auto-generated OpenAPI docs at `/docs`

---

## Phase 2 — Desktop App Refactor

- [ ] Rename `gui/` → `desktop/` (update all imports)
- [ ] Create `desktop/transport.py` — abstraction layer with two modes:
  - `LocalTransport` — calls `processing/` functions directly (offline/default)
  - `RemoteTransport` — calls the FastAPI backend over HTTP
- [ ] Update `desktop/app_window.py` to use `transport.py` instead of calling filters directly
- [ ] Add a "Server URL" setting in the Settings tab (for remote mode)
- [ ] Add a "Local / Remote" toggle in Settings

---

## Phase 3 — Web Frontend

> Decision: **Gradio** (fast, Python, ~1 day) vs **React + Tailwind** (polished, ~1 week)
> TODO: pick one before starting this phase

### Option A — Gradio
- [ ] Create `web/app.py` — Gradio interface
- [ ] Add image input + filter buttons wired to the API
- [ ] Add sliders for brightness, contrast, saturation, blur, noise
- [ ] Add ML section (Remove Background)

### Option B — React
- [ ] Scaffold with Vite + Tailwind in `web/`
- [ ] Build sidebar, canvas, and filter panel components matching desktop design
- [ ] Wire all filter calls to the FastAPI backend
- [ ] Add drag-and-drop image upload
- [ ] Add before/after comparison slider (Priority 5 from DEV_NOTES)

---

## Phase 4 — Docker

- [ ] Create `Dockerfile` for the FastAPI backend
- [ ] Create `Dockerfile` (or use Gradio's built-in) for the web frontend
- [ ] Create `docker-compose.yml`:
  - `ml-api` service (FastAPI, port 8000)
  - `web-ui` service (Gradio or React, port 7860 / 3000)
  - `model-cache` volume for ML model weights (`~/.imagelab/models/`)
- [ ] Add `.dockerignore`
- [ ] Test full stack with `docker compose up`

---

## Phase 5 — Polish

- [ ] Add API key / simple auth to the backend (optional, for public deployment)
- [ ] Add rate limiting to ML endpoints
- [ ] Write integration tests for the API
- [ ] Update `README.md` with setup instructions for all three run modes:
  - Desktop (local)
  - Desktop (remote API)
  - Web + API via Docker
- [ ] Add before/after screenshots to README (from DEV_NOTES)

---

## Notes

- `processing/` stays **unchanged** — pure functions, no GUI or HTTP concerns
- Desktop app should work **fully offline** (LocalTransport) by default
- ML model weights cached to `~/.imagelab/models/` and shared via Docker volume
- See `DEV_NOTES.md` for the full ML feature roadmap (background removal, depth bokeh, super-resolution, inpainting, colorization)
