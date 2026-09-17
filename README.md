# pycomplexity

AST-based cyclomatic complexity analyzer for Python source files.

## About

`pycomplexity` statically analyzes Python functions and reports their
cyclomatic complexity — the number of linearly independent paths through
the function body. It uses only the standard-library `ast` module, so it
runs without any runtime dependencies and produces deterministic output.

## Features

- Recursive directory scanning with glob-based `.py` filtering.
- Per-function complexity scoring with configurable `--warn` / `--error`
  thresholds.
- Human-readable terminal output with `ok`, `warn`, and `error` labels.
- Machine-readable `--json` output.
- Async function and comprehension-aware scoring.

## Installation

```bash
pip install pycomplexity
```

For development:

```bash
git clone https://github.com/noahalexandercampbell/pycomplexity.git
cd pycomplexity
pip install -e .[dev]
```

## Usage

```bash
pycomplexity src/

pycomplexity --warn 4 --error 8 mymodule.py

pycomplexity --json src/ > report.json
```

Exit codes:

- `0` — no functions exceeded the warn threshold.
- `1` — at least one function is at or above the warn threshold.

## Project Structure

```
pycomplexity/
  pycomplexity.py      # AST-based complexity engine
  pycomplexity_cli.py  # argparse CLI entrypoint
  tests/               # pytest suite
  docs/                # additional documentation
  pyproject.toml       # build configuration
  README.md
```

## Tags

`cli`, `static-analysis`, `ast`, `complexity`, `python`, `developer-tools`

## License

MIT
