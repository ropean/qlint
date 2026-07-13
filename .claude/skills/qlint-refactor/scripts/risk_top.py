#!/usr/bin/env python
"""Compact top-N risk JSON for the qlint-refactor skill loop."""
import argparse
import json
import os
import subprocess
import sys
import tempfile


def _run_qlint(cwd: str, window: int) -> dict:
    fd, out_path = tempfile.mkstemp(prefix="qlint_skill_", suffix=".json")
    os.close(fd)
    try:
        proc = subprocess.run(
            [
                "qlint",
                cwd,
                "--output", out_path,
                "--format", "json",
                "--no-open",
                "--risk-window", str(window),
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if proc.returncode != 0:
            print(
                json.dumps({"error": "qlint failed", "stderr": proc.stderr.strip()}),
                file=sys.stderr,
            )
            sys.exit(proc.returncode or 1)
        with open(out_path) as fh:
            return json.load(fh)
    finally:
        try:
            os.unlink(out_path)
        except OSError:
            pass


def main() -> None:
    ap = argparse.ArgumentParser(description="Compact top-N risk for qlint-refactor")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--cwd", default=".")
    ap.add_argument("--window", type=int, default=90)
    args = ap.parse_args()

    data = _run_qlint(args.cwd, args.window)
    gr = data.get("gitRisk", {})
    files = gr.get("top_risk_files", [])[: args.top]
    out_files = []
    for f in files:
        s = f["signals"]
        out_files.append(
            {
                "file": f["file"],
                "risk_score": f["risk_score"],
                "risk_level": f["risk_level"],
                "top_reason": f["reasons"][0] if f["reasons"] else "",
                "all_reasons": f["reasons"],
                "complexity": s["complexity"],
                "recent_commits": s["recent_commits"],
                "recent_churn": s["recent_churn"],
                "bug_fix_ratio": s["bug_fix_ratio"],
                "authors": s["authors"],
                "smells": s["smells"],
                "security_issues": s["security_issues"],
            }
        )
    print(
        json.dumps(
            {
                "available": gr.get("available", False),
                "window_days": gr.get("window_days", args.window),
                "grade": data.get("grade"),
                "qualityScore": data.get("qualityScore"),
                "files": out_files,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
