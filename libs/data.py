from dataclasses import asdict, astuple, dataclass, replace


@dataclass(frozen=True)
class GameSpecification:
    """ゲームの仕様"""

    max_size = 256


@dataclass(frozen=True)
class Direction:
    """方向"""

    up = 0
    down = 1
    left = 2
    right = 3


@dataclass(frozen=True)
class StaticDieTypes:
    """定型抜き型のタイプ"""

    full = 1
    even_row = 2
    even_column = 3


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
