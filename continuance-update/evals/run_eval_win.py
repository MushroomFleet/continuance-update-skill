#!/usr/bin/env python3
"""Windows-safe trigger eval for a skill description.

WHY THIS EXISTS.  skill-creator's own scripts/run_eval.py reads the `claude -p`
stream with select.select() on a subprocess pipe.  That is POSIX-only: on
Windows select() accepts sockets and nothing else, so the read loop raises
OSError, every query is scored as "did not trigger", and the report comes back
with every POSITIVE failing and every NEGATIVE passing vacuously.  A skill that
triggers on everything would score identically.

    >>> select.select([p.stdout], [], [], 1.0)
    OSError: [WinError 10093] ...

This keeps the parts that matter - the command-file injection that puts the
description in front of the model, and matching on the Skill tool's input - and
replaces the streaming read with a plain blocking capture.  Slower per query
(no early exit), correct on Windows.

Same eval-set format:  [{ "query": ..., "should_trigger": bool }, ...]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def parse_skill(skill_path: Path):
    text = (skill_path / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        raise SystemExit("no frontmatter in SKILL.md")
    fm = m.group(1)
    name = re.search(r"^name:\s*(.+)$", fm, re.M).group(1).strip()
    # description may wrap over several lines until the next `key:` at col 0
    d = re.search(r"^description:\s*(.+?)(?=\n[a-z_]+:|\Z)", fm, re.M | re.DOTALL)
    return name, " ".join(d.group(1).split())


def run_query(query, skill_name, description, project_root, timeout, model):
    """True if the model reached for this skill.  One `claude -p` per call.

    MEASURES THE INSTALLED SKILL, not an injected copy.  skill-creator's own
    harness writes a temp command carrying a unique id and asks whether THAT
    was invoked - which is right for a draft that is not installed yet, and
    wrong here.  The real skill IS installed, so the model reaches for the real
    one and the unique id never appears anywhere.  Confirmed on a raw stream:

        Skill{'skill': 'continuance-update'}        <- the real one
        (no continuance-update-skill-<uid> in any tool_use)

    That is why the first run of this scored 0% on every positive INCLUDING
    the literal phrase "update the continuance".  Matching the skill NAME
    measures the thing in its real configuration, which is what a trigger eval
    is for.  Cost: a candidate description cannot be A/B'd without editing the
    installed SKILL.md first.
    """
    del description        # the installed SKILL.md is the description under test
    clean = skill_name
    cmd = ["claude", "-p", query, "--output-format", "stream-json", "--verbose"]
    if model:
        cmd += ["--model", model]
    # CLAUDECODE is a guard against interactive nesting; a subprocess is safe.
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    try:
        out = subprocess.run(cmd, cwd=project_root, env=env, timeout=timeout,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
                             ).stdout.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return False
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") != "assistant":
            continue
        for c in ev.get("message", {}).get("content", []):
            # The Skill tool specifically.  A Read of SKILL.md is the model
            # looking AT the skill, not reaching FOR it, and counting that
            # would inflate every rate.
            if c.get("type") != "tool_use" or c.get("name") != "Skill":
                continue
            if clean in json.dumps(c.get("input", {})):
                return True
    return False


def main():
    ap = argparse.ArgumentParser(description="Windows-safe skill trigger eval")
    ap.add_argument("--eval-set", required=True)
    ap.add_argument("--skill-path", required=True)
    ap.add_argument("--description", help="override the description under test")
    ap.add_argument("--runs-per-query", type=int, default=3)
    ap.add_argument("--num-workers", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--trigger-threshold", type=float, default=0.5)
    ap.add_argument("--model")
    ap.add_argument("--project-root", default=".")
    args = ap.parse_args()

    skill_path = Path(args.skill_path)
    name, desc = parse_skill(skill_path)
    if args.description:
        desc = args.description
    items = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    root = str(Path(args.project_root).resolve())

    print(f"skill: {name}\nqueries: {len(items)} x {args.runs_per_query} runs\n",
          file=sys.stderr)

    triggers = {}
    with ThreadPoolExecutor(max_workers=args.num_workers) as ex:
        futs = {}
        for it in items:
            for _ in range(args.runs_per_query):
                f = ex.submit(run_query, it["query"], name, desc, root,
                              args.timeout, args.model)
                futs[f] = it
        for f in as_completed(futs):
            it = futs[f]
            try: r = f.result()
            except Exception: r = False
            triggers.setdefault(it["query"], []).append(r)

    by_query = {it["query"]: it for it in items}
    rows, passed = [], 0
    for q, ts in triggers.items():
        rate = sum(ts) / len(ts)
        want = by_query[q]["should_trigger"]
        ok = rate >= args.trigger_threshold if want else rate < args.trigger_threshold
        passed += ok
        rows.append((want, ok, rate, q))

    rows.sort(key=lambda r: (not r[0], r[3]))
    print(f"{'want':>5} {'got':>6}  {'':2} query", file=sys.stderr)
    for want, ok, rate, q in rows:
        print(f"{'YES' if want else 'no':>5} {rate:>6.0%}  {'  ' if ok else '<<'} {q}",
              file=sys.stderr)
    print(f"\n{passed}/{len(rows)} passed", file=sys.stderr)

    json.dump({"skill": name, "description": desc,
               "results": [{"query": q, "should_trigger": w, "trigger_rate": r,
                            "pass": ok} for w, ok, r, q in rows],
               "summary": {"total": len(rows), "passed": passed,
                           "failed": len(rows) - passed}},
              sys.stdout, indent=2)
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
