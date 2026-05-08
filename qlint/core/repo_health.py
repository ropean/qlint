from pathlib import Path


REQUIRED = "required"
RECOMMENDED = "recommended"


_CHECKS = [
    ("LICENSE", REQUIRED, ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"]),
    ("README", REQUIRED, ["README.md", "README", "README.rst", "README.txt"]),
    (".gitignore", REQUIRED, [".gitignore"]),
    (
        "Package metadata",
        REQUIRED,
        [
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "package.json",
            "Cargo.toml",
            "go.mod",
            "Gemfile",
            "pom.xml",
            "build.gradle",
            "build.gradle.kts",
        ],
    ),
    (
        "CI config",
        REQUIRED,
        [
            ".github/workflows",
            ".gitlab-ci.yml",
            ".circleci",
            "azure-pipelines.yml",
            "Jenkinsfile",
            ".travis.yml",
        ],
    ),
    (
        "Tests directory",
        RECOMMENDED,
        ["tests", "test", "__tests__", "spec", "specs"],
    ),
    ("CHANGELOG", RECOMMENDED, ["CHANGELOG.md", "CHANGELOG", "HISTORY.md"]),
    ("CONTRIBUTING", RECOMMENDED, ["CONTRIBUTING.md", "CONTRIBUTING"]),
    (".editorconfig", RECOMMENDED, [".editorconfig"]),
    (
        "Code of conduct",
        RECOMMENDED,
        ["CODE_OF_CONDUCT.md", "CODE_OF_CONDUCT"],
    ),
]


def _find(root: Path, candidates: list[str]) -> str | None:
    for c in candidates:
        if (root / c).exists():
            return c
    return None


def analyze_repo_health(root: str) -> dict:
    base = Path(root)
    checks: list[dict] = []
    required_total = 0
    required_passed = 0
    for name, category, candidates in _CHECKS:
        found = _find(base, candidates)
        passed = found is not None
        checks.append(
            {
                "name": name,
                "category": category,
                "passed": passed,
                "found": found,
                "candidates": candidates,
            }
        )
        if category == REQUIRED:
            required_total += 1
            if passed:
                required_passed += 1
    overall = sum(1 for c in checks if c["passed"])
    score = round(overall / len(checks) * 100) if checks else 0
    required_score = (
        round(required_passed / required_total * 100) if required_total else 100
    )
    return {
        "score": score,
        "required_score": required_score,
        "checks": checks,
        "passed_count": overall,
        "total_count": len(checks),
    }
