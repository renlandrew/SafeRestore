# SafeRestore — MVP Overview

**Mission:** *Safe AI-assisted CT reading = a machine you can trust **+** a human who can catch it.*
**Machine half = David** (Core / Use / Prove — make the model trustworthy) · **Human half = Nick**
(Teach — train the reader to catch the model's residual errors). **One failure, two defenses.**

---

## How it works · what runs today · what to build next

| Module | How it works (principle) | What works now (verified) | What to build on it (owner) |
|---|---|---|---|
| **Core + backend**<br>`restore_server.py` | Loads the **real** model, a **2.5D DeblurUNet** (4 channels = prev/center/next slice + degradation level; 1.93M params; val PSNR 37.4 dB). Per CT: HU-normalize → degrade with a **real physics forward model** (Gaussian PSF + Poisson-Gaussian noise) → restore → compute PSNR / change → return images + metrics + a "largest-change" flag. **One engine feeds both halves: the restoration feeds validation; the flagged failures feed human training.** | `/health` and `/restore` working; **+4.22 dB** on real CT; accepts DICOM/PNG; ~60–180 ms/slice on CPU; model weight bundled in the repo | Feed real **low-dose↔full-dose paired** data to reproduce **+2.35 dB**; support full **multi-slice DICOM** volumes; **export failures in a format the human-training drill can load** (engineering: **David** leads, Andrew assists) |
| **Use · Studio**<br>(machine half · frontend) | A procedural CT phantom **or** an uploaded real CT → degraded to a synthetic "quarter-dose" → restored → PSNR measured live. **Every output ships with an evidence panel + a "needs-review" flag.** | Offline phantom demo; upload / one-click sample → real model via backend; shows input/restored PSNR, change amount, 4 evidence badges, the regulatory-boundary banner | Run experiments on a **real CT set**: dose-response curve, do-no-harm stats, **a failure catalog (= the "threat model" for the human half)**; replace the hard-coded badges with numbers from your own runs (**David · machine half**) |
| **Prove · Evidence**<br>(machine half · frontend) | Pick a model → show **4 layers of task-based evidence** (Clinical Rescue / Monte-Carlo stability / anatomy Dice / Mayo real-world transfer) + a composite **Evidence Score** bar chart + failure audit + risk memo + JSON export | Scores **6 models head-to-head**; 4 evidence cards (numbers = **real notebook results**); one-click **Evidence Pack (.json)** export | Numbers are **hard-coded** now → upgrade to run the 4 layers **live on an uploaded model**; David feeds in his real experiment results (machine-side evidence; Andrew / advanced) |
| **Teach → the human half**<br>(human half · frontend) | The same degradation engine **run in reverse — not education, but the human-side safety defense**: the reader practices on clean/degraded/restored images to catch where the AI changed something it shouldn't, **fighting automation bias** (people over-trust AI and rubber-stamp its errors) | "Spot the hallucination" game (currently **random synthetic lesions**); a degradation slider linked to confidence/PSNR | **Replace the synthetic lesions with David's real failure cases** as the questions; run a **pre/post study** proving "we can train people to catch the AI's errors" (= **safety evidence**, not "is the lesson good"); produce the human half of the proof (**Nick · human half**) |

## Honest: what it **is** vs **isn't** (say this out loud)
- ✅ **Is:** a working **real model** on **real CT**, a 4-layer evidence framework, a complete offline-capable front + back end.
- ⛔ **Isn't yet:** uses **synthetic** degradation (not real low-dose originals); **single-slice**; Prove numbers are **pre-stored**; the human drill uses **synthetic** lesions; **research/education only — not diagnosis**.
- 👉 **Those "isn'ts" are exactly the students' work** — David turns synthetic→real and single→volume; Nick turns synthetic lesions→David's real failures and "a quiz"→measurable evidence against automation bias.

---

# 10-minute talk (read aloud) — with live-demo cues

> Cues in **[brackets]** = do this on screen. Target ~10 min at a normal pace. Have the app open first:
> `python3 restore_server.py` running, page open at the **Engine** tab.

### 0:00 — Hook & mission (1 min)
"Hospitals are starting to put AI between the scanner and the radiologist — AI that cleans up, denoises,
and restores CT images. Here's the uncomfortable question nobody answers: *how do you know that AI made
the image better, and not just different?* If it invents a vessel or erases a faint bleed, a doctor could
read a lie.
Our project, **SafeRestore**, is built on one idea: **safe AI-assisted CT reading has two halves — a
machine you can trust, and a human who can catch it when it's wrong.** Most teams only do the first half.
We do both. Our tagline is simple: **we sell evidence, not images.**"

### 1:00 — The problem, sharpened (1.5 min)
"Two real problems. **One:** there's no independent, vendor-neutral way to prove a CT-restoration model is
safe — companies grade their own homework with PSNR, a score that can go up while the anatomy gets
corrupted. **Two — and this is the part everyone forgets — automation bias.** When people are handed an AI
result, they over-trust it and rubber-stamp its mistakes. So even a validated model isn't safe if the
human reading it has switched their brain off.
**[Engine tab on screen]** That's why SafeRestore is one engine with two defenses: validate the machine,
**and** train the human. Same failure, caught twice."

### 2:30 — The principle: one engine (1.5 min)
"Here's how the engine works. **[point to the Degrade → Restore → Score diagram]** We take a clean CT, we
**degrade** it with a real physics model of a low-dose scanner — Gaussian blur plus the actual
Poisson-Gaussian noise of fewer photons. Then a **trained neural network restores** it. Then — and this is
the whole point — we **score** it on four layers of *task-based* evidence, not just PSNR: does it recover
clinically relevant signal, is it stable under noise, does it preserve real anatomy, and does it transfer
to *real* hospital data. The model is real and it's already trained — 1.9 million parameters, validated at
37.4 dB. It's bundled in our repo; you clone it and it runs."

### 4:00 — Demo, machine half: Use (1.5 min)
"Let me show you, on a **real** CT slice. **[Use tab → click 'Load sample CT' → 'Run SafeRestore']**
On the left, the full-dose reference. In the middle, the noisy quarter-dose input. On the right, our
model's restoration — and live, measured against the reference, **plus 4.2 decibels**. **[point to the
amber box]** But notice this: the system doesn't just hand back a prettier picture. It ships the image
**with its evidence** — and it flags this region as 'needs radiologist review,' because that's where the
model changed the most. **Every output comes with proof and a confession.** That's the machine half —
that's David's territory."

### 5:30 — Demo, machine half: Prove (1 min)
"Now, is our model actually any good? **[Prove tab]** We score *any* restoration model on those four
evidence layers. **[point to the bar chart]** Here's ours against five classical filters — it wins on the
combination of benefit and safety, not just sharpness. **[scroll the 4 cards]** Real numbers from our
validation: best signal recovery, anatomy preserved, transfers to real Mayo Clinic low-dose CT at plus
2.35 dB — and, honestly, it's noise-sensitive in 62% of cases, which we disclose, not hide. **[click
Export]** And it all exports as a shareable Evidence Pack. That's the independent report card."

### 6:30 — Demo, human half: Teach + the connection (1.5 min)
"So the machine's validated. Are we safe? Not yet — remember automation bias. **[Teach tab]** This is the
human half. The *same engine, run backwards*, trains the person. **[the 'spot the hallucination' game]**
Three AI outputs; one invented a structure that isn't real. The reader has to catch it. **[click one]**
Here's the connection that makes this **one product and not three features:** the failures David's
validation finds become the exact cases Nick trains humans to catch. **One failure, two defenses** — the
machine flags it, and the trained human catches it. Remove either, and the system is still unsafe."

### 8:00 — Honest limits + what's next (1.5 min)
"Let me be straight about what this **is** and **isn't**, because over-claiming is the one thing we refuse
to do. It **is** a working real model on real CT with a real evidence framework you can run offline. It
**isn't** finished: the degradation is synthetic, it's single-slice, some numbers are pre-stored, and it's
**research and education only — not diagnosis.**
And those gaps are exactly the work. **David** takes the machine half to real paired clinical data and
builds the failure catalog. **Nick** takes the human half and runs a real study — can we measurably train
people to catch this AI's errors? Two students, two halves of one safety system."

### 9:30 — Close (30 sec)
"CT restoration AI is already moving toward patients. SafeRestore makes sure that before it gets there, the
machine is proven trustworthy **and** the human is trained to catch what's left. A machine you can trust,
and a human who can catch it. That's safety — and that's what we're building. Thank you."

---
*Phase 1 boundary: research / QA / education only — not for diagnosis, not a medical device, not for direct clinical interpretation.*
