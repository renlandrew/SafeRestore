# Task Card — Nick · the HUMAN half of safety

**Mission:** Prove we can **measurably train people to catch the AI's errors** — so the human using
the AI isn't fooled by it. This is the *human-side defense* of the same safety system David builds
the machine-side of.

> Read `README.md` (mission + rules) first. You are **not** building an education product — you are
> producing the **human half of the safety evidence**.

## The real problem you're attacking: automation bias
When people get an AI result, they over-trust it and rubber-stamp its mistakes. A validated model
(David) is necessary but **not sufficient** — if the human can't catch the model's residual errors,
the system is still unsafe. Your job is to show that **training fixes this, with data.**

## Your research question & hypothesis
- **Question:** After practicing on the AI's *real* failure cases, do people catch more of its errors
  (and stop over-trusting it)?
- **Hypothesis:** Yes — measurably higher error-catching after the drill, vs. people who only read a warning.

## What to do (each step has a "done =")
**Step 1 — Lock the reader (Week 0–1)**
- One sentence: *who* is the human in the loop (e.g. a student/clinician reading AI-assisted CT) + the
  **3 failure types** they must learn to catch (hallucinated structure, erased weak signal, over-smoothing).
- **done =** the reader + the 3 error types written down.

**Step 2 — Build the drill from DAVID'S REAL FAILURES (Week 1–2)**
- Use the **Teach** surface, but feed it **David's real failure cases** (not synthetic blobs). 3–4 steps:
  see clean/restored, find where the AI changed something it shouldn't, decide "trust / send to human."
- **done =** a drill someone can finish solo, using real failures.

**Step 3 — Your experiment: does training beat automation bias? (Week 2) ← core science**
- Recruit **≥10 people**. **Pre-test:** score them catching the AI's errors on a set of cases.
  → run the drill → **post-test** on new cases. If you can, add a **control** (warning text only, no drill).
- Measure: error-catch rate (and over-trust rate) before vs after, drill vs control.
- **done =** an anonymous score table: pre vs post (and drill vs control if managed).

**Step 4 — Analyze + safety memo (Week 3)**
- One figure: error-catching before/after (and vs control). State limits honestly (small n, informal).
- **done =** 1-page memo: *"we can train the human half — here's the evidence,"* + what it does NOT prove + boundary.

**Step 5 — Capstone + demo (Week 3–4)**
- Final step: the reader runs Use + Prove on a real case and decides trust/refer — i.e. *both defenses* in their hands.
- Record a 30–45s demo clip for the video.
- **done =** capstone flow + demo clip.

## Resources you'll mainly use
`saferestore-mvp/index.html` (Teach surface) · **David's real failure cases** · Worksheet Parts 2, 9, 10.

## Your guardrails (on top of the team rules)
- **You are producing safety evidence, not a course.** Frame everything as "can the human catch the AI's errors," not "is my lesson fun."
- **Use David's REAL failures**, not synthetic ones — that's what makes it the same system, not a side project.
- **Study ethics:** voluntary, verbal-consent, anonymous scores only.
- **Honest stats:** with n≈10 you can't claim significance — say "early signal," show the numbers, note limits.
- **One drill + one study.** Don't build a learning platform.

## What you deliver to the pitch
- **The human half of the safety proof** — your differentiator vs every model-only team:
  *"a validated model isn't safe if the human rubber-stamps it; we can measurably train the human to catch
  its errors — here's the before/after."*
- **The unified market point:** the same buyer who wants the validated model (David) also needs trained,
  un-foolable readers — you're selling *both halves of safety to one customer*, not a separate course.

## Judge questions to prep
- "Isn't validating the model enough?" → No — automation bias; the human still rubber-stamps errors. Safety needs both halves.
- "How do you know training actually works?" → your pre/post (vs control) data, with honest limits.
- "Who pays for the 'human' part?" → the same hospital/developer deploying the AI; trained readers are part of safe deployment.
