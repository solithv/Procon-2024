import json
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import ray

from libs import Cell, Game
from libs.network import API

ray.init(num_cpus=os.cpu_count() - 2)


@dataclass
class DebugConfig:
    size: Cell
    seed: int | None = None


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


def main(input_json: str | Path | dict, debug_config: DebugConfig | None = None):
    if isinstance(input_json, (str, Path)):
        with open(input_json) as f:
            input_json = json.load(f)

    if debug_config is None:
        game = Game(input_json)
    else:
        game = Game(input_json, debug=debug_config.size, debug_seed=debug_config.seed)
    dump_initialize(game)

    game.main()

    save_logs(game)


def reproduce(input_: str | Path | dict, output: str | Path | dict):
    if isinstance(input_, (str, Path)):
        with open(input_, "r") as f:
            input_ = json.load(f)
    game = Game(input_)

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


def with_server():
    api = API()
    input_problem = api.get_problem()
    print(input_problem)
    game = Game(input_problem)

    dump_initialize(game)

    game.rough_arrange()
    game.arrange()

    response = api.post_answer(game.format_log())
    print(response)
    save_logs(game)


if __name__ == "__main__":
    sample_input = {
        "board": {
            "width": 6,
            "height": 4,
            "start": ["220103", "213033", "022103", "322033"],
            "goal": ["000000", "111222", "222233", "333333"],
        },
        # "board": {
        #     "width": 6,
        #     "height": 6,
        #     "start": ["012345", "123450", "234501", "345012", "450123", "501234"],
        #     "goal": ["000000", "111222", "222233", "333333", "012345", "012345"],
        # },
        "general": {
            "n": 2,
            "patterns": [
                {"p": 25, "width": 4, "height": 2, "cells": ["0111", "1001"]},
                {"p": 26, "width": 2, "height": 2, "cells": ["10", "01"]},
            ],
        },
    }
    debug_config = DebugConfig(
        # size=Cell(x=np.random.randint(8, 257), y=np.random.randint(8, 257))
        # size=Cell(x=8, y=8)
        size=Cell(x=128, y=128)
    )

    # main(sample_input, debug_config=debug_config)
    main("./logs/dump.json")
    # reproduce("./logs/dump.json", "./logs/log.json")
    # with_server()

    # game = Game(sample_input)
    # print(game.board.field)
