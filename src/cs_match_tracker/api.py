from fastapi import FastAPI, HTTPException

import cs_match_tracker.match_history as mh
from cs_match_tracker.schemas import Match

app = FastAPI(title="CS Match Tracker")


@app.get("/matches", response_model=list[Match])
def read_matches() -> list[Match]:
    try:
        match_history = mh.load_match_history(mh.MATCH_HISTORY_PATH)
        return match_history
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404, detail="Match history not found. Please run update first."
        ) from exc
