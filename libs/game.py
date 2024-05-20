from .patterns import CuttingDie, Board
from .data import CuttingInfo, Cell, Direction


class Game:
    def __init__(self, game_input: dict) -> None:
        self.log: list[CuttingInfo] = []
        self.board = Board(
            width=game_input["board"]["width"],
            height=game_input["board"]["height"],
            pattern=game_input["board"]["start"],
        )
        self.goal = Board(
            width=game_input["board"]["width"],
            height=game_input["board"]["height"],
            pattern=game_input["board"]["goal"],
        )

        self.make_standard_dies()
        for i, pattern in enumerate(game_input["general"]["patterns"], len(self.dies)):
            self.dies.append(
                CuttingDie(
                    i, pattern["width"], pattern["height"], pattern=pattern["cells"]
                )
            )

    def make_standard_dies(self):
        self.dies: list[CuttingDie] = []
        for i in range(9):
            for j in range(3):
                id = 3 * i + j - 2 * bool(i)
                self.dies.append(CuttingDie.make_standard(id=id, size=2**i, type=j + 1))
                if i < 1:
                    break

    def check_board(self):
        return self.board.field == self.goal.field

    def search_static_die(self, size, type):
        for die in self.dies:
            if die.width == die.height == size and die.type == type:
                return die

    def row_two_piece_replace(self, corner_target: Cell, target: Cell):
        # 左上のみ対応(仮)
        for i in reversed(range(9)):
            size = 2**i
            while True:
                if size <= target.x - corner_target.x - 1:
                    self.board.apply_die(
                        self.search_static_die(size, 1),
                        Cell(target.x - size, target.y),
                        Direction.right,
                    )
                    corner_target.x += size
                else:
                    break
        if target.x - corner_target.x == 1:
            self.board.apply_die(
                self.search_static_die(size, 1),
                Cell(target.x, target.y),
                Direction.right,
            )
