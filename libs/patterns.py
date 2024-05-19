import numpy as np
from .data import Direction


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


class PunchingDie(Pattern):
    def __init__(
        self,
        width: int,
        height: int,
        pattern: list[str] = None,
        array: np.ndarray = None,
    ) -> None:
        super().__init__(width, height, pattern, array)
        self.field = np.bool_(self.field)

    @classmethod
    def make_general(cls, size: int):
        type_1_array = np.full((size, size), True)
        if size == 1:
            return (cls(size, size, array=type_1_array),)
        else:
            type_1 = cls(size, size, array=type_1_array)
            type_2_array = type_1_array.copy()
            type_2_array[1::2] = False
            type_2 = cls(size, size, array=type_2_array)
            type_3_array = type_1_array.copy()
            type_3_array[:, 1::2] = False
            type_3 = cls(size, size, array=type_3_array)
            return type_1, type_2, type_3


class Board(Pattern):
    def __init__(
        self,
        width: int,
        height: int,
        pattern: list[str] = None,
        array: np.ndarray = None,
    ) -> None:
        super().__init__(width, height, pattern, array)

    def apply_die(self, die: PunchingDie, x: int, y: int, direction: int):
        if x >= self.width or y >= self.height:
            raise ValueError
        if -x >= die.width or -y >= die.height:
            raise ValueError

        x_start = 0 if x < 0 else x
        die_x_start = -x if x < 0 else 0
        y_start = 0 if y < 0 else y
        die_y_start = -y if y < 0 else 0
        x_end = self.width if self.width < die.width + x else die.width + x
        die_x_end = (
            die.width + x - self.width if self.width < die.width + x else self.width
        )
        y_end = self.height if self.height < die.height + y else die.height + y
        die_y_end = (
            die.height + y - self.height
            if self.height < die.height + y
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
        print(self.field)
