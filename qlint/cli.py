"""qlint — multi-language code quality scanner."""

import argparse
import hashlib
import os
import platform
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from qlint import __version__
from qlint.core.traversal import walk_codebase
from qlint.core.metrics import analyze_file
from qlint.core.complexity import analyze_complexity
from qlint.core.smells import analyze_smells
from qlint.core.security import scan_security
from qlint.core.duplicates import find_duplicates
from qlint.core.quality import calculate_quality_score
from qlint.core.git_risk import analyze_git_risk
from qlint.core.bus_factor import analyze_bus_factor
from qlint.core.repo_health import analyze_repo_health
from qlint.core.markers import analyze_markers, summarize_markers
from qlint.reports.report_json import generate_json
from qlint.reports.report_html import generate_html
from qlint.reports.report_md import generate_md


def _results_dir() -> str:
    downloads = Path.home() / "Downloads"
    base = downloads if downloads.is_dir() else Path.home()
    out = base / "qlint-reports"
    out.mkdir(parents=True, exist_ok=True)
    return str(out)


def make_output_dir(target_path: str) -> str:
    abs_path = os.path.abspath(target_path)
    dirname = os.path.basename(abs_path.rstrip("/\\")) or "scan"
    slug = "".join(c if c.isalnum() or c in "-" else "_" for c in dirname).strip("_")
    short_hash = hashlib.sha1(abs_path.encode()).hexdigest()[:7]
    out_dir = os.path.join(_results_dir(), f"{slug}-{short_hash}")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def open_file(path: str) -> None:
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["open", path], check=False)
        elif system == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", path], check=False)
    except Exception:
        pass


def scan(root: str, verbose: bool = False, risk_window_days: int = 90) -> dict:
    started = datetime.now(timezone.utc)
    print(f"Scanning: {root}", file=sys.stderr)
    raw_files = walk_codebase(root)
    print(f"Found {len(raw_files)} files", file=sys.stderr)

    analyzed = []
    for file_info in raw_files:
        if verbose:
            print(f"  Analyzing: {file_info['relative_path']}", file=sys.stderr)
        af = analyze_file(file_info)
        af["complexity"] = analyze_complexity(af)
        af["smells"] = analyze_smells(af)
        af["security_issues"] = scan_security(af)
        af["markers"] = analyze_markers(af)
        analyzed.append(af)

    print("Running duplication analysis...", file=sys.stderr)
    duplicates = find_duplicates(analyzed)

    abs_root = os.path.abspath(root)
    print("Analyzing git risk...", file=sys.stderr)
    git_risk_summary = analyze_git_risk(abs_root, analyzed, window_days=risk_window_days)
    print("Analyzing bus factor...", file=sys.stderr)
    bus_factor = analyze_bus_factor(abs_root, analyzed)
    print("Checking repo health...", file=sys.stderr)
    repo_health = analyze_repo_health(abs_root)
    markers_summary = summarize_markers(analyzed)

    languages: dict = defaultdict(lambda: {"files": 0, "lines": 0})
    for f in analyzed:
        languages[f["language"]]["files"] += 1
        languages[f["language"]]["lines"] += f["metrics"]["loc"]

    total_files = len(analyzed)
    total_lines = sum(f["metrics"]["loc"] for f in analyzed)
    flagged = sum(f.get("complexity", {}).get("flagged_count", 0) for f in analyzed)
    avg_c = sum(
        f.get("complexity", {}).get("avg_complexity", 0) for f in analyzed
    ) / max(total_files, 1)

    analysis = {
        "root": os.path.abspath(root),
        "files": analyzed,
        "total_files": total_files,
        "total_lines": total_lines,
        "languages": dict(languages),
        "duplicates": duplicates,
        "git_risk_summary": git_risk_summary,
        "total_smells": sum(len(f.get("smells", [])) for f in analyzed),
        "total_security_issues": sum(
            len(f.get("security_issues", [])) for f in analyzed
        ),
        "complexity_summary": {
            "flagged_count": flagged,
            "avg_complexity": round(avg_c, 2),
        },
        "scan_utc": started.isoformat(timespec="seconds"),
        "scan_date_label": started.astimezone().strftime("%m%d%y-%H%M"),
        "markers": markers_summary,
        "repo_health": repo_health,
        "bus_factor": bus_factor,
    }
    analysis["quality"] = calculate_quality_score(analysis)
    return analysis


def print_summary(analysis: dict) -> None:
    q = analysis["quality"]
    print(f"\n{'=' * 50}")
    print("  qlint — Code Quality Report")
    print(f"{'=' * 50}")
    print(f"  Grade:           {q['grade']} ({q['score']}/100)")
    print(f"  Files:           {analysis['total_files']}")
    print(f"  Total Lines:     {analysis['total_lines']:,}")
    print(f"  Languages:       {', '.join(analysis['languages'].keys())}")
    print(f"  Security Issues: {analysis['total_security_issues']}")
    print(f"  Code Smells:     {analysis['total_smells']}")
    print(
        f"  Dup Blocks:      {analysis['duplicates'].get('total_duplicate_blocks', 0)}"
    )
    print(f"{'=' * 50}\n")


_LEVEL_TAG = {
    "critical": "[CRITICAL]",
    "high":     "[ HIGH   ]",
    "medium":   "[ MEDIUM ]",
    "low":      "[ LOW    ]",
}


def print_risk_narrative(analysis: dict, top_n: int = 5) -> None:
    summary = analysis.get("git_risk_summary", {})
    if not summary.get("available"):
        print("\nGit risk: not available (not a git repo or no history)\n")
        return
    files = summary.get("top_risk_files", [])
    window = summary.get("window_days", 90)
    print(f"\n{'=' * 60}")
    print(f"  Predictive Risk Report — last {window} days")
    print(f"{'=' * 60}")
    if not files:
        print("  No file activity in window. Nothing to flag.\n")
        return
    print(f"  Top {min(top_n, len(files))} files most likely to cause your next outage:\n")
    for idx, f in enumerate(files[:top_n], 1):
        tag = _LEVEL_TAG.get(f["risk_level"], "[ ?      ]")
        print(f"  {idx}. {tag}  {f['file']}")
        print(f"     risk score: {f['risk_score']}")
        for reason in f["reasons"]:
            print(f"       • {reason}")
        s = f["signals"]
        print(
            f"     signals: complexity={s['complexity']}  "
            f"recent_commits={s['recent_commits']}  "
            f"recent_churn={s['recent_churn']}  "
            f"bug_fix_ratio={s['bug_fix_ratio']}  "
            f"authors={s['authors']}  "
            f"smells={s['smells']}  "
            f"security={s['security_issues']}"
        )
        print()


def _resolve_dir(raw: str) -> Path | None:
    """Expand ~, normalise separators, resolve symlinks. Returns None if not a dir."""
    try:
        p = Path(raw.strip()).expanduser().resolve()
        return p if p.is_dir() else None
    except (ValueError, OSError):
        return None


def prompt_path() -> str:
    print("qlint — no path specified.")
    while True:
        try:
            raw = input("Enter directory to scan (or 'q' to quit): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nqlint: cancelled", file=sys.stderr)
            sys.exit(130)
        if raw.lower() in ("q", "quit", "exit"):
            sys.exit(0)
        p = _resolve_dir(raw)
        if p:
            return str(p)
        print(f"  Not a directory: '{raw}'. Please try again.")


_VALID_FORMATS = {"json", "html", "md"}


def _select_formats(args) -> set[str]:
    selected: set[str] = set()
    if args.format:
        for token in args.format.replace(",", " ").split():
            t = token.lower()
            if t not in _VALID_FORMATS:
                print(
                    f"qlint: unknown format '{token}' (valid: json, html, md)",
                    file=sys.stderr,
                )
                sys.exit(2)
            selected.add(t)
    if args.output:
        selected.add("json")
    if args.html:
        selected.add("html")
    if args.md:
        selected.add("md")
    return selected or set(_VALID_FORMATS)


def main() -> None:
    try:
        _run()
    except KeyboardInterrupt:
        print("\nqlint: cancelled", file=sys.stderr)
        sys.exit(130)


def _run() -> None:
    parser = argparse.ArgumentParser(
        prog="qlint",
        description="qlint — multi-language code quality scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  qlint                        # interactive: prompts for path
  qlint /path/to/repo          # scan, write JSON+HTML+Markdown, open HTML
  qlint /path/to/repo --format json,md
  qlint /path/to/repo --html report.html
  qlint /path/to/repo --json-only
  qlint /path/to/repo -v       # verbose per-file output
        """,
    )
    parser.add_argument(
        "path", nargs="?", help="Directory to scan (prompts if omitted)"
    )
    parser.add_argument("--output", "-o", help="Custom JSON output path")
    parser.add_argument("--html", help="Custom HTML output path")
    parser.add_argument("--md", help="Custom Markdown output path")
    parser.add_argument(
        "--format",
        "-f",
        help="Comma-separated formats to emit: json,html,md (default: all)",
    )
    parser.add_argument(
        "--json-only", action="store_true", help="Skip files, print JSON to stdout"
    )
    parser.add_argument(
        "--no-open", action="store_true", help="Do not auto-open HTML report"
    )
    parser.add_argument(
        "--risk",
        action="store_true",
        help="Print predictive risk report (top 5 files most likely to break)",
    )
    parser.add_argument(
        "--risk-window",
        type=int,
        default=90,
        help="Days of git history to consider as 'recent' for risk (default: 90)",
    )
    parser.add_argument(
        "--risk-md",
        help="Write standalone risk markdown report to PATH",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print summary block (default when no --risk/--json-only)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show per-file progress"
    )
    parser.add_argument("--version", action="version", version=f"qlint {__version__}")
    args = parser.parse_args()

    target = args.path
    if not target:
        target = prompt_path()
    else:
        resolved = _resolve_dir(target)
        if not resolved:
            print(f"qlint: '{target}' is not a directory", file=sys.stderr)
            sys.exit(1)
        target = str(resolved)

    analysis = scan(target, verbose=args.verbose, risk_window_days=args.risk_window)
    print_summary(analysis)

    if args.risk:
        print_risk_narrative(analysis)

    if args.json_only:
        print(generate_json(analysis))
        return

    explicit_format = bool(
        args.format or args.output or args.html or args.md or args.risk_md
    )
    risk_only = args.risk and not explicit_format
    if risk_only:
        return

    formats = _select_formats(args)

    out_dir = make_output_dir(target)
    suffix = f"-{analysis.get('scan_date_label', '')}" if analysis.get("scan_date_label") else ""
    json_path = str(Path(args.output).expanduser().resolve()) if args.output else os.path.join(out_dir, f"report{suffix}.json")
    html_path = str(Path(args.html).expanduser().resolve()) if args.html else os.path.join(out_dir, f"report{suffix}.html")
    md_path = str(Path(args.md).expanduser().resolve()) if args.md else os.path.join(out_dir, f"report{suffix}.md")
    risk_md_path = (
        str(Path(args.risk_md).expanduser().resolve()) if args.risk_md else None
    )

    if "json" in formats:
        generate_json(analysis, output_path=json_path)
        print(f"JSON: {json_path}", file=sys.stderr)
    if "html" in formats:
        generate_html(analysis, output_path=html_path)
        print(f"HTML: {html_path}", file=sys.stderr)
    if "md" in formats:
        generate_md(analysis, output_path=md_path)
        print(f"MD:   {md_path}", file=sys.stderr)
    if risk_md_path:
        from qlint.reports.report_risk_md import generate_risk_md
        generate_risk_md(analysis, output_path=risk_md_path)
        print(f"RISK: {risk_md_path}", file=sys.stderr)

    if "html" in formats and not args.no_open and not args.risk:
        open_file(html_path)
