import json


def _files_table(files: list[dict]) -> str:
    top = sorted(files, key=lambda f: f["metrics"]["loc"], reverse=True)[:10]
    rows = ""
    for f in top:
        sc = len(f.get("security_issues", []))
        rows += (
            f'<tr class="border-b hover:bg-gray-50">'
            f'<td class="py-2 px-4 text-sm font-mono">{f["relative_path"]}</td>'
            f'<td class="py-2 px-4 text-sm">{f["language"]}</td>'
            f'<td class="py-2 px-4 text-sm text-right">{f["metrics"]["loc"]}</td>'
            f'<td class="py-2 px-4 text-sm text-right">{f["metrics"]["functions"]}</td>'
            f'<td class="py-2 px-4 text-sm text-right">{f.get("complexity", {}).get("avg_complexity", 0)}</td>'
            f'<td class="py-2 px-4 text-sm text-right">{len(f.get("smells", []))}</td>'
            f'<td class="py-2 px-4 text-sm text-right{"text-red-600 font-bold" if sc else ""}">{sc}</td>'
            f"</tr>"
        )
    header = '<tr class="border-b-2 text-gray-600 text-sm"><th class="py-2 px-4">File</th><th class="py-2 px-4">Language</th><th class="py-2 px-4 text-right">LOC</th><th class="py-2 px-4 text-right">Functions</th><th class="py-2 px-4 text-right">Complexity</th><th class="py-2 px-4 text-right">Smells</th><th class="py-2 px-4 text-right">Security</th></tr>'
    return f'<div class="bg-white rounded-xl shadow p-5 mb-6 overflow-x-auto"><h2 class="font-semibold text-gray-700 mb-3">Top Files by Size</h2><table class="w-full text-left"><thead>{header}</thead><tbody>{rows}</tbody></table></div>'


def _complexity_table(files: list[dict]) -> str:
    top = sorted(
        files,
        key=lambda f: f.get("complexity", {}).get("max_complexity", 0),
        reverse=True,
    )[:5]
    rows = ""
    for f in top:
        max_c = f.get("complexity", {}).get("max_complexity", 0)
        if not max_c:
            continue
        bg = "#ef4444" if max_c > 15 else "#f59e0b" if max_c > 10 else "#22c55e"
        badge = f'<span class="px-2 py-1 rounded text-xs font-bold text-white" style="background:{bg}">{max_c}</span>'
        rows += (
            f'<tr class="border-b hover:bg-gray-50">'
            f'<td class="py-2 px-4 text-sm font-mono">{f["relative_path"]}</td>'
            f'<td class="py-2 px-4 text-sm">{f["language"]}</td>'
            f'<td class="py-2 px-4 text-sm text-center">{badge}</td>'
            f'<td class="py-2 px-4 text-sm text-right">{f.get("complexity", {}).get("flagged_count", 0)}</td>'
            f"</tr>"
        )
    empty = "<tr><td colspan='4' class='py-4 text-center text-gray-400'>No high complexity detected</td></tr>"
    header = '<tr class="border-b-2 text-gray-600 text-sm"><th class="py-2 px-4">File</th><th class="py-2 px-4">Language</th><th class="py-2 px-4 text-center">Max Complexity</th><th class="py-2 px-4 text-right">Flagged Functions</th></tr>'
    return f'<div class="bg-white rounded-xl shadow p-5 mb-6 overflow-x-auto"><h2 class="font-semibold text-gray-700 mb-3">High Complexity Files</h2><table class="w-full text-left"><thead>{header}</thead><tbody>{rows or empty}</tbody></table></div>'


def _security_table(files: list[dict]) -> str:
    issues = [
        (f["relative_path"], i) for f in files for i in f.get("security_issues", [])
    ]
    rows = ""
    for path, issue in issues[:20]:
        sev_color = {
            "critical": "#ef4444",
            "error": "#f97316",
            "warning": "#f59e0b",
        }.get(issue["severity"], "#6b7280")
        badge = f'<span class="px-2 py-1 rounded text-xs font-bold text-white" style="background:{sev_color}">{issue["severity"].upper()}</span>'
        rows += (
            f'<tr class="border-b hover:bg-gray-50">'
            f'<td class="py-2 px-4 text-sm font-mono">{path}</td>'
            f'<td class="py-2 px-4 text-sm text-right">{issue["line"]}</td>'
            f'<td class="py-2 px-4 text-sm">{badge}</td>'
            f'<td class="py-2 px-4 text-sm">{issue["message"]}</td>'
            f"</tr>"
        )
    empty = "<tr><td colspan='4' class='py-4 text-center text-gray-400'>No security issues found</td></tr>"
    header = '<tr class="border-b-2 text-gray-600 text-sm"><th class="py-2 px-4">File</th><th class="py-2 px-4 text-right">Line</th><th class="py-2 px-4">Severity</th><th class="py-2 px-4">Issue</th></tr>'
    return f'<div class="bg-white rounded-xl shadow p-5 mb-6 overflow-x-auto"><h2 class="font-semibold text-gray-700 mb-3">Security Issues</h2><table class="w-full text-left"><thead>{header}</thead><tbody>{rows or empty}</tbody></table></div>'


def _prepare_chart_data(analysis: dict) -> dict:
    lang_data = analysis.get("languages", {})
    smells_by_type: dict[str, int] = {}
    for f in analysis["files"]:
        for s in f.get("smells", []):
            smells_by_type[s["type"]] = smells_by_type.get(s["type"], 0) + 1
    dup = analysis.get("duplicates", {})
    cs = analysis.get("complexity_summary", {})
    return {
        "lang_labels": json.dumps(list(lang_data.keys())),
        "lang_values": json.dumps([v["lines"] for v in lang_data.values()]),
        "smell_labels": json.dumps(list(smells_by_type.keys())),
        "smell_values": json.dumps(list(smells_by_type.values())),
        "radar": [
            max(0, 100 - cs.get("flagged_count", 0) * 5),
            max(0, 100 - dup.get("duplication_percentage", 0)),
            max(0, 100 - analysis.get("total_smells", 0) * 2),
            max(0, 100 - analysis.get("total_security_issues", 0) * 10),
            analysis["quality"]["score"],
        ],
    }


def _chart_scripts(cd: dict) -> str:
    return (
        f"<script>"
        f"new Chart(document.getElementById('langChart'), {{type:'doughnut',data:{{labels:{cd['lang_labels']},datasets:[{{data:{cd['lang_values']},backgroundColor:['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6','#ec4899','#06b6d4','#84cc16']}}]}},options:{{plugins:{{legend:{{position:'bottom',labels:{{font:{{size:11}}}}}}}}}}}});"
        f"new Chart(document.getElementById('smellChart'), {{type:'bar',data:{{labels:{cd['smell_labels']},datasets:[{{label:'Count',data:{cd['smell_values']},backgroundColor:'#f59e0b'}}]}},options:{{plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true}}}}}}}});"
        f"new Chart(document.getElementById('qualityChart'), {{type:'radar',data:{{labels:['Complexity','Duplication','Code Smells','Security','Overall'],datasets:[{{label:'Score',data:{cd['radar']},fill:true,backgroundColor:'rgba(59,130,246,0.2)',borderColor:'#3b82f6'}}]}},options:{{scales:{{r:{{beginAtZero:true,max:100}}}}}}}});"
        f"</script>"
    )


def generate_html(analysis: dict, output_path: str = None) -> str:
    quality = analysis["quality"]
    color = {
        "A": "#22c55e",
        "B": "#84cc16",
        "C": "#f59e0b",
        "D": "#f97316",
        "F": "#ef4444",
    }.get(quality["grade"], "#6b7280")
    dup = analysis.get("duplicates", {})
    files = analysis["files"]
    cd = _prepare_chart_data(analysis)
    html = (
        '<!DOCTYPE html><html lang="en">'
        '<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">'
        "<title>Code Scanner Report</title>"
        '<script src="https://cdn.tailwindcss.com"></script>'
        '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script></head>'
        '<body class="bg-gray-100 font-sans"><div class="max-w-7xl mx-auto p-6">'
        f'<div class="bg-white rounded-xl shadow p-6 mb-6"><h1 class="text-3xl font-bold text-gray-800 mb-1">Code Scanner Report</h1><p class="text-gray-500 text-sm">{analysis["root"]}</p></div>'
        f'<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">'
        f'<div class="bg-white rounded-xl shadow p-5 text-center"><div class="text-4xl font-bold" style="color:{color}">{quality["grade"]}</div><div class="text-gray-500 text-sm mt-1">Quality Grade</div><div class="text-2xl font-semibold text-gray-700">{quality["score"]}/100</div></div>'
        f'<div class="bg-white rounded-xl shadow p-5 text-center"><div class="text-4xl font-bold text-blue-600">{analysis["total_files"]}</div><div class="text-gray-500 text-sm mt-1">Total Files</div></div>'
        f'<div class="bg-white rounded-xl shadow p-5 text-center"><div class="text-4xl font-bold text-indigo-600">{analysis["total_lines"]:,}</div><div class="text-gray-500 text-sm mt-1">Total Lines</div></div>'
        f'<div class="bg-white rounded-xl shadow p-5 text-center"><div class="text-4xl font-bold text-red-500">{analysis.get("total_security_issues", 0)}</div><div class="text-gray-500 text-sm mt-1">Security Issues</div></div></div>'
        '<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">'
        '<div class="bg-white rounded-xl shadow p-5"><h2 class="font-semibold text-gray-700 mb-3">Language Distribution</h2><canvas id="langChart" height="200"></canvas></div>'
        '<div class="bg-white rounded-xl shadow p-5"><h2 class="font-semibold text-gray-700 mb-3">Code Smells by Type</h2><canvas id="smellChart" height="200"></canvas></div>'
        '<div class="bg-white rounded-xl shadow p-5"><h2 class="font-semibold text-gray-700 mb-3">Quality Breakdown</h2><canvas id="qualityChart" height="200"></canvas></div></div>'
        f'<div class="bg-white rounded-xl shadow p-5 mb-6"><h2 class="font-semibold text-gray-700 mb-3">Duplication Analysis</h2><div class="grid grid-cols-3 gap-4 text-center">'
        f'<div><div class="text-2xl font-bold text-orange-500">{dup.get("total_duplicate_blocks", 0)}</div><div class="text-sm text-gray-500">Duplicate Blocks</div></div>'
        f'<div><div class="text-2xl font-bold text-orange-500">{dup.get("duplication_percentage", 0)}%</div><div class="text-sm text-gray-500">Duplication Rate</div></div>'
        f'<div><div class="text-2xl font-bold text-gray-700">{analysis.get("total_smells", 0)}</div><div class="text-sm text-gray-500">Code Smells</div></div></div></div>'
        + _files_table(files)
        + _complexity_table(files)
        + _security_table(files)
        + f"</div>{_chart_scripts(cd)}</body></html>"
    )
    if output_path:
        with open(output_path, "w") as fh:
            fh.write(html)
    return html
