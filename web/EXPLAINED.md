# Web Frontend - Explained

Everything lives in a single `index.html` file. No build tools, no npm, no frameworks.
Here's a breakdown of every piece.

---

## Structure Overview

The file has three sections:
1. **HTML** - the page structure (what you see)
2. **CSS** (inside `<style>`) - the styling (how it looks)
3. **JavaScript** (inside `<script>`) - the logic (how it works)

---

## HTML Structure

### Header
```
.header  >  .header-icon  +  .header-text (h1 + p)
```
The purple icon + "Image Lab" title bar at the top. Matches the desktop GUI header exactly.

### Main Layout (3-column flexbox)
```
.main  >  .sidebar  +  .canvas-area  +  .right-panel
```
- **Sidebar** (left, 215px) - Quick Actions (Load/Save), History (Undo/Redo/Reset), View History toggle
- **Canvas Area** (centre, flex: 1) - Shows the image preview or a placeholder when no image is loaded
- **Right Panel** (right, 295px) - Adjustments sliders + Creative Filters buttons + AI Features

### Hidden Elements
- `#file-input` - A hidden `<input type="file">` that opens the OS file picker when "Load Image" is clicked
- `#loading` - A semi-transparent overlay that shows "Processing..." during API calls
- `#placeholder` - The "No image loaded" message, hidden once an image is loaded

---

## CSS - How It Looks

### Colour Tokens
All colours are defined as CSS variables in `:root { }` and match the desktop GUI's `AppWindow` class:
- `--bg: #F5F5F7` - page background (light grey)
- `--card: #FFFFFF` - card/panel backgrounds (white)
- `--primary: #18181B` - dark buttons (Load Image, slider thumbs)
- `--accent: #7C3AED` - purple accent (header icon, AI buttons)
- `--border: #E5E7EB` - borders and dividers
- `--text-muted: #9CA3AF` - secondary/hint text

### Layout
Uses CSS Flexbox throughout:
- `body` is a vertical flex (header on top, main below)
- `.main` is a horizontal flex (sidebar | canvas | right panel)
- `.sidebar` and `.right-panel` have fixed widths; `.canvas-area` stretches to fill

### Slider Styling
The `input[type="range"]` is styled with `-webkit-appearance: none` to replace the browser default.
The thumb is a dark circle (`--primary`), the track is a light pill (`--border`).

### Collapsible Cards
Cards use a `.collapsed` CSS class. When collapsed, `.card-content` gets `display: none`.
The toggle button switches between up-arrow and down-arrow characters.

---

## JavaScript - How It Works

### State Management
```js
let currentBlob = null;   // the image you're currently editing (as a Blob)
let originalBlob = null;  // the image you originally loaded (for Reset)
let undoStack = [];        // previous versions of currentBlob
let redoStack = [];        // versions you've undone (for Redo)
```
Images are stored as **Blobs** (binary data in memory). Every time you apply a filter,
the old image is pushed to `undoStack`, and the new result from the API becomes `currentBlob`.

### How Filters Work (the key flow)

1. User clicks a filter button (e.g. "Sharpen")
2. `applyFilter("sharpen")` is called
3. Current image blob is pushed to undo stack
4. A `FormData` is created with the image blob as a file upload
5. `fetch()` sends a POST request to `/filters/sharpen` with the image
6. The API processes the image and returns a new PNG
7. The response is read as a blob (`res.blob()`)
8. `currentBlob` is updated, and `showPreview()` displays it via `URL.createObjectURL()`

### Slider Filters
Same flow, but the URL includes a query parameter:
- Brightness/Contrast/Saturation: slider value 0-200 maps to factor 0.0-2.0
  - e.g. slider at 150 -> `POST /filters/brightness?factor=1.50`
- Blur: slider value is the radius directly (1-10)
  - e.g. `POST /filters/blur?radius=5`
- Noise: slider value 0-100 maps to intensity 0.0-1.0
  - e.g. slider at 30 -> `POST /filters/noise?intensity=0.30`

Sliders use `oninput` (updates the label as you drag) and `onchange` (fires the API call on release).

### Undo / Redo
- **Undo**: pops from `undoStack`, pushes current to `redoStack`
- **Redo**: pops from `redoStack`, pushes current to `undoStack`
- **Reset**: pushes current to undo, sets current back to `originalBlob`
- Any new filter action clears the `redoStack` (just like the desktop GUI)

### Save Image
Creates a temporary `<a>` element with `download` attribute pointing to a blob URL, then clicks it.
This triggers the browser's file download dialog.

### Drag & Drop
The canvas area listens for `dragover`, `dragleave`, and `drop` events.
When you drop an image file, it loads it the same way the file picker does.

### Keyboard Shortcuts
Matches the desktop GUI:
- `Ctrl/Cmd + O` - Load Image
- `Ctrl/Cmd + S` - Save Image
- `Ctrl/Cmd + Z` - Undo
- `Shift + Ctrl/Cmd + Z` or `Ctrl + Y` - Redo

### Loading State
While an API call is in progress:
- A semi-transparent overlay shows "Processing..."
- All buttons are disabled to prevent double-clicks

### Error Handling
If the API returns an error, the undo stack entry is popped (reverting state),
and an alert shows the error message.

---

## How It Connects to the API

The frontend assumes the API is running at the same origin (same host:port).
This is because FastAPI serves `index.html` at `/` and mounts the `web/` folder at `/static`.

When running with Docker:
```
Browser -> http://localhost:8000      -> serves index.html
Browser -> http://localhost:8000/filters/blur  -> API endpoint
```

Both are served from the same FastAPI server, so no cross-origin issues.

### API Endpoints Used

| Frontend Action       | API Endpoint                          |
|-----------------------|---------------------------------------|
| Brightness slider     | `POST /filters/brightness?factor=X`  |
| Contrast slider       | `POST /filters/contrast?factor=X`    |
| Saturation slider     | `POST /filters/saturation?factor=X`  |
| Blur slider           | `POST /filters/blur?radius=X`        |
| Noise slider          | `POST /filters/noise?intensity=X`    |
| Sharpen button        | `POST /filters/sharpen`              |
| Glitch button         | `POST /filters/glitch`               |
| Invert button         | `POST /filters/invert`               |
| Vignette button       | `POST /filters/vignette`             |
| Pixelate button       | `POST /filters/pixelate`             |
| Retro button          | `POST /filters/retro`                |
| Pencil button         | `POST /filters/pencil`               |
| Smart Enhance button  | `POST /filters/smart-enhance`        |

All endpoints accept a `multipart/form-data` POST with a `file` field (the image),
and return a PNG image as the response body.
