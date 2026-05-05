# qlint

Multi-language code quality scanner. Walks any codebase and produces JSON + HTML reports covering complexity, duplication, security, and code smells.

## Install

```bash
pip install -e .
```

## Usage

```bash
qlint /path/to/repo          # scan and open HTML report
qlint /path/to/repo --no-open
qlint /path/to/repo --json-only
qlint /path/to/repo -v       # verbose per-file output
qlint                        # interactive: prompts for path
```

Reports are written to `~/Downloads/qlint-reports/<repo>/`.

### Options

| Flag | Description |
|------|-------------|
| `--output, -o` | Custom JSON output path |
| `--html` | Custom HTML output path |
| `--json-only` | Skip HTML, print JSON to stdout |
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
| **Git Risk** | `risk = (complexity × churn) / authors` — predicts high-debt files using git history |

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
      "git_risk": { "commits": 12, "churn": 340, "authors": 2, "risk_score": 25.5 }
    }
  ],
  "qualityScore": 87,
  "grade": "B",
  "gitRisk": {
    "available": true,
    "top_risk_files": []
  }
}
```

## Development

```bash
make install   # pip install -e ".[dev]"
make lint      # ruff check
make format    # ruff format
make build     # python3 -m build
```

## Requirements

- Python 3.11+
- `git` in PATH (for git risk analysis; optional)
