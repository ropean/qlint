from datetime import datetime, timezone


def _section(title: str, body: str) -> str:
    return f"## {title}\n\n{body}\n\n"


def _summary(analysis: dict) -> str:
    q = analysis["quality"]
    dup = analysis.get("duplicates", {})
    langs = ", ".join(analysis["languages"].keys()) or "—"
    rows = [
        ("Grade", f"**{q['grade']}** ({q['score']}/100)"),
        ("Files", f"{analysis['total_files']:,}"),
        ("Total Lines", f"{analysis['total_lines']:,}"),
        ("Languages", langs),
        ("Security Issues", str(analysis.get("total_security_issues", 0))),
        ("Code Smells", str(analysis.get("total_smells", 0))),
        ("Duplicate Blocks", str(dup.get("total_duplicate_blocks", 0))),
        ("Duplication Rate", f"{dup.get('duplication_percentage', 0)}%"),
    ]
    body = "| Metric | Value |\n| --- | --- |\n"
    body += "\n".join(f"| {k} | {v} |" for k, v in rows)
    return _section("Summary", body)


def _languages(analysis: dict) -> str:
    langs = analysis.get("languages", {})
    if not langs:
        return ""
    body = "| Language | Files | Lines |\n| --- | ---: | ---: |\n"
    for name, stats in sorted(langs.items(), key=lambda kv: -kv[1]["lines"]):
        body += f"| {name} | {stats['files']} | {stats['lines']:,} |\n"
    return _section("Languages", body.rstrip())


def _top_files(files: list[dict]) -> str:
    top = sorted(files, key=lambda f: f["metrics"]["loc"], reverse=True)[:10]
    if not top:
        return ""
    body = (
        "| File | Language | LOC | Functions | Complexity | Smells | Security |\n"
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |\n"
    )
    for f in top:
        sc = len(f.get("security_issues", []))
        body += (
            f"| `{f['relative_path']}` | {f['language']} | "
            f"{f['metrics']['loc']} | {f['metrics']['functions']} | "
            f"{f.get('complexity', {}).get('avg_complexity', 0)} | "
            f"{len(f.get('smells', []))} | {sc} |\n"
        )
    return _section("Top Files by Size", body.rstrip())


def _high_complexity(files: list[dict]) -> str:
    top = sorted(
        files,
        key=lambda f: f.get("complexity", {}).get("max_complexity", 0),
        reverse=True,
    )[:5]
    rows = [f for f in top if f.get("complexity", {}).get("max_complexity", 0)]
    if not rows:
        return _section("High Complexity Files", "_No high complexity detected._")
    body = (
        "| File | Language | Max Complexity | Flagged Functions |\n"
        "| --- | --- | ---: | ---: |\n"
    )
    for f in rows:
        c = f.get("complexity", {})
        body += (
            f"| `{f['relative_path']}` | {f['language']} | "
            f"{c.get('max_complexity', 0)} | {c.get('flagged_count', 0)} |\n"
        )
    return _section("High Complexity Files", body.rstrip())


def _security(files: list[dict]) -> str:
    issues = [
        (f["relative_path"], i) for f in files for i in f.get("security_issues", [])
    ]
    if not issues:
        return _section("Security Issues", "_No security issues found._")
    body = "| File | Line | Severity | Issue |\n| --- | ---: | --- | --- |\n"
    for path, issue in issues[:20]:
        body += (
            f"| `{path}` | {issue['line']} | "
            f"**{issue['severity'].upper()}** | {issue['message']} |\n"
        )
    suffix = ""
    if len(issues) > 20:
        suffix = f"\n\n_…and {len(issues) - 20} more._"
    return _section("Security Issues", body.rstrip() + suffix)


def _duplication(analysis: dict) -> str:
    dup = analysis.get("duplicates", {})
    body = (
        f"- Duplicate blocks: **{dup.get('total_duplicate_blocks', 0)}**\n"
        f"- Duplication rate: **{dup.get('duplication_percentage', 0)}%**\n"
        f"- Code smells: **{analysis.get('total_smells', 0)}**"
    )
    return _section("Duplication", body)


def _git_risk(analysis: dict) -> str:
    summary = analysis.get("git_risk_summary", {})
    if not summary.get("available"):
        return ""
    files = summary.get("top_risk_files", [])
    if not files:
        return ""
    window = summary.get("window_days", 90)
    body = (
        f"_Risk = recent_churn × complexity × (1 + 2·bug_fix_ratio) × "
        f"(1 + 0.15·authors) / 100  · window: {window}d_\n\n"
        "| File | Risk | Commits | Churn | Authors | Complexity |\n"
        "| --- | ---: | ---: | ---: | ---: | ---: |\n"
    )
    for f in files:
        body += (
            f"| `{f['file']}` | **{f['risk_score']}** | {f['commits']} | "
            f"{f['churn']} | {f['authors']} | {f['complexity']} |\n"
        )
    return _section("Predictive Risk — Top Files", body.rstrip())


def generate_md(analysis: dict, output_path: str = None) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = (
        f"# Code Scanner Report\n\n"
        f"`{analysis['root']}`  \n"
        f"_Generated {ts}_\n\n"
        + _summary(analysis)
        + _languages(analysis)
        + _duplication(analysis)
        + _top_files(analysis["files"])
        + _high_complexity(analysis["files"])
        + _security(analysis["files"])
        + _git_risk(analysis)
    ).rstrip() + "\n"
    if output_path:
        with open(output_path, "w") as fh:
            fh.write(md)
    return md
