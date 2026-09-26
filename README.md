# cs-match-tracker

A command-line application for retrieving Counter-Strike team match history
from CSAPI, storing it locally, and exposing saved results through an HTTP API.

## Features

- Fetch recent match history for a team by its CSAPI identifier.
- Limit the number of matches requested during an update.
- Store the raw JSON response in `data/match_history.json`.
- Display saved events, teams, maps, scores, and winners without another API
  request.
- Retrieve saved match history through a FastAPI endpoint.

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
uv run cs-match-tracker update --team-id 9565 --limit 2
```

Display the saved match history:

```bash
uv run cs-match-tracker show
```

Start the API:

```bash
uv run uvicorn cs_match_tracker.api:app --reload
```

## Usage

### Update match history

```bash
uv run cs-match-tracker update --team-id <team-id> [--limit <count>]
```

`--team-id` is required. `--limit` defaults to `5`.

The command writes the CSAPI response to `data/match_history.json`, replacing
the previously saved response. The `data/` directory contains local runtime
data and is excluded from Git.

### Show saved match history

```bash
uv run cs-match-tracker show
```

The command reads `data/match_history.json` and prints the event, date,
best-of format, participating teams, map scores, and winner for each saved
match. Run `update` before `show` when no local history exists.

### HTTP API

Create the local match history before starting the API:

```bash
uv run cs-match-tracker update --team-id 9565 --limit 2
uv run uvicorn cs_match_tracker.api:app --reload
```

Retrieve the saved matches:

```bash
curl http://127.0.0.1:8000/matches
```

`GET /matches` returns `200 OK` with a JSON array of saved matches. If
`data/match_history.json` does not exist, it returns `404 Not Found`:

```json
{
  "detail": "Match history not found. Please run update first."
}
```

## Development

Run the automated tests and code quality checks from the repository root:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict .
```
