# cs-match-tracker

A command-line application being developed to track Counter-Strike teams,
browse match history, and compare team performance.

Currently, only the application entry point and development tooling are in place.

## Requirements

- Python 3.14 or newer. The project selects Python 3.14 via `.python-version`.
- [uv](https://docs.astral.sh/uv/).

## Run

Run the following command from the repository root.

### Windows (PowerShell)

```powershell
uv run main.py
```

### Linux and macOS

```bash
uv run main.py
```

The current entry point prints:

```text
Hello from cs-match-tracker!
```

## Development checks

Run these commands from the repository root:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict .
```

Ruff checks lint rules and formatting. mypy checks the project in strict mode.
