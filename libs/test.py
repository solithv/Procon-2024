from .data import Cell
from .game import Game


def swap_test(game: Game):
    for x_1 in range(game.board.width):
        for y_1 in range(game.board.height):
            for x_2 in range(game.board.width):
                for y_2 in range(game.board.height):
                    if x_1 == x_2 and y_1 == y_2:
                        continue
                    previous = game.board.field.copy()
                    cell_1 = Cell(x_1, y_1)
                    cell_2 = Cell(x_2, y_2)
                    try:
                        game.swap(game.board, cell_1, cell_2)
                    except Exception as e:
                        print(f"error occurred with: {cell_1} and {cell_2}")
                        raise e
                    assert (
                        previous[y_1, x_1] == game.board.field[y_2, x_2]
                    ), f"swap failed at {cell_1}, {cell_2}"
                    assert (
                        previous[y_2, x_2] == game.board.field[y_1, x_1]
                    ), f"swap failed at {cell_1}, {cell_2}"
                    diff = previous == game.board.field
                    if previous[y_1, x_1] == previous[y_2, x_2]:
                        assert diff.all(), f"swap broken at {cell_1}, {cell_2}"
                    else:
                        assert ~diff[y_1, x_1], diff
                        assert ~diff[y_2, x_2], diff
                        diff[y_1, x_1] = ~diff[y_1, x_1]
                        diff[y_2, x_2] = ~diff[y_2, x_2]
                        assert diff.all(), f"swap broken at {cell_1}, {cell_2}"
