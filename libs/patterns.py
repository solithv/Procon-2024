import numpy as np
from .data import Direction, Cell, StaticDieTypes


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

    def apply_die(self, die: CuttingDie, cell: Cell, direction: int):
        if cell.x >= self.width or cell.y >= self.height:
            raise ValueError
        if -cell.x >= die.width or -cell.y >= die.height:
            raise ValueError

        x_start = 0 if cell.x < 0 else cell.x
        die_x_start = -cell.x if cell.x < 0 else 0
        y_start = 0 if cell.y < 0 else cell.y
        die_y_start = -cell.y if cell.y < 0 else 0
        x_end = self.width if self.width < die.width + cell.x else die.width + cell.x
        die_x_end = (
            die.width + cell.x - self.width
            if self.width < die.width + cell.x
            else self.width
        )
        y_end = (
            self.height if self.height < die.height + cell.y else die.height + cell.y
        )
        die_y_end = (
            die.height + cell.y - self.height
            if self.height < die.height + cell.y
            else self.height
        )

        mask = np.full_like(self.field, False, dtype=np.bool_)
        mask[y_start:y_end, x_start:x_end] = die.field[
            die_y_start:die_y_end, die_x_start:die_x_end
        ]
        if direction in (Direction.up, Direction.down):
            for _x in range(x_start, x_end):
                temp = self.field[:, _x]
                if direction == Direction.up:
                    self.field[:, _x] = np.concatenate(
                        [temp[~mask[:, _x]], temp[mask[:, _x]]]
                    )
                else:
                    self.field[:, _x] = np.concatenate(
                        [temp[mask[:, _x]], temp[~mask[:, _x]]]
                    )

        else:
            for _y in range(y_start, y_end):
                temp = self.field[_y]
                if direction == Direction.left:
                    self.field[_y] = np.concatenate([temp[~mask[_y]], temp[mask[_y]]])
                else:
                    self.field[_y] = np.concatenate([temp[mask[_y]], temp[~mask[_y]]])
        return
