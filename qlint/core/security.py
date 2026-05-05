import ast
import re

SECRET_PATTERNS = [
    (
        r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([A-Za-z0-9_\-]{16,})["\']',
        "Hardcoded API key",
    ),
    (
        r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']{6,})["\']',
        "Hardcoded password",
    ),
    (
        r'(?i)(secret[_-]?key|secret)\s*[=:]\s*["\']([A-Za-z0-9_\-]{16,})["\']',
        "Hardcoded secret",
    ),
    (
        r'(?i)(token|auth[_-]?token)\s*[=:]\s*["\']([A-Za-z0-9_\-\.]{20,})["\']',
        "Hardcoded token",
    ),
    (
        r'(?i)(aws[_-]?access[_-]?key|aws[_-]?secret)\s*[=:]\s*["\']([A-Z0-9]{16,})["\']',
        "AWS credentials",
    ),
    (
        r'(?i)(private[_-]?key)\s*[=:]\s*["\']([A-Za-z0-9_\-]{16,})["\']',
        "Hardcoded private key",
    ),
    (r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", "Embedded private key"),
]

JS_TS_PATTERNS = [
    (r"\beval\s*\(", "Use of eval()"),
    (r"\bnew\s+Function\s*\(", "Use of Function constructor"),
    (r"\bdocument\.write\s*\(", "Use of document.write()"),
    (r"innerHTML\s*=", "Direct innerHTML assignment (XSS risk)"),
]


class _PyDangerousCallVisitor(ast.NodeVisitor):
    _DIRECT = {
        "eval": "Use of eval()",
        "exec": "Use of exec()",
        "__import__": "Dynamic import via __import__",
    }
    _ATTR = {
        ("pickle", "loads"): "Unsafe pickle deserialization",
        ("pickle", "load"): "Unsafe pickle deserialization",
        ("os", "system"): "Use of os.system()",
    }

    def __init__(self):
        self.issues = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in self._DIRECT:
            self.issues.append(
                {
                    "type": "dangerous_function",
                    "severity": "error",
                    "line": node.lineno,
                    "message": self._DIRECT[node.func.id],
                }
            )
        elif isinstance(node.func, ast.Attribute) and isinstance(
            node.func.value, ast.Name
        ):
            key = (node.func.value.id, node.func.attr)
            if key == ("subprocess", "call"):
                has_shell = any(
                    kw.arg == "shell"
                    and isinstance(kw.value, ast.Constant)
                    and kw.value.value is True
                    for kw in node.keywords
                )
                if has_shell:
                    self.issues.append(
                        {
                            "type": "dangerous_function",
                            "severity": "error",
                            "line": node.lineno,
                            "message": "Shell injection risk: subprocess.call with shell=True",
                        }
                    )
            elif key in self._ATTR:
                self.issues.append(
                    {
                        "type": "dangerous_function",
                        "severity": "error",
                        "line": node.lineno,
                        "message": self._ATTR[key],
                    }
                )
        self.generic_visit(node)


def _scan_python_dangerous(content: str) -> list[dict]:
    try:
        tree = ast.parse(content)
        visitor = _PyDangerousCallVisitor()
        visitor.visit(tree)
        return visitor.issues
    except SyntaxError:
        return []


def _outside_string(line: str, pos: int) -> bool:
    """Heuristic: true when pos appears to be in code, not a quoted string."""
    before = line[:pos]
    return (before.count('"') % 2 == 0) and (before.count("'") % 2 == 0)


def _scan_js_ts_dangerous(content: str) -> list[dict]:
    issues = []
    for i, line in enumerate(content.splitlines(), 1):
        for pattern, message in JS_TS_PATTERNS:
            m = re.search(pattern, line)
            if m and _outside_string(line, m.start()):
                issues.append(
                    {
                        "type": "dangerous_function",
                        "severity": "error",
                        "line": i,
                        "message": message,
                    }
                )
    return issues


def scan_security(file_info: dict) -> list[dict]:
    content = file_info.get("content", "")
    lang = file_info["language"]
    issues = []

    for i, line in enumerate(content.splitlines(), 1):
        for pattern, message in SECRET_PATTERNS:
            if re.search(pattern, line):
                issues.append(
                    {
                        "type": "secret",
                        "severity": "critical",
                        "line": i,
                        "message": message,
                    }
                )

    if lang == "Python":
        issues += _scan_python_dangerous(content)
    elif lang in ("JavaScript", "TypeScript"):
        issues += _scan_js_ts_dangerous(content)

    return issues
