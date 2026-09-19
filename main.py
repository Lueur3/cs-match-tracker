import asyncio

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


async def run() -> None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await fetch_team_match_history(client, 9565, 2)
        print(response.json())


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
