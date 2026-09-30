"""Tests for pycomplexity core library."""

from __future__ import annotations

import pathlib

from pycomplexity import (
    FileReport,
    FunctionReport,
    ThresholdConfig,
    analyze,
    to_json,
)


def _write(tmp_path: pathlib.Path, name: str, content: str) -> pathlib.Path:
    target = tmp_path / name
    target.write_text(content, encoding="utf-8")
    return target


def test_trivial_function_has_complexity_one(tmp_path: pathlib.Path) -> None:
    target = _write(
        tmp_path,
        "trivial.py",
        "def trivial():\n    return 1\n",
    )
    reports = analyze([str(target)])
    assert len(reports) == 1
    assert [fn.name for fn in reports[0].functions] == ["trivial"]
    assert reports[0].functions[0].complexity == 1


def test_single_if_adds_one(tmp_path: pathlib.Path) -> None:
    target = _write(
        tmp_path,
        "ifonly.py",
        "def with_if(x):\n    if x > 0:\n        return 1\n    return 0\n",
    )
    reports = analyze([str(target)])
    assert reports[0].functions[0].complexity == 2


def test_if_elif_else_chain(tmp_path: pathlib.Path) -> None:
    target = _write(
        tmp_path,
        "elif.py",
        """
def score(x):
    if x < 0:
        return -1
    elif x == 0:
        return 0
    else:
        return 1
""",
    )
    reports = analyze([str(target)])
    assert reports[0].functions[0].complexity == 3


def test_nested_if_counts_each(tmp_path: pathlib.Path) -> None:
    target = _write(
        tmp_path,
        "nested_if.py",
        """
def nested(x, y):
    if x:
        if y:
            return 1
        return 2
    return 3
""",
    )
    reports = analyze([str(target)])
    assert reports[0].functions[0].complexity == 3


def test_boolop_and_or_count(tmp_path: pathlib.Path) -> None:
    target = _write(
        tmp_path,
        "bool.py",
        "def check(a, b):\n    return a and b or True\n",
    )
    reports = analyze([str(target)])
    assert reports[0].functions[0].complexity == 3


def test_multiple_except_handlers(tmp_path: pathlib.Path) -> None:
    target = _write(
        tmp_path,
        "try.py",
        """
def risky():
    try:
        x = 1
    except ValueError:
        x = 0
    except KeyError:
        x = -1
    return x
""",
    )
    reports = analyze([str(target)])
    assert reports[0].functions[0].complexity == 3


def test_threshold_warn_only(tmp_path: pathlib.Path) -> None:
    target = _write(
        tmp_path,
        "ok.py",
        """
def trivial():
    return 1

def moderately_complex(x):
    if x:
        return 1
    elif x > 0:
        return 2
    return 3
""",
    )
    reports = analyze([str(target)], threshold=ThresholdConfig(warn=3, error=10))
    by_name = {fn.name: fn for fn in reports[0].functions}
    assert by_name["trivial"].complexity == 1
    assert by_name["moderately_complex"].complexity == 3


def test_nested_functions_are_reported(tmp_path: pathlib.Path) -> None:
    target = _write(
        tmp_path,
        "nested.py",
        """
def outer():
    if True:
        def inner():
            if True:
                pass
        return inner
    return outer
""",
    )
    reports = analyze([str(target)])
    by_name = {fn.name: fn for fn in reports[0].functions}
    assert by_name["outer"].complexity == 3
    assert by_name["inner"].complexity == 2


def test_non_py_files_are_skipped(tmp_path: pathlib.Path) -> None:
    _write(tmp_path, "readme.txt", "hello")
    _write(tmp_path, "mod.py", "def ok():\n    return 1\n")
    reports = analyze([str(tmp_path)])
    assert len(reports) == 1
    assert [fn.name for fn in reports[0].functions] == ["ok"]


def test_to_json_contains_expected_keys() -> None:
    report = FileReport(
        filepath="example.py",
        functions=[
            FunctionReport(
                name="foo",
                lineno=1,
                complexity=1,
                filepath="example.py",
            )
        ],
    )
    payload = to_json([report])
    assert "example.py" in payload
    assert "foo" in payload
