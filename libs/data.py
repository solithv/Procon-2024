from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Direction:
    up = 0
    down = 1
    left = 2
    right = 3


@dataclass(frozen=True)
class StaticDieTypes:
    full = 1
    even_row = 2
    even_column = 3


@dataclass
class CuttingInfo:
    p: int
    x: int
    y: int
    s: Direction

    def to_dict(self) -> str:
        return asdict(self)

    def __repr__(self) -> str:
        return str(self.to_dict())


@dataclass
class Cell:
    x: int
    y: int


@dataclass
class CornerCells:
    nw: Cell
    ne: Cell
    sw: Cell
    se: Cell
