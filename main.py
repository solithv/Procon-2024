import json

import numpy as np
from libs import Game, Cell


def save_logs(game: Game):
    np.savetxt("./board.txt", game.board.field, "%d")
    np.savetxt("./gaol.txt", game.goal.field, "%d")
    np.savetxt("./result_map.txt", game.check_board(), "%d")
    with open("./result.txt", "w") as f:
        f.write(f"True: {np.count_nonzero(game.check_board())}\n")
        f.write(f"False: {np.count_nonzero(~game.check_board())}\n")
        f.write(
            f"True rate: {np.count_nonzero(game.check_board())/(game.board.width*game.board.height):%}"
        )
    with open("./log.json", "w") as f:
        json.dump(game.format_log(), f, indent=2)


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
    game = Game(sample_input, Cell(128, 128), 123)

    game.rough_arrange()

    save_logs(game)


if __name__ == "__main__":
    main()
