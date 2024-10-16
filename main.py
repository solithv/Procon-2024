from datetime import datetime
import json
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import ray

from libs import Cell, Game
from libs.arg_parse import parser
from libs.network import API


@dataclass
class DebugConfig:
    size: Cell
    seed: int | None = None


ray.init(num_cpus=os.cpu_count() - 2)


def save_logs(game: Game, log_dir: str | Path = "./logs"):
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(log_dir / "board.txt", game.board.field, "%d")
    np.savetxt(log_dir / "goal.txt", game.goal.field, "%d")
    # np.savetxt(log_dir / "result_map.txt", game.check_board(), "%d")
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


def offline(
    input_json: str | Path | dict,
    log_dir: str | Path = "./logs",
    debug_config: DebugConfig | None = None,
):
    log_dir = Path(log_dir, str(datetime.now()))
    if isinstance(input_json, (str, Path)):
        with open(input_json) as f:
            input_json = json.load(f)

    if debug_config is None:
        game = Game(input_json)
    else:
        game = Game(input_json, debug=debug_config.size, debug_seed=debug_config.seed)
    dump_initialize(game, log_dir)

    game.main()

    save_logs(game, log_dir)


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


def online(retry: int, interval: float, log_dir: str | Path = "./logs"):
    log_dir = Path(log_dir, str(datetime.now()))
    api = API()
    input_problem = api.get_problem(retry, interval)
    print(input_problem)
    game = Game(input_problem)

    dump_initialize(game, log_dir)

    print("start resolving...")
    game.main()

    response = api.post_answer(game.format_log(), retry, interval)
    print(response)
    save_logs(game, log_dir)


def main():
    args = parser.parse_args()
    if args.debug:
        game_input = args.json
        debug_config = None
        if args.force or not game_input:
            x = args.width or np.random.randint(8, 257)
            y = args.height or np.random.randint(8, 257)
            debug_config = DebugConfig(size=Cell(x=x, y=y), seed=args.seed)
        if not game_input:
            game_input = {
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

        offline(game_input, args.log, debug_config)

    else:
        online(args.retry, args.interval, args.log)


if __name__ == "__main__":
    main()
