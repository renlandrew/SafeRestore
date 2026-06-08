# Resources — what you're getting to start

Everything below is handed to you so you do **not** start from zero. Your job is to build *on top*,
not rebuild it.

## 1. The working MVP (your demo + your tools)
- `saferestore-mvp/index.html` — the app. Offline phantom demo: just open it.
- `saferestore-mvp/restore_server.py` — runs the **real trained model** on real CT.
- `saferestore-mvp/sample_ct.dcm` — a real anonymized CT slice (one-click demo).
- Run instructions: `saferestore-mvp/README.md` (two modes: offline, and real-model).

## 2. The real model + data
- **Model weight:** `deblur_25d_v2.pt` (2.5D DeblurUNet, val PSNR 37.42 dB) — **already bundled in the
  repo** at `saferestore-mvp/`. The server finds it automatically; no setup needed.
- **CT data:** for David's experiments Andrew sends a folder of de-identified CT slices separately
  (medical data does not go in the repo). Backup real CT is bundled (`sample_ct.dcm`) and in pydicom's test files.
- ⚠️ Use only the CT data Andrew gives you. Do not download patient data from anywhere else.

## 3. Prior evidence you may cite (read-only — this is the team's earlier validation)
From our research notebook (cite as "prior internal validation"):
- Task rescue (CRM, N=50 held-out): **+0.0324** mean target gain — best vs 4 classical filters.
- External real CT (Mayo paired): **+2.35 dB PSNR** (95% CI 2.03–2.67), 100% win.
- Anatomy (Dice vs full-dose): **0.6137 → 0.7395**.
- Stability (Monte Carlo, 1000 runs): net-positive but **62% noise-sensitive** (disclosed honestly).
> You cite these as background, but **David must also generate his own numbers** on his own data.

## 4. The business/pitch content you already wrote
- The completed **Worksheet Part 1–10** (thesis, customer, market, product, evidence, competition,
  regulatory, impact, pitch). This *is* your Ventura framework, half-done. Reuse it.

## 5. Source starter pack (for market/regulatory claims — cite these, don't invent stats)
- CT scale & device variation: CADTH/NCBI Canadian Medical Imaging Inventory — https://www.ncbi.nlm.nih.gov/books/NBK607343/
- FDA AI-enabled medical devices — https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices
- Health Canada SaMD guidance — https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/application-information/guidance-documents/software-medical-device-guidance-document.html
- AAPM Low-Dose CT Grand Challenge (why task-based eval > PSNR/SSIM) — https://www.aapm.org/GrandChallenge/LowDoseCT/

## 6. Ventura
- Site: https://ventura-innovation.com — register Jun 15. Read the Submission & Judges pages when live.
- Framework to hit: problem · solution · target market · business model · real-world impact.

## Who to ask
- Stuck > 1 hour on the same thing? Bring me a **specific** question + what you already tried.
- Use Ventura's Workshop-Month mentors too — show them the MVP and ask for pitch feedback.
