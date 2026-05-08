def _complexity_penalty(analysis: dict) -> float:
    flagged = analysis.get("complexity_summary", {}).get("flagged_count", 0)
    total_funcs = max(
        sum(f["metrics"].get("functions", 0) for f in analysis.get("files", [])), 1
    )
    return min(flagged / total_funcs, 1.0) * 30


def _duplication_penalty(analysis: dict) -> float:
    dup_pct = analysis.get("duplicates", {}).get("duplication_percentage", 0)
    return min(dup_pct / 100, 1.0) * 25


def _smells_penalty(analysis: dict) -> float:
    files = analysis.get("files", [])
    per_file = sum(len(f.get("smells", [])) for f in files) / max(len(files), 1)
    return min(per_file / 5, 1.0) * 25


def _security_penalty(analysis: dict) -> float:
    files = analysis.get("files", [])
    critical = sum(
        1
        for f in files
        for i in f.get("security_issues", [])
        if i["severity"] == "critical"
    )
    errors = sum(
        1
        for f in files
        for i in f.get("security_issues", [])
        if i["severity"] == "error"
    )
    return min((critical * 10 + errors * 3) / 20, 1.0) * 20


def _markers_penalty(analysis: dict) -> float:
    total = analysis.get("markers", {}).get("total", 0)
    loc = max(analysis.get("total_lines", 1), 1)
    density = total / loc * 1000  # markers per kLOC
    return min(density / 50, 1.0) * 4


def _repo_health_penalty(analysis: dict) -> float:
    rh = analysis.get("repo_health", {})
    if not rh:
        return 0.0
    required_score = rh.get("required_score", 100)
    deficit = max(0, 100 - required_score) / 100
    return deficit * 4


def _bus_factor_penalty(analysis: dict) -> float:
    bf = analysis.get("bus_factor", {})
    if not bf.get("available"):
        return 0.0
    factor = bf.get("repo_bus_factor", 99)
    if factor >= 3:
        return 0.0
    if factor == 2:
        return 1.0
    return 3.0  # factor == 1 (or 0 with no commits)


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def calculate_quality_score(analysis: dict) -> dict:
    score = 100.0
    score -= _complexity_penalty(analysis)
    score -= _duplication_penalty(analysis)
    score -= _smells_penalty(analysis)
    score -= _security_penalty(analysis)
    score -= _markers_penalty(analysis)
    score -= _repo_health_penalty(analysis)
    score -= _bus_factor_penalty(analysis)
    rounded = round(max(0.0, min(100.0, score)))
    return {"score": rounded, "grade": _grade(rounded)}
