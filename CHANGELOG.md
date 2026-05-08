# Changelog

## 0.3.0 — 2026-05-08

### Added
- **Three new quality dimensions** integrated into the score:
  - **Markers** — TODO / FIXME / HACK / XXX / BUG / NOTE detector with strict
    matching (requires trailing colon, rejects matches inside string literals,
    skips Markdown / HTML to avoid prose false positives).
  - **Repo Health** — checklist for LICENSE, README, .gitignore, package
    metadata, CI config, tests directory, CHANGELOG, CONTRIBUTING,
    .editorconfig, code of conduct. Reports a hygiene score plus a separate
    `required_score`.
  - **Bus Factor** — repo-level bus factor (minimum authors covering 50% of
    commits) plus per-file single-author warnings (≥80% share by one author).
- **Predictive Risk overhaul** — recency-weighted formula
  `recent_churn × complexity × (1 + 2·bug_fix_ratio) × (1 + 0.15·authors) / 100`
  with configurable window (default 90 days), risk levels, structured signals,
  and human-readable reasons.
- **`--risk` CLI flag** — chunked top-5 narrative on stdout.
- **`--risk-window N`** — configurable recency window in days.
- **`--risk-md PATH`** — standalone risk Markdown report.
- **`qlint-refactor` skill** at `.claude/skills/qlint-refactor/` — packaged
  Claude Code skill driving a behavior-preserving refactor loop using
  `risk_score` as the success signal. Ships with `risk_top.py` and
  `verify.py` helper scripts.
- **Themed HTML report** — Resend-inspired dark/light themes, frost-blue
  borders, theme toggle persisted via localStorage, embedded SVG favicon as
  base64 data URI, theme-aware Chart.js charts.
- **Landing page** at `index.html` reusing the report's palette and theme
  toggle. Suitable for GitHub Pages.
- **Local-time HHMM in default report filenames** —
  `report-MMDDYY-HHMM.{html,json,md}` so back-to-back scans no longer
  overwrite each other.
- **`scan_utc` field** in analysis carrying ISO-8601 UTC timestamp; HTML's
  `<time datetime>` element + JS `toLocaleString` render the viewer's local
  timezone.
- **GitHub Actions CI workflow** running ruff + a self-scan smoke check on
  Python 3.11 and 3.12.

### Changed
- Default report filenames now include a date-time suffix.
- Per-repo output directory uses a hyphen separator instead of underscore.
- `git_risk.parse_git_log` is now public and tracks per-file author commit
  counts as a dict so other analyzers can reuse the same git pass.
- All numeric cells in the HTML report routed through formatting helpers:
  thousand separators on counts, two decimals on floats.

### Fixed
- Markers regex no longer false-positives on prose, regex source, or string
  literals.
- `traversal._load_gitignore_spec` flattened from nesting depth 6 to 3 by
  extracting `_read_gitignore_lines` and `_anchor_pattern` helpers.

## 0.2.1 — earlier

- Markdown report + format selection.
- Cross-platform path input.
- Initial predictive risk via git history.
