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
            f"True rate: {np.count_nonzero(game.check_board())/game.board.field.size:%}"
        )
    with (log_dir / "log.json").open("w") as f:
        json.dump(game.format_log(), f, indent=2)


def dump_initialize(game: Game, log_dir: str | Path = "./logs"):
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    initialize = {
        "board": {
            "width": game.board.width,
            "height": game.board.height,
            "start": ["".join(map(str, row)) for row in game.board.field],
            "goal": ["".join(map(str, row)) for row in game.goal.field],
        },
        "general": {
            "n": len(game.dies) - 25,
            "patterns": [
                {
                    "p": pattern.id,
                    "width": pattern.width,
                    "height": pattern.height,
                    "cells": [
                        "".join(map(str, row)) for row in pattern.field.astype(int)
                    ],
                }
                for pattern in game.dies[25:]
            ],
        },
    }
    with (log_dir / "dump.json").open("w") as f:
        json.dump(initialize, f, indent=2)


def main():
    sample_input = {
        "board": {
            "width": 6,
            "height": 4,
            "start": ["220103", "213033", "022103", "322033"],
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
    # width = 8
    # height = 8
    print(width, height)
    seed = None
    game = Game(sample_input, Cell(width, height), seed)
    dump_initialize(game)

    game.rough_arrange()
    game.arrange()

    save_logs(game)


def reproduce(input: str | Path | dict, output: str | Path | dict):
    if isinstance(input, (str, Path)):
        with open(input, "r") as f:
            input = json.load(f)
    game = Game(input)

    if isinstance(output, (str, Path)):
        with open(output, "r") as f:
            output = json.load(f)
    [
        game.apply_die(
            game.board, game.dies[info["p"]], Cell(info["x"], info["y"]), info["s"]
        )
        for info in output["ops"]
    ]

    save_logs(game, "./reproduce")


if __name__ == "__main__":
    main()
    reproduce("./logs/dump.json", "./logs/log.json")
