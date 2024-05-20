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


@dataclass
class StaticDieTypes:
    full = 1
    even_row = 2
    even_column = 3


@dataclass
class Cell:
    x: int
    y: int
