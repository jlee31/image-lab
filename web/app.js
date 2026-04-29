// ── State ───────────────────────────────────────────────────────────────────
const API = window.location.origin;
let currentBlob = null;   // current image as Blob
let originalBlob = null;  // original loaded image
let undoStack = [];
let redoStack = [];

const preview = document.getElementById("preview");
const placeholder = document.getElementById("placeholder");
const loading = document.getElementById("loading");
const fileInput = document.getElementById("file-input");

// ── Load / Save ─────────────────────────────────────────────────────────────

function loadImage() { fileInput.click(); }

fileInput.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  originalBlob = file;
  currentBlob = file;
  undoStack = [];
  redoStack = [];
  clearHistory();
  resetSliders();
  showPreview(currentBlob);
  addHistory("Loaded: " + file.name);
  fileInput.value = "";
});

function saveImage() {
  if (!currentBlob) return alert("No image to save.");
  const a = document.createElement("a");
  const url = URL.createObjectURL(currentBlob);
  a.href = url;
  a.download = "image-lab-export.png";
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function showPreview(blob) {
  const url = URL.createObjectURL(blob);
  preview.onload = () => URL.revokeObjectURL(url);
  preview.src = url;
  preview.style.display = "block";
  placeholder.style.display = "none";
}

// ── Undo / Redo / Reset ─────────────────────────────────────────────────────

function pushUndo() {
  undoStack.push(currentBlob);
  redoStack = [];
}

function undo() {
  if (!undoStack.length) return;
  redoStack.push(currentBlob);
  currentBlob = undoStack.pop();
  showPreview(currentBlob);
  addHistory("Undo");
}

function redo() {
  if (!redoStack.length) return;
  undoStack.push(currentBlob);
  currentBlob = redoStack.pop();
  showPreview(currentBlob);
  addHistory("Redo");
}

function resetImage() {
  if (!originalBlob) return;
  pushUndo();
  currentBlob = originalBlob;
  showPreview(currentBlob);
  resetSliders();
  addHistory("Reset to original");
}

// ── Slider helpers ──────────────────────────────────────────────────────────

function updateSliderLabel(name, value) {
  const el = document.getElementById("val-" + name);
  if (name === "blur") el.textContent = value + "px";
  else el.textContent = value + "%";
}

function resetSliders() {
  ["brightness", "contrast", "saturation"].forEach(n => {
    document.getElementById("slider-" + n).value = 100;
    document.getElementById("val-" + n).textContent = "100%";
  });
  document.getElementById("slider-blur").value = 0;
  document.getElementById("val-blur").textContent = "0px";
  document.getElementById("slider-noise").value = 0;
  document.getElementById("val-noise").textContent = "0%";
}

async function applySlider(name, rawValue) {
  if (!currentBlob) return;

  // Skip no-ops
  if (name === "blur" && Number(rawValue) === 0) return;
  if (name === "noise" && Number(rawValue) === 0) return;
  if ((name === "brightness" || name === "contrast" || name === "saturation") && Number(rawValue) === 100) return;

  pushUndo();

  const form = new FormData();
  form.append("file", currentBlob, "image.png");

  let url;
  if (name === "blur") {
    url = API + "/filters/blur?radius=" + rawValue;
  } else if (name === "noise") {
    url = API + "/filters/noise?intensity=" + (rawValue / 100).toFixed(2);
  } else {
    url = API + "/filters/" + name + "?factor=" + (rawValue / 100).toFixed(2);
  }

  await sendFilter(url, form, capitalize(name) + ": " + rawValue);
}

// ── One-click filter ────────────────────────────────────────────────────────

async function applyFilter(name, prefix = "filters") {
  if (!currentBlob) return alert("Load an image first.");
  pushUndo();

  const form = new FormData();
  form.append("file", currentBlob, "image.png");

  await sendFilter(API + '/' + prefix + '/' + name, form, capitalize(name));
}

// ── API call helper ─────────────────────────────────────────────────────────

async function sendFilter(url, form, label) {
  setLoading(true);
  try {
    const res = await fetch(url, { method: "POST", body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Server error" }));
      throw new Error(err.detail || "Filter failed");
    }
    currentBlob = await res.blob();
    showPreview(currentBlob);
    addHistory(label);
  } catch (e) {
    undoStack.pop(); // revert the push
    alert("Error: " + e.message);
  } finally {
    setLoading(false);
  }
}

function setLoading(on) {
  loading.classList.toggle("visible", on);
  document.querySelectorAll(".filter-btn, .sb-btn").forEach(b => b.disabled = on);
}

// ── History ─────────────────────────────────────────────────────────────────

function addHistory(text) {
  const log = document.getElementById("history-log");
  const entry = document.createElement("div");
  entry.className = "history-entry";
  entry.textContent = text;
  log.appendChild(entry);
}

function clearHistory() {
  const log = document.getElementById("history-log");
  log.querySelectorAll(".history-entry").forEach(e => e.remove());
}

function toggleHistory() {
  document.getElementById("history-log").classList.toggle("visible");
}

// ── Collapsible cards ───────────────────────────────────────────────────────

function toggleCard(id) {
  const card = document.getElementById(id);
  card.classList.toggle("collapsed");
  const btn = card.querySelector(".toggle");
  btn.textContent = card.classList.contains("collapsed") ? "\u2228" : "\u2227";
}

// ── Drag & drop ─────────────────────────────────────────────────────────────

const canvasArea = document.getElementById("canvas-area");
canvasArea.addEventListener("dragover", e => { e.preventDefault(); canvasArea.style.outline = "2px dashed var(--accent)"; });
canvasArea.addEventListener("dragleave", () => { canvasArea.style.outline = "none"; });
canvasArea.addEventListener("drop", e => {
  e.preventDefault();
  canvasArea.style.outline = "none";
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith("image/")) {
    originalBlob = file;
    currentBlob = file;
    undoStack = [];
    redoStack = [];
    clearHistory();
    resetSliders();
    showPreview(currentBlob);
    addHistory("Loaded: " + file.name);
  }
});

// ── Keyboard shortcuts ──────────────────────────────────────────────────────

document.addEventListener("keydown", e => {
  const mod = e.metaKey || e.ctrlKey;
  if (mod && e.key === "o") { e.preventDefault(); loadImage(); }
  if (mod && e.key === "s") { e.preventDefault(); saveImage(); }
  if (mod && e.key === "z" && !e.shiftKey) { e.preventDefault(); undo(); }
  if (mod && e.key === "z" && e.shiftKey) { e.preventDefault(); redo(); }
  if (e.ctrlKey && e.key === "y") { e.preventDefault(); redo(); }
});

// ── Util ────────────────────────────────────────────────────────────────────

function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1).replaceAll("-", " "); }
