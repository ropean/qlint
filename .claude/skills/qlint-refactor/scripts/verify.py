#!/usr/bin/env python3
"""Verify a single file's risk_score against a baseline for qlint-refactor."""
import argparse
import json
import os
import subprocess
import sys
import tempfile


def _scan(cwd: str, window: int) -> dict:
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


def _record_for(data: dict, target: str) -> dict | None:
    for f in data.get("gitRisk", {}).get("top_risk_files", []):
        if f["file"] == target:
            return f
    return None


def _verdict(delta: float) -> str:
    if delta < -0.01:
        return "improved"
    if delta > 0.01:
        return "regressed"
    return "unchanged"


def main() -> None:
    ap = argparse.ArgumentParser(description="Verify risk delta for one file")
    ap.add_argument("file", help="Relative path of file to check (matches gitRisk.file)")
    ap.add_argument(
        "--baseline",
        type=float,
        default=None,
        help="Baseline risk_score; if given, compute delta + verdict",
    )
    ap.add_argument("--cwd", default=".")
    ap.add_argument("--window", type=int, default=90)
    args = ap.parse_args()

    data = _scan(args.cwd, args.window)
    rec = _record_for(data, args.file)

    if rec is None:
        out = {
            "file": args.file,
            "found": False,
            "message": (
                "file not in gitRisk.top_risk_files — likely no recent activity "
                "in the window or the file was filtered out by traversal"
            ),
        }
        if args.baseline is not None:
            out["baseline"] = args.baseline
            out["delta"] = round(0.0 - args.baseline, 2)
            out["verdict"] = _verdict(out["delta"])
            out["risk_score"] = 0.0
            out["improved"] = out["verdict"] == "improved"
        print(json.dumps(out, indent=2))
        return

    after = rec["risk_score"]
    out = {
        "file": args.file,
        "found": True,
        "risk_score": after,
        "risk_level": rec["risk_level"],
        "reasons": rec["reasons"],
        "signals": rec["signals"],
    }
    if args.baseline is not None:
        delta = round(after - args.baseline, 2)
        out["baseline"] = args.baseline
        out["delta"] = delta
        out["verdict"] = _verdict(delta)
        out["improved"] = delta < 0
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
