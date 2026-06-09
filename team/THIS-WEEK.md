# 📌 This week's task — due NEXT class

**Assigned:** today · **Due:** before next class (≈1 week) · **Size:** a few hours, finish it solo.

> This is your *one* job this week. The bigger plan (`TASK-David.md` / `TASK-Nick.md`) is for after —
> ignore it for now. Just produce the small deliverable below and bring it next class.
>
> **Mission:** safety = a machine you can trust (**David**) **+** a human who can catch it (**Nick**).

---

## David — get a real number on real CT

**Goal:** show the real model working on real CT, and start measuring "does it help, does it harm."

1. **Get the model server running.** Use `saferestore-mvp/README.md` (real-model mode). Andrew will help
   you start it at the end of today's class. ✅ done = status pill turns green, or one real restore works.
2. **Restore 6–8 real CT slices** (the `sample_ct.dcm` + the slices Andrew sends you). For each, write down:
   input PSNR, restored PSNR, Δ, max-change. Put it in a Google Sheet / table.
3. **Save 2 screenshots:** one clear win, and one where the amber "needs-review" box appears.
4. **Write 3 sentences:** what your numbers show + **what they do NOT prove** + the Phase-1 boundary.

**Bring to next class:** the table (6–8 rows) + 2 screenshots + 3 sentences. That's it.

---

## Nick — first evidence we can train the human to catch the AI's errors

**Goal:** the first hint that practice makes people catch the AI's mistakes (the human half of safety).

1. **Write the target:** one sentence — *who* is the human in the loop + the **3 error types** they must catch (hallucinated structure / erased signal / over-smoothing).
2. **Build the mini-drill:** open the **Teach** surface in `saferestore-mvp/index.html`. Write a 1-page script: what to show, what to ask ("where did the AI change something it shouldn't — trust or refer?").
3. **Mini pre/post on 3–5 people** (friends/family OK): pre-score them catching AI errors on 4 cases → run the drill 5 min → post-score on 4 new cases. Record scores in a small table.
4. **Write 2 sentences:** did they catch more after? (honest — "early signal, n=4") + one thing to improve.

**Bring to next class:** the 1-page script + the pre/post score table + 2 sentences. That's it.

---

## The 5 rules you must follow (short version)
1. **Don't overclaim** — always write what your result does NOT prove.
2. **Label demo vs real CT** — never mix them in one number or screenshot.
3. **Save your numbers** (sheet + screenshots) so you can show *how* you got them.
4. **Report failures honestly** — finding where it breaks is a win, not a problem.
5. **Data:** use only what Andrew gives you. (Nick: participants are voluntary, scores anonymous — no names.)

## What you already have vs. what Andrew sends
- ✅ The model file `deblur_25d_v2.pt` is **already in the repo** (`saferestore-mvp/`) — the server finds it automatically.
- 📨 Andrew sends a small folder of ~8–10 de-identified CT slices (for David's table).
- If the server setup fights you for more than ~30 min, message Andrew — don't lose the week to install.
