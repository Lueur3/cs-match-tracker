import datetime
import json
from pathlib import Path

import pytest

from cs_match_tracker.match_history import (
    load_match_history,
    read_match_history,
    save_match_history,
    show_match_history,
)
from cs_match_tracker.schemas import Match


def test_save_and_show_match_history(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
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

    test_file = tmp_path / "data" / "matches.json"

    save_match_history(test_file, binary_data)
    show_match_history(test_file)
    matches = load_match_history(test_file)

    captured = capsys.readouterr().out

    expected_output = "".join(
        [
            "BLAST Open Porto 2026, Best of 3, date: 2026-09-04\n",
            "Team Vitality vs Team FURIA\n",
            "Maps:\n",
            "  Nuke: 6:13\n",
            "Winner team is Vitality\n",
            "-" * 50,
            "\n",
        ]
    )

    assert len(matches) == 1

    match = matches[0]

    assert isinstance(match, Match)
    assert match.date == datetime.date(2026, 9, 4)
    assert match.id == test_data[0]["id"]
    assert match.team1.name == "Vitality"
    assert read_match_history(test_file) == binary_data
    assert captured == expected_output
