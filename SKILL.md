---
name: continuance-update
description: Read, create or update CONTINUANCE.md - a Past/Present/Future checkpoint at a repository root that answers "where does this project stand, and what happens next". It has TWO jobs and both trigger it. ANSWERING - whenever the user asks where we are, what is left, what is outstanding, what was being worked on, what state something is in, or to be caught up on a repository: consult CONTINUANCE.md and report from it rather than re-reading the codebase. RECORDING - whenever the user asks to update the continuance, save or write a checkpoint, record or capture the current state, note where things stand before stopping, or resume from a previous session; at the end of a working session; and before a release. Also use when a project has a seamless-continuance.md, progress.md, STATUS.md, NOTES.md or similar hand-maintained state file that should be superseded by the formal structure.
---

# Continuance

`CONTINUANCE.md` is a **read-only checkpoint at the root of a repository**. It
answers two questions that otherwise cost an hour of reading:

- *(human)* what state is this project in, and what happens next?
- *(agent)* what was I doing, and what may I safely pick up?

It is not a changelog, not a design document and not a task tracker. Those
exist and are better at their jobs. This is the **one page** you read before
touching anything.

---

## The structure

```markdown
---
project: <name>
description: <one line - what this project IS, not what state it is in>
updated: <YYYY-MM-DD> · <short sha> · <branch>
---

# <name> — Continuance

## Past
<one stub per completed unit of work.  See "Past is stubs" below.>

## Present
<what is being worked on RIGHT NOW.  The main section.>

## Future
<everything outstanding, IN IMPLEMENTATION ORDER.>

## Lessons
<things learned that changed a decision.  Numbered, permanent.>
```

Order is deliberate: **Past, Present, Future, Lessons.** A reader arriving cold
wants the chronology. It only works because Past stays short — see below.

**Target: the whole file under 200 lines.** If it grows past that, Past is not
being compacted hard enough. A checkpoint nobody reads is worse than none.

On a long-lived project, Lessons is the one section that can outgrow the cap
on its own even with Past fully compacted — it's permanent and append-only, so
it has no lossy compaction to fall back on. When that happens, Lessons splits
into a sibling `LESSONS.md`; see "Splitting off LESSONS.md" below. Most
projects never need this — it's a last resort, not a default second file.

---

## Past is STUBS, not history

This is the rule that keeps the file usable at month twelve.

**Detail lives in the planning artifact. Past only confirms completion.**

```markdown
## Past

- [x] `stage50-QA-action-plan.md` — enemy scale, weapon drops, chainsaw, ammo economy, patrol AI · D92–D93
- [x] `stage60-endless-hub-terrain.md` — the hub no longer ends · D94
- [x] `stage70-open-world-survival-...md` — holy ground and limbo · D95
```

One line each: **the artifact, a clause of what it did, and the identifiers**
(decision numbers, tags, PRs — whatever the project already uses). Nothing else.
Anyone who wants the reasoning opens the artifact; re-telling it here makes two
copies that drift.

Where a project has **no** planning artifacts, stub against the next best
durable anchor — a tag, a milestone, a PR number, a commit range:

```markdown
- [x] `v1.4.0` — batch import, retries, the S3 migration · 2026-05-11
```

### Compaction

Keep the **most recent 8–12 stubs** as written. Older ones collapse into one
line per release or milestone:

```markdown
- [x] **v0.1 → v1.0** — engine, toolchain, three levels, the audio stack (D1–D91)
```

Compact **on update**, automatically. Do not wait to be asked, and do not leave
it for a human to remember.

---

## Present is the main section

What is in flight *now* — not what is planned, not what just shipped.

```markdown
## Present

**Stage 95 — weapons in hands and active upgrades.** Parts A–D built and green;
Part E (harness) in progress.

- Working file: `stage95-weapons-fix-and-bonus-buff-integration-plan.md`
- Blocked on: nothing
- Uncommitted: `entity.cpp`, `worldtest.cpp`
```

If nothing is in flight, **say so plainly** — `*Nothing in progress. Next up is
the first item under Future.*` An empty Present is information; a stale one is a
trap.

Name what is **blocked**, and on what. That is the single most useful line for
whoever picks the project up next.

---

## Future is ordered, and is not yours to reorder

**Future is derived from outstanding items in the planning artifacts**, in the
sequence those plans establish. It is a scratchpad that changes **at planning
time**, not at update time.

```markdown
## Future

1. `stage99-...md` — <one line> *(planned, not started)*
2. **T4** — `trigger_multiple` has never been placed in a map *(content, not code)*
3. **R1b** — re-file the Defender submission after the next packed build
4. *Unplanned:* endless-hub landmarks — no artifact yet
```

**Never reorder it. Never add to it from inference.** "This is done" is
verifiable from git; "this is next" is a judgment the human owns, and a tool
that silently rewrites someone's plan is one they stop trusting.

You may:
- **tick off** an item the artifact or git shows complete (and stub it into Past),
- **annotate** an item whose status changed (blocked, superseded, decided against).

You may not: resequence, invent, or quietly drop. If an item looks wrong,
**say so in the reply** — not in the file.

---

## Lessons

Things learned that **changed a decision**. Not observations, not trivia.

```markdown
## Lessons

1. **Check the instrument before the code.** Three stages running, the first
   failing result was the measurement, not the implementation — a check that
   asserted a superseded model, one that sampled a pixel the weapon never
   reached, one that ran a shorter sweep than the thing it was comparing to.
2. **A comment that contradicts the code is a bug report.** The viewmodel was
   drawn over the HUD for four milestones, against a comment directly above it
   saying it should be under.
```

Numbered and **permanent** — they only ever get appended to. A lesson that
stops being true is *annotated*, never deleted; knowing something was believed
and then disproved is itself the lesson.

**Add one only when it would have changed what you just did.** A Lessons
section that collects everything gets skimmed, and then the useful ones are lost
with the rest.

### Splitting off LESSONS.md

When the file is still at or near 200 lines **after** compacting Past,
tightening Present, and trimming Lessons prose down to bolded claims, split
Lessons into a sibling file at the repo root:

```markdown
---
project: <name>
---

# <name> — Lessons

1. **Check the instrument before the code.** ...
2. **A comment that contradicts the code is a bug report.** ...
```

Move **every** lesson, not just the oldest — a lesson is permanent, full-text,
and numbered for citation, so there's no lossy version of it to leave behind
the way a Past stub leaves detail behind in its planning artifact. Leave
`## Lessons` in CONTINUANCE.md as a **permanent one-line pointer**:

```markdown
## Lessons

See `LESSONS.md` (1–14).
```

This is a one-way, one-time move per project. Once split:

- **Numbers never change.** Lesson 7 is Lesson 7 forever, now living in
  `LESSONS.md`. Plans and commit messages cite lessons by number —
  renumbering would break every live reference scattered across the repo.
- **New lessons append to `LESSONS.md` directly**, continuing the same count.
  Never repopulate CONTINUANCE.md's Lessons section — that just recreates the
  bloat the split was meant to fix.
- **The 200-line cap does not apply to `LESSONS.md`.** It's an archive, not a
  checkpoint — no headmatter sha or branch to go stale. Keep entries lean with
  the same discipline (bolded claim first, narrative trimmed to what's
  non-obvious), but don't chase a line target there.
- **Check both files when a Lesson is asked about or cited.** A reference to
  "Lesson 7" predates the split as often as not — resolve it wherever the
  numbering actually lives, don't assume which file holds it.

---

## Reading one — the other half of the job

**A question is not a request to write.** When the user asks *where are we*,
*what's left*, *what were we doing* or *catch me up*, they want an **answer**,
not a rewritten file.

1. **Read `CONTINUANCE.md`** if it exists. Answer from it — Present first, then
   the head of Future, then whatever they actually asked about. If its Lessons
   section is a pointer to `LESSONS.md` and the question touches a lesson or
   past decision, **read `LESSONS.md` too** — a pointer means moved, not gone.
2. **Say when it was last updated.** The headmatter carries a date and a sha;
   if HEAD has moved a long way past that sha, **say so** — a checkpoint the
   project has outrun is worse than none, and the user needs to know which they
   are reading.
3. **Offer to update it** if it is stale. Do not update it unprompted: they
   asked a question, and silently rewriting a file in response to a question is
   how a tool earns distrust.
4. **If there is no `CONTINUANCE.md`**, answer from git and the artifacts as
   you normally would — then say one could exist, and offer.

This is half of why the file is worth maintaining. A checkpoint nobody consults
is just a chore.

---

## Creating one

When no `CONTINUANCE.md` exists:

1. **Look for one under another name** — `seamless-continuance.md`,
   `progress.md`, `STATUS.md`, `NOTES.md`, `docs/state.md`. If found:
   **absorb its content into the new structure and LEAVE THE OLD FILE IN
   PLACE.** It is superseded, not deleted — and say so in the reply so the
   supersession is a decision the user can see, not a silent replacement.
2. **Read git** — `git log --oneline -40`, `git tag`, `git status --short`,
   current branch and HEAD.
3. **Find the planning artifacts** — `stage*.md`, `plan*.md`, `roadmap*.md`,
   `docs/`, anything TINS-shaped. These supply Past's stubs and Future's order.
4. **Write it**, then show the user the Future section specifically and ask
   whether the order is right. It is the one part you cannot derive.

---

## Updating one

Sources, **in this order of authority**:

| Source | Supplies | Trust |
| --- | --- | --- |
| **git** | what actually happened | highest — a commit is a fact |
| **the conversation** | *why*, and what is in flight | high for this session, blind outside it |
| **the existing file** | what is still outstanding | the record of intent |
| planning artifacts | Future's order and Past's stubs | authoritative for sequence |

Then:

1. **Read the recorded `updated:` sha.** Everything since it is new. If the
   file has no sha, use the last 40 commits and say the range was guessed.
2. **Auto-promote Present → Past** for anything git shows landed. Write the
   stub; do not re-tell the work.
3. **Rewrite Present** from the working tree and the conversation.
4. **Touch Future only to tick or annotate.** Never resequence.
5. **Compact Past** if it has grown past ~12 detailed stubs.
6. **Append a Lesson** only if something was genuinely learned. Check for
   `LESSONS.md` first — if the project has already split, append there and
   continue its numbering; otherwise append to CONTINUANCE.md's own Lessons
   section as before.
7. **If the file is still at or near 200 lines** after 5 and after trimming
   Lessons prose to bolded claims, split Lessons into `LESSONS.md` now — see
   "Splitting off LESSONS.md" above. Last resort, not the first move.
8. **Stamp the headmatter** — date, new short sha, branch.

### The rule that keeps it honest

> **"Done" means committed.** Never write a Past stub for work that exists only
> in the working tree or only in the conversation. If it is not in git it is
> **Present**, and saying otherwise is how a checkpoint starts lying — which
> costs more than having no checkpoint at all.

---

## What this is not

- **Not a changelog.** Git is the changelog. Past points at artifacts.
- **Not a task tracker.** Future is a reading of the plans, not a replacement.
- **Not a design document.** Reasoning lives in the planning artifacts.
- **Not a place for detail.** Every line earns its space or it is compacted.
- **Not two files by default.** `LESSONS.md` exists only for projects that
  outgrew the cap even after compaction — most projects never need it.

---

## Anti-patterns

| Symptom | What it means | Fix |
| --- | --- | --- |
| Past is longer than Present + Future | Not compacting | Stubs, then collapse to milestones |
| Future has grown items nobody planned | Inferring work | Only artifacts and the human add to Future |
| Present describes last week | Not updated on stop | Update before ending a session, not before starting one |
| A stub for uncommitted work | "Done" drifted from "committed" | Move it back to Present |
| Lessons full of observations | Everything is being recorded | Only what changed a decision |
| Lessons still bloated after compaction | It's permanent and full-text — no lossy compaction left | Split into `LESSONS.md`, leave a pointer |
| Over 200 lines | All of the above | Compact Past, trim Present, then split Lessons if still over |

---

## Reporting back

After writing, tell the user:

- **what moved** — which items were promoted, and on what evidence,
- **what you did not touch** — Future's order, explicitly,
- **anything that looked wrong** but was left alone,
- the new line count, if it is near the limit,
- **if this update split off `LESSONS.md`** — say so explicitly. It's a
  one-time structural change, not a routine edit.

A checkpoint the user has not read is one they cannot rely on. Say what changed
so they do not have to diff it.
