import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import cs_match_tracker.match_history as mh
from cs_match_tracker.api import app


def test_get_matches_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    test_data = [
        {
            "id": 2396948,
            "team1": {"id": 9565, "name": "Vitality", "score": 2, "rank": 4},
            "team2": {"id": 8297, "name": "FURIA", "score": 1, "rank": 7},
            "maps": [
                {"id": 5, "name": "Nuke", "team1_score": 6, "team2_score": 13},
            ],
            "best_of": 3,
            "date": "2026-09-04",
            "event": "BLAST Open Porto 2026",
            "winner": {"id": 9565, "name": "Vitality"},
        },
    ]

    binary_data = json.dumps(test_data, ensure_ascii=False).encode("utf-8")

    fake_file = tmp_path / "matches.json"

    mh.save_match_history(fake_file, binary_data)

    monkeypatch.setattr(mh, "MATCH_HISTORY_PATH", fake_file)

    client = TestClient(app)

    response = client.get("/matches")

    assert response.status_code == 200
    assert response.json() == test_data


def test_get_matches_file_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    non_existent_file = tmp_path / "non_existent.json"
    monkeypatch.setattr(mh, "MATCH_HISTORY_PATH", non_existent_file)

    client = TestClient(app)
    response = client.get("/matches")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Match history not found. Please run update first."
    }
