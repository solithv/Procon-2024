from libs import Game, Direction
from libs.data import Cell


def main():
    sample_input = {
        "board": {
            "width": 6,
            "height": 4,
            "start": ["012345", "213033", "022103", "322033"],
            "goal": ["000000", "111222", "222233", "333333"],
        },
        "general": {
            "n": 2,
            "patterns": [
                {"p": 25, "width": 4, "height": 2, "cells": ["0111", "1001"]},
                {"p": 26, "width": 2, "height": 2, "cells": ["10", "01"]},
            ],
        },
    }
    game = Game(sample_input)
    # print(len(game.dies))

    # game.board.apply_die(game.dies[26], Cell(1, 1), Direction.left)
    print(game.board.field)
    game.row_two_piece_replace(Cell(0, 0), Cell(5, 0))
    print(game.board.field)


if __name__ == "__main__":
    main()
