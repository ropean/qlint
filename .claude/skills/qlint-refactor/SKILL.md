---
name: qlint-refactor
description: Inspect or reduce qlint risk scores. Activate when working in a project with qlint installed and the user asks to list/show/rank top risk files, explain why a file is risky, refactor risky files, reduce technical debt, lower a risk score, run the risk loop, or clean up the highest-risk files identified by qlint.
---

# qlint-refactor

A scanner-as-signal feedback loop. Pick the top-risk file from `qlint --risk`,
propose a minimal behavior-preserving refactor, re-scan, verify the score
dropped. Stop when top-5 are all `risk_score < 50` or after 3 failed attempts
on the same file.

## When to activate

- Project has qlint installed (`pyproject.toml` mentions qlint, or a top-level
  `qlint/` package exists) AND the user asks to: list/show/rank top risk
  files, explain why a file is risky, refactor risky files, reduce risk, clean
  up risky code, lower the risk score of file X, run the risk loop.

## When NOT to activate

- General refactoring with no qlint context.
- Adding features or fixing functional bugs.
- Style-only changes (formatting, naming-only) — they don't move the score.

## Workflow

### 1. Confirm clean working tree

`git status` first. If there are uncommitted changes, ask the user to commit
or stash before establishing the baseline — risk scores compare apples to
apples only on committed history.

### 2. Establish baseline

```bash
python .claude/skills/qlint-refactor/scripts/risk_top.py --top 5
```

Record the top-1 file's `risk_score` as **baseline**. Note `top_reason` —
it tells you which lever the score is sensitive to (complexity vs. churn vs.
bug-fix-ratio vs. authors).

### 3. Locate the actual offender inside the file

Read the target file. `signals.complexity` is an *average* — find the
**single function** with the highest cyclomatic complexity, or the densest
smell cluster. That's the target. Do not refactor the whole file at once;
re-scan tells you if you picked the right hot spot.

### 4. Propose a minimal, behavior-preserving refactor

**Allowed moves:**
- Extract function (split a long function into named sub-steps)
- Flatten nested conditionals (early return / guard clauses)
- Replace duplicated branches with a small lookup table
- Rename for clarity, paired with one of the above

**Not allowed:**
- Behavior changes
- Public API / signature changes (no caller updates needed)
- Mass formatting-only diffs (won't move risk_score)
- New abstractions for hypothetical reuse (R-philosophy: three similar
  lines beats premature abstraction)

Show the diff to the user before applying.

### 5. Apply and verify

After applying, verify against baseline:

```bash
python .claude/skills/qlint-refactor/scripts/verify.py <relative/path/to/file> --baseline <BASELINE>
```

Read the JSON. Key fields:
- `verdict`: `improved` / `unchanged` / `regressed`
- `delta`: signed change in `risk_score`

### 6. Decide

| Verdict | Action |
|---|---|
| `improved` (delta < 0) | Confirm with user; commit; pick next risk file (back to step 2). |
| `unchanged` or `regressed` | Roll back. Try a different angle on the same file. |
| 3 failed attempts on one file | Skip it. Document why ("score driven by churn × authors, not refactor-able"). Move to the next file. |

### 7. Exit conditions

Stop when ANY of:
- All top-5 files have `risk_score < 50`
- User says stop
- 3 changes in a row (across files) all failed to improve

Print a final summary: starting top-1 score → ending top-1 score, files
touched, files skipped (with reasons).

## Hard constraints

- **One refactor per cycle.** A risky file with 6 issues — pick ONE.
- **Per-cycle commit.** Each accepted refactor is its own commit; the user
  reviews diff before each. Never amend silently.
- **Max 3 attempts per file** before skipping. Sunk-cost beats progress.
- **Baseline integrity.** Re-establish baseline after each accepted commit;
  don't trust stale numbers.

## Example session

```
User: Run the qlint risk loop on this repo.

Agent: git status → clean.
       baseline:
         qlint/cli.py — risk 18.12 (active churn 294 lines / window)
       largest function in cli.py: _run(), cyclomatic 12.
       plan: extract the argparse block into _build_parser().

[shows diff]
[user approves]

Agent: applied. verifying…
       qlint/cli.py: 18.12 → 14.70 (delta -3.42, improved)

       commit message: refactor: extract _build_parser from _run
       proceed? next target qlint/core/traversal.py (risk 11.11)
```
