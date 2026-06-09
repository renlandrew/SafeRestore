# Task Card — David · the MACHINE half of safety

**Mission:** Prove, on *real* CT, that the restoration model improves image quality **without damaging
anatomy** — and find exactly where it breaks. You make the *machine* trustworthy; Nick trains the *human*
to catch what's left.

> Read `README.md` (mission + rules) first. You own the **Use** surface + the machine-side safety evidence.

## Your research question & hypothesis
- **Question:** Does the restoration model improve quality on real low-dose CT while preserving structure?
- **Hypothesis:** It improves PSNR/SSIM and preserves anatomy at low–moderate degradation, but becomes
  unsafe (over-corrects / hallucinates) past some degradation level.

## What to do (each step has a "done =")
**Step 1 — Get it running (Week 0–1)**
- Run `restore_server.py` on the CT folder Andrew gives you; restore one slice.
- **done =** you can show one real CT → restored, with a real +dB number.

**Step 2 — Your baseline numbers (Week 1)**
- Run degrade→restore→measure on **≥30 real slices**. Log PSNR/SSIM gain, mean/max change per slice.
- Bucket each as **rescue / neutral / iatrogenic (made-worse)**.
- **done =** a saved CSV + counts (e.g. "22 rescue / 5 neutral / 3 iatrogenic").

**Step 3 — Your experiment: dose–response (Week 2) ← this is your core science**
- Vary degradation (`blur_level` 2→8). For each level, measure mean PSNR gain **and** iatrogenic rate.
- **done =** one figure: "benefit & damage vs degradation level," with the safe-zone / danger-zone marked.

**Step 4 — Failure catalog (Week 2–3)**
- Collect the worst cases. For each: the image + one line on *why* it failed (edge? small vessel?).
- **done =** ≥5 documented failures. These are the **threat model** — hand them to Nick; they become exactly what his human-side training defends against.

**Step 5 — Safety Report + demo (Week 3–4)**
- 1 page: what the evidence shows · **what it does NOT prove** · the Phase-1 boundary.
- Tune the Use surface to look clean on a real slice; record a 30–45s demo clip for the video.
- **done =** report PDF + demo clip.

## Resources you'll mainly use
`saferestore-mvp/restore_server.py` · the CT folder from Andrew · Worksheet Parts 4, 6, 7 · the Mayo/Dice
prior numbers (to compare your results against).

## Your guardrails (on top of the team rules)
- **Do NOT train or modify the model.** You validate the given one. Your contribution is the *experiment*.
- **Real vs phantom:** all your headline numbers must be on REAL CT. The phantom is only the offline demo.
- **Timebox:** ~2 weeks of experiments, then freeze. A clean dose-response curve + 5 failures is enough.
- **Reproducible:** keep the seed fixed, save every CSV, date your log.

## What you deliver to the pitch
- The **live MVP demo** (the high point of the video): real CT in → restored → +X dB → amber "review" flag.
- The **safety claim with evidence:** "we tested N slices; it helps in the safe zone, and here's the
  failure we found and disclose."

## Judge questions to prep
- "How do you know it isn't hallucinating?" → failure catalog + anatomy-preservation data.
- "Why not just trust the big vendors?" → we're the **independent evidence layer**, vendor-neutral.
- "What's the number behind that slide?" → know it cold.
