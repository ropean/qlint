# qlint

Multi-language code quality scanner. Walks any codebase and produces JSON, HTML, and Markdown reports covering complexity, duplication, security, code smells, and **predictive risk** (which files are most likely to cause your next outage).

## Install

```bash
# from PyPI
pip install qlint

# from source
git clone https://github.com/ropean/qlint.git
cd qlint
pip install -e .
```

### Using uv

```bash
# as a standalone CLI tool (from PyPI)
uv tool install qlint

# run without installing
uvx qlint /path/to/repo

# from source
git clone https://github.com/ropean/qlint.git
cd qlint
uv tool install --editable .
# or, inside a uv-managed project
uv add qlint
```

## Usage

```bash
qlint /path/to/repo                  # JSON + HTML + Markdown; auto-opens HTML
qlint /path/to/repo --format md      # Markdown only
qlint /path/to/repo --format json,md # JSON + Markdown, no HTML, no auto-open
qlint /path/to/repo --no-open
qlint /path/to/repo --json-only      # print JSON to stdout, no files
qlint /path/to/repo -v               # verbose per-file output
qlint                                # interactive: prompts for path

qlint /path/to/repo --risk           # predictive risk report (top 5 chunked narrative)
qlint /path/to/repo --risk --risk-window 30
qlint /path/to/repo --risk-md /tmp/risk.md   # standalone markdown risk report
```

Reports are written to `~/Downloads/qlint-reports/<repo>/` as `report.json`, `report.html`, and `report.md`. HTML auto-opens only when an HTML report is produced. `--risk` alone prints to the console and writes nothing.

### Options

| Flag | Description |
|------|-------------|
| `--format, -f` | Comma-separated formats: `json`, `html`, `md` (default: all three) |
| `--output, -o` | Custom JSON output path (implies `json`) |
| `--html` | Custom HTML output path (implies `html`) |
| `--md` | Custom Markdown output path (implies `md`) |
| `--risk` | Print predictive risk report (top 5 files most likely to break) |
| `--risk-window` | Days of git history to consider as "recent" (default 90) |
| `--risk-md` | Write standalone risk Markdown report to PATH |
| `--json-only` | Skip files, print JSON to stdout |
| `--no-open` | Do not auto-open HTML report |
| `--verbose, -v` | Show per-file progress |
| `--version` | Show version |

## Analysis Features

| Feature | What it detects |
|---------|----------------|
| **Complexity** | Cyclomatic complexity per function, flags > 10 |
| **Duplication** | Duplicate 6-line blocks across files |
| **Security** | Hardcoded secrets, dangerous functions (`eval`, `exec`, …) |
| **Code Smells** | Long functions, deep nesting, long parameter lists |
| **Predictive Risk** | Recency-weighted: `recent_churn × complexity × (1 + 2·bug_fix_ratio) × (1 + 0.15·authors) / 100`. Each top file gets a `risk_level` (critical/high/medium/low), structured `signals`, and human-readable `reasons`. |

## Predictive Risk

`qlint --risk` highlights the files most likely to cause your next outage by combining:

- **Static signals** — complexity, smells, security issues
- **Git signals (recent window)** — churn, commit frequency, bug-fix ratio, author count

Bug-fix detection scans commit subjects for `fix|bug|hotfix|patch|revert` (case-insensitive). Files with a high share of recent bug-fix commits get amplified scores — past fix density is a strong predictor of future fixes.

Risk levels are bucketed: `critical` (≥50), `high` (≥20), `medium` (≥5), `low` (<5).

## Languages

Python, JavaScript, TypeScript, Java, Go, Ruby, Rust, C, C++, C#, PHP, Swift, Kotlin, Scala, Shell, HTML, CSS, SQL, YAML, JSON, and more.

## JSON Output

```json
{
  "scanId": "...",
  "timestamp": "...",
  "repository": { "path": "...", "totalFiles": 42, "totalLines": 8500, "languages": {} },
  "files": [
    {
      "path": "src/main.py",
      "language": "Python",
      "metrics": { "loc": 120, "code": 95, "comments": 10, "blank": 15, "functions": 8, "classes": 2, "complexity": 4.2 },
      "smells": [],
      "security_issues": [],
      "git_risk": {
        "commits": 12, "churn": 340, "authors": 2,
        "risk_score": 25.5, "risk_level": "high",
        "signals": { "...": "see gitRisk.top_risk_files for the full shape" },
        "reasons": ["active churn (340 lines / window)"]
      }
    }
  ],
  "qualityScore": 87,
  "grade": "B",
  "gitRisk": {
    "available": true,
    "window_days": 90,
    "top_risk_files": [
      {
        "file": "src/main.py",
        "risk_score": 25.5,
        "risk_level": "high",
        "reasons": ["active churn (340 lines / window)"],
        "signals": {
          "complexity": 4.2,
          "recent_commits": 5,
          "recent_churn": 340,
          "all_time_commits": 12,
          "all_time_churn": 600,
          "authors": 2,
          "bug_fix_ratio": 0.4,
          "smells": 1,
          "security_issues": 0
        }
      }
    ]
  }
}
```

## Claude Code skill — `qlint-refactor`

The `.claude/skills/qlint-refactor/` directory ships a Claude Code skill that turns the scanner into a feedback signal: it picks the riskiest file, proposes a behavior-preserving refactor, re-scans, and verifies the score dropped.

**Loop:**

1. Baseline via `scripts/risk_top.py` (top-N risk JSON)
2. Locate the worst function in the top-1 file
3. Propose a minimal refactor (extract function, flatten conditionals, lookup tables)
4. Apply, then `scripts/verify.py FILE --baseline N.NN` → `improved` / `unchanged` / `regressed`
5. Roll back on no-improve; max 3 attempts per file; exit when all top-5 are `risk_score < 50`

**Activates on prompts like** *"list top risk files"*, *"explain why this file is risky"*, *"refactor the risky code"*, *"reduce risk score"*, *"run the risk loop"*.

## Development

```bash
make install   # pip install -e ".[dev]"
make lint      # ruff check
make format    # ruff format
make build     # python -m build
```

## Requirements

- Python 3.11+
- `git` in PATH (for predictive risk; optional — `--risk` degrades gracefully on non-git dirs)
