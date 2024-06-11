from typing import Self
import numpy as np

from .data import Cell, CornerCells, CuttingInfo, Direction, StaticDieTypes


class Pattern:
    def __init__(
        self, width: int, height: int, pattern: list[str] | np.ndarray
    ) -> None:
        """基底クラス

        Args:
            width (int): 横幅
            height (int): 縦幅
            pattern (list[str] | np.ndarray): パターン. Defaults to None.
        """
        self.width = width
        self.height = height
        if isinstance(pattern, np.ndarray):
            self.field = pattern
        else:
            self.field = self.load_pattern(pattern)

    def load_pattern(self, pattern: list[str]) -> np.ndarray:
        """パターンを読み込み

        Args:
            pattern (list[str]): 問題フォーマット形式のパターン

        Returns:
            np.ndarray: 読み込んだパターン
        """
        pattern = np.array([list(map(int, row)) for row in pattern])
        return pattern


class CuttingDie(Pattern):
    def __init__(
        self,
        id: int,
        width: int,
        height: int,
        pattern: list[str] | np.ndarray,
        type: StaticDieTypes = None,
    ) -> None:
        """抜き型

        Args:
            id (int): 抜き型の連番id
            width (int): 横幅
            height (int): 縦幅
            pattern (list[str] | np.ndarray): パターン
            type (StaticDieTypes, optional): 定型抜き型のタイプ. Defaults to None.
        """
        super().__init__(width, height, pattern)
        self.field = np.bool_(self.field)
        self.id = id
        self.type = type

    @classmethod
    def make_standard(cls, id: int, size: int, type: int) -> Self:
        """定型抜き型を作成

        Args:
            id (int): 抜き型の連番id
            size (int): 縦横幅
            type (int): 定型抜き型のタイプ

        Raises:
            ValueError: typeが定型抜き型のタイプでない

        Returns:
            Self: 定型抜き型
        """
        pattern = np.full((size, size), True)
        match type:
            case StaticDieTypes.FULL:
                pass
            case StaticDieTypes.EVEN_ROW:
                pattern[1::2] = False
            case StaticDieTypes.EVEN_COLUMN:
                pattern[:, 1::2] = False
            case _:
                raise ValueError(f"{type} is not StaticDieType")
        return cls(id=id, width=size, height=size, type=type, pattern=pattern)


class Board(Pattern):
    def __init__(
        self, width: int, height: int, pattern: list[str] | np.ndarray
    ) -> None:
        """盤面

        Args:
            width (int): 横幅
            height (int): 縦幅
            pattern (list[str] | np.ndarray): パターン
        """
        super().__init__(width, height, pattern)
        self.corners = CornerCells(
            nw=Cell(0, 0),
            ne=Cell(self.width - 1, 0),
            sw=Cell(0, self.height - 1),
            se=Cell(self.width - 1, self.height - 1),
        )

    def _apply_die(self, die: CuttingDie, cell: Cell, direction: int) -> CuttingInfo:
        """抜き型を適用

        Args:
            die (CuttingDie): 適用する抜き型
            cell (Cell): 適用する座標
            direction (int): 適用する方向

        Raises:
            ValueError: 適用範囲外

        Returns:
            CuttingInfo: 操作内容
        """
        if (
            cell.x >= self.width
            or cell.y >= self.height
            or -cell.x >= die.width
            or -cell.y >= die.height
        ):
            raise ValueError("out of bounds.")

        mask_start = Cell(x=0 if cell.x < 0 else cell.x, y=0 if cell.y < 0 else cell.y)
        mask_end = Cell(
            x=self.width if self.width < die.width + cell.x else die.width + cell.x,
            y=self.height if self.height < die.height + cell.y else die.height + cell.y,
        )
        die_start = Cell(x=-cell.x if cell.x < 0 else 0, y=-cell.y if cell.y < 0 else 0)
        die_end = Cell(
            x=self.width - cell.x if self.width < die.width + cell.x else die.width,
            y=(
                self.height - cell.y
                if self.height < die.height + cell.y
                else die.height
            ),
        )

        mask = np.zeros_like(self.field, dtype=np.bool_)
        mask[mask_start.y : mask_end.y, mask_start.x : mask_end.x] = die.field[
            die_start.y : die_end.y, die_start.x : die_end.x
        ]
        if direction in (Direction.UP, Direction.DOWN):
            for x in range(mask_start.x, mask_end.x):
                temp = self.field[:, x]
                if direction == Direction.UP:
                    self.field[:, x] = np.concatenate(
                        [temp[~mask[:, x]], temp[mask[:, x]]]
                    )
                else:
                    self.field[:, x] = np.concatenate(
                        [temp[mask[:, x]], temp[~mask[:, x]]]
                    )

        else:
            for y in range(mask_start.y, mask_end.y):
                temp = self.field[y]
                if direction == Direction.LEFT:
                    self.field[y] = np.concatenate([temp[~mask[y]], temp[mask[y]]])
                else:
                    self.field[y] = np.concatenate([temp[mask[y]], temp[~mask[y]]])
        return CuttingInfo(p=die.id, x=int(cell.x), y=int(cell.y), s=direction)

    def copy(self):
        return Board(self.width, self.height, self.field.copy())
