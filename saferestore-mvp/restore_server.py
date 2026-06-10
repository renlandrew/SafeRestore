#!/usr/bin/env python3
"""
SafeRestore — real-model restore server.

Loads the ACTUAL trained 2.5D DeblurUNet (deblur_25d_v2.pt) and exposes it
behind a tiny HTTP endpoint so the MVP web app can run real CT restoration
instead of the in-browser phantom.

Pipeline per request (mirrors the notebook's controlled evaluation
baseline -> blur -> recover -> measure):
  1. read upload (DICOM folder/volume via pydicom, or PNG/JPG slice via PIL)
  2. map to the model's HU-normalized [0,1] space
  3. degrade with the real forward model (gaussian PSF + quarter-dose
     Poisson-Gaussian noise) so we have a clean reference for PSNR
  4. restore with the trained DeblurUNet
  5. measure PSNR / MAE / max-abs-change in HU-01 space (matches the
     notebook's Mayo magnitudes, e.g. ~0.003 mean change)
  6. return windowed PNGs + real metrics + the largest-change region
     (the "needs radiologist review" flag, computed from the real model)

Run:
  pip install flask flask-cors torch pydicom pillow opencv-python numpy
  python3 restore_server.py            # serves on http://localhost:5005
Env:
  DEBLUR_CKPT  path to weights (default: ~/Downloads/deblur_25d_v2.pt)
  PORT         default 5005
"""
import os, io, base64, math, time, threading, uuid
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_LOCAL_CKPT = os.path.join(_HERE, "deblur_25d_v2.pt")   # bundled next to this script in the repo
CKPT = os.environ.get("DEBLUR_CKPT") or (
    _LOCAL_CKPT if os.path.exists(_LOCAL_CKPT) else os.path.expanduser("~/Downloads/deblur_25d_v2.pt"))
PORT = int(os.environ.get("PORT", "5005"))

# ── constants from the notebook ──────────────────────────────────
HU_MIN, HU_MAX = -1024.0, 3072.0
HU_RANGE = HU_MAX - HU_MIN
BLUR_LEVEL_MAX = 8.0
DIFFUSION_ALPHA = 0.20
WIN_C, WIN_W = 40.0, 400.0          # display window (soft-tissue/brain-ish)

import torch
import torch.nn as nn
import cv2
import pydicom
from PIL import Image
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS


# ── model (plain 2.5D DeblurUNet — matches the checkpoint exactly) ─
class _ConvBlock(nn.Module):
    def __init__(self, i, o):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(i, o, 3, padding=1, bias=False), nn.BatchNorm2d(o), nn.ReLU(True),
            nn.Conv2d(o, o, 3, padding=1, bias=False), nn.BatchNorm2d(o), nn.ReLU(True))
    def forward(self, x): return self.conv(x)

class DeblurUNet25D(nn.Module):
    """in = [prev, center, next, blur_level_map]; residual on the center channel."""
    def __init__(self, in_ch=4, out_ch=1, base=32):
        super().__init__()
        c = [base, base*2, base*4, base*8]
        self.enc1, self.enc2 = _ConvBlock(in_ch, c[0]), _ConvBlock(c[0], c[1])
        self.enc3, self.enc4 = _ConvBlock(c[1], c[2]), _ConvBlock(c[2], c[3])
        self.pool = nn.MaxPool2d(2)
        self.up3, self.dec3 = nn.ConvTranspose2d(c[3], c[2], 2, stride=2), _ConvBlock(c[2]*2, c[2])
        self.up2, self.dec2 = nn.ConvTranspose2d(c[2], c[1], 2, stride=2), _ConvBlock(c[1]*2, c[1])
        self.up1, self.dec1 = nn.ConvTranspose2d(c[1], c[0], 2, stride=2), _ConvBlock(c[0]*2, c[0])
        self.out_conv = nn.Conv2d(c[0], out_ch, 1)
    def forward(self, x):
        e1 = self.enc1(x); e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2)); e4 = self.enc4(self.pool(e3))
        d3 = self.dec3(torch.cat([self.up3(e4), e3], 1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], 1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], 1))
        return x[:, 1:2] + self.out_conv(d1)


def load_model():
    ck = torch.load(CKPT, map_location="cpu", weights_only=False)
    m = DeblurUNet25D(in_ch=int(ck.get("in_ch", 4)), out_ch=1, base=int(ck.get("base", 32)))
    m.load_state_dict(ck["model"])
    m.eval()
    return m, float(ck.get("val_psnr", float("nan"))), int(ck.get("in_ch", 4))

MODEL, VAL_PSNR, IN_CH = load_model()
print(f"[restore_server] loaded {CKPT}  in_ch={IN_CH}  val_psnr={VAL_PSNR:.2f}  "
      f"params={sum(p.numel() for p in MODEL.parameters()):,}")


# ── degradation forward model (real, from the notebook) ──────────
def gaussian_psf(img01, blur_level, alpha=DIFFUSION_ALPHA):
    if blur_level <= 0: return img01.copy()
    sigma = math.sqrt(max(1e-8, 2.0 * alpha * float(blur_level)))
    return np.clip(cv2.GaussianBlur(img01, (0, 0), sigma, borderType=cv2.BORDER_REPLICATE), 0, 1)

def poisson_gaussian(img01, blur_level=3.0, seed=0):
    # Noise co-varies with blur_level so the (blur, dose) pair stays inside the
    # model's training joint distribution (heavy blur => quarter-dose noise).
    t = min(1.0, max(0.0, blur_level / BLUR_LEVEL_MAX))
    peak = 1400.0 - 1150.0 * t          # high blur -> lower photon count (noisier)
    sigma_g = 0.0015 + 0.0045 * t
    rng = np.random.default_rng(seed)
    p = rng.poisson(np.clip(img01 * peak, 0, None)).astype(np.float32) / peak
    return np.clip(p + rng.normal(0, sigma_g, img01.shape).astype(np.float32), 0, 1)


# ── restore slices with the real model ───────────────────────────
def restore01(deg01, blur_level):
    H, W = deg01.shape
    pH, pW = math.ceil(H/16)*16, math.ceil(W/16)*16
    pad = np.zeros((pH, pW), np.float32); pad[:H, :W] = deg01
    t = float(blur_level) / BLUR_LEVEL_MAX
    tmap = np.full_like(pad, t)
    inp = np.stack([pad, pad, pad, tmap], 0)[None]          # single slice -> neighbors = center
    with torch.no_grad():
        out = MODEL(torch.from_numpy(inp))[0, 0, :H, :W].numpy()
    return np.clip(out, 0, 1)

def restore_volume01(deg_vol01, blur_level, batch_size=8, progress=None):
    """Run the 2.5D model across a CT volume using real prev/center/next slices."""
    n, H, W = deg_vol01.shape
    pH, pW = math.ceil(H/16)*16, math.ceil(W/16)*16
    padded = np.zeros((n, pH, pW), np.float32)
    padded[:, :H, :W] = deg_vol01
    t = float(blur_level) / BLUR_LEVEL_MAX
    tmap = np.full((pH, pW), t, np.float32)
    outs = []

    for start in range(0, n, batch_size):
        rows = []
        for i in range(start, min(start + batch_size, n)):
            prev_i = max(0, i - 1)
            next_i = min(n - 1, i + 1)
            rows.append(np.stack([padded[prev_i], padded[i], padded[next_i], tmap], 0))
        inp = np.stack(rows, 0)
        with torch.no_grad():
            out = MODEL(torch.from_numpy(inp))[:, 0, :H, :W].numpy()
        outs.append(out)
        if progress:
            progress(min(start + batch_size, n), n)

    return np.clip(np.concatenate(outs, axis=0), 0, 1)


# ── IO helpers ───────────────────────────────────────────────────
def read_dicom(raw, name=""):
    ds = pydicom.dcmread(io.BytesIO(raw), force=True)
    if not hasattr(ds, "pixel_array"):
        raise ValueError("DICOM has no pixel data")

    arr = ds.pixel_array.astype(np.float32)
    slope = float(getattr(ds, "RescaleSlope", 1.0))
    intercept = float(getattr(ds, "RescaleIntercept", 0.0))

    meta = {
        "name": name,
        "instance": _meta_number(getattr(ds, "InstanceNumber", None)),
        "slice_location": _meta_number(getattr(ds, "SliceLocation", None)),
        "z": None,
    }
    ipp = getattr(ds, "ImagePositionPatient", None)
    if ipp is not None and len(ipp) >= 3:
        meta["z"] = _meta_number(ipp[2])

    hu = arr * slope + intercept
    x01 = (np.clip(hu, HU_MIN, HU_MAX) - HU_MIN) / HU_RANGE
    return x01.astype(np.float32), meta

def _meta_number(v):
    try:
        return float(v)
    except Exception:
        return None

def read_upload(raw, name=""):
    """returns (x01 HU-normalized [0,1], source_kind)."""
    # try DICOM first
    try:
        x01, _ = read_dicom(raw, name)
        if x01.ndim == 2:
            return x01.astype(np.float32), "dicom"
    except Exception:
        pass
    # fallback: ordinary image -> assume it is a windowed display image,
    # invert the display window to put it back into HU-01 model space.
    img = Image.open(io.BytesIO(raw)).convert("L")
    d01 = np.asarray(img, np.float32) / 255.0
    hu = d01 * WIN_W + (WIN_C - WIN_W / 2.0)
    x01 = (np.clip(hu, HU_MIN, HU_MAX) - HU_MIN) / HU_RANGE
    return x01.astype(np.float32), "image"

def dicom_sort_key(item):
    meta = item["meta"]
    if meta["z"] is not None:
        return (0, meta["z"], meta["name"])
    if meta["slice_location"] is not None:
        return (1, meta["slice_location"], meta["name"])
    if meta["instance"] is not None:
        return (2, meta["instance"], meta["name"])
    return (3, meta["name"])

def read_request_scan(files):
    """Return (volume01[N,H,W], source_kind, source_count)."""
    dicoms = []
    for f in files:
        name = f.filename or ""
        raw = f.read()
        if not raw:
            continue
        try:
            x01, meta = read_dicom(raw, name)
            if x01.ndim == 2:
                dicoms.append({"x01": x01, "meta": meta})
            elif x01.ndim == 3:
                for i, sl in enumerate(x01):
                    frame_meta = dict(meta)
                    frame_meta["instance"] = (meta["instance"] or 0) + i
                    frame_meta["name"] = f"{name}#{i}"
                    dicoms.append({"x01": sl, "meta": frame_meta})
        except Exception:
            if len(files) == 1:
                x01, kind = read_upload(raw, name)
                return x01[None, ...], kind, 1

    if not dicoms:
        raise ValueError("no readable DICOM slices found in upload")

    dicoms.sort(key=dicom_sort_key)
    target_h, target_w = dicoms[0]["x01"].shape
    slices = []
    for item in dicoms:
        sl = item["x01"]
        if sl.shape != (target_h, target_w):
            sl = cv2.resize(sl, (target_w, target_h), interpolation=cv2.INTER_AREA)
        slices.append(sl.astype(np.float32))

    kind = "dicom_volume" if len(slices) > 1 else "dicom"
    return np.stack(slices, axis=0), kind, len(slices)

def resize_volume_for_inference(vol01, max_side=512):
    n, H, W = vol01.shape
    if max(H, W) <= max_side:
        return vol01
    s = float(max_side) / max(H, W)
    new_size = (int(W * s), int(H * s))
    return np.stack([cv2.resize(sl, new_size, interpolation=cv2.INTER_AREA) for sl in vol01], axis=0)

def window_disp(x01):
    """HU-01 [0,1] -> windowed display [0,1] for the eye."""
    hu = x01 * HU_RANGE + HU_MIN
    return np.clip((hu - (WIN_C - WIN_W/2.0)) / WIN_W, 0, 1)

def png_b64(x01):
    d = (window_disp(x01) * 255.0).astype(np.uint8)
    ok, buf = cv2.imencode(".png", d)
    return "data:image/png;base64," + base64.b64encode(buf.tobytes()).decode()

def psnr(a, b):
    mse = float(np.mean((a - b) ** 2))
    return 99.0 if mse < 1e-9 else 10.0 * math.log10(1.0 / mse)

def flag_region(rec01, deg01):
    """largest-change location = the 'needs review' flag, from the real model."""
    diff = cv2.GaussianBlur(np.abs(rec01 - deg01), (0, 0), 3)
    y, x = np.unravel_index(int(np.argmax(diff)), diff.shape)
    H, W = diff.shape
    return {"x": round(x / W, 4), "y": round(y / H, 4)}

def degrade_volume(vol01, blur_level, progress=None):
    out = []
    for i, sl in enumerate(vol01):
        out.append(poisson_gaussian(gaussian_psf(sl, blur_level), blur_level=blur_level, seed=7 + i))
        if progress:
            progress(i + 1, len(vol01))
    return np.stack(out, axis=0)


# ── app ──────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

PROGRESS = {}
PROGRESS_LOCK = threading.Lock()

def set_progress(job_id, **fields):
    if not job_id:
        return
    with PROGRESS_LOCK:
        state = PROGRESS.setdefault(job_id, {})
        state.update(fields)
        state["updated_at"] = time.time()

@app.route("/")
def index():
    return send_from_directory(_HERE, "index.html")

@app.route("/sample_ct.dcm")
def sample_ct():
    return send_from_directory(_HERE, "sample_ct.dcm")

@app.route("/health")
def health():
    return jsonify(ok=True, model="DeblurUNet25D", ckpt=os.path.basename(CKPT),
                   in_ch=IN_CH, val_psnr=round(VAL_PSNR, 2),
                   params=sum(p.numel() for p in MODEL.parameters()))

@app.route("/progress/<job_id>")
def progress(job_id):
    with PROGRESS_LOCK:
        state = dict(PROGRESS.get(job_id, {}))
    if not state:
        return jsonify(ok=False, phase="waiting", done=0, total=0, percent=0)
    state["ok"] = True
    return jsonify(state)

@app.route("/restore", methods=["POST", "OPTIONS"])
def restore():
    if request.method == "OPTIONS":
        return ("", 204)
    upload_files = request.files.getlist("files") or request.files.getlist("file")
    if not upload_files:
        return jsonify(error="no file"), 400
    blur_level = request.form.get("blur_level", 6.0, type=float)
    job_id = request.form.get("job_id") or uuid.uuid4().hex
    t0 = time.time()
    set_progress(job_id, phase="reading", done=0, total=0, percent=0, label="reading DICOM files")

    try:
        vol01, kind, source_count = read_request_scan(upload_files)
    except Exception as e:
        set_progress(job_id, phase="error", done=0, total=0, percent=0, label=str(e))
        return jsonify(error=str(e)), 400

    vol01 = resize_volume_for_inference(vol01)
    n_slices = int(len(vol01))
    set_progress(job_id, phase="degrading", done=0, total=n_slices, percent=5, label=f"preparing {n_slices} slice(s)")
    deg_vol01 = degrade_volume(
        vol01,
        blur_level,
        progress=lambda done, total: set_progress(
            job_id,
            phase="degrading",
            done=int(done),
            total=int(total),
            percent=5 + int(25 * done / max(total, 1)),
            label=f"degrading slice {done} of {total}",
        ),
    )
    set_progress(job_id, phase="restoring", done=0, total=n_slices, percent=35, label=f"restoring 0 of {n_slices} slice(s)")
    rec_vol01 = restore_volume01(
        deg_vol01,
        blur_level,
        progress=lambda done, total: set_progress(
            job_id,
            phase="restoring",
            done=int(done),
            total=int(total),
            percent=35 + int(60 * done / max(total, 1)),
            label=f"restoring slice {done} of {total}",
        ),
    )
    set_progress(job_id, phase="measuring", done=n_slices, total=n_slices, percent=97, label="measuring output")

    display_idx = int(len(vol01) // 2)
    x01 = vol01[display_idx]
    deg01 = deg_vol01[display_idx]
    rec01 = rec_vol01[display_idx]

    p_in, p_out = psnr(deg_vol01, vol01), psnr(rec_vol01, vol01)
    metrics = {
        "input_psnr": round(p_in, 2),
        "restored_psnr": round(p_out, 2),
        "delta_psnr": round(p_out - p_in, 2),
        "max_abs_change": round(float(np.max(np.abs(rec_vol01 - deg_vol01))), 4),
        "mean_abs_change": round(float(np.mean(np.abs(rec_vol01 - deg_vol01))), 5),
        "mae_to_clean": round(float(np.mean(np.abs(rec_vol01 - vol01))), 5),
        "blur_level": blur_level,
        "source": kind,
        "slices": int(len(vol01)),
        "source_files": int(source_count),
        "display_slice": int(display_idx + 1),
        "ms": int((time.time() - t0) * 1000),
    }
    set_progress(job_id, phase="done", done=n_slices, total=n_slices, percent=100, label=f"done: {n_slices} slice(s)")
    return jsonify(
        ok=True, real=True, model="DeblurUNet25D (2.5D)", val_psnr=round(VAL_PSNR, 2),
        job_id=job_id,
        reference=png_b64(x01), degraded=png_b64(deg01), restored=png_b64(rec01),
        flag=flag_region(rec01, deg01), metrics=metrics,
    )

if __name__ == "__main__":
    print(f"[restore_server] http://localhost:{PORT}  (POST /restore, GET /health)")
    app.run(host="127.0.0.1", port=PORT, debug=False, threaded=True)
