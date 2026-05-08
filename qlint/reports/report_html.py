import base64
import json

# Inline SVG favicon → base64 data URI. Single-file output, works offline.
_FAVICON_SVG = (
    b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
    b'<rect x="2" y="2" width="60" height="60" rx="14" fill="#0a0a0a"/>'
    b'<rect x="2" y="2" width="60" height="60" rx="14" fill="none" '
    b'stroke="#3b9eff" stroke-width="1.5" stroke-opacity="0.55"/>'
    b'<text x="32" y="40" font-family="Georgia, serif" font-size="42" '
    b'font-weight="400" fill="#f0f0f0" text-anchor="middle">q</text>'
    b"</svg>"
)
FAVICON_DATA = "data:image/svg+xml;base64," + base64.b64encode(_FAVICON_SVG).decode()


CSS = """
*,*::before,*::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
html { color-scheme: dark; }
html[data-theme="light"] { color-scheme: light; }

:root, [data-theme="dark"] {
  --bg: #000000;
  --bg-card: rgba(255, 255, 255, 0.018);
  --bg-hover: rgba(255, 255, 255, 0.04);
  --text: #f0f0f0;
  --text-muted: #a1a4a5;
  --text-faint: #5c5c5c;
  --border: rgba(214, 235, 253, 0.19);
  --border-soft: rgba(217, 237, 254, 0.10);
  --orange: #ff801f;
  --orange-bg: rgba(255, 89, 0, 0.18);
  --green: #11ff99;
  --green-bg: rgba(17, 255, 153, 0.14);
  --blue: #3b9eff;
  --blue-bg: rgba(0, 117, 255, 0.20);
  --yellow: #ffc53d;
  --yellow-bg: rgba(255, 197, 61, 0.18);
  --red: #ff5c79;
  --red-bg: rgba(255, 32, 71, 0.20);
}
[data-theme="light"] {
  --bg: #fafbfc;
  --bg-card: #ffffff;
  --bg-hover: #f4f6f8;
  --text: #0a0e1a;
  --text-muted: #5c6166;
  --text-faint: #9aa0a6;
  --border: rgba(15, 32, 64, 0.12);
  --border-soft: rgba(15, 32, 64, 0.06);
  --orange: #d96b0f;
  --orange-bg: rgba(217, 107, 15, 0.10);
  --green: #00a86b;
  --green-bg: rgba(0, 168, 107, 0.12);
  --blue: #0975ff;
  --blue-bg: rgba(9, 117, 255, 0.10);
  --yellow: #c89a00;
  --yellow-bg: rgba(255, 197, 61, 0.20);
  --red: #d8264a;
  --red-bg: rgba(216, 38, 74, 0.10);
}

body {
  background: var(--bg);
  color: var(--text);
  font: 400 16px/1.5 "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  transition: background 0.18s ease, color 0.18s ease;
  min-height: 100vh;
}

.shell { max-width: 1280px; margin: 0 auto; padding: 56px 32px 96px; }

.hero {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 24px; padding: 0 0 48px; margin-bottom: 56px;
  border-bottom: 1px solid var(--border);
}
.hero h1 {
  font-family: "Iowan Old Style", "Apple Garamond", Baskerville, "Times New Roman", serif;
  font-size: clamp(40px, 6.5vw, 76px);
  line-height: 1.0;
  letter-spacing: -0.04em;
  font-weight: 400;
  margin: 0 0 14px;
}
.hero .root {
  font-family: ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, monospace;
  font-size: 13px; color: var(--text-muted); word-break: break-all;
}
.hero .meta { font-size: 13px; color: var(--text-faint); margin-top: 4px; }

.theme-toggle {
  background: transparent; color: var(--text);
  border: 1px solid var(--border); border-radius: 9999px;
  padding: 7px 16px; font-size: 13px; font-weight: 500;
  cursor: pointer; transition: background 0.15s, border-color 0.15s;
  display: inline-flex; align-items: center; gap: 8px;
  font-family: inherit; flex-shrink: 0;
}
.theme-toggle:hover { background: var(--bg-hover); }
.theme-toggle .icon { width: 14px; height: 14px; display: inline-block; }
[data-theme="dark"] .theme-toggle .moon { display: none; }
[data-theme="light"] .theme-toggle .sun { display: none; }

.section { margin-bottom: 56px; }
.section-title {
  font-size: 12px; text-transform: uppercase; letter-spacing: 0.10em;
  color: var(--text-muted); font-weight: 600; margin: 0 0 20px;
}

.kpis {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 56px;
}
.kpi {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px; padding: 24px;
}
.kpi .label {
  font-size: 11px; text-transform: uppercase; letter-spacing: 0.10em;
  color: var(--text-muted); font-weight: 600;
}
.kpi .value {
  font-family: "Iowan Old Style", Baskerville, "Times New Roman", serif;
  font-size: 56px; line-height: 1.0; letter-spacing: -0.025em;
  margin: 14px 0 6px; font-weight: 400;
}
.kpi.grade .value { display: flex; align-items: baseline; gap: 14px; }
.kpi.grade .grade-letter { font-size: 76px; }
.kpi.grade .grade-score {
  font-size: 22px; color: var(--text-muted);
  font-family: "Inter", sans-serif; font-weight: 400; letter-spacing: 0;
}
.kpi .sub { font-size: 13px; color: var(--text-faint); }
.grade-A { color: var(--green); }
.grade-B { color: var(--green); }
.grade-C { color: var(--yellow); }
.grade-D { color: var(--orange); }
.grade-F { color: var(--red); }

.charts-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px; padding: 22px;
}
.card h3 {
  font-size: 12px; text-transform: uppercase; letter-spacing: 0.10em;
  color: var(--text-muted); font-weight: 600; margin: 0 0 16px;
}
.card.has-table { padding: 0; overflow: hidden; }
.card.has-table h3 { padding: 22px 22px 0; margin-bottom: 16px; }
.card.has-table .formula { padding: 0 22px 16px; margin: 0; }

.dup-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.dup-stat { text-align: center; padding: 12px 8px; }
.dup-stat .v {
  font-family: "Iowan Old Style", Baskerville, serif;
  font-size: 36px; line-height: 1.0; letter-spacing: -0.02em; font-weight: 400;
}
.dup-stat .l {
  font-size: 11px; color: var(--text-muted); margin-top: 6px;
  text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600;
}

.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th {
  text-align: left; font-weight: 600; font-size: 11px;
  text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted);
  padding: 14px 22px; border-bottom: 1px solid var(--border);
  background: transparent;
}
td {
  padding: 14px 22px; border-bottom: 1px solid var(--border-soft);
  vertical-align: middle;
}
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover td { background: var(--bg-hover); }
.mono {
  font-family: ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, monospace;
  font-size: 13px;
}
.right { text-align: right; }
.center { text-align: center; }
.col-reason {
  font-size: 12px; color: var(--text-muted); margin-top: 4px;
}

.badge {
  display: inline-flex; align-items: center; padding: 3px 10px;
  border-radius: 9999px; font-size: 11px; font-weight: 600;
  letter-spacing: 0.04em; text-transform: uppercase;
  border: 1px solid transparent; line-height: 1.4; white-space: nowrap;
}
.badge.critical { background: var(--red-bg);    color: var(--red);    border-color: var(--red); }
.badge.high     { background: var(--orange-bg); color: var(--orange); border-color: var(--orange); }
.badge.medium   { background: var(--yellow-bg); color: var(--yellow); }
.badge.low      { background: var(--green-bg);  color: var(--green);  }
.badge.warning  { background: var(--yellow-bg); color: var(--yellow); }
.badge.error    { background: var(--orange-bg); color: var(--orange); }

.bar {
  height: 4px; background: var(--border-soft); border-radius: 9999px;
  overflow: hidden; min-width: 80px;
}
.bar > span { display: block; height: 100%; border-radius: 9999px; }

.empty {
  text-align: center; padding: 32px;
  color: var(--text-faint); font-size: 14px;
}
.formula {
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 11px; color: var(--text-faint); margin: -8px 0 16px;
}

@media (max-width: 1000px) {
  .kpis { grid-template-columns: repeat(2, 1fr); }
  .charts-grid { grid-template-columns: 1fr; }
}
@media (max-width: 600px) {
  .shell { padding: 32px 16px 64px; }
  .hero { flex-direction: column; }
  .kpis { grid-template-columns: 1fr; }
  .kpi .value { font-size: 44px; }
  .kpi.grade .grade-letter { font-size: 60px; }
}
"""

# Inline pre-paint script: read localStorage / system pref BEFORE first paint
# to avoid theme flash. Must run synchronously in <head>.
THEME_BOOT = """
(function(){
  try {
    var saved = localStorage.getItem('qlint-theme');
    var sys = (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', saved || sys);
  } catch(e) {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
})();
"""


def _grade_class(grade: str) -> str:
    return f"grade-{grade}" if grade in ("A", "B", "C", "D", "F") else "grade-A"


def _files_table(files: list[dict]) -> str:
    top = sorted(files, key=lambda f: f["metrics"]["loc"], reverse=True)[:10]
    rows = ""
    for f in top:
        sc = len(f.get("security_issues", []))
        sec_cell = (
            f'<td class="right"><span class="badge critical">{sc}</span></td>'
            if sc
            else f'<td class="right">{sc}</td>'
        )
        rows += (
            f"<tr>"
            f'<td class="mono">{f["relative_path"]}</td>'
            f"<td>{f['language']}</td>"
            f'<td class="right">{f["metrics"]["loc"]:,}</td>'
            f'<td class="right">{f["metrics"]["functions"]}</td>'
            f'<td class="right">{f.get("complexity", {}).get("avg_complexity", 0)}</td>'
            f'<td class="right">{len(f.get("smells", []))}</td>'
            f"{sec_cell}"
            f"</tr>"
        )
    head = (
        "<tr>"
        "<th>File</th><th>Language</th>"
        '<th class="right">LOC</th>'
        '<th class="right">Functions</th>'
        '<th class="right">Complexity</th>'
        '<th class="right">Smells</th>'
        '<th class="right">Security</th>'
        "</tr>"
    )
    return (
        '<div class="card has-table">'
        "<h3>Top Files by Size</h3>"
        f'<div class="table-wrap"><table><thead>{head}</thead><tbody>{rows}</tbody></table></div>'
        "</div>"
    )


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
        cls = "critical" if max_c > 15 else "high" if max_c > 10 else "low"
        badge = f'<span class="badge {cls}">{max_c}</span>'
        rows += (
            f"<tr>"
            f'<td class="mono">{f["relative_path"]}</td>'
            f"<td>{f['language']}</td>"
            f'<td class="center">{badge}</td>'
            f'<td class="right">{f.get("complexity", {}).get("flagged_count", 0)}</td>'
            f"</tr>"
        )
    body = rows or '<tr><td colspan="4" class="empty">No high complexity detected</td></tr>'
    head = (
        "<tr>"
        "<th>File</th><th>Language</th>"
        '<th class="center">Max Complexity</th>'
        '<th class="right">Flagged Functions</th>'
        "</tr>"
    )
    return (
        '<div class="card has-table">'
        "<h3>High Complexity Files</h3>"
        f'<div class="table-wrap"><table><thead>{head}</thead><tbody>{body}</tbody></table></div>'
        "</div>"
    )


def _security_table(files: list[dict]) -> str:
    issues = [
        (f["relative_path"], i) for f in files for i in f.get("security_issues", [])
    ]
    rows = ""
    for path, issue in issues[:20]:
        sev = issue["severity"].lower()
        cls = "critical" if sev == "critical" else "error" if sev == "error" else "warning"
        badge = f'<span class="badge {cls}">{issue["severity"].upper()}</span>'
        rows += (
            f"<tr>"
            f'<td class="mono">{path}</td>'
            f'<td class="right">{issue["line"]}</td>'
            f"<td>{badge}</td>"
            f'<td>{issue["message"]}</td>'
            f"</tr>"
        )
    body = rows or '<tr><td colspan="4" class="empty">No security issues found</td></tr>'
    head = (
        "<tr>"
        "<th>File</th>"
        '<th class="right">Line</th>'
        "<th>Severity</th><th>Issue</th>"
        "</tr>"
    )
    return (
        '<div class="card has-table">'
        "<h3>Security Issues</h3>"
        f'<div class="table-wrap"><table><thead>{head}</thead><tbody>{body}</tbody></table></div>'
        "</div>"
    )


def _risk_table(analysis: dict) -> str:
    summary = analysis.get("git_risk_summary", {})
    if not summary.get("available"):
        return ""
    files = summary.get("top_risk_files", [])
    if not files:
        return ""
    window = summary.get("window_days", 90)
    max_score = max((f["risk_score"] for f in files), default=1) or 1
    rows = ""
    for f in files:
        pct = max(2, int(f["risk_score"] / max_score * 100))
        level = f.get("risk_level", "low")
        bar_color_var = (
            "var(--red)" if level == "critical"
            else "var(--orange)" if level == "high"
            else "var(--yellow)" if level == "medium"
            else "var(--green)"
        )
        bar = f'<div class="bar"><span style="width:{pct}%;background:{bar_color_var}"></span></div>'
        reason = (f.get("reasons") or [""])[0]
        reason_html = (
            f'<div class="col-reason">{reason}</div>' if reason else ""
        )
        s = f.get("signals", {})
        rows += (
            f"<tr>"
            f'<td class="mono">{f["file"]}{reason_html}</td>'
            f'<td><span class="badge {level}">{level}</span></td>'
            f'<td class="right" style="font-weight:600">{f["risk_score"]}</td>'
            f'<td class="right">{s.get("recent_commits", f.get("commits", 0))}</td>'
            f'<td class="right">{s.get("recent_churn", f.get("churn", 0))}</td>'
            f'<td class="right">{s.get("bug_fix_ratio", 0)}</td>'
            f'<td class="right">{f.get("authors", 1)}</td>'
            f'<td class="right">{f.get("complexity", 0)}</td>'
            f"<td>{bar}</td>"
            f"</tr>"
        )
    head = (
        "<tr>"
        "<th>File</th>"
        "<th>Level</th>"
        '<th class="right">Score</th>'
        '<th class="right">Recent Commits</th>'
        '<th class="right">Recent Churn</th>'
        '<th class="right">Bug-fix Ratio</th>'
        '<th class="right">Authors</th>'
        '<th class="right">Complexity</th>'
        "<th>Risk Bar</th>"
        "</tr>"
    )
    return (
        '<div class="card has-table">'
        "<h3>Predictive Risk — Top Files</h3>"
        f'<div class="formula">recent_churn × complexity × (1 + 2·bug_fix_ratio) × '
        f"(1 + 0.15·authors) / 100  ·  window: {window}d</div>"
        f'<div class="table-wrap"><table><thead>{head}</thead><tbody>{rows}</tbody></table></div>'
        "</div>"
    )


def _prepare_chart_data(analysis: dict) -> dict:
    lang_data = analysis.get("languages", {})
    smells_by_type: dict[str, int] = {}
    for f in analysis["files"]:
        for s in f.get("smells", []):
            smells_by_type[s["type"]] = smells_by_type.get(s["type"], 0) + 1
    dup = analysis.get("duplicates", {})
    cs = analysis.get("complexity_summary", {})
    return {
        "lang_labels": list(lang_data.keys()),
        "lang_values": [v["lines"] for v in lang_data.values()],
        "smell_labels": list(smells_by_type.keys()),
        "smell_values": list(smells_by_type.values()),
        "radar": [
            max(0, 100 - cs.get("flagged_count", 0) * 5),
            max(0, 100 - dup.get("duplication_percentage", 0)),
            max(0, 100 - analysis.get("total_smells", 0) * 2),
            max(0, 100 - analysis.get("total_security_issues", 0) * 10),
            analysis["quality"]["score"],
        ],
    }


def _chart_script(cd: dict) -> str:
    payload = json.dumps(cd)
    return f"""
<script>
const QLINT_DATA = {payload};

function getThemeColors() {{
  const s = getComputedStyle(document.documentElement);
  const get = n => s.getPropertyValue(n).trim();
  return {{
    text: get('--text'), muted: get('--text-muted'), border: get('--border'),
    blue: get('--blue'), orange: get('--orange'), green: get('--green'),
    yellow: get('--yellow'), red: get('--red'),
  }};
}}

let qlintCharts = [];
function buildCharts() {{
  qlintCharts.forEach(c => c.destroy());
  qlintCharts = [];
  const t = getThemeColors();
  Chart.defaults.color = t.muted;
  Chart.defaults.borderColor = t.border;
  Chart.defaults.font.family = '"Inter", system-ui, sans-serif';
  Chart.defaults.font.size = 11;
  const palette = [t.blue, t.green, t.yellow, t.orange, t.red, '#9b6bff', '#3bd0ff', '#ff80c0'];

  qlintCharts.push(new Chart(document.getElementById('langChart'), {{
    type: 'doughnut',
    data: {{ labels: QLINT_DATA.lang_labels, datasets: [{{
      data: QLINT_DATA.lang_values, backgroundColor: palette, borderColor: 'transparent', borderWidth: 0
    }}]}},
    options: {{
      cutout: '65%',
      plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{size: 11}}, color: t.muted, padding: 12 }} }} }}
    }}
  }}));

  qlintCharts.push(new Chart(document.getElementById('smellChart'), {{
    type: 'bar',
    data: {{ labels: QLINT_DATA.smell_labels, datasets: [{{
      label: 'Count', data: QLINT_DATA.smell_values, backgroundColor: t.orange, borderRadius: 4
    }}]}},
    options: {{
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        y: {{ beginAtZero: true, ticks: {{color: t.muted}}, grid: {{color: t.border}}, border: {{color: t.border}} }},
        x: {{ ticks: {{color: t.muted}}, grid: {{display: false}}, border: {{color: t.border}} }}
      }}
    }}
  }}));

  qlintCharts.push(new Chart(document.getElementById('qualityChart'), {{
    type: 'radar',
    data: {{ labels: ['Complexity','Duplication','Smells','Security','Overall'], datasets: [{{
      label: 'Score', data: QLINT_DATA.radar, fill: true,
      backgroundColor: t.blue + '33', borderColor: t.blue, pointBackgroundColor: t.blue,
      pointRadius: 3, borderWidth: 2
    }}]}},
    options: {{
      plugins: {{ legend: {{ display: false }} }},
      scales: {{ r: {{
        beginAtZero: true, max: 100, suggestedMin: 0,
        angleLines: {{color: t.border}}, grid: {{color: t.border}},
        ticks: {{color: t.muted, backdropColor: 'transparent', stepSize: 25}},
        pointLabels: {{color: t.muted, font: {{size: 11}}}}
      }}}}
    }}
  }}));
}}

buildCharts();

document.querySelector('.theme-toggle').addEventListener('click', () => {{
  const cur = document.documentElement.getAttribute('data-theme') || 'dark';
  const next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  try {{ localStorage.setItem('qlint-theme', next); }} catch(e) {{}}
  buildCharts();
}});
</script>
"""


def generate_html(analysis: dict, output_path: str = None) -> str:
    quality = analysis["quality"]
    grade_cls = _grade_class(quality["grade"])
    dup = analysis.get("duplicates", {})
    files = analysis["files"]
    cd = _prepare_chart_data(analysis)

    html = (
        '<!DOCTYPE html><html lang="en"><head>'
        '<meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        f'<link rel="icon" type="image/svg+xml" href="{FAVICON_DATA}">'
        "<title>qlint — Code Quality Report</title>"
        f"<script>{THEME_BOOT}</script>"
        f"<style>{CSS}</style>"
        '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'
        "</head><body>"
        '<div class="shell">'
        # Hero
        '<header class="hero"><div>'
        "<h1>Code Quality Report</h1>"
        f'<div class="root">{analysis["root"]}</div>'
        "</div>"
        '<button class="theme-toggle" type="button" aria-label="Toggle theme">'
        '<svg class="icon sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>'
        '<svg class="icon moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'
        '<span class="label">Theme</span>'
        "</button>"
        "</header>"
        # KPIs
        '<section class="section"><h2 class="section-title">Overview</h2>'
        '<div class="kpis">'
        f'<div class="kpi grade"><div class="label">Quality Grade</div>'
        f'<div class="value"><span class="grade-letter {grade_cls}">{quality["grade"]}</span>'
        f'<span class="grade-score">{quality["score"]}/100</span></div>'
        f'<div class="sub">overall</div></div>'
        f'<div class="kpi"><div class="label">Total Files</div>'
        f'<div class="value">{analysis["total_files"]:,}</div>'
        f'<div class="sub">scanned</div></div>'
        f'<div class="kpi"><div class="label">Total Lines</div>'
        f'<div class="value">{analysis["total_lines"]:,}</div>'
        f'<div class="sub">across all files</div></div>'
        f'<div class="kpi"><div class="label">Security</div>'
        f'<div class="value">{analysis.get("total_security_issues", 0)}</div>'
        f'<div class="sub">issues found</div></div>'
        "</div></section>"
        # Charts
        '<section class="section"><h2 class="section-title">Visuals</h2>'
        '<div class="charts-grid">'
        '<div class="card"><h3>Language Distribution</h3><canvas id="langChart" height="220"></canvas></div>'
        '<div class="card"><h3>Smells by Type</h3><canvas id="smellChart" height="220"></canvas></div>'
        '<div class="card"><h3>Quality Breakdown</h3><canvas id="qualityChart" height="220"></canvas></div>'
        "</div></section>"
        # Duplication
        '<section class="section"><h2 class="section-title">Duplication</h2>'
        '<div class="card"><div class="dup-grid">'
        f'<div class="dup-stat"><div class="v" style="color:var(--orange)">{dup.get("total_duplicate_blocks", 0)}</div><div class="l">Duplicate Blocks</div></div>'
        f'<div class="dup-stat"><div class="v" style="color:var(--orange)">{dup.get("duplication_percentage", 0)}%</div><div class="l">Duplication Rate</div></div>'
        f'<div class="dup-stat"><div class="v">{analysis.get("total_smells", 0)}</div><div class="l">Code Smells</div></div>'
        "</div></div></section>"
        # Tables
        '<section class="section"><h2 class="section-title">Inventory</h2>'
        + _files_table(files)
        + "</section>"
        '<section class="section"><h2 class="section-title">Complexity</h2>'
        + _complexity_table(files)
        + "</section>"
        '<section class="section"><h2 class="section-title">Security</h2>'
        + _security_table(files)
        + "</section>"
        '<section class="section"><h2 class="section-title">Predictive Risk</h2>'
        + _risk_table(analysis)
        + "</section>"
        "</div>"  # /shell
        + _chart_script(cd)
        + "</body></html>"
    )
    if output_path:
        with open(output_path, "w") as fh:
            fh.write(html)
    return html
