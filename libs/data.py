from abc import ABC
from dataclasses import asdict, astuple, dataclass, replace
from enum import IntEnum, auto


class DataClassBase(ABC):
    def tuple(self) -> tuple:
        return astuple(self)

    def dict(self) -> dict:
        return asdict(self)

    def __repr__(self) -> str:
        return str(self.dict())

    def copy(self):
        return replace(self)


class GameSpecification(IntEnum):
    """ゲームの仕様"""

    MAX_SIZE = 256


class Direction(IntEnum):
    """方向"""

    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class StaticDieTypes(IntEnum):
    """定型抜き型のタイプ"""

    FULL = 1
    EVEN_ROW = auto()
    EVEN_COLUMN = auto()


@dataclass
class CuttingInfo(DataClassBase):
    """操作内容"""

    p: int
    x: int
    y: int
    s: int


@dataclass
class Cell(DataClassBase):
    """座標"""

    x: int
    y: int


@dataclass
class CornerCells(DataClassBase):
    """角のセル"""

    nw: Cell
    ne: Cell
    sw: Cell
    se: Cell

    def members(self) -> tuple[Cell]:
        return self.nw, self.ne, self.sw, self.se
