import json
import uuid
from datetime import datetime, timezone


def generate_json(analysis: dict, output_path: str = None) -> str:
    report = {
        "scanId": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repository": {
            "path": analysis["root"],
            "totalFiles": analysis["total_files"],
            "totalLines": analysis["total_lines"],
            "languages": analysis["languages"],
        },
        "files": [
            {
                "path": f["relative_path"],
                "language": f["language"],
                "metrics": {
                    "loc": f["metrics"]["loc"],
                    "code": f["metrics"]["code"],
                    "comments": f["metrics"]["comments"],
                    "blank": f["metrics"]["blank"],
                    "functions": f["metrics"]["functions"],
                    "classes": f["metrics"]["classes"],
                    "complexity": f.get("complexity", {}).get("avg_complexity", 0),
                },
                "smells": f.get("smells", []),
                "security_issues": f.get("security_issues", []),
                "markers": f.get("markers", []),
                "git_risk": f.get("git_risk", {}),
            }
            for f in analysis["files"]
        ],
        "analysis": {
            "complexity": analysis.get("complexity_summary", {}),
            "duplicates": analysis.get("duplicates", {}),
            "total_smells": analysis.get("total_smells", 0),
            "total_security_issues": analysis.get("total_security_issues", 0),
        },
        "qualityScore": analysis["quality"]["score"],
        "grade": analysis["quality"]["grade"],
        "gitRisk": analysis.get("git_risk_summary", {"available": False, "top_risk_files": []}),
        "markers": analysis.get("markers", {"total": 0, "by_type": {}, "top_files": [], "samples": []}),
        "repoHealth": analysis.get("repo_health", {"score": 0, "checks": []}),
        "busFactor": analysis.get("bus_factor", {"available": False}),
        "scanUtc": analysis.get("scan_utc"),
    }

    json_str = json.dumps(report, indent=2)
    if output_path:
        with open(output_path, "w") as f:
            f.write(json_str)
    return json_str
