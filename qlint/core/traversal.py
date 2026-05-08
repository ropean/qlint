import os
from pathlib import Path, PurePosixPath

import pathspec

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".mypy_cache",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "coverage",
    ".pytest_cache",
}

LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JavaScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".go": "Go",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".cpp": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cs": "C#",
    ".php": "PHP",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".scala": "Scala",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "CSS",
    ".sass": "CSS",
    ".sql": "SQL",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".xml": "XML",
    ".md": "Markdown",
    ".r": "R",
    ".R": "R",
    ".dart": "Dart",
    ".lua": "Lua",
}


def detect_language(path: str) -> str:
    ext = Path(path).suffix.lower()
    return LANGUAGE_MAP.get(ext, "Unknown")


def _anchor_pattern(stripped: str, prefix: str) -> str:
    """Anchor a sub-directory .gitignore pattern relative to the repo root."""
    if stripped.startswith("!"):
        return "!" + prefix + "/" + stripped[1:].lstrip("/")
    return prefix + "/" + stripped.lstrip("/")


def _read_gitignore_lines(gi_path: Path, rel_dir: Path) -> list[str]:
    try:
        text = gi_path.read_text(encoding="utf-8", errors="replace")
    except (PermissionError, OSError):
        return []
    is_root = str(rel_dir) == "."
    prefix = "" if is_root else str(PurePosixPath(rel_dir))
    out: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        out.append(stripped if is_root else _anchor_pattern(stripped, prefix))
    return out


def _load_gitignore_spec(root: Path) -> pathspec.PathSpec:
    """Collect all .gitignore patterns from root and every subdirectory."""
    lines: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")
        ]
        if ".gitignore" not in filenames:
            continue
        rel_dir = Path(dirpath).relative_to(root)
        lines.extend(_read_gitignore_lines(Path(dirpath) / ".gitignore", rel_dir))
    return pathspec.PathSpec.from_lines("gitwildmatch", lines)


def walk_codebase(root: str) -> list[dict]:
    files = []
    root_path = Path(root).resolve()
    spec = _load_gitignore_spec(root_path)

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [
            d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")
        ]

        for filename in filenames:
            filepath = Path(dirpath) / filename
            ext = filepath.suffix.lower()
            if ext not in LANGUAGE_MAP and ext not in {
                ".txt",
                ".cfg",
                ".ini",
                ".toml",
                ".lock",
            }:
                continue

            # Use forward slashes for cross-platform gitignore matching.
            rel = filepath.relative_to(root_path)
            rel_posix = rel.as_posix()
            if spec.match_file(rel_posix):
                continue

            try:
                stat = filepath.stat()
                files.append(
                    {
                        "path": str(filepath),
                        "relative_path": str(rel),
                        "language": detect_language(str(filepath)),
                        "size": stat.st_size,
                    }
                )
            except (PermissionError, OSError):
                continue

    return files
