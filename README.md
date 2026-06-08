# SafeRestore

**The trust layer for CT-restoration AI** — one engine (*degrade ⇄ restore ⇄ evidence*) with three
surfaces: **prove** a model is safe, **use** it to restore real CT, **teach** people to catch AI errors.
Thesis: **evidence, not images.**

This repo is self-contained — clone it and you have the **frontend + backend + the trained model**.

## What's inside
```
saferestore-mvp/
  index.html          frontend — the web app (works offline on its own)
  restore_server.py   backend — runs the real trained model on real CT
  deblur_25d_v2.pt    the trained 2.5D DeblurUNet weight (bundled, val PSNR 37.42 dB)
  sample_ct.dcm       a real anonymized CT slice for a one-click demo
team/                 the student task package (start at team/THIS-WEEK.md)
```

## Quick start

### Frontend only (offline, zero setup)
Open `saferestore-mvp/index.html` in a browser. Phantom demo runs entirely in-browser.

### Frontend + backend (the real model on real CT)
```bash
# 1) backend — install once, then run (the weight is already bundled)
pip install -r saferestore-mvp/requirements.txt
python3 saferestore-mvp/restore_server.py            # http://localhost:5005

# 2) frontend — serve the page over http, then open it
python3 -m http.server 4178 --directory saferestore-mvp
#   → open http://localhost:4178
```
In **Use · Studio** the status turns green (`● real model: DeblurUNet25D`). Click **Load sample CT** →
**Run SafeRestore** to restore real CT with real metrics. Full details: `saferestore-mvp/README.md`.

## Students start here
👉 **`team/THIS-WEEK.md`** is your assignment. Read `team/README.md` for the rules. Your task cards are
`team/TASK-David.md` / `team/TASK-Nick.md`.

## Boundary
Research / QA / education only. **Not** for diagnosis, **not** a medical device, **not** for direct
clinical interpretation. Every restored image carries a "radiologist review required" flag.
