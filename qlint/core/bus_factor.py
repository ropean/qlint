from pathlib import Path

from qlint.core.git_risk import is_git_repo, parse_git_log


_SINGLE_AUTHOR_THRESHOLD = 0.80
_COVERAGE_TARGET = 0.50


def _repo_bus_factor(author_totals: dict[str, int]) -> tuple[int, int]:
    if not author_totals:
        return 0, 0
    total = sum(author_totals.values())
    if total == 0:
        return 0, 0
    sorted_counts = sorted(author_totals.values(), reverse=True)
    covered = 0
    for i, c in enumerate(sorted_counts, start=1):
        covered += c
        if covered >= total * _COVERAGE_TARGET:
            return i, total
    return len(sorted_counts), total


def analyze_bus_factor(root: str, analyzed_files: list[dict]) -> dict:
    if not is_git_repo(root):
        return {"available": False}

    git_stats = parse_git_log(root, window_days=10**9)

    author_totals: dict[str, int] = {}
    for fp, s in git_stats.items():
        for author, c in s["authors"].items():
            author_totals[author] = author_totals.get(author, 0) + c

    bus_factor, total_commits = _repo_bus_factor(author_totals)

    top_authors = sorted(
        (
            {"author": a, "commits": c, "share": round(c / total_commits, 3)}
            for a, c in author_totals.items()
        ),
        key=lambda r: r["commits"],
        reverse=True,
    )[:10]

    tracked = {Path(f["relative_path"]).as_posix() for f in analyzed_files}
    single_author_files: list[dict] = []
    for fp, s in git_stats.items():
        if fp not in tracked:
            continue
        authors = s["authors"]
        if not authors:
            continue
        file_total = sum(authors.values())
        top_author, top_count = max(authors.items(), key=lambda kv: kv[1])
        share = top_count / file_total if file_total else 0
        if share >= _SINGLE_AUTHOR_THRESHOLD and file_total >= 2:
            single_author_files.append(
                {
                    "file": fp,
                    "top_author": top_author,
                    "share": round(share, 2),
                    "commits": file_total,
                }
            )
    single_author_files.sort(key=lambda r: (-r["commits"], r["file"]))
    single_author_files = single_author_files[:15]

    return {
        "available": True,
        "repo_bus_factor": bus_factor,
        "total_authors": len(author_totals),
        "total_commits": total_commits,
        "coverage_target": _COVERAGE_TARGET,
        "top_authors": top_authors,
        "single_author_files": single_author_files,
        "single_author_threshold": _SINGLE_AUTHOR_THRESHOLD,
    }
