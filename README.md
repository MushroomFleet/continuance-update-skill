# continuance-update

**A Claude Code skill that maintains `CONTINUANCE.md` — a one-page Past/Present/Future checkpoint at the root of a repository that answers "where does this project stand, and what happens next?"**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

---

## The problem

Every project accumulates a gap between what the repository contains and what anyone actually knows about it.

Git tells you what changed. It does not tell you what was *in flight* when someone stopped. The plans tell you what was intended. They do not tell you which parts landed. And the agent you were working with three days ago has no memory of any of it — so every session begins with the same expensive re-derivation: read the log, skim the plans, guess at the state, hope.

The usual response is a hand-maintained state file — `progress.md`, `STATUS.md`, `NOTES.md`, `seamless-continuance.md`. These work for about three weeks. Then they grow, then they go stale, then nobody reads them, and a stale checkpoint is worse than none because it lies with confidence.

## What this does

`continuance-update` gives that file a **formal structure and a discipline for maintaining it**, and teaches an agent to keep it honest.

`CONTINUANCE.md` is a read-only checkpoint that answers two questions:

- *(human)* what state is this project in, and what happens next?
- *(agent)* what was I doing, and what may I safely pick up?

It is not a changelog, not a design document, not a task tracker. Those exist and are better at their jobs. This is the **one page you read before touching anything** — and the target is the whole file under 200 lines, permanently.

```markdown
---
project: <name>
description: <one line — what this project IS, not what state it is in>
updated: <YYYY-MM-DD> · <short sha> · <branch>
---

# <name> — Continuance

## Past      <- one stub per completed unit of work. Stubs, not history.
## Present   <- what is being worked on RIGHT NOW. The main section.
## Future    <- everything outstanding, IN IMPLEMENTATION ORDER.
## Lessons   <- things learned that changed a decision. Numbered, permanent.
```

## Two jobs, and both of them trigger the skill

This is the design decision the whole skill turns on.

**RECORDING** — "update the continuance", "save a checkpoint before we stop", "record where things stand". The skill reads git, the conversation, the existing file and the planning artifacts, then writes.

**ANSWERING** — "where are we?", "what's still outstanding?", "catch me up on this repo". The skill consults `CONTINUANCE.md` and **answers from it** rather than re-reading the codebase. It reports when the file was last updated, and says so plainly if HEAD has moved a long way past the recorded sha.

A question is not a request to write. Asking "where are we?" gets you an answer, not a silently rewritten file — the skill offers to update a stale checkpoint rather than doing it unprompted.

Half the value of maintaining a checkpoint is that something actually reads it. A checkpoint nobody consults is just a chore.

## The rules that keep it usable at month twelve

Most state files fail the same handful of ways. Each rule below exists to close one of them.

**Past is stubs, not history.** One line per completed unit of work: the artifact, a clause of what it did, the identifiers. Detail lives in the planning artifact — re-telling it here makes two copies that drift.

```markdown
- [x] `stage60-endless-hub-terrain.md` — the hub no longer ends · D94
- [x] `v1.4.0` — batch import, retries, the S3 migration · 2026-05-11
```

**Past compacts automatically.** The most recent 8–12 stubs stay as written; older ones collapse into one line per release or milestone. On update, without being asked.

**"Done" means committed.** Never write a Past stub for work that exists only in the working tree or only in the conversation. If it is not in git, it is Present. This is the rule that stops a checkpoint from lying.

**Future is not the agent's to reorder.** Future is derived from the planning artifacts, in the sequence those plans establish. The skill may *tick off* an item git shows complete, and *annotate* one whose status changed. It may not resequence, invent, or quietly drop. If an item looks wrong, it says so in the reply — not in the file. A tool that silently rewrites someone's plan is one they stop trusting.

**Lessons are permanent and rare.** Only things that *changed a decision* — not observations, not trivia. A lesson that stops being true gets annotated, never deleted; knowing something was believed and then disproved is itself the lesson.

**An empty Present is information.** If nothing is in flight, the file says so plainly. A stale Present is a trap.

## Migrating an existing state file

If your project already has `seamless-continuance.md`, `progress.md`, `STATUS.md`, `NOTES.md` or similar, the skill absorbs its content into the formal structure and **leaves the old file in place** — superseded, not deleted — and tells you it did. Supersession should be a decision you can see, not a silent replacement.

## Installation

Drop the `continuance-update/` directory into your skills folder:

```bash
# User-level — available in every project
git clone https://github.com/MushroomFleet/continuance-update-skill.git
cp -r continuance-update-skill/continuance-update ~/.claude/skills/

# Or project-level — this repository only
cp -r continuance-update-skill/continuance-update .claude/skills/
```

Then just talk normally. The skill fires on both jobs:

```
> update the continuance
> save a checkpoint before we stop for the day
> where are we on this project?
> what's still outstanding?
> I'm new to this repo — catch me up on where it stands
```

## Repository layout

```
continuance-update/
├── SKILL.md                 the skill itself — structure, rules, anti-patterns
└── evals/
    ├── trigger-set.json     18 queries, 9 positive / 9 negative
    ├── run_eval_win.py      Windows-capable trigger-rate harness
    └── README.md            why not skill-creator's runner, and the baseline
```

## Trigger evals

Skill descriptions are load-bearing — a skill that never fires is a skill you do not have, and one that fires on everything is worse. `evals/` carries an 18-query trigger set and a harness that measures both rates.

```bash
cd continuance-update/evals
python run_eval_win.py \
  --eval-set trigger-set.json \
  --skill-path .. \
  --runs-per-query 3 --num-workers 8
```

**Baseline — 2026-08-02, n=3: 18/18 passed.** Mean positive rate 93%, mean negative rate 3.7%.

The number worth knowing: before the two-jobs rewrite, the positive rate was **52%**. The original description framed the skill purely as a writing action, so instructions to *record* state fired at 100% while questions *about* state fired at **0%** — including "where are we on this project?". Listing those phrases in the description was not enough. The skill had to actually claim the reading job, which is why `SKILL.md` has a *Reading one* section.

`evals/README.md` also documents why the stock `skill-creator` runner cannot produce a valid number on Windows — it reads the `claude -p` stream with `select.select()`, which accepts sockets only, so every query scores as "did not trigger" and the report comes back looking like a result. A skill that triggered on everything would score identically.

**n=3 is small.** A 67% or 33% is one run either way and sits inside the noise. Raise `--runs-per-query` before reading anything into a single-step difference.

## What this is not

- **Not a changelog.** Git is the changelog. Past points at artifacts.
- **Not a task tracker.** Future is a *reading* of the plans, not a replacement for them.
- **Not a design document.** Reasoning lives in the planning artifacts.
- **Not a place for detail.** Every line earns its space or it is compacted.

## License

Apache License 2.0 — see [LICENSE](LICENSE).

---

## 📚 Citation

### Academic Citation

If you use this codebase in your research or project, please cite:

```bibtex
@software{continuance_update_skill,
  title = {continuance-update: a Past/Present/Future checkpoint skill for repository state},
  author = {Drift Johnson},
  year = {2026},
  url = {https://github.com/MushroomFleet/continuance-update-skill},
  version = {1.0.0}
}
```

### Donate:

[![Ko-Fi](https://cdn.ko-fi.com/cdn/kofi3.png?v=3)](https://ko-fi.com/driftjohnson)
