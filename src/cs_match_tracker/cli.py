import argparse
import asyncio
import sys

import httpx2

import cs_match_tracker.match_history as mh


async def update_match_history(team_id: int, limit: int) -> None:
    async with httpx2.AsyncClient(timeout=10.0) as client:
        response = await mh.fetch_team_match_history(client, team_id, limit)
        mh.save_match_history(mh.MATCH_HISTORY_PATH, response.content)
        print(f"Data saved: {mh.MATCH_HISTORY_PATH}")


def handle_update(team_id: int, limit: int) -> None:
    try:
        asyncio.run(update_match_history(team_id, limit))
    except httpx2.HTTPError as e:
        print(f"Failed to update match history: {e}", file=sys.stderr)
        sys.exit(1)


def handle_show() -> None:
    try:
        mh.show_match_history(mh.MATCH_HISTORY_PATH)
    except FileNotFoundError:
        print("No saved match history. Run the update command first.", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Get team match history")

    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    update = subparsers.add_parser("update", help="Update match history")
    update.add_argument("--team-id", type=int, help="Team id", required=True)
    update.add_argument("--limit", type=int, default=5, help="Limit of match history")

    subparsers.add_parser("show", help="Show match history")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    match args.subcommand:
        case "update":
            handle_update(args.team_id, args.limit)
        case "show":
            handle_show()
