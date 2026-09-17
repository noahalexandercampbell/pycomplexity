"""Cyclomatic complexity analysis for Python source code."""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FunctionReport:
    """Per-function complexity report."""

    name: str
    lineno: int
    complexity: int
    filepath: str

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "lineno": self.lineno,
            "complexity": self.complexity,
            "filepath": self.filepath,
        }


@dataclass
class FileReport:
    """Per-file complexity report."""

    filepath: str
    functions: list[FunctionReport]

    def as_dict(self) -> dict:
        return {
            "filepath": self.filepath,
            "functions": [f.as_dict() for f in self.functions],
        }


@dataclass
class ThresholdConfig:
    """Thresholds for flagging functions."""

    warn: int = 5
    error: int = 10


class _ComplexityVisitor(ast.NodeVisitor):
    """Walks a function body and accumulates a complexity score."""

    def __init__(self) -> None:
        self.complexity: int = 1

    def visit_If(self, node: ast.If) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def generic_visit(self, node: ast.AST) -> None:
        ast.NodeVisitor.generic_visit(self, node)


def _analyze_file(
    filepath: str, threshold: ThresholdConfig
) -> FileReport:
    source = Path(filepath).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=filepath)
    reports: list[FunctionReport] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            visitor = _ComplexityVisitor()
            for child in ast.iter_child_nodes(node):
                visitor.visit(child)
            reports.append(
                FunctionReport(
                    name=node.name,
                    lineno=node.lineno,
                    complexity=visitor.complexity,
                    filepath=filepath,
                )
            )

    return FileReport(filepath=filepath, functions=reports)


def analyze(
    paths: list[str],
    threshold: Optional[ThresholdConfig] = None,
) -> list[FileReport]:
    """Analyze one or more Python files or directories.

    Returns a list of :class:`FileReport` objects.  Only ``.py`` files are
    considered; everything else is silently skipped.
    """
    if threshold is None:
        threshold = ThresholdConfig()

    reports: list[FileReport] = []

    def _process(path: str) -> None:
        p = Path(path)
        if p.is_dir():
            for child in sorted(p.rglob("*.py")):
                _process(str(child))
        elif p.suffix == ".py" and p.is_file():
            reports.append(_analyze_file(str(p), threshold))

    for entry in paths:
        _process(entry)

    return reports


def to_json(reports: list[FileReport]) -> str:
    return json.dumps([r.as_dict() for r in reports], indent=2)
