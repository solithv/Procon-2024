from libs import Game, PunchingDie, Direction


def main():
    board_input = {
        "width": 6,
        "height": 4,
        "start": ["220103", "213033", "022103", "322033"],
        "goal": ["000000", "111222", "222233", "333333"],
    }
    game = Game(
        board_input["width"],
        board_input["height"],
        board_input["start"],
        board_input["goal"],
    )

    die = PunchingDie(4, 2, ["1111", "1111"])
    game.board.apply_die(die, 1, 1, Direction.left)


if __name__ == "__main__":
    main()
