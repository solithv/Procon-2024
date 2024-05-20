from .patterns import CuttingDie, Board
from .data import CuttingInfo


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
        self.dies = []
        for i in range(9):
            for j in range(3):
                id = 3 * i + j - 2 * bool(i)
                self.dies.append(CuttingDie.make_standard(id, 2**i, j + 1))
                if i < 1:
                    break

    def check_board(self):
        return self.board.field == self.goal.field
