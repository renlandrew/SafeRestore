# SafeRestore — Team Brief (read this first)

**To:** David & Nick **From:** Andrew (mentor) **Competition:** Ventura 2026

---

## The mission (one paragraph)
Making AI-assisted CT reading **safe** has **two halves**: the **machine** must be trustworthy, *and* the
**human** using it must be able to catch when it's wrong. Validating the model alone is **not** safety —
because of **automation bias**, people over-trust AI and rubber-stamp its mistakes. So SafeRestore does
both: **David makes the machine trustworthy** (prove the restoration model is do-no-harm on real CT), and
**Nick makes the reader un-foolable** (prove we can measurably train people to catch the AI's residual
errors). Same mission, two halves of one safety system.

> **Thesis:** *Safe AI-assisted CT reading = a machine you can trust **+** a human who can catch it.*

## Team & roles
- **David — the MACHINE half:** is the restoration safe & do-no-harm on real CT, and where does it break? (`TASK-David.md`)
- **Nick — the HUMAN half:** can we measurably train people to catch this AI's errors / beat automation bias? (`TASK-Nick.md`)
- **Andrew** — mentor. Gives you the engine, data, and feedback. You present, not me.

## Why this is ONE thing, not two features
The **same failure is the glue.** When David's validation catches the model doing something unsafe, *that
exact failure* becomes what Nick trains a human to catch. **One failure → two defenses** (machine-side +
human-side). And there's **one buyer**: whoever deploys this AI needs *both* — a validated model **and**
readers who won't rubber-stamp it. Remove either half and the system is still unsafe. That's why it's one
product, not a validator with a teaching tab bolted on.

```
        a real CT  →  [David] machine-side defense: validate, flag the failure
                              │  the SAME failure
                              ▼
                       [Nick] human-side defense: train a person to catch that failure
                              ▼
                 a safe AI-assisted read = both defenses pass
```

## Ventura target & hard dates
| Date | What |
|---|---|
| **Jun 15, 2026** | Registration opens — register day one |
| **Jun 15 – Jul 15** | Workshop Month — attend sessions, bring the MVP + results for feedback |
| **Jul 29 (midnight)** | **Submit: 3–5 min pitch video + materials** (confirm exact length on the Submission page) |
| **Aug 13** | Winners announced |

**This is a pitch competition, not a science fair.** The deliverable is a *video* judged on Ventura's
framework: **problem · solution · target market · business model · real-world impact**. Your experiments
exist to give the pitch real evidence — timebox them; the demo + story win.

---

## 🚦 Ground rules — how you must work (READ EVERY WEEK)
These are not optional. The whole project's value is that it is honest. Break these and we have nothing.

1. **Never overclaim. State what the evidence does NOT prove.** No "clinically ready," no "diagnoses." Every claim gets a limit sentence.
2. **Separate DEMO from REAL.** Always label whether a number/image came from the synthetic phantom or from real CT through the real model.
3. **Every number must be reproducible.** Save the script, data, seed, CSV. Keep a dated log.
4. **Failures are the product — report them, don't hide them.** For David they're the threat model; for Nick they're the training material. Cherry-picking is a red flag to judges.
5. **Stay in scope.** David: validate the *given* model — don't train new models. Nick: one drill + one study to test the *human* half — don't build a whole learning platform.
6. **Data ethics (hard line).** Only de-identified / public CT — never patient identifiers. For Nick's study: voluntary, verbal consent, **anonymous scores only** (no names).
7. **Keep the Phase-1 boundary on every artifact.** "Research / QA / education only — not diagnosis, not a medical device." Put it on the demo and the last slide.
8. **You must be able to explain every number on screen.** If it's on your slide, a judge can ask "how did you get that?" — have the answer.

**Hard lines (instant credibility-killers):** claiming diagnosis · using real patient PHI · showing a number you can't reproduce · hiding a known failure · presenting the phantom result as if it were real CT.

---

## How you work together (stay ONE system)
- **Weekly 30-min sync.** David hands Nick the new real failure cases; Nick tells David which failures humans miss most (so David knows what to hunt).
- **One shared repo, one engine, one mission.** Both build on the same `saferestore-mvp/`. Same failures flow between you.
- **One integrated demo:** the same real CT → David flags a real failure (machine defense) → that failure becomes Nick's drill item and a person catches it (human defense). That shared moment is your pitch's spine.

## Resources I'm giving you → see `RESOURCES.md`
## Your task cards → `TASK-David.md`, `TASK-Nick.md` · This week's sprint → `THIS-WEEK.md`

## Team definition of done (by Jul 26, so you can submit early)
- [ ] David (machine half): Safety Report (1 pg) + dose-response figure + failure catalog (≥5) + Use demo clip
- [ ] Nick (human half): "automation-bias" study memo (1 pg) + pre/post results figure + the drill (built on David's failures) + demo clip
- [ ] Together: 3–5 min pitch video + deck — one failure, two defenses, boundary on the last slide
- [ ] Submitted **Jul 28** (a day early)
