import datetime

from pydantic import BaseModel


class MatchTeam(BaseModel):
    id: int
    name: str
    score: int
    rank: int


class Winner(BaseModel):
    id: int
    name: str


class MapResult(BaseModel):
    id: int
    name: str
    team1_score: int
    team2_score: int


class Match(BaseModel):
    id: int
    team1: MatchTeam
    team2: MatchTeam
    maps: list[MapResult]
    best_of: int
    date: datetime.date
    event: str
    winner: Winner
