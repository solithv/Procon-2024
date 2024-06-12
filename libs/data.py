from dataclasses import asdict, astuple, dataclass, replace


@dataclass(frozen=True)
class GameSpecification:
    """ゲームの仕様"""

    MAX_SIZE = 256


@dataclass(frozen=True)
class Direction:
    """方向"""

    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


@dataclass(frozen=True)
class StaticDieTypes:
    """定型抜き型のタイプ"""

    FULL = 1
    EVEN_ROW = 2
    EVEN_COLUMN = 3


@dataclass
class CuttingInfo:
    """操作内容"""

    p: int
    x: int
    y: int
    s: int

    def tuple(self) -> tuple:
        return astuple(self)

    def dict(self) -> dict:
        return asdict(self)

    def __repr__(self) -> str:
        return str(self.dict())


@dataclass
class Cell:
    """座標"""

    x: int
    y: int

    def copy(self):
        return replace(self)


@dataclass
class CornerCells:
    """角のセル"""

    nw: Cell
    ne: Cell
    sw: Cell
    se: Cell

    def members(self) -> tuple[Cell]:
        return self.nw, self.ne, self.sw, self.se
