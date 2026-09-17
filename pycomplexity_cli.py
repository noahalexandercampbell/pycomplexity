"""Command-line interface for pycomplexity."""

from __future__ import annotations

import argparse
import sys

from pycomplexity import ThresholdConfig, analyze, to_json


class _HelpArgs:
    help_requested = True


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pycomplexity",
        description="Analyze cyclomatic complexity of Python source files.",
    )
    p.add_argument("paths", nargs="+", help="Python files or directories to scan")
    p.add_argument(
        "--warn",
        type=int,
        default=5,
        help="Complexity threshold for warnings (default: 5)",
    )
    p.add_argument(
        "--error",
        type=int,
        default=10,
        help="Complexity threshold for errors (default: 10)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit raw JSON instead of the default human-readable table",
    )
    return p


def _parse_args(argv: list[str] | None = None):
    parser = _build_parser()
    try:
        return parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:
            return _HelpArgs()
        raise


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if isinstance(args, _HelpArgs) or args is None:
        return 0

    threshold = ThresholdConfig(warn=args.warn, error=args.error)
    reports = analyze(args.paths, threshold=threshold)

    if args.json:
        print(to_json(reports))
        return 0

    has_issues = False
    for report in reports:
        for fn in report.functions:
            if fn.complexity >= threshold.error:
                label = "error"
            elif fn.complexity >= threshold.warn:
                label = "warn"
                has_issues = True
            else:
                label = "ok"

            flag = {"error": "!", "warn": "~", "ok": " "}[label]
            print(f"{flag} {report.filepath}:{fn.lineno} {fn.name} -> {fn.complexity}")
            if label != "ok":
                has_issues = True

    return 1 if has_issues else 0


if __name__ == "__main__":
    sys.exit(main())
