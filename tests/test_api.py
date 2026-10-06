import json
from pathlib import Path

import httpx2
import pytest
from fastapi.testclient import TestClient

import cs_match_tracker.match_history as mh
from cs_match_tracker.api import app


@pytest.fixture
def test_data() -> list[dict[str, object]]:
    return [
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


@pytest.fixture
def test_data_2() -> list[dict[str, object]]:
    return [
        {
            "id": 2396949,
            "team1": {"id": 7020, "name": "Spirit", "score": 2, "rank": 1},
            "team2": {"id": 11283, "name": "Falcons", "score": 0, "rank": 3},
            "maps": [
                {"id": 3, "name": "Ancient", "team1_score": 13, "team2_score": 11},
                {"id": 5, "name": "Nuke", "team1_score": 13, "team2_score": 8},
            ],
            "best_of": 3,
            "date": "2026-09-05",
            "event": "BLAST Open Porto 2026",
            "winner": {"id": 7020, "name": "Spirit"},
        },
        {
            "id": 2396943,
            "team1": {"id": 7020, "name": "Spirit", "score": 2, "rank": 1},
            "team2": {"id": 8297, "name": "FURIA", "score": 0, "rank": 7},
            "maps": [
                {"id": 11, "name": "Cache", "team1_score": 13, "team2_score": 5},
                {"id": 3, "name": "Ancient", "team1_score": 13, "team2_score": 10},
            ],
            "best_of": 3,
            "date": "2026-08-31",
            "event": "BLAST Open Porto 2026",
            "winner": {"id": 7020, "name": "Spirit"},
        },
    ]


def test_get_matches_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, test_data: list[dict[str, object]]
) -> None:

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


def test_update_matches_success_default_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, test_data: list[dict[str, object]]
) -> None:
    test_team = {"team_id": 9565}

    binary_data = json.dumps(test_data).encode("utf-8")

    fake_file = tmp_path / "saved_matches.json"
    monkeypatch.setattr(mh, "MATCH_HISTORY_PATH", fake_file)

    async def fake_fetch(
        client: httpx2.AsyncClient, team_id: int, limit: int
    ) -> httpx2.Response:
        assert team_id == 9565
        assert limit == 5
        return httpx2.Response(status_code=200, content=binary_data)

    monkeypatch.setattr(mh, "fetch_team_match_history", fake_fetch)

    client = TestClient(app)
    response = client.post("/matches/update", json=test_team)

    assert response.status_code == 200
    assert response.json() == test_data
    assert fake_file.read_bytes() == binary_data


def test_update_matches_missing_team_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_fetch(*args: object, **kwargs: object) -> httpx2.Response:
        raise AssertionError(
            "External request should not be called on validation error"
        )

    monkeypatch.setattr(mh, "fetch_team_match_history", fake_fetch)

    client = TestClient(app)
    response = client.post("/matches/update", json={})

    assert response.status_code == 422


def test_update_matches_network_error(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_fetch(*args: object, **kwargs: object) -> httpx2.Response:
        raise httpx2.ConnectError("Connection failed")

    monkeypatch.setattr(mh, "fetch_team_match_history", fake_fetch)
    client = TestClient(app)
    response = client.post("/matches/update", json={"team_id": 9565})

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Failed to update matches from external service."
    }


def test_update_matches_invalid_payload_preserves_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, test_data: list[dict[str, object]]
) -> None:
    old_bytes = json.dumps(test_data).encode("utf-8")

    fake_file = tmp_path / "saved_matches.json"
    mh.save_match_history(fake_file, old_bytes)
    monkeypatch.setattr(mh, "MATCH_HISTORY_PATH", fake_file)

    async def fake_fetch(*args: object, **kwargs: object) -> httpx2.Response:
        return httpx2.Response(
            status_code=200, content=b"<html>Cloudflare Error</html>"
        )

    monkeypatch.setattr(mh, "fetch_team_match_history", fake_fetch)

    client = TestClient(app)
    response = client.post("/matches/update", json={"team_id": 9565})

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Failed to update matches from external service."
    }
    assert fake_file.read_bytes() == old_bytes


def test_correct_filtered_matches(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    test_data_2: list[dict[str, object]],
) -> None:

    binary_data = json.dumps(test_data_2, ensure_ascii=False).encode("utf-8")

    fake_file = tmp_path / "matches.json"

    mh.save_match_history(fake_file, binary_data)

    monkeypatch.setattr(mh, "MATCH_HISTORY_PATH", fake_file)

    client = TestClient(app)
    response = client.get(
        "/matches",
        params={"team_id": 7020, "date_from": "2026-08-01", "date_to": "2026-09-01"},
    )

    result = response.json()

    assert response.status_code == 200
    assert result == [test_data_2[1]]


def test_empty_filtered_matches(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    test_data_2: list[dict[str, object]],
) -> None:
    binary_data = json.dumps(test_data_2, ensure_ascii=False).encode("utf-8")

    fake_file = tmp_path / "matches.json"

    mh.save_match_history(fake_file, binary_data)

    monkeypatch.setattr(mh, "MATCH_HISTORY_PATH", fake_file)

    client = TestClient(app)
    response = client.get(
        "/matches",
        params={"team_id": 1, "date_from": "2026-08-01", "date_to": "2026-09-01"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_wrong_format_filtered_matches() -> None:
    client = TestClient(app)

    response = client.get(
        "/matches",
        params={"date_from": "not a date"},
    )

    assert response.status_code == 422


def test_wrong_date_range(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    test_data_2: list[dict[str, object]],
) -> None:
    binary_data = json.dumps(test_data_2, ensure_ascii=False).encode("utf-8")

    fake_file = tmp_path / "matches.json"

    mh.save_match_history(fake_file, binary_data)

    monkeypatch.setattr(mh, "MATCH_HISTORY_PATH", fake_file)
    client = TestClient(app)

    response = client.get(
        "/matches",
        params={"date_from": "2026-09-10", "date_to": "2026-09-01"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "date_from cannot be after date_to"
