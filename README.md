# cs-match-tracker

A command-line application for retrieving Counter-Strike team match history from
CSAPI, storing it locally, and displaying a readable match summary.

## Features

- Fetch recent match history for a team by its CSAPI identifier.
- Limit the number of matches returned by the API.
- Store the raw JSON response in `data/match_history.json`.
- Display saved events, teams, maps, scores, and winners without another API
  request.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)
- An internet connection when updating match history

## Quick Start

Install the project dependencies from the repository root:

```bash
uv sync
```

Fetch and save the two most recent matches for team `9565`:

```bash
uv run main.py update --team-id 9565 --limit 2
```

Display the saved match history:

```bash
uv run main.py show
```

## Usage

### Update match history

```bash
uv run main.py update --team-id <team-id> [--limit <count>]
```

`--team-id` is required. `--limit` defaults to `5`.

The command writes the CSAPI response to `data/match_history.json`, replacing
the previously saved response. The `data/` directory contains local runtime
data and is excluded from Git.

### Show saved match history

```bash
uv run main.py show
```

The command reads `data/match_history.json` and prints the event, date,
best-of format, participating teams, map scores, and winner for each saved
match. Run `update` before `show` when no local history exists.

## Development

Run the code quality checks from the repository root:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict .
```
