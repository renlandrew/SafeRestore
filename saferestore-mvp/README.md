# SafeRestore — MVP web app

**One engine, three surfaces.** A self-contained web app that makes the integrated SafeRestore
story demoable — and the **Use** surface now runs the **actual trained DeblurUNet model** on **real CT data**,
not just a phantom.

---

## Two ways to run

### 1. Offline phantom demo (zero setup, works anywhere)
```bash
open saferestore-mvp/index.html        # or double-click
```
Everything runs in the browser: a procedural CT phantom is degraded → restored (edge-preserving
bilateral) → PSNR measured live on `<canvas>`. Good for pitching on any laptop with no internet.

### 2. Real-model mode (runs the trained network on real CT)
```bash
# terminal A — start the model server (loads deblur_25d_v2.pt)
pip install flask flask-cors torch pydicom pillow opencv-python numpy   # one time
python3 saferestore-mvp/restore_server.py        # serves http://localhost:5005

# then open the app served by Flask
#   → open http://localhost:5005
#
# Optional: serve the page separately over http if you prefer
python3 -m http.server 4178 --directory saferestore-mvp
#   → open http://localhost:4178
```
In the **Use · Studio** tab the status pill turns green (`● real model: DeblurUNet25D · val 37.42 dB`).
Click **Load sample CT** (a real bundled DICOM) → **Run SafeRestore**. The image is sent to the server,
degraded with the real physics forward model, restored by the trained network, and you get **real metrics**
(e.g. +4.22 dB on the sample) plus the model's actual largest-change region as the "needs review" flag.
You can also **Upload 3D CT folder** with a DICOM series of your own. The server sorts the slices, runs
the 2.5D model with real prev/center/next slice context, reports volume-level metrics, and displays a
representative denoised slice. If the server is off, the app silently falls back to the offline phantom
— the demo never breaks.

---

## What it shows

| Surface | Owner | What a judge sees |
|---|---|---|
| **Engine** (home) | shared core | The thesis + the 4 validated evidence layers from the notebook |
| **Use · Studio** | **David** | **Real trained model** restoring **real CT** (or phantom offline); every output ships with an evidence panel + a real "needs review" flag |
| **Prove · Evidence** | **Andrew** | Pick any model → 4-layer Evidence Pack, Evidence Score vs all baselines, failure audit, risk memo, exportable `.json` |
| **Teach · Academy** | **Nick** | "Spot the hallucination" lab + a degradation slider showing why *looks-sharper ≠ correct* |

Header **▶ Run the aha demo** auto-tours one scan through all three surfaces (uses the offline phantom so it
always works).

---

## The real model (`restore_server.py`)

- Loads `deblur_25d_v2.pt` — a **2.5D DeblurUNet** (`in_ch=4`, `base=32`, 1.93M params, val PSNR 37.42 dB).
  Input channels = `[prev_slice, center_slice, next_slice, blur_level_map]`; residual on the center channel.
- Per request it runs the notebook's controlled loop: **read DICOM series → sort/stack slices → map to HU-normalized [0,1] → degrade
  (gaussian PSF + dose-matched Poisson-Gaussian noise) → restore → measure**. Metrics are in HU-01 space,
  matching the notebook's Mayo magnitudes (mean change ~0.01–0.02).
- DICOM is read with true HU (slope/intercept). Single-slice DICOM and PNG/JPG are still accepted by the
  server for fallback/sample use.
- Endpoints: `GET /health`, `POST /restore` (multipart `files` DICOM series or `file` fallback + optional
  `blur_level`). CORS open.
- Env: `DEBLUR_CKPT` (default `~/Downloads/deblur_25d_v2.pt`), `PORT` (default 5005).

### Honest note on the model + data
The trained net is a denoiser/deblurrer for **real CT**. On the cartoon phantom it is out-of-distribution
(it "corrects" unrealistic edges, which scores as change) — that's why **real-model mode uses real CT**
(`sample_ct.dcm`, a public anonymized slice shipped with pydicom) and the phantom path uses the in-browser
bilateral filter. Numbers shown are computed live; the headline evidence figures in **Prove** are the real
notebook results (`CRM` / `FACTS` in `index.html`).

---

## Phase-1 boundary (baked into the UI)
Research / QA / model-validation / education artifacts only. **Not** diagnosis, **not** a cleared device,
**not** for direct clinical interpretation. Every restored image carries a "radiologist review required" flag.

## Where each owner takes it next
- **David / Use:** point `restore_server.py` at a real low-dose/full-dose paired set; add streaming/progress for large multi-slice DICOM volumes.
- **Andrew / Prove:** turn `prove()` into a real call to a `/validate` endpoint that runs the 4 layers on an uploaded model's outputs.
- **Nick / Teach:** make the capstone require students to run Use + Prove on a real case and submit the exported Evidence Pack.

**Integration contract:** every surface speaks the same `degrade()` / `restore()` / `score_evidence()` — keep that stable and the three products stay one product.

## Files
```
index.html          the app (single file, offline-capable)
restore_server.py   Flask server that runs the real trained DeblurUNet
sample_ct.dcm       a real anonymized CT slice for one-click real-model demo
README.md           this file
```
