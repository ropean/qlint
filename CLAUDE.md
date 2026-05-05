# Code Scanner — Ground Rules

## Project Overview
A Python CLI code scanner that walks codebases and extracts quality metrics.
Output: JSON + HTML reports with complexity, duplication, security, and smell analysis.

## Rules

### R1: Design Before Code
Always sketch the JSON output schema and CLI interface BEFORE implementing a new feature.
Catch misalignments early — asking "What will you build?" before any feature saves re-prompts.

### R2: Feedback Loop Is Mandatory
After every feature change, run the scanner on itself:
```bash
qlint . --summary
```
If quality score drops, fix before moving on. Real output catches bugs faster than reading code.

### R3: Validate JSON Output
After changes that touch metrics or reports, verify the JSON schema is intact:
```bash
qlint . --output /tmp/check.json && python -c "import json; d=json.load(open('/tmp/check.json')); print('OK:', d['grade'], d['qualityScore'])"
```

### R4: Module Boundaries
Each analysis feature lives in `qlint/core/`. Reports live in `qlint/reports/`.
Do NOT mix analysis logic into report code or vice versa.

### R5: Error Handling at Boundaries Only
Trust Python stdlib. Only catch exceptions at file I/O boundaries (read errors, permission denied).
Do not add try/except inside analysis functions unless the input is external user data.

### R6: No Comments on Obvious Code
Only comment WHY, never WHAT. A function named `analyze_python_complexity` needs no docstring.

## Custom Commands

### /scan-self
Run scanner on this project and open report:
```bash
qlint . --summary --html report.html --output report.json && open report.html
```

### /scan-validate
Scan and validate JSON schema integrity:
```bash
qlint . --output /tmp/scan_validate.json 2>/dev/null && python -c "
import json
d = json.load(open('/tmp/scan_validate.json'))
required = ['scanId', 'timestamp', 'repository', 'files', 'qualityScore', 'grade']
missing = [k for k in required if k not in d]
print('PASS' if not missing else f'MISSING: {missing}')
print(f'Grade: {d[\"grade\"]} ({d[\"qualityScore\"]}/100), Files: {d[\"repository\"][\"totalFiles\"]}')
"
```

### /scan-full <path>
Full scan with both reports:
```bash
qlint <path> --summary --html /tmp/scan_report.html --output /tmp/scan_report.json && open /tmp/scan_report.html
```

## Feedback Loop Protocol
1. Implement feature
2. Run `qlint . --summary`
3. Compare score to baseline (baseline: B, 83/100)
4. If score drops > 5 points, investigate before continuing
5. Run `qlint /path/to/real/codebase --summary` to test on real input
