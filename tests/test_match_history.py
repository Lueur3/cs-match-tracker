import json
from pathlib import Path

import pytest

from main import read_match_history, save_match_history, show_match_history


def test_save_and_show_match_history(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    test_data = [
        {
            "team1": {
                "name": "Vitality",
            },
            "team2": {
                "name": "FURIA",
            },
            "maps": [
                {"name": "Nuke", "team1_score": 6, "team2_score": 13},
            ],
            "best_of": 3,
            "date": "2026-09-04",
            "event": "BLAST Open Porto 2026",
            "winner": {"name": "Vitality"},
        },
    ]

    binary_data = json.dumps(test_data, ensure_ascii=False).encode("utf-8")

    test_file = tmp_path / "data" / "matches.json"

    save_match_history(test_file, binary_data)
    show_match_history(test_file)

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

    assert read_match_history(test_file) == binary_data
    assert captured == expected_output
