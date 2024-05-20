from dataclasses import dataclass


@dataclass
class Direction:
    up = 0
    down = 1
    left = 2
    right = 3


@dataclass
class CuttingInfo:
    p: int
    x: int
    y: int
    s: Direction
