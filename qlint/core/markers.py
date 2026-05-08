import re

# Require ':' after the keyword (universal convention) and reject matches
# preceded by a quote — kills false positives like '{"TODO": "high"}' dict
# keys and prose containing the words "bug" or "note".
MARKER_PATTERN = re.compile(
    r'(?<![\'"])\b(TODO|FIXME|HACK|XXX|BUG|NOTE):\s*(.*)',
    re.IGNORECASE,
)
TRACKED_TYPES = {"TODO", "FIXME", "HACK", "XXX", "BUG", "NOTE"}
SKIP_LANGUAGES = {"Markdown", "HTML"}


def analyze_markers(file_info: dict) -> list[dict]:
    if file_info.get("language") in SKIP_LANGUAGES:
        return []
    content = file_info.get("content")
    if not content:
        return []
    out: list[dict] = []
    for lineno, line in enumerate(content.splitlines(), start=1):
        m = MARKER_PATTERN.search(line)
        if not m:
            continue
        marker_type = m.group(1).upper()
        if marker_type not in TRACKED_TYPES:
            continue
        text = m.group(2).strip().lstrip(":-").strip()
        out.append(
            {
                "type": marker_type,
                "line": lineno,
                "text": text[:160],
            }
        )
    return out


def summarize_markers(analyzed_files: list[dict]) -> dict:
    by_type: dict[str, int] = {}
    per_file: dict[str, dict] = {}
    samples: list[dict] = []
    total = 0
    for f in analyzed_files:
        markers = f.get("markers", [])
        if not markers:
            continue
        path = f["relative_path"]
        per_file[path] = {"count": len(markers), "types": {}}
        for m in markers:
            t = m["type"]
            by_type[t] = by_type.get(t, 0) + 1
            per_file[path]["types"][t] = per_file[path]["types"].get(t, 0) + 1
            total += 1
            if len(samples) < 30:
                samples.append({"file": path, **m})
    top_files = sorted(
        ({"file": p, **v} for p, v in per_file.items()),
        key=lambda r: r["count"],
        reverse=True,
    )[:10]
    return {
        "total": total,
        "by_type": dict(sorted(by_type.items(), key=lambda kv: -kv[1])),
        "top_files": top_files,
        "samples": samples,
    }
