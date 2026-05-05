import ast
import re


COMMENT_PATTERNS = {
    "Python": r"^\s*#",
    "JavaScript": r"^\s*//",
    "TypeScript": r"^\s*//",
    "Java": r"^\s*//",
    "Go": r"^\s*//",
    "C": r"^\s*//",
    "C++": r"^\s*//",
    "C#": r"^\s*//",
    "Ruby": r"^\s*#",
    "Shell": r"^\s*#",
    "PHP": r"^\s*(//)|(#)",
    "Rust": r"^\s*//",
}


def count_lines(content: str, language: str) -> dict:
    lines = content.splitlines()
    total = len(lines)
    blank = sum(1 for line in lines if not line.strip())
    comment_pattern = COMMENT_PATTERNS.get(language)
    if comment_pattern:
        comment = sum(1 for line in lines if re.match(comment_pattern, line))
    else:
        comment = 0
    return {
        "total": total,
        "code": total - blank - comment,
        "blank": blank,
        "comment": comment,
    }


def count_functions_classes_python(content: str) -> dict:
    try:
        tree = ast.parse(content)
        functions = sum(
            1
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
        classes = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
        return {"functions": functions, "classes": classes}
    except SyntaxError:
        return {"functions": 0, "classes": 0}


def count_functions_classes_generic(content: str, language: str) -> dict:
    patterns = {
        "JavaScript": (r"\bfunction\s+\w+\s*\(", r"\bclass\s+\w+"),
        "TypeScript": (r"\bfunction\s+\w+\s*\(", r"\bclass\s+\w+"),
        "Java": (
            r"\b(?:public|private|protected|static)?\s+\w+\s+\w+\s*\(",
            r"\bclass\s+\w+",
        ),
        "Go": (r"\bfunc\s+\w+", r"\btype\s+\w+\s+struct"),
        "Ruby": (r"\bdef\s+\w+", r"\bclass\s+\w+"),
    }
    if language not in patterns:
        return {"functions": 0, "classes": 0}
    func_pat, class_pat = patterns[language]
    return {
        "functions": len(re.findall(func_pat, content, re.MULTILINE)),
        "classes": len(re.findall(class_pat, content, re.MULTILINE)),
    }


def analyze_file(file_info: dict) -> dict:
    try:
        with open(file_info["path"], "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (PermissionError, OSError):
        return {
            **file_info,
            "metrics": {
                "loc": 0,
                "comments": 0,
                "blank": 0,
                "code": 0,
                "functions": 0,
                "classes": 0,
            },
            "content": "",
        }

    lang = file_info["language"]
    line_counts = count_lines(content, lang)

    if lang == "Python":
        sym_counts = count_functions_classes_python(content)
    else:
        sym_counts = count_functions_classes_generic(content, lang)

    return {
        **file_info,
        "content": content,
        "metrics": {
            "loc": line_counts["total"],
            "code": line_counts["code"],
            "comments": line_counts["comment"],
            "blank": line_counts["blank"],
            "functions": sym_counts["functions"],
            "classes": sym_counts["classes"],
        },
    }
