import ast
import re


class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []

    def _calc_complexity(self, node):
        complexity = 1
        for child in ast.walk(node):
            if isinstance(
                child,
                (
                    ast.If,
                    ast.While,
                    ast.For,
                    ast.ExceptHandler,
                    ast.With,
                    ast.Assert,
                    ast.comprehension,
                ),
            ):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def visit_FunctionDef(self, node):
        complexity = self._calc_complexity(node)
        self.functions.append(
            {
                "name": node.name,
                "line": node.lineno,
                "complexity": complexity,
                "flagged": complexity > 10,
            }
        )
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef


def analyze_python_complexity(content: str) -> dict:
    try:
        tree = ast.parse(content)
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        functions = visitor.functions
        if not functions:
            return {
                "functions": [],
                "avg_complexity": 0,
                "max_complexity": 0,
                "flagged_count": 0,
            }
        avg = sum(f["complexity"] for f in functions) / len(functions)
        max_c = max(f["complexity"] for f in functions)
        return {
            "functions": functions,
            "avg_complexity": round(avg, 2),
            "max_complexity": max_c,
            "flagged_count": sum(1 for f in functions if f["flagged"]),
        }
    except SyntaxError:
        return {
            "functions": [],
            "avg_complexity": 0,
            "max_complexity": 0,
            "flagged_count": 0,
        }


def analyze_generic_complexity(content: str, language: str) -> dict:
    decision_patterns = {
        "JavaScript": r"\b(if|else if|while|for|switch|catch|&&|\|\|)\b",
        "TypeScript": r"\b(if|else if|while|for|switch|catch|&&|\|\|)\b",
        "Java": r"\b(if|else if|while|for|switch|catch|&&|\|\|)\b",
        "Go": r"\b(if|else if|for|switch|select|&&|\|\|)\b",
    }
    pattern = decision_patterns.get(language)
    if not pattern:
        return {"avg_complexity": 0, "max_complexity": 0, "flagged_count": 0}
    count = len(re.findall(pattern, content))
    complexity = 1 + count
    return {
        "avg_complexity": complexity,
        "max_complexity": complexity,
        "flagged_count": 1 if complexity > 10 else 0,
    }


def analyze_complexity(file_info: dict) -> dict:
    lang = file_info["language"]
    content = file_info.get("content", "")
    if lang == "Python":
        return analyze_python_complexity(content)
    return analyze_generic_complexity(content, lang)
