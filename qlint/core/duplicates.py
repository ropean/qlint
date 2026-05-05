import hashlib
from collections import defaultdict


def _normalize_line(line: str) -> str:
    return line.strip()


def _chunk_lines(lines: list[str], size: int = 6) -> list[tuple]:
    normalized = [_normalize_line(line) for line in lines]
    chunks = []
    for i in range(len(normalized) - size + 1):
        block = normalized[i : i + size]
        if any(b for b in block):
            chunks.append((i + 1, tuple(block)))
    return chunks


def find_duplicates(all_files: list[dict]) -> dict:
    chunk_map = defaultdict(list)

    for file_info in all_files:
        content = file_info.get("content", "")
        lines = content.splitlines()
        if len(lines) < 6:
            continue
        for line_num, chunk in _chunk_lines(lines):
            h = hashlib.md5("\n".join(chunk).encode()).hexdigest()
            chunk_map[h].append(
                {
                    "file": file_info["relative_path"],
                    "line": line_num,
                    "preview": chunk[0][:80],
                }
            )

    duplicates = {k: v for k, v in chunk_map.items() if len(v) > 1}

    file_dup_counts = defaultdict(int)
    for locations in duplicates.values():
        seen_files = set()
        for loc in locations:
            if loc["file"] not in seen_files:
                file_dup_counts[loc["file"]] += 1
                seen_files.add(loc["file"])

    top_offenders = sorted(file_dup_counts.items(), key=lambda x: x[1], reverse=True)[
        :5
    ]

    return {
        "total_duplicate_blocks": len(duplicates),
        "top_offenders": [{"file": f, "duplicate_blocks": c} for f, c in top_offenders],
        "duplication_percentage": round(
            len(duplicates)
            / max(sum(len(chunk_map[k]) for k in chunk_map) / 6, 1)
            * 100,
            1,
        )
        if chunk_map
        else 0,
    }
