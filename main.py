import asyncio
from pathlib import Path

import httpx

MATCH_HISTORY_PATH = Path("data/match_history.json")


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


async def run() -> None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await fetch_team_match_history(client, 9565, 2)
        save_match_history(MATCH_HISTORY_PATH, response.content)
        print(f"Data saved: {MATCH_HISTORY_PATH}")


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
