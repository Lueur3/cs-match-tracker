import json
from pathlib import Path

import httpx


async def fetch_team_match_history(
    client: httpx.AsyncClient, team_id: int, limit: int
) -> httpx.Response:
    params = {"limit": limit}

    response = await client.get(
        url=f"https://api.csapi.de/teams/{team_id}/matchhistory",
        params=params,
    )
    response.raise_for_status()
    return response


def save_match_history(file_path: Path, match_history: bytes) -> None:
    parent_dir = file_path.parent
    parent_dir.mkdir(parents=True, exist_ok=True)

    file_path.write_bytes(match_history)


def read_match_history(file_path: Path) -> bytes:
    return file_path.read_bytes()


def show_match_history(file_path: Path) -> None:
    match_history = read_match_history(file_path)
    data = json.loads(match_history)
    for item in data:
        date = item["date"]
        event = item["event"]
        best_of = item["best_of"]
        winner = item["winner"]["name"]

        print(f"{event}, Best of {best_of}, date: {date}")

        team1, team2 = item["team1"]["name"], item["team2"]["name"]

        print(f"Team {team1} vs Team {team2}")
        maps = item["maps"]
        print("Maps:")
        for map_data in maps:
            print(
                f"  {map_data['name']}: {map_data['team1_score']}:{map_data['team2_score']}"
            )

        print(f"Winner team is {winner}")
        print("-" * 50)
