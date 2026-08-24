# AST / Tree-sitter extraction

import ast
from pathlib import Path
from typing import Dict


def extract_ast_signatures(file_path: Path | str) -> Dict[str, str]:
    """Extracts top-level class and function signatures using Python AST."""
    path = Path(file_path)
    if not path.exists() or path.suffix != ".py":
        return {}

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    signatures = {}

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            args = [arg.arg for arg in node.args.args]
            signatures[node.name] = f"def {node.name}({', '.join(args)}) -> None"
        elif isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            signatures[node.name] = f"class {node.name}: methods={methods}"

    return signatures