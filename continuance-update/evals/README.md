# Trigger evals for `continuance-update`

## Running

```bash
python run_eval_win.py \
  --eval-set trigger-set.json \
  --skill-path .. \
  --runs-per-query 3 --num-workers 8
```

Each run spawns `claude -p` as a subprocess, so 18 queries x 3 runs is 54
calls and takes ten to fifteen minutes. Background it.

## Why not skill-creator's runner

Two reasons, both discovered the hard way and both worth knowing before you
trust a number from either tool.

**1. `scripts/run_eval.py` cannot run on Windows.** It reads the `claude -p`
stream with `select.select()` on a subprocess pipe, and on Windows `select`
accepts sockets only:

    OSError: [WinError 10093]

Every query scores as "did not trigger". The report comes back with every
POSITIVE failing and every NEGATIVE passing vacuously - and **a skill that
triggered on everything would score identically.** It looks like a result.

**2. Its detection assumes the skill is NOT installed.** It writes a temporary
command carrying a unique id and asks whether *that* was invoked. Correct for a
draft; wrong once the skill is installed, because the model reaches for the
real one:

    Skill{'skill': 'continuance-update'}     <- the real skill
    (no continuance-update-skill-<uid> in any tool_use)

`run_eval_win.py` matches the skill NAME via the `Skill` tool specifically -
not `Read`, since reading SKILL.md is the model looking *at* the skill rather
than reaching *for* it, and counting that inflates every rate.

The cost of matching the installed skill is that a candidate description cannot
be A/B'd without editing SKILL.md first. Edit, run, revert if worse.

## Baseline — 2026-08-02, n=3

18 queries, 3 runs each. **18/18 passed.**

    mean positive rate   93%    (52% before the two-jobs rewrite)
    mean negative rate  3.7%    (0% before)

The rewrite that moved it: the description originally framed the skill as a
writing action, so instructions to RECORD state fired at 100% while questions
ABOUT state fired at 0% - four of them, including "where are we on this
project?". Listing those phrases in the description was not enough; the skill
had to actually claim the reading job, and SKILL.md gained a `Reading one`
section so a question gets answered rather than answered-with-a-file-rewrite.

**n=3 is small.** A 67% or 33% is one run either way and sits inside the noise;
only the 0 -> 100 moves are safely outside it. Raise `--runs-per-query` before
reading anything into a single-step difference.
