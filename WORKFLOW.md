# Code Scanner — Workflow

pry is a linear pipeline. Each stage enriches a shared file record and passes it to the next.

## Pipeline Overview

```
User Input (path)
      │
      ▼
  pry/cli.py              ← entry point, orchestrates all stages
      │
      ├── 1. traversal     → discover files
      ├── 2. metrics       → read + measure each file
      ├── 3. complexity    → cyclomatic complexity per function
      ├── 4. smells        → code smell detection
      ├── 5. security      → secret and dangerous-call detection
      ├── 6. duplicates    → cross-file duplicate block detection
      ├── 7. quality       → aggregate score and grade
      │
      └── 8. reports
               ├── report_json.py  → scan_results/<name>/report.json
               └── report_html.py  → scan_results/<name>/report.html
```

---

## Stage 1 — File Discovery (`core/traversal.py`)

Walks the target directory with `os.walk`, skipping noise directories:

```
.git  node_modules  __pycache__  .venv  dist  build  .next  coverage  ...
```

Detects language from file extension (30+ extensions supported). Produces a list of file records:

```python
{'path': '/abs/path', 'relative_path': 'src/foo.py', 'language': 'Python', 'size': 1234}
```

---

## Stage 2 — Basic Metrics (`core/metrics.py`)

Reads each file (UTF-8, ignoring encoding errors) and counts:

| Metric | Method |
|--------|--------|
| Total lines | `splitlines()` |
| Blank lines | empty after `strip()` |
| Comment lines | language-specific regex (e.g. `^\s*#` for Python) |
| Code lines | total − blank − comment |
| Functions / Classes | `ast.parse` for Python; regex for others |

The raw `content` string is kept on the record so later stages don't re-read the file.

---

## Stage 3 — Complexity (`core/complexity.py`)

**Python** — AST-based, per function:

Visits every `FunctionDef` / `AsyncFunctionDef`. Starts at 1, adds 1 for each decision point:
`if`, `while`, `for`, `ExceptHandler`, `With`, `Assert`, `comprehension`, `BoolOp` (each extra operand).

**Other languages** — regex count of decision keywords over the whole file (coarse estimate).

Functions with complexity > 10 are flagged.

---

## Stage 4 — Code Smells (`core/smells.py`)

**Python** — AST-based, with exact line numbers:

| Smell | Threshold |
|-------|-----------|
| Long function | > 50 lines |
| Long parameter list | > 5 parameters |
| Deep nesting | > 4 levels of `if`/`for`/`while`/`with`/`try` |

**Other languages** — indentation depth heuristic (≥ 4 tab-widths = deep nesting).

---

## Stage 5 — Security (`core/security.py`)

Two independent passes:

**Secrets (all languages, regex per line)**

Matches patterns for hardcoded API keys, passwords, tokens, AWS credentials, and embedded private keys. A match on a line triggers a `critical` issue.

**Dangerous calls**

- *Python* — AST `Call` node visitor. Only flags actual function calls: `eval()`, `exec()`, `__import__()`, `os.system()`, `pickle.loads()`, `subprocess.call(shell=True)`. String literals containing these names are ignored.
- *JavaScript / TypeScript* — regex with a quote-counting heuristic to skip matches inside string literals.

---

## Stage 6 — Duplication (`core/duplicates.py`)

Runs **after all per-file analysis** because it needs to compare across files.

1. Slide a 6-line window over each file, normalising lines (strip whitespace).
2. Hash each window with MD5.
3. Any hash that appears in 2+ locations is a duplicate block.
4. Count duplicate blocks per file; report the top 5 offenders.

---

## Stage 7 — Quality Score (`core/quality.py`)

Starts at 100 and applies four weighted penalties:

| Dimension | Weight | Signal |
|-----------|--------|--------|
| Complexity | 30% | ratio of flagged functions to total functions |
| Duplication | 25% | duplication percentage |
| Code smells | 25% | smells per file (normalised at 5/file = max penalty) |
| Security | 20% | critical issues × 10 + error issues × 3 (normalised at 20) |

Score is clamped to [0, 100] and converted to a letter grade:

```
≥ 90 → A    ≥ 80 → B    ≥ 70 → C    ≥ 60 → D    < 60 → F
```

---

## Stage 8 — Reports

**Output directory** — `scan_results/<dirname>_<7-char-sha1>/`

The directory name is derived from the target's basename + a SHA-1 hash of its absolute path. The same target always resolves to the same directory (last run overwrites previous).

**`report_json.py`** — Emits a structured JSON document:

```json
{
  "scanId": "uuid",
  "timestamp": "ISO-8601",
  "repository": { "path", "totalFiles", "totalLines", "languages" },
  "files": [ { "path", "language", "metrics", "smells", "security_issues" } ],
  "analysis": { "complexity", "duplicates", "total_smells", "total_security_issues" },
  "qualityScore": 99,
  "grade": "A"
}
```

**`report_html.py`** — Builds a self-contained HTML page (Tailwind CSS + Chart.js via CDN):

- Summary cards (grade, files, lines, security issues)
- Three charts: language distribution (doughnut), smells by type (bar), quality radar
- Duplication summary
- Three detail tables: top files by LOC, high-complexity files, security issues

The HTML is assembled from five helper functions (`_files_table`, `_complexity_table`, `_security_table`, `_prepare_chart_data`, `_chart_scripts`) so each piece stays under 50 lines.

---

## Key Design Decisions

**Content reuse** — Stage 2 attaches `content` to each file record. Stages 3–5 read from memory, not disk.

**Per-file vs. cross-file** — Stages 3–5 are embarrassingly parallel (each file is independent). Stage 6 (duplication) intentionally runs last because it requires all files to be in memory simultaneously.

**AST over regex for Python** — Regex cannot distinguish a function call from the same name in a string literal or comment. AST operates on the parsed syntax tree, eliminating false positives entirely.

**Stable output paths** — Hashing the absolute path instead of using a timestamp means repeated scans of the same target overwrite the previous result rather than accumulating directories.
