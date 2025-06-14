from typing import NamedTuple

class Box(NamedTuple):
    x1: int
    y1: int
    x2: int
    y2: int
    label: str
    score: float
