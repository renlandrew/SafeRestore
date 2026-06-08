# SafeRestore — Team Brief (read this first)

**To:** David & Nick **From:** Andrew (mentor) **Competition:** Ventura 2026

---

## The project in one paragraph
SafeRestore is the **trust layer for CT-restoration AI**. One engine — *degrade ⇄ restore ⇄
evidence* — powers three things: **prove** a restoration model is safe, **use** it to revive
low-dose/old-scanner CT, and **teach** people to catch when AI lies. You two are building the
**Use** and **Teach** products on top of a working engine and MVP I'm handing you. The thesis you
sell is **"evidence, not images."**

## Team & roles
- **David** — owns **Use / Safety**: is the restoration safe & helpful on *real* CT? (your card: `TASK-David.md`)
- **Nick** — owns **Teach / Learning**: does degradation-practice make people better at spotting AI errors? (your card: `TASK-Nick.md`)
- **Andrew** — mentor. I give you the engine, data, and feedback. I do **not** do your build. You present, not me.

## Ventura target & hard dates
| Date | What |
|---|---|
| **Jun 15, 2026** | Registration opens — register day one |
| **Jun 15 – Jul 15** | Workshop Month — attend sessions, bring the MVP + your results for feedback |
| **Jul 29 (midnight)** | **Submit: 3–5 min pitch video + materials** (confirm exact length on the Submission page) |
| **Aug 13** | Winners announced |

**This is a pitch competition, not a science fair.** The deliverable is a *video* judged on
Ventura's framework: **problem · solution · target market · business model · real-world impact**.
Your experiments exist to give the pitch real evidence — timebox them; the demo + story win.

---

## 🚦 Ground rules — how you must work (READ EVERY WEEK)

These are not optional. The whole project's value is that it is honest. Break these and we have nothing.

1. **Never overclaim. State what the evidence does NOT prove.**
   No "clinically ready," no "diagnoses," no "better than radiologists." Every claim gets a limit
   sentence next to it. (See the worksheet Part 5 phrasing — copy that tone.)
2. **Separate DEMO from REAL.** Always label whether a number/image came from the synthetic phantom
   or from real CT through the real model. Never blur the two in a slide.
3. **Every number must be reproducible.** Save the script, the data, the seed, the CSV. If you can't
   regenerate it, you can't show it. Keep a dated log of what you ran and what you got.
4. **Failures are the product — report them, don't hide them.** A cherry-picked all-green result is a
   red flag to judges. Show where it breaks; that's what makes SafeRestore credible.
5. **Stay in scope.** David: validate the *given* model — do **not** train new models. Nick: build the
   *one* "spot-the-error" lesson + study — do **not** build a whole learning platform. When in doubt, cut.
6. **Data ethics (hard line).** Only de-identified / public CT — never real patient identifiers.
   For Nick's study: participation is voluntary, get a verbal yes, store only anonymous scores
   (no names, no personal info).
7. **Keep the Phase-1 boundary on every artifact.** "Research / QA / education only — not diagnosis,
   not a medical device." Put it on the demo, the report, and the last slide. Judges love a team that
   knows its limits.
8. **You must be able to explain every number on screen.** If it's on your slide, a judge can ask
   "how did you get that?" — have the answer. Understand the MVP before you demo it.

**Hard lines (instant credibility-killers):** claiming diagnosis · using real patient PHI · showing a
number you can't reproduce · hiding a known failure · presenting the phantom result as if it were real CT.

---

## How you work together (stay ONE project)
- **Weekly 30-min sync** (pick a fixed time). David hands Nick new real failure cases; Nick tells David
  which structures students miss most (so David knows what to test).
- **One shared folder/repo, one engine.** Both of you build on the same `saferestore-mvp/` — do not fork
  into two unrelated things. Same thesis, same demo data.
- **One integrated demo at the end:** the same real CT goes through Use (David proves it's safe) → Teach
  (Nick uses it to train a person). That shared moment is your pitch's spine.

## Resources I'm giving you → see `RESOURCES.md`
## Your task cards → `TASK-David.md`, `TASK-Nick.md`

## Team definition of done (by Jul 26, so you can submit early)
- [ ] David: Restoration Safety Report (1 pg) + dose-response figure + failure catalog (≥5) + Use demo clip
- [ ] Nick: Learning-Impact memo (1 pg) + pre/post results figure + micro-lesson + Teach demo clip
- [ ] Together: 3–5 min pitch video + deck, every claim backed, boundary on the last slide
- [ ] Submitted **Jul 28** (a day early — never trust the midnight deadline)
