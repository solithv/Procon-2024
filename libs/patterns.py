import numpy as np

from .data import Cell, CornerCells, CuttingInfo, Direction, StaticDieTypes


class Pattern:
    def __init__(
        self,
        width: int,
        height: int,
        pattern: list[str] = None,
        array: np.ndarray = None,
    ) -> None:
        self.width = width
        self.height = height
        if pattern is not None:
            self.field = self.load_pattern(pattern)
        elif array is not None:
            self.field = array
        else:
            raise ValueError

    def load_pattern(self, pattern: list[str]):
        pattern = np.array([list(map(int, row)) for row in pattern])
        return pattern


class CuttingDie(Pattern):
    def __init__(
        self,
        id: int,
        width: int,
        height: int,
        type: StaticDieTypes = None,
        pattern: list[str] = None,
        array: np.ndarray = None,
    ) -> None:
        super().__init__(width, height, pattern, array)
        self.field = np.bool_(self.field)
        self.id = id
        self.type = type

    @classmethod
    def make_standard(cls, id: int, size: int, type: int):
        array = np.full((size, size), True)
        match type:
            case StaticDieTypes.full:
                pass
            case StaticDieTypes.even_row:
                array[1::2] = False
            case StaticDieTypes.even_column:
                array[:, 1::2] = False
            case _:
                raise ValueError
        return cls(id=id, width=size, height=size, type=type, array=array)


class Board(Pattern):
    def __init__(
        self,
        width: int,
        height: int,
        pattern: list[str] = None,
        array: np.ndarray = None,
    ) -> None:
        super().__init__(width, height, pattern, array)
        self.corners = CornerCells(
            nw=Cell(0, 0),
            ne=Cell(self.width - 1, 0),
            sw=Cell(0, self.height - 1),
            se=Cell(self.width - 1, self.height - 1),
        )

    def apply_die(self, die: CuttingDie, cell: Cell, direction: int):
        if cell.x >= self.width or cell.y >= self.height:
            raise ValueError
        if -cell.x >= die.width or -cell.y >= die.height:
            raise ValueError

        mask_start = Cell(x=0 if cell.x < 0 else cell.x, y=0 if cell.y < 0 else cell.y)
        mask_end = Cell(
            x=self.width if self.width < die.width + cell.x else die.width + cell.x,
            y=self.height if self.height < die.height + cell.y else die.height + cell.y,
        )
        die_start = Cell(x=-cell.x if cell.x < 0 else 0, y=-cell.y if cell.y < 0 else 0)
        die_end = Cell(
            x=self.width - cell.x if self.width < die.width + cell.x else self.width,
            y=(
                self.height - cell.y
                if self.height < die.height + cell.y
                else self.height
            ),
        )

        mask = np.zeros_like(self.field, dtype=np.bool_)
        mask[mask_start.y : mask_end.y, mask_start.x : mask_end.x] = die.field[
            die_start.y : die_end.y, die_start.x : die_end.x
        ]
        if direction in (Direction.up, Direction.down):
            for x in range(mask_start.x, mask_end.x):
                temp = self.field[:, x]
                if direction == Direction.up:
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
                if direction == Direction.left:
                    self.field[y] = np.concatenate([temp[~mask[y]], temp[mask[y]]])
                else:
                    self.field[y] = np.concatenate([temp[mask[y]], temp[~mask[y]]])
        return CuttingInfo(p=die.id, x=cell.x, y=cell.y, s=direction)
