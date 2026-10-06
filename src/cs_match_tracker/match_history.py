from datetime import date
from pathlib import Path

import httpx2
from pydantic import TypeAdapter

from cs_match_tracker.schemas import Match

MATCH_HISTORY_PATH = Path("data/match_history.json")
MATCHES_ADAPTER: TypeAdapter[list[Match]] = TypeAdapter(list[Match])


async def fetch_team_match_history(
    client: httpx2.AsyncClient, team_id: int, limit: int
) -> httpx2.Response:
    params = {"limit": limit}

    response = await client.get(
        url=f"https://api.csapi.de/teams/{team_id}/matchhistory",
        params=params,
    )
    response.raise_for_status()
    return response


async def update_match_history(
    client: httpx2.AsyncClient, file_path: Path, team_id: int, limit: int
) -> list[Match]:
    response = await fetch_team_match_history(client, team_id, limit)
    matches = MATCHES_ADAPTER.validate_json(response.content)
    save_match_history(file_path, response.content)

    return matches


def save_match_history(file_path: Path, match_history: bytes) -> None:
    parent_dir = file_path.parent
    parent_dir.mkdir(parents=True, exist_ok=True)

    file_path.write_bytes(match_history)


def load_match_history(file_path: Path) -> list[Match]:
    raw_bytes = read_match_history(file_path)
    matches = MATCHES_ADAPTER.validate_json(raw_bytes)

    return matches


def read_match_history(file_path: Path) -> bytes:
    return file_path.read_bytes()


def filter_matches(
    matches: list[Match],
    team_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[Match]:

    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("date_from cannot be after date_to")

    filtered: list[Match] = []

    for match in matches:
        if (
            team_id is not None
            and match.team1.id != team_id
            and match.team2.id != team_id
        ):
            continue

        if date_from is not None and match.date < date_from:
            continue

        if date_to is not None and match.date > date_to:
            continue

        filtered.append(match)

    return filtered


def show_match_history(file_path: Path) -> None:
    match_history = load_match_history(file_path)
    for match in match_history:
        date = match.date
        event = match.event
        best_of = match.best_of
        winner = match.winner.name

        print(f"{event}, Best of {best_of}, date: {date}")

        team1, team2 = match.team1.name, match.team2.name

        print(f"Team {team1} vs Team {team2}")
        maps = match.maps
        print("Maps:")
        for map_data in maps:
            print(f"  {map_data.name}: {map_data.team1_score}:{map_data.team2_score}")

        print(f"Winner team is {winner}")
        print("-" * 50)
