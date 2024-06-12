import json
from pathlib import Path

import numpy as np

from libs import Cell, Game


def save_logs(game: Game, log_dir: str | Path = "./logs"):
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(log_dir / "board.txt", game.board.field, "%d")
    np.savetxt(log_dir / "goal.txt", game.goal.field, "%d")
    np.savetxt(log_dir / "result_map.txt", game.check_board(), "%d")
    with (log_dir / "result.txt").open("w") as f:
        f.write(f"Width: {game.board.width}\n")
        f.write(f"Height: {game.board.height}\n\n")
        f.write(f"n: {len(game.logs)}\n\n")
        f.write(f"True: {np.count_nonzero(game.check_board())}\n")
        f.write(f"False: {np.count_nonzero(~game.check_board())}\n")
        f.write(
            f"True rate: {np.count_nonzero(game.check_board())/(game.board.width*game.board.height):%}"
        )
    with (log_dir / "log.json").open("w") as f:
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
    width = np.random.randint(8, 257)
    height = np.random.randint(8, 257)
    print(width, height)
    game = Game(sample_input, Cell(width, height), None)

    game.rough_arrange()
    game.arrange()

    save_logs(game)


if __name__ == "__main__":
    main()
