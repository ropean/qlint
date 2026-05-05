import ast


class SmellVisitor(ast.NodeVisitor):
    def __init__(self, lines: list[str]):
        self.lines = lines
        self.smells = []

    def _get_nesting(self, node):
        depth = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                depth = max(depth, self._node_depth(child))
        return depth

    def _node_depth(self, node, current=0):
        max_d = current
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                max_d = max(max_d, self._node_depth(child, current + 1))
        return max_d

    def visit_FunctionDef(self, node):
        end_line = getattr(node, "end_lineno", node.lineno + len(self.lines))
        length = end_line - node.lineno + 1
        if length > 50:
            self.smells.append(
                {
                    "type": "long_function",
                    "severity": "warning" if length <= 100 else "error",
                    "line": node.lineno,
                    "message": f'Function "{node.name}" is {length} lines (limit: 50)',
                }
            )

        args_count = len(node.args.args) + len(node.args.kwonlyargs)
        if args_count > 5:
            self.smells.append(
                {
                    "type": "long_parameter_list",
                    "severity": "warning",
                    "line": node.lineno,
                    "message": f'Function "{node.name}" has {args_count} parameters (limit: 5)',
                }
            )

        nesting = self._node_depth(node)
        if nesting > 4:
            self.smells.append(
                {
                    "type": "deep_nesting",
                    "severity": "warning",
                    "line": node.lineno,
                    "message": f'Function "{node.name}" has nesting depth {nesting} (limit: 4)',
                }
            )

        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef


def analyze_python_smells(content: str) -> list[dict]:
    lines = content.splitlines()
    try:
        tree = ast.parse(content)
        visitor = SmellVisitor(lines)
        visitor.visit(tree)
        return visitor.smells
    except SyntaxError:
        return []


def analyze_generic_smells(content: str, language: str) -> list[dict]:
    smells = []
    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.expandtabs()
        depth = (len(stripped) - len(stripped.lstrip())) // 4
        if depth > 4:
            smells.append(
                {
                    "type": "deep_nesting",
                    "severity": "warning",
                    "line": i,
                    "message": f"Indentation depth {depth} exceeds limit (4)",
                }
            )
    return smells


def analyze_smells(file_info: dict) -> list[dict]:
    lang = file_info["language"]
    content = file_info.get("content", "")
    if lang == "Python":
        return analyze_python_smells(content)
    return analyze_generic_smells(content, lang)
