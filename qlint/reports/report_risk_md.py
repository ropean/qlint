from datetime import datetime, timezone


_LEVEL_BADGE = {
    "critical": "🔴 CRITICAL",
    "high": "🟠 HIGH",
    "medium": "🟡 MEDIUM",
    "low": "🟢 LOW",
}


def _file_block(idx: int, f: dict) -> str:
    s = f["signals"]
    badge = _LEVEL_BADGE.get(f["risk_level"], f["risk_level"].upper())
    reasons = "\n".join(f"- {r}" for r in f["reasons"])
    return (
        f"### {idx}. {badge} — `{f['file']}`\n\n"
        f"**Risk score:** {f['risk_score']}\n\n"
        f"**Why this file is risky**\n{reasons}\n\n"
        f"**Signals**\n\n"
        f"| Metric | Value |\n"
        f"| --- | ---: |\n"
        f"| Avg complexity | {s['complexity']} |\n"
        f"| Recent commits ({s.get('window_days', '')}d) | {s['recent_commits']} |\n"
        f"| Recent churn (lines) | {s['recent_churn']} |\n"
        f"| All-time commits | {s['all_time_commits']} |\n"
        f"| Authors | {s['authors']} |\n"
        f"| Bug-fix ratio (recent) | {s['bug_fix_ratio']} |\n"
        f"| Code smells | {s['smells']} |\n"
        f"| Security issues | {s['security_issues']} |\n"
    )


def generate_risk_md(analysis: dict, output_path: str = None) -> str:
    summary = analysis.get("git_risk_summary", {})
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    root = analysis.get("root", "")
    if not summary.get("available"):
        md = (
            f"# Predictive Risk Report\n\n"
            f"`{root}`  \n_Generated {ts}_\n\n"
            f"_Git risk unavailable: not a git repository or no history found._\n"
        )
    else:
        window = summary.get("window_days", 90)
        files = summary.get("top_risk_files", [])
        for f in files:
            f["signals"]["window_days"] = window
        header = (
            f"# Predictive Risk Report\n\n"
            f"`{root}`  \n_Generated {ts}_\n\n"
            f"**Window:** last {window} days  \n"
            f"**Formula:** `recent_churn × complexity × (1 + 2·bug_fix_ratio) × "
            f"(1 + 0.15·authors) / 100`\n\n"
            f"---\n\n"
        )
        if not files:
            body = "_No file activity in the recent window. Nothing to flag._\n"
        else:
            n = min(5, len(files))
            body = (
                f"## Top {n} files most likely to cause your next outage\n\n"
                + "\n".join(_file_block(i + 1, f) for i, f in enumerate(files[:5]))
            )
            if len(files) > 5:
                body += "\n\n## Others (rank 6–10)\n\n"
                body += "| Rank | File | Risk | Level |\n| ---: | --- | ---: | --- |\n"
                for i, f in enumerate(files[5:10], start=6):
                    body += (
                        f"| {i} | `{f['file']}` | {f['risk_score']} | "
                        f"{f['risk_level']} |\n"
                    )
        md = header + body
    if output_path:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(md.rstrip() + "\n")
    return md
