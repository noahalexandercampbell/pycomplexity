"""Tests for pycomplexity CLI entrypoint."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import pytest

import pycomplexity
from pycomplexity import analyze, to_json
from pycomplexity_cli import main, _build_parser


def _write(tmp_path: pathlib.Path, name: str, content: str) -> pathlib.Path:
    target = tmp_path / name
    target.write_text(content, encoding="utf-8")
    return target


def test_help_returns_zero() -> None:
    assert main(["--help"]) == 0


def test_direct_main_returns_zero_for_clean_file(tmp_path: pathlib.Path) -> None:
    target = _write(
        tmp_path,
        "clean.py",
        "def trivial():\n    return 1\n",
    )
    assert main([str(target)]) == 0


def test_direct_main_returns_one_for_noisy_file(tmp_path: pathlib.Path) -> None:
    target = _write(
        tmp_path,
        "noisy.py",
        "def noisy(x):\n    if x:\n        pass\n",
    )
    assert main([str(target), "--warn", "1"]) == 1


def test_custom_thresholds(tmp_path: pathlib.Path) -> None:
    target = _write(
        tmp_path,
        "edge.py",
        "def edge(x):\n    if x:\n        return 1\n    return 0\n",
    )
    # Complexity 2 should be below warn=3, so clean.
    assert main([str(target), "--warn", "3", "--error", "10"]) == 0
    # Complexity 2 above warn=2 -> noisy.
    assert main([str(target), "--warn", "2", "--error", "10"]) == 1


def test_json_flag_prints_json(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = _write(
        tmp_path,
        "sample.py",
        "def sample():\n    return 1\n",
    )
    rc = main([str(target), "--json"])
    assert rc == 0
    out, _ = capsys.readouterr()
    assert "sample" in out


def test_directory_is_recursed(tmp_path: pathlib.Path) -> None:
    sub = tmp_path / "pkg"
    sub.mkdir()
    _write(tmp_path, "root.py", "def root():\n    return 1\n")
    _write(sub, "child.py", "def child():\n    return 1\n")

    reports = analyze([str(tmp_path)])
    names = {fn.name for r in reports for fn in r.functions}
    assert names == {"root", "child"}


def test_cli_directory_integration(tmp_path: pathlib.Path) -> None:
    _write(tmp_path, "ok.py", "def ok():\n    return 1\n")
    assert main([str(tmp_path)]) == 0


def test_parse_known_args_error_path(tmp_path: pathlib.Path) -> None:
    with pytest.raises(SystemExit) as excinfo:
        _build_parser().parse_args(["--bogus"])
    assert excinfo.value.code != 0
