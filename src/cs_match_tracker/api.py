from datetime import date

import httpx2
from fastapi import FastAPI, HTTPException, status
from pydantic import ValidationError

import cs_match_tracker.match_history as mh
from cs_match_tracker.schemas import Match, UpdateMatchesRequest

app = FastAPI(title="CS Match Tracker")


@app.get("/matches", response_model=list[Match])
def read_matches(
    team_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[Match]:
    try:
        match_history = mh.load_match_history(mh.MATCH_HISTORY_PATH)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match history not found. Please run update first.",
        ) from exc
    try:
        return mh.filter_matches(match_history, team_id, date_from, date_to)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc


@app.post("/matches/update", response_model=list[Match])
async def update_matches(body: UpdateMatchesRequest) -> list[Match]:
    try:
        async with httpx2.AsyncClient(timeout=10.0) as client:
            matches = await mh.update_match_history(
                client, mh.MATCH_HISTORY_PATH, body.team_id, body.limit
            )
            return matches
    except (httpx2.HTTPError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to update matches from external service.",
        ) from exc
