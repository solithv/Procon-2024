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

    UP = 0
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

    def is_corner(self, corner: Cell):
        return corner in self.members()

    def is_n(self, corner: Cell):
        assert self.is_corner(corner), f"{corner} is not corner cell"
        return corner.y in (self.nw.y, self.ne.y)

    def is_s(self, corner: Cell):
        assert self.is_corner(corner), f"{corner} is not corner cell"
        return corner.y in (self.sw.y, self.se.y)

    def is_w(self, corner: Cell):
        assert self.is_corner(corner), f"{corner} is not corner cell"
        return corner.x in (self.nw.x, self.sw.x)

    def is_e(self, corner: Cell):
        assert self.is_corner(corner), f"{corner} is not corner cell"
        return corner.x in (self.ne.x, self.se.x)

    @property
    def n(self):
        assert self.nw.y == self.ne.y
        return self.nw.y

    @property
    def s(self):
        assert self.sw.y == self.se.y
        return self.sw.y

    @property
    def w(self):
        assert self.nw.x == self.sw.x
        return self.nw.x

    @property
    def e(self):
        assert self.ne.x == self.se.x
        return self.ne.x
