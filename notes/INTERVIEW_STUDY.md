# Image Lab — Project & Interview Study Guide

> Written to re-orient yourself after time away, and to prep for an interview that
> uses **FastAPI** and **Selenium**. Read top-to-bottom once, then use the
> "Talking Points" and "Likely Questions" sections as flashcards the night before.

**Heads-up:** This project uses FastAPI heavily and well. It does **not** use
Selenium anywhere — there is no browser-automation code in the repo. The Selenium
section below is a focused primer plus an honest bridge: *how you would test this
project's web UI with Selenium*. Don't claim the project uses Selenium in the
interview; instead say "I built the web app this would drive, here's how I'd test it."

---

## 1. What the project is (the 30-second pitch)

Image Lab is a **photo editor** that ships in three forms over one shared image-
processing core:

1. A **desktop GUI** (CustomTkinter) — `python3 main.py`
2. A **REST API** (FastAPI + Uvicorn) — `uvicorn api.main:app`
3. A **web app** (vanilla HTML/CSS/JS, no framework) served by that same API

The interesting engineering idea: **one processing layer, three front-ends.** The
filters are plain functions that take a NumPy image and return a NumPy image. The
desktop app calls them directly; the web app reaches them over HTTP. Nothing about
a filter knows or cares which front-end called it.

It also has two "resume-worthy" ML features built on transfer learning:
- **Background removal** (U²-Net via the `rembg` library)
- **Image classification** (ResNet50 pretrained on ImageNet)
- **An adversarial-ML security endpoint** (FGSM attack against that classifier)

---

## 2. Architecture (the mental model to hold)

```
                       ┌─────────────────────────────┐
                       │   processing/  (pure core)  │
                       │   numpy image → numpy image │
                       │   - filters/   (brightness, blur, …) │
                       │   - ml/        (bg removal, classify) │
                       │   - security/  (fgsm attack)          │
                       └───────────────┬─────────────┘
                                       │ called directly        │ called over HTTP
                          ┌────────────┴───────┐      ┌──────────┴───────────┐
                          │  desktop_gui/      │      │  api/  (FastAPI)     │
                          │  CustomTkinter     │      │  routers + main.py   │
                          └────────────────────┘      └──────────┬───────────┘
                                                                 │ serves + is called by
                                                       ┌─────────┴─────────┐
                                                       │  web/ (HTML/JS)   │
                                                       │  fetch() calls    │
                                                       └───────────────────┘
```

### The layers, concretely

| Layer | Folder | Role | Key idea |
|-------|--------|------|----------|
| **Core** | `processing/` | Image math. No web, no GUI imports. | A filter is `f(np.ndarray, params) -> np.ndarray`. Pure, testable, reusable. |
| **API** | `api/` | Wraps the core in HTTP endpoints. | Decode bytes → numpy → call core → encode numpy → bytes. |
| **Web** | `web/` | Browser UI that calls the API. | Single `index.html`, no build step. State lives in JS Blobs. |
| **Desktop** | `desktop_gui/` | Native UI that calls the core directly. | CustomTkinter, mixin-based window. |

**Why this matters in an interview:** it's a clean **separation of concerns**. The
boundary between "business logic" and "transport" is exactly where it should be.
You can test the core without a server, and test the API without a browser.

---

## 3. FastAPI — deep dive (your strongest interview material)

This is the part the interview cares about. Know it cold.

### 3.1 App assembly — `api/main.py`

```python
app = FastAPI(title="Image Lab API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)   # cross-origin

app.include_router(filters.router)   # /filters/*
app.include_router(ml.router)        # /ml/*
app.include_router(security.router)  # /security/*

app.mount("/static", StaticFiles(directory=WEB_DIR))  # serve web/ assets
```

Things to be able to explain:
- **`FastAPI()`** is the ASGI application object. Uvicorn runs it.
- **Middleware** wraps every request/response. Here, CORS lets a browser on one
  origin call the API on another. `allow_origins=["*"]` is wide-open — fine for a
  demo, but you should *know* it's a thing you'd tighten in production.
- **`include_router`** composes the app from sub-apps (see Routers below).
- **`mount`** attaches a whole sub-application (static file server) at a path.
- **Exception handlers** (`@app.exception_handler(...)`) centralize error → JSON
  conversion so every error returns a consistent shape instead of a stack trace.
  The catch-all logs the traceback server-side but returns a generic 500 to the
  client — good security hygiene (don't leak internals).

### 3.2 Routers — `api/routers/filters.py`

A **router** is a mini-app you can develop in isolation and bolt on:

```python
router = APIRouter(prefix="/filters", tags=["Filters"])

@router.post("/blur")
async def blur(
    file: UploadFile = File(...),                       # uploaded image
    radius: float = Query(default=2.0, ge=1.0, le=10.0) # ?radius=… , validated
):
    image = _decode_image(await file.read())
    return _encode_image(apply_blur_with_radius(image, radius))
```

Be ready to explain every piece:
- **`@router.post("/blur")`** → registers `POST /filters/blur` (prefix + path).
- **`async def`** → the handler is a coroutine; FastAPI runs it on the event loop.
- **`UploadFile = File(...)`** → declares a multipart file-upload param. `File(...)`
  with `...` (Ellipsis) means **required**. `UploadFile` is a streaming wrapper —
  you call `await file.read()` to get the bytes.
- **`radius: float = Query(default=2.0, ge=1.0, le=10.0)`** → a query-string param
  (`?radius=5`) with **automatic validation**. Send `radius=99` and FastAPI returns
  a `422 Unprocessable Entity` *before your code runs*. This validation-from-type-
  hints is FastAPI's headline feature (it's Pydantic underneath).
- The function **returns a `StreamingResponse`** of PNG bytes (`media_type="image/png"`).

### 3.3 The request/response data flow (very interview-friendly)

The browser can't ship a NumPy array, so the API translates at the boundary:

```python
def _decode_image(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, np.uint8)         # raw bytes → 1-D uint8 array
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR) # → decoded BGR image (H,W,3)
    if image is None:
        raise HTTPException(400, "Could not decode image. Send a valid PNG/JPEG.")
    return image

def _encode_image(image: np.ndarray) -> StreamingResponse:
    pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))  # BGR→RGB
    buf = io.BytesIO()           # in-memory file
    pil.save(buf, format="PNG")  # serialize to PNG bytes
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
```

One-liner to memorize: **"bytes → numpy → process → numpy → bytes."** The core
filters never see HTTP; they just see images.

Note the **OpenCV BGR vs. everyone-else RGB** gotcha: OpenCV decodes to BGR, so the
code converts to RGB before handing to Pillow. A classic "why are my colors swapped"
bug, and a good detail to mention.

### 3.4 Uvicorn — what actually serves requests

FastAPI is just an app object; it doesn't open a socket. **Uvicorn** is the ASGI
server that listens on the TCP port, parses HTTP, and calls into FastAPI.

```bash
uvicorn api.main:app        # module path `api.main`, app object `app`
uvicorn api.main:app --reload   # auto-restart on file change (dev)
```

Mental split: **Uvicorn = the waiter taking orders at the door; FastAPI = the
kitchen routing each order to the right cook (your handler).**

### 3.5 Auto-generated docs (great to demo live)

Because routes are typed, FastAPI generates an OpenAPI schema and interactive docs
for free at **`/docs`** (Swagger UI) and **`/redoc`**. If asked "how would you let a
frontend dev explore the API?" the answer is: it's already there at `/docs`.

### 3.6 Lazy model loading (a nice senior-ish detail)

In `security.py` and `classification.py`, the heavy ML imports/models load **inside**
the handler / behind `@lru_cache`, not at import time:

```python
@lru_cache(maxsize=1)        # load ResNet50 once, reuse forever
def _load_model(): ...
```

Why: keeps app boot fast, keeps unrelated unit tests fast, and pays the multi-hundred-
MB Torch cost only when someone actually hits an ML endpoint. Good thing to volunteer
when asked about performance / startup time.

### 3.7 The full endpoint map

| Method & path | Does | Param |
|---|---|---|
| `GET /` | Serves `web/index.html` (or health JSON) | — |
| `POST /filters/blur` | Gaussian blur | `radius` 1–10 |
| `POST /filters/brightness` | Brightness | `factor` 0–2 |
| `POST /filters/contrast` | Contrast | `factor` 0–2 |
| `POST /filters/saturation` | Saturation | `factor` 0–2 |
| `POST /filters/noise` | Add noise | `intensity` 0–1 |
| `POST /filters/{sharpen,glitch,invert,vignette,pixelate,retro,pencil,smart-enhance}` | One-click effects | none |
| `POST /ml/remove-background` | U²-Net background removal | none |
| `POST /security/fgsm-attack` | Adversarial attack on classifier | `epsilon` form field |

---

## 4. Testing the API — `tests/test_main.py` (interview gold)

FastAPI ships a **`TestClient`** (built on `httpx`/Starlette) that calls your app
**in-process** — no running server, no network:

```python
from fastapi.testclient import TestClient
from api.main import app
client = TestClient(app)

def test_root_returns_200():
    assert client.get("/").status_code == 200

def test_filter():
    img_bytes = make_test_image()  # a tiny black PNG built with numpy+cv2
    res = client.post("/filters/blur",
                      files={"file": ("test.png", io.BytesIO(img_bytes), "image/png")})
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"
```

Points worth making:
- **`TestClient` is synchronous** and spins the app up in memory → fast, deterministic.
- The `files={...}` dict is exactly how you simulate a multipart upload in a test.
- Tests assert on **status code and content-type**, not pixel values — they verify
  the *contract*, not the image math (that'd be a separate unit test on the core fn).
- Run with **`pytest`**; coverage via `pytest-cov`.

This is the natural contrast to Selenium: `TestClient` tests the **API contract**;
Selenium tests the **rendered UI in a real browser**. Different layers of the pyramid.

---

## 5. Selenium primer + how it fits THIS project

The repo has no Selenium, but the interview wants it, and you *do* have a real web UI
(`web/index.html`) that a Selenium suite could drive. Here's the primer plus the bridge.

### 5.1 The five things to know about Selenium

1. **What it is:** a browser-automation library. It launches a real browser
   (Chrome/Firefox) via a **WebDriver** and lets your Python script click, type,
   navigate, and read the page — i.e. **end-to-end / UI testing** as a real user.

2. **The driver:** `webdriver.Chrome()` starts a browser session. Selenium 4+ even
   manages the driver binary for you (Selenium Manager), so often no manual setup.

3. **Finding elements:** `driver.find_element(By.ID, "load-btn")`,
   `By.CSS_SELECTOR`, `By.XPATH`, etc. Then `.click()`, `.send_keys("text")`,
   `.text`, `.get_attribute("src")`.

4. **Waiting (the #1 thing interviewers probe):** pages are async. **Never** sprinkle
   `time.sleep()`. Use **explicit waits**:
   ```python
   from selenium.webdriver.support.ui import WebDriverWait
   from selenium.webdriver.support import expected_conditions as EC
   WebDriverWait(driver, 10).until(
       EC.presence_of_element_located((By.ID, "preview-img")))
   ```
   This polls until the condition is true or times out. Implicit waits exist too but
   explicit waits are the recommended, predictable approach.

5. **Cleanup:** `driver.quit()` closes the browser and frees the session (use a
   fixture / `try…finally` so it always runs).

### 5.2 A Selenium test you *could* write for this project

This is the honest, impressive answer: "Here's the E2E test I'd add for the web UI."

```python
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_load_and_blur_shows_preview():
    driver = webdriver.Chrome()
    try:
        driver.get("http://localhost:8000")          # the FastAPI-served page

        # upload an image into the hidden <input type="file" id="file-input">
        driver.find_element(By.ID, "file-input").send_keys(os.path.abspath("sample.jpg"))

        # the preview <img> should appear once the file loads
        preview = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "preview-img")))
        before_src = preview.get_attribute("src")

        # click a filter button and assert the preview changed
        driver.find_element(By.XPATH, "//button[contains(., 'Sharpen')]").click()
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, "preview-img").get_attribute("src") != before_src)
    finally:
        driver.quit()
```

The narrative that ties it together: **the server under test is the FastAPI app from
section 3; Selenium drives the browser that calls it; the assertions verify the full
round-trip (UI click → `fetch` → `/filters/sharpen` → new PNG → DOM update).**
(`file-input` and the upload flow are real — see `web/EXPLAINED.md`. You'd add the
`id="preview-img"` / confirm exact selectors against `web/index.html` before relying
on them.)

### 5.3 FastAPI + Selenium together — the testing pyramid

| Layer | Tool here | Speed | What it catches |
|---|---|---|---|
| Unit | `pytest` on `processing/` functions | fastest | filter math bugs |
| Integration / API | FastAPI `TestClient` | fast | wrong status, bad contract, decode errors |
| End-to-end / UI | **Selenium** against the running server | slow | broken buttons, JS bugs, real-browser issues |

If asked "when Selenium vs. TestClient?": **TestClient verifies the API in isolation
(no browser); Selenium verifies the user-facing behavior in a real browser.** You want
many of the former and a few of the latter (classic pyramid).

---

## 6. The ML / security features (your "interesting project" story)

You don't need ML depth for a FastAPI/Selenium interview, but these make the project
memorable. One paragraph each.

- **Background removal** (`processing/ml/background_removal.py`): uses the `rembg`
  library, which wraps **U²-Net** (salient-object-detection CNN) running on ONNX
  Runtime. Produces a foreground mask, returns a transparent-background PNG (BGRA,
  alpha=0 on background). Transfer learning by reuse — no training, just inference.

- **Classification** (`processing/ml/classification.py`): **ResNet50** pretrained on
  ImageNet (1000 classes). Pipeline: BGR→RGB→preprocess→`model(batch)`→**softmax**
  logits→top-5 labels. Cached with `@lru_cache` so weights load once.

- **FGSM adversarial attack** (`POST /security/fgsm-attack`): the security flourish.
  Implements **Fast Gradient Sign Method** (Goodfellow et al., 2015): compute the
  gradient of the loss w.r.t. the *input pixels*, then nudge each pixel by
  `epsilon * sign(grad)`, bounded by an **L∞** budget so the change is imperceptible.
  Returns top-5 predictions before/after, whether the top-1 label `fooled`, the
  measured L∞ distance, and the adversarial PNG (base64). Great "I explored ML
  robustness/security" talking point.

---

## 7. Packaging / deployment

- **`Dockerfile`**: `python:3.12-slim` base, installs OpenCV system libs
  (`libgl1`, `libglib2.0-0`), pip-installs `requirements-api.txt`, copies
  `api/ processing/ web/`, runs `uvicorn api.main:app --host 0.0.0.0 --port 8000`.
- **`docker-compose.yml`**: builds the image, maps `8000:8000`, bind-mounts `./web`
  so frontend edits show up without a rebuild.
- **Run locally:** `pip install -r requirements-api.txt && uvicorn api.main:app`, then
  open `http://localhost:8000`. **Or** `docker compose up`.
- Two requirements files on purpose: `requirements-gui.txt` (lightweight, just
  Tk+OpenCV) vs. `requirements-api.txt` (adds FastAPI, Torch, rembg, test tools).

---

## 8. Talking points (say these out loud)

- "I separated **pure image-processing logic** from **transport**, so the same filter
  functions serve a desktop GUI *and* a web API."
- "FastAPI gives me **type-hint-driven validation** for free — out-of-range params get
  a 422 before my code runs."
- "I used **routers** to keep filters, ML, and security as independently-developed
  sub-apps composed in `main.py`."
- "I load heavy ML models **lazily** behind `lru_cache` so app boot and unrelated
  tests stay fast."
- "I test the API in-process with FastAPI's **`TestClient`** (asserting the contract:
  status + content-type), and I'd layer **Selenium** on top for true end-to-end
  browser tests of the web UI."
- "Centralized **exception handlers** return consistent JSON and avoid leaking stack
  traces to clients."

## 9. Likely interview questions (and the crisp answer)

- **What is FastAPI / why use it?** → Modern async Python web framework; auto request
  validation + serialization from type hints (Pydantic), auto OpenAPI docs, ASGI/async.
- **`async def` vs `def` in a route?** → `async def` runs on the event loop, good for
  I/O-bound awaits; plain `def` routes are run in a threadpool so they don't block.
- **How does file upload work?** → `UploadFile = File(...)`, multipart/form-data,
  `await file.read()` for bytes.
- **How do you validate input?** → Type hints + `Query/Path/Body(...)` constraints
  (`ge`, `le`); failures → automatic 422.
- **What's Uvicorn?** → The ASGI server that actually listens on the socket and calls
  the FastAPI app.
- **How do you test a FastAPI app?** → `TestClient` (in-process, no server) with pytest.
- **Selenium explicit vs implicit wait?** → Explicit (`WebDriverWait + expected_
  conditions`) waits for a specific condition, recommended; implicit sets a global
  poll timeout for element lookups. Avoid `time.sleep`.
- **How do you find/interact with elements in Selenium?** → `find_element(By.…)` then
  `.click()/.send_keys()/.text`; `driver.quit()` to tear down.
- **TestClient vs Selenium — when each?** → API contract in isolation vs. real-browser
  end-to-end; many of the former, few of the latter.

---

## 10. How I'd make the architecture better (the "what would you improve?" answer)

The current design is deliberately simple, and that's a defensible choice for a demo.
But interviewers love "what would you change?" — here's a tiered list, **with the most
important one being a real issue in the current code.** Lead with #1; it shows you
actually understand how async servers work.

### 10.1 ⭐ Fix the blocking event loop (the big one)

**The problem:** every handler is declared `async def`, but the work inside
(`cv2`, Pillow, Torch) is **synchronous, CPU-bound** and never `await`s anything:

```python
@router.post("/blur")
async def blur(file: UploadFile = File(...), radius: float = Query(...)):
    image = _decode_image(await file.read())          # the only real await
    return _encode_image(apply_blur_with_radius(image, radius))  # blocks the loop!
```

When an `async def` handler runs CPU-bound code without awaiting, it **hogs the single
event-loop thread** — every other in-flight request stalls until it finishes. Under
concurrent load this serializes everything. ResNet50 inference makes it dramatic.

**Two fixes (know both):**

1. **Easiest — just drop `async`.** A plain `def` handler is run by FastAPI in a
   threadpool automatically, so it won't block the loop:

   ```python
   @router.post("/blur")
   def blur(file: UploadFile = File(...), radius: float = Query(...)):
       ...
   ```

   (You'd read the file with `file.file.read()` since you're no longer in async land.)

2. **Keep `async`, offload the heavy part:** push the CPU work to a worker thread:

   ```python
   import anyio
   @router.post("/blur")
   async def blur(file: UploadFile = File(...), radius: float = Query(...)):
       data = await file.read()
       image = _decode_image(data)
       result = await anyio.to_thread.run_sync(apply_blur_with_radius, image, radius)
       return _encode_image(result)
   ```

**The rule to recite:** "Use `async def` only when the handler actually `await`s I/O.
For blocking/CPU-bound work, use plain `def` (FastAPI threadpools it) or offload with
`run_in_executor` / `anyio.to_thread`." This is *the* classic FastAPI gotcha.

### 10.2 Use Pydantic response models (and fill in the empty `schemas.py`)

`api/schemas.py` is currently empty, and `/security/fgsm-attack` returns a raw `dict`.
Define typed models so responses are validated, documented, and self-describing:

```python
# schemas.py
from pydantic import BaseModel
class Prediction(BaseModel):
    label: str
    confidence: float
class FgsmResult(BaseModel):
    epsilon: float
    linf_distance: float
    fooled: bool
    original_prediction: list[Prediction]
    adversarial_prediction: list[Prediction]
    adversarial_image_base64: str

# router
@router.post("/fgsm-attack", response_model=FgsmResult)
```

Payoff: `/docs` now shows the exact response shape, and FastAPI guarantees the contract.

### 10.3 Kill the duplication with a dependency (`Depends`)

`_decode_image` is copy-pasted into all three routers. Make it a **dependency** and
inject it — this is FastAPI's headline DI feature and a great thing to demo:

```python
async def get_image(file: UploadFile = File(...)) -> np.ndarray:
    return _decode_image(await file.read())

@router.post("/blur")
def blur(image: np.ndarray = Depends(get_image), radius: float = Query(...)):
    return _encode_image(apply_blur_with_radius(image, radius))
```

One place to change decode logic / add validation; every route inherits it.

### 10.4 Validate uploads (size + type) — security & robustness

Right now you can POST a 2 GB file or a non-image and only fail deep in OpenCV. Add an
upload guard (size cap + content-type allowlist) in that same `get_image` dependency,
returning a clean `413`/`415`. Cheap, and a good "I think about abuse cases" signal.

### 10.5 Warm up models on startup with a lifespan handler

First hit to an ML endpoint pays the multi-hundred-MB load and times out the user. Use
FastAPI's **lifespan** to load (or pre-warm) on boot, and add `/healthz` + `/readyz`:

```python
from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app):
    _load_model()        # warm ResNet50 before traffic
    yield
app = FastAPI(lifespan=lifespan)
```

(Trade-off: slower boot. For serverless you might keep it lazy. Mention you know both.)

### 10.6 Config via `pydantic-settings`, not hard-coded values

`allow_origins=["*"]`, ports, and model names are hard-coded. Move them into a
`Settings(BaseSettings)` object read from env vars, so dev/prod differ by config, and
**tighten CORS** to known origins in production.

### 10.7 Heavy jobs → background queue (for the future ML features)

Super-resolution / inpainting can take many seconds — too long for a sync HTTP request.
Pattern: endpoint enqueues a job (Celery/RQ/Arq), returns a `job_id`, client polls
`GET /jobs/{id}`. Even FastAPI's built-in `BackgroundTasks` covers the simple cases.
Shows you can scale past "everything in the request thread."

### 10.8 Smaller polish (mention if time allows)

- **API versioning** — prefix routers with `/v1` so you can evolve without breaking clients.
- **Result caching** — key on `hash(image_bytes + params)`; identical re-requests skip recompute.
- **Observability** — structured logs with a request-id, basic metrics, timing middleware.
- **Prod server** — run Uvicorn under Gunicorn with multiple workers; multi-stage,
  non-root Dockerfile.
- **Test depth** — parametrize filter tests, add the Selenium E2E layer from §5, wire
  `pytest-cov` into CI (there's already a ruff GitHub Action to model it on).

### 10.9 If asked "which would you do first?"

> "Number one is fixing the async handlers — it's a correctness/throughput issue that's
> invisible until you have concurrent load. Then response models + a shared `Depends`
> for decoding and upload validation, because they're cheap and harden the contract.
> The queue and caching I'd only add when a real heavy endpoint or real traffic
> justifies the complexity — I wouldn't over-engineer a demo."

That last sentence matters: showing you **won't gold-plate** is as valuable as the list.

---

## 11. 20-minute refresh plan (night before)

1. Re-read sections **3 (FastAPI)**, **4 (TestClient)**, **5 (Selenium)** — that's the core.
2. Run it: `uvicorn api.main:app --reload`, open `/docs`, fire a `/filters/blur` from
   the Swagger UI, watch the validation reject `radius=99`.
3. Run `pytest -q` and read `tests/test_main.py` once more.
4. Skim **section 9** as flashcards.

> Source files to peek at if you want the real thing: `api/main.py`,
> `api/routers/filters.py`, `tests/test_main.py`, `web/EXPLAINED.md`,
> `notes/DEV_NOTES.md`.
