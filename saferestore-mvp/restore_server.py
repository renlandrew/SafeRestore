#!/usr/bin/env python3
"""
SafeRestore — real-model restore server.

Loads the ACTUAL trained 2.5D DeblurUNet (deblur_25d_v2.pt) and exposes it
behind a tiny HTTP endpoint so the MVP web app can run real CT restoration
instead of the in-browser phantom.

Pipeline per request (mirrors the notebook's controlled evaluation
baseline -> blur -> recover -> measure):
  1. read upload (DICOM via pydicom, or PNG/JPG via PIL)
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
import os, io, base64, math, time
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
from flask import Flask, request, jsonify
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


# ── restore one slice with the real model ────────────────────────
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


# ── IO helpers ───────────────────────────────────────────────────
def read_upload(raw, name=""):
    """returns (x01 HU-normalized [0,1], source_kind)."""
    # try DICOM first
    try:
        ds = pydicom.dcmread(io.BytesIO(raw), force=True)
        if hasattr(ds, "pixel_array"):
            hu = ds.pixel_array.astype(np.float32) * float(getattr(ds, "RescaleSlope", 1.0)) \
                 + float(getattr(ds, "RescaleIntercept", 0.0))
            x01 = (np.clip(hu, HU_MIN, HU_MAX) - HU_MIN) / HU_RANGE
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


# ── app ──────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

@app.route("/health")
def health():
    return jsonify(ok=True, model="DeblurUNet25D", ckpt=os.path.basename(CKPT),
                   in_ch=IN_CH, val_psnr=round(VAL_PSNR, 2),
                   params=sum(p.numel() for p in MODEL.parameters()))

@app.route("/restore", methods=["POST", "OPTIONS"])
def restore():
    if request.method == "OPTIONS":
        return ("", 204)
    if "file" not in request.files:
        return jsonify(error="no file"), 400
    blur_level = request.form.get("blur_level", 6.0, type=float)
    raw = request.files["file"].read()
    name = request.files["file"].filename or ""
    t0 = time.time()

    x01, kind = read_upload(raw, name)
    # resize very large slices for snappy CPU inference (keep aspect, cap 512)
    H, W = x01.shape
    if max(H, W) > 512:
        s = 512.0 / max(H, W)
        x01 = cv2.resize(x01, (int(W*s), int(H*s)), interpolation=cv2.INTER_AREA)

    deg01 = poisson_gaussian(gaussian_psf(x01, blur_level), blur_level=blur_level, seed=7)
    rec01 = restore01(deg01, blur_level)

    p_in, p_out = psnr(deg01, x01), psnr(rec01, x01)
    metrics = {
        "input_psnr": round(p_in, 2),
        "restored_psnr": round(p_out, 2),
        "delta_psnr": round(p_out - p_in, 2),
        "max_abs_change": round(float(np.max(np.abs(rec01 - deg01))), 4),
        "mean_abs_change": round(float(np.mean(np.abs(rec01 - deg01))), 5),
        "mae_to_clean": round(float(np.mean(np.abs(rec01 - x01))), 5),
        "blur_level": blur_level,
        "source": kind,
        "ms": int((time.time() - t0) * 1000),
    }
    return jsonify(
        ok=True, real=True, model="DeblurUNet25D (2.5D)", val_psnr=round(VAL_PSNR, 2),
        reference=png_b64(x01), degraded=png_b64(deg01), restored=png_b64(rec01),
        flag=flag_region(rec01, deg01), metrics=metrics,
    )

if __name__ == "__main__":
    print(f"[restore_server] http://localhost:{PORT}  (POST /restore, GET /health)")
    app.run(host="127.0.0.1", port=PORT, debug=False, threaded=True)
