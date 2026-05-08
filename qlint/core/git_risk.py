import re
import subprocess
import time
from pathlib import Path

BUG_FIX_PATTERN = re.compile(r"\b(fix|bug|hotfix|patch|revert)\b", re.IGNORECASE)


def _run(cmd: list[str], cwd: str) -> str:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60)
    return result.stdout if result.returncode == 0 else ""


def _is_git_repo(root: str) -> bool:
    out = _run(["git", "rev-parse", "--is-inside-work-tree"], root)
    return out.strip() == "true"


def _parse_git_log(root: str, window_days: int) -> dict[str, dict]:
    out = _run(
        [
            "git",
            "log",
            "--numstat",
            "--format=COMMIT:%at|%ae|%s",
            "--diff-filter=ACDMR",
        ],
        root,
    )
    cutoff = int(time.time()) - window_days * 86400
    stats: dict[str, dict] = {}
    cur_author = ""
    cur_is_fix = False
    cur_in_window = False
    for raw in out.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("COMMIT:"):
            parts = line[7:].split("|", 2)
            if len(parts) != 3:
                continue
            ts_s, author, subject = parts
            try:
                ts = int(ts_s)
            except ValueError:
                ts = 0
            cur_author = author
            cur_is_fix = bool(BUG_FIX_PATTERN.search(subject))
            cur_in_window = ts >= cutoff
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added_s, deleted_s, filepath = parts
        if added_s == "-" or deleted_s == "-":
            continue
        try:
            churn = int(added_s) + int(deleted_s)
        except ValueError:
            continue
        filepath = Path(filepath).as_posix()
        s = stats.setdefault(
            filepath,
            {
                "all_commits": 0,
                "all_churn": 0,
                "authors": set(),
                "recent_commits": 0,
                "recent_churn": 0,
                "bug_fix_commits": 0,
            },
        )
        s["all_commits"] += 1
        s["all_churn"] += churn
        s["authors"].add(cur_author)
        if cur_in_window:
            s["recent_commits"] += 1
            s["recent_churn"] += churn
            if cur_is_fix:
                s["bug_fix_commits"] += 1
    return stats


def _risk_score(
    complexity: float, recent_churn: int, bug_fix_ratio: float, authors: int
) -> float:
    base = recent_churn * complexity
    multiplier = (1.0 + 2.0 * bug_fix_ratio) * (1.0 + 0.15 * authors)
    return round(base * multiplier / 100.0, 2)


def _risk_level(score: float) -> str:
    if score >= 50:
        return "critical"
    if score >= 20:
        return "high"
    if score >= 5:
        return "medium"
    return "low"


def _reasons(signals: dict) -> list[str]:
    out: list[str] = []
    bfr = signals["bug_fix_ratio"]
    rc = signals["recent_churn"]
    cx = signals["complexity"]
    auth = signals["authors"]
    sm = signals.get("smells", 0)
    sec = signals.get("security_issues", 0)
    if bfr >= 0.3:
        out.append(f"{int(bfr * 100)}% of recent commits are bug fixes")
    if rc > 100 and cx >= 10:
        out.append(f"high churn ({rc} lines / window) with complexity {cx}")
    elif rc > 50:
        out.append(f"active churn ({rc} lines / window)")
    if auth >= 4:
        out.append(f"{auth} authors → coordination cost")
    if sec > 0:
        out.append(f"{sec} security issue(s) in this file")
    if sm >= 3:
        out.append(f"{sm} code smells flagged")
    if not out:
        out.append("baseline risk only")
    return out


def analyze_git_risk(
    root: str, analyzed_files: list[dict], window_days: int = 90
) -> dict:
    if not _is_git_repo(root):
        return {
            "available": False,
            "window_days": window_days,
            "top_risk_files": [],
        }

    git_stats = _parse_git_log(root, window_days)

    for af in analyzed_files:
        rel = Path(af["relative_path"]).as_posix()
        gs = git_stats.get(rel)
        complexity = af.get("complexity", {}).get("avg_complexity", 1) or 1
        if gs is None:
            authors = 1
            all_commits = 0
            all_churn = 0
            recent_commits = 0
            recent_churn = 0
            bug_fix_commits = 0
        else:
            authors = len(gs["authors"])
            all_commits = gs["all_commits"]
            all_churn = gs["all_churn"]
            recent_commits = gs["recent_commits"]
            recent_churn = gs["recent_churn"]
            bug_fix_commits = gs["bug_fix_commits"]
        bug_fix_ratio = (
            bug_fix_commits / recent_commits if recent_commits else 0.0
        )
        score = _risk_score(complexity, recent_churn, bug_fix_ratio, authors)
        signals = {
            "complexity": complexity,
            "recent_commits": recent_commits,
            "recent_churn": recent_churn,
            "all_time_commits": all_commits,
            "all_time_churn": all_churn,
            "authors": authors,
            "bug_fix_ratio": round(bug_fix_ratio, 2),
            "smells": len(af.get("smells", [])),
            "security_issues": len(af.get("security_issues", [])),
        }
        af["git_risk"] = {
            "commits": all_commits,
            "churn": all_churn,
            "authors": authors,
            "risk_score": score,
            "risk_level": _risk_level(score),
            "signals": signals,
            "reasons": _reasons(signals),
        }

    ranked = sorted(
        [f for f in analyzed_files if f["git_risk"]["signals"]["all_time_commits"] > 0],
        key=lambda f: f["git_risk"]["risk_score"],
        reverse=True,
    )[:10]

    return {
        "available": True,
        "window_days": window_days,
        "top_risk_files": [
            {
                "file": f["relative_path"],
                "risk_score": f["git_risk"]["risk_score"],
                "risk_level": f["git_risk"]["risk_level"],
                "signals": f["git_risk"]["signals"],
                "reasons": f["git_risk"]["reasons"],
                "commits": f["git_risk"]["signals"]["all_time_commits"],
                "churn": f["git_risk"]["signals"]["all_time_churn"],
                "authors": f["git_risk"]["signals"]["authors"],
                "complexity": f["git_risk"]["signals"]["complexity"],
            }
            for f in ranked
        ],
    }
