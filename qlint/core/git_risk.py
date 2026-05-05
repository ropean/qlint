import subprocess
from pathlib import Path


def _run(cmd: list[str], cwd: str) -> str:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
    return result.stdout if result.returncode == 0 else ""


def _is_git_repo(root: str) -> bool:
    out = _run(["git", "rev-parse", "--is-inside-work-tree"], root)
    return out.strip() == "true"


def _parse_git_log(root: str) -> dict[str, dict]:
    """One git log pass → per-file {commits, churn, authors}."""
    out = _run(
        ["git", "log", "--numstat", "--format=AUTHOR:%ae", "--diff-filter=ACDMR"],
        root,
    )
    stats: dict[str, dict] = {}
    current_author = ""
    for raw in out.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("AUTHOR:"):
            current_author = line[7:]
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added_s, deleted_s, filepath = parts
        # Skip binary files (git outputs "-" for binary diffs)
        if added_s == "-" or deleted_s == "-":
            continue
        try:
            churn = int(added_s) + int(deleted_s)
        except ValueError:
            continue
        # Normalise to forward slashes so it matches relative_path from traversal
        filepath = Path(filepath).as_posix()
        if filepath not in stats:
            stats[filepath] = {"commits": 0, "churn": 0, "authors": set()}
        stats[filepath]["commits"] += 1
        stats[filepath]["churn"] += churn
        stats[filepath]["authors"].add(current_author)

    # Freeze author sets to counts
    return {
        fp: {
            "commits": v["commits"],
            "churn": v["churn"],
            "authors": len(v["authors"]),
        }
        for fp, v in stats.items()
    }


def _risk_score(complexity: float, churn: int, authors: int) -> float:
    return round((complexity * churn) / max(authors, 1), 2)


def analyze_git_risk(root: str, analyzed_files: list[dict]) -> dict:
    if not _is_git_repo(root):
        return {"available": False, "top_risk_files": []}

    git_stats = _parse_git_log(root)

    for af in analyzed_files:
        rel = Path(af["relative_path"]).as_posix()
        gs = git_stats.get(rel, {"commits": 0, "churn": 0, "authors": 1})
        complexity = af.get("complexity", {}).get("avg_complexity", 1) or 1
        af["git_risk"] = {
            "commits": gs["commits"],
            "churn": gs["churn"],
            "authors": gs["authors"],
            "risk_score": _risk_score(complexity, gs["churn"], gs["authors"]),
        }

    ranked = sorted(
        [f for f in analyzed_files if f["git_risk"]["churn"] > 0],
        key=lambda f: f["git_risk"]["risk_score"],
        reverse=True,
    )[:10]

    return {
        "available": True,
        "top_risk_files": [
            {
                "file": f["relative_path"],
                "risk_score": f["git_risk"]["risk_score"],
                "commits": f["git_risk"]["commits"],
                "churn": f["git_risk"]["churn"],
                "authors": f["git_risk"]["authors"],
                "complexity": f.get("complexity", {}).get("avg_complexity", 0),
            }
            for f in ranked
        ],
    }
