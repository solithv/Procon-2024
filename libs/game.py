from .patterns import PunchingDie, Board


class Game:
    def __init__(
        self, width: int, height: int, start: list[str], goal: list[str]
    ) -> None:
        self.general_dies = []
        for size in tuple(2**i for i in range(9)):
            self.general_dies.extend(PunchingDie.make_general(size))
        self.board = Board(width=width, height=height, pattern=start)
        self.goal = Board(width=width, height=height, pattern=goal)

    def check_board(self):
        return self.board.field == self.goal.field
