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
    rounded = round(max(0.0, min(100.0, score)))
    return {"score": rounded, "grade": _grade(rounded)}
