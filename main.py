from libs import Game, Cell


def main():
    sample_input = {
        "board": {
            "width": 6,
            "height": 4,
            "start": ["012345", "678901", "234567", "890123"],
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
    game = Game(sample_input, Cell(8, 8))

    print(game.board.field)
    game.swap(Cell(0, 0), Cell(7, 7))
    game.swap(Cell(0, 7), Cell(7, 0))
    print(game.board.field)

    print(game.log_to_json())


if __name__ == "__main__":
    main()
