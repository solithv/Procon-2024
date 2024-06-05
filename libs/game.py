import json

import numpy as np

from .data import Cell, CuttingInfo, Direction, StaticDieTypes, GameSpecification
from .patterns import Board, CuttingDie


class Game:
    def __init__(self, game_input: dict, debug: Cell = None) -> None:
        """ゲームを管理するクラス

        Args:
            game_input (dict): APIから受け取るデータをdict形式として入力
        """
        self.logs: list[CuttingInfo] = []
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

        self.dies: list[CuttingDie] = []
        self.generate_standard_dies()
        for i, pattern in enumerate(game_input["general"]["patterns"], len(self.dies)):
            self.dies.append(
                CuttingDie(
                    i, pattern["width"], pattern["height"], pattern=pattern["cells"]
                )
            )

        self.full_die = self.get_static_die(
            size=GameSpecification.max_size, type=StaticDieTypes.full
        )

        if debug:
            np.random.seed(0)
            pattern = np.random.randint(0, 3, (debug.y, debug.x))
            self.board = Board(debug.x, debug.y, pattern.copy())
            np.random.shuffle(pattern)
            self.goal = Board(debug.x, debug.y, pattern)

    def generate_standard_dies(self) -> None:
        """定型抜き型を作成"""
        for i in range(9):
            for j in range(3):
                id = 3 * i + j - 2 * bool(i)
                self.dies.append(CuttingDie.make_standard(id=id, size=2**i, type=j + 1))
                if i < 1:
                    break

    def log_to_json(self) -> str:
        """回答フォーマットを作成

        Returns:
            str: JSON形式データ
        """
        return json.dumps(
            {"n": len(self.logs), "ops": [log.dict() for log in self.logs]}
        )

    def check_board(self) -> np.ndarray:
        """現在盤面と最終盤面を比較

        Returns:
            np.ndarray: 一致箇所がTrueのbool map
        """
        return self.board.field == self.goal.field

    @property
    def is_goal(self) -> bool:
        """完成しているか"""
        return self.check_board().all()

    def get_static_die(self, size: int, type: int) -> CuttingDie:
        """定型抜き型を取得

        Args:
            size (int): 縦横のサイズ
            type (int): 抜き型のタイプ(1, 2, 3)

        Returns:
            CuttingDie: 抜き型
        """
        for die in self.dies:
            if die.width == die.height == size and die.type == type:
                return die

    def apply_die(
        self, board: Board, die: CuttingDie, cell: Cell, direction: int
    ) -> None:
        """抜き型を適用

        Args:
            board (Board): 抜き型を適用する対象のboard
            die (CuttingDie): 適用する抜き型
            cell (Cell): 適用する座標
            direction (int): 適用する方向(Directionで定義)
        """
        self.logs.append(board._apply_die(die=die, cell=cell, direction=direction))
        # print(board.field)

    def _swap_edge_horizontal(
        self, board: Board, corner_target: Cell, target: Cell
    ) -> None:
        """横方向に角との2点交換

        Args:
            board (Board): 対象のboard
            corner_target (Cell): 角の座標
            target (Cell): 交換対象の座標

        Returns:
            Board: 適用後のboard
        """

        def get_margin():
            match corner:
                case board.corners.nw:
                    return target.x - corner_target.x - 1
                case board.corners.ne:
                    return corner_target.x - target.x - 1
                case board.corners.sw:
                    return target.x - corner_target.x - 1
                case board.corners.se:
                    return corner_target.x - target.x - 1
                case _:
                    raise ValueError(f"{corner} is not corner cell")

        def get_offset_x():
            match corner:
                case board.corners.nw:
                    return -size
                case board.corners.ne:
                    return 1
                case board.corners.sw:
                    return -size
                case board.corners.se:
                    return 1
                case _:
                    raise ValueError(f"{corner} is not corner cell")

        def get_offset_y():
            match corner:
                case board.corners.nw:
                    return -size + 1
                case board.corners.ne:
                    return -size + 1
                case board.corners.sw:
                    return 0
                case board.corners.se:
                    return 0
                case _:
                    raise ValueError(f"{corner} is not corner cell")

        corner = corner_target.copy()
        corner_target = corner_target.copy()  # id被り対策
        match corner:
            case board.corners.nw:
                direction = Direction.right
            case board.corners.ne:
                direction = Direction.left
            case board.corners.sw:
                direction = Direction.right
            case board.corners.se:
                direction = Direction.left
            case _:
                raise ValueError(
                    f"corner_target must be corner cell but input {corner_target}."
                )

        while margin := get_margin():
            size = int(np.power(2, np.floor(np.log2(margin))))
            self.apply_die(
                board,
                self.get_static_die(size, StaticDieTypes.full),
                Cell(target.x + get_offset_x(), target.y + get_offset_y()),
                direction,
            )
            if direction == Direction.right:
                corner_target.x += size
            else:
                corner_target.x -= size

        size = 1
        self.apply_die(
            board,
            self.get_static_die(size, StaticDieTypes.full),
            Cell(target.x, target.y + get_offset_y()),
            direction,
        )

        return board

    def _swap_edge_vertical(
        self, board: Board, corner_target: Cell, target: Cell
    ) -> None:
        """縦方向に角との2点交換

        Args:
            board (Board): 対象のboard
            corner_target (Cell): 角の座標
            target (Cell): 交換対象の座標

        Returns:
            Board: 適用後のboard
        """

        def get_margin():
            match corner:
                case board.corners.nw:
                    return target.y - corner_target.y - 1
                case board.corners.ne:
                    return target.y - corner_target.y - 1
                case board.corners.sw:
                    return corner_target.y - target.y - 1
                case board.corners.se:
                    return corner_target.y - target.y - 1
                case _:
                    raise ValueError(f"{corner} is not corner cell")

        def get_offset_x():
            match corner:
                case board.corners.nw:
                    return -size + 1
                case board.corners.ne:
                    return 0
                case board.corners.sw:
                    return -size + 1
                case board.corners.se:
                    return 0
                case _:
                    raise ValueError(f"{corner} is not corner cell")

        def get_offset_y():
            match corner:
                case board.corners.nw:
                    return -size
                case board.corners.ne:
                    return -size
                case board.corners.sw:
                    return 1
                case board.corners.se:
                    return 1
                case _:
                    raise ValueError(f"{corner} is not corner cell")

        corner = corner_target.copy()
        corner_target = corner_target.copy()  # id被り対策
        match corner:
            case board.corners.nw:
                direction = Direction.down
            case board.corners.ne:
                direction = Direction.down
            case board.corners.sw:
                direction = Direction.up
            case board.corners.se:
                direction = Direction.up
            case _:
                raise ValueError(
                    f"corner_target must be corner cell but input {corner_target}"
                )

        while margin := get_margin():
            size = int(np.power(2, np.floor(np.log2(margin))))
            self.apply_die(
                board,
                self.get_static_die(size, StaticDieTypes.full),
                Cell(target.x + get_offset_x(), target.y + get_offset_y()),
                direction,
            )
            if direction == Direction.down:
                corner_target.y += size
            else:
                corner_target.y -= size

        size = 1
        self.apply_die(
            board,
            self.get_static_die(size, StaticDieTypes.full),
            Cell(target.x + get_offset_x(), target.y),
            direction,
        )

        return board

    def _swap_edges(self, board: Board, target_1: Cell, target_2: Cell) -> None:
        """角のブロック内で任意の2点を交換

        Args:
            board (Board): 対象のboard
            target_1 (Cell): 交換対象
            target_2 (Cell): 交換対象

        Returns:
            Board: 適用後のboard
        """
        if target_1.x == target_2.x:
            if target_1.y in (0, board.height - 1):
                board = self._swap_edge_vertical(board, target_1, target_2)
                return board
            elif target_2.y in (0, board.height - 1):
                board = self._swap_edge_vertical(board, target_2, target_1)
                return board
            else:
                raise ValueError("non swappable targets")
        elif target_1.y == target_2.y:
            if target_1.x in (0, board.width - 1):
                board = self._swap_edge_horizontal(board, target_1, target_2)
                return board
            elif target_2.x in (0, board.width - 1):
                board = self._swap_edge_horizontal(board, target_2, target_1)
                return board
            else:
                raise ValueError("non swappable targets")

        if target_1.y > target_2.y:
            target_1, target_2 = target_2, target_1

        direction_str = ""
        if target_1 == board.corners.nw and target_2 == board.corners.se:
            direction_str += "n"
        elif min(target_1.y, target_2.y) == 0 and target_2.y != board.height - 1:
            direction_str += "n"
        elif max(target_1.y, target_2.y) == board.height - 1:
            direction_str += "s"
            if target_1.y < target_2.y:
                target_1, target_2 = target_2, target_1
        else:
            raise ValueError

        if target_1.x > target_2.x:
            target_1, target_2 = target_2, target_1
        if min(target_1.x, target_2.x) == 0 and target_2.x != board.width - 1:
            direction_str += "w"
        elif max(target_1.x, target_2.x) == board.width - 1:
            direction_str += "e"
            if target_1.x < target_2.x:
                target_1, target_2 = target_2, target_1
        else:
            raise ValueError

        corner = getattr(board.corners, direction_str)
        board = self._swap_edge_vertical(board, corner, target_1)
        board = self._swap_edge_horizontal(board, corner, target_2)
        board = self._swap_edge_vertical(board, corner, target_1)

        return board

    def _move_to_edge_row(
        self, board: Board, target_row: int, direction: int = Direction.up
    ) -> Board:
        """行を辺に移動

        Args:
            board (Board): 対象のboard
            target_row (int): 辺に移動させたい行のindex
            direction (int, optional): 移動方向(up or down). Defaults to Direction.up.

        Returns:
            Board: 適用後のboard
        """
        match direction:
            case Direction.up:
                if (
                    -self.full_die.height
                    < target_row - self.full_die.height
                    < self.board.height
                ):
                    self.apply_die(
                        board,
                        self.full_die,
                        Cell(x=0, y=target_row - self.full_die.height),
                        direction,
                    )
            case Direction.down:
                if 0 < target_row + 1 < self.board.height:
                    self.apply_die(
                        board,
                        self.full_die,
                        Cell(x=0, y=target_row + 1),
                        direction,
                    )
            case _:
                raise ValueError("unsupported direction")
        return board

    def _move_to_edge_column(
        self, board: Board, target_column: int, direction: int = Direction.left
    ) -> Board:
        """列を辺に移動

        Args:
            board (Board): 対象のboard
            target_column (int): 辺に移動させたい列のindex
            direction (int, optional): 移動方向(left or right). Defaults to Direction.left.

        Returns:
            Board: 適用後のboard
        """
        match direction:
            case Direction.left:
                if (
                    -self.full_die.width
                    < target_column - self.full_die.width
                    < self.board.width
                ):
                    self.apply_die(
                        board,
                        self.full_die,
                        Cell(x=target_column - self.full_die.width, y=0),
                        direction,
                    )
            case Direction.right:
                if 0 < target_column + 1 < self.board.width:
                    self.apply_die(
                        board,
                        self.full_die,
                        Cell(x=target_column + 1, y=0),
                        direction,
                    )
            case _:
                raise ValueError("unsupported direction")

        return board

    def swap(self, board: Board, target_1: Cell, target_2: Cell) -> Board:
        """任意の2点を交換

        Args:
            board (Board): 対象のboard
            target_1 (Cell): 交換対象
            target_2 (Cell): 交換対象

        Returns:
            Board: 適用後のboard
        """
        block_size = max(abs(target_1.x - target_2.x), abs(target_1.y - target_2.y))
        block_size = int(np.power(2, np.ceil(np.log2(block_size))))

        if np.sign(target_1.x - target_2.x) != np.sign(target_1.y - target_2.y):
            if (
                np.array([target_1.y, target_2.y]).mean()
                < board.height
                - (board.width / board.height)
                * np.array([target_1.x, target_2.x]).mean()
            ):
                # NW
                block_cell = Cell(
                    x=min(target_1.x, target_2.x), y=min(target_1.y, target_2.y)
                )
                board = self._move_to_edge_row(board, block_cell.y)
                board = self._move_to_edge_column(board, block_cell.x)
                board = self._swap_edges(
                    board,
                    Cell(x=target_1.x - block_cell.x, y=target_1.y - block_cell.y),
                    Cell(x=target_2.x - block_cell.x, y=target_2.y - block_cell.y),
                )
                board = self._move_to_edge_column(
                    board, board.width - block_cell.x - 1, Direction.right
                )
                board = self._move_to_edge_row(
                    board, board.height - block_cell.y - 1, Direction.down
                )
            else:
                # SE
                block_cell = Cell(
                    x=max(target_1.x, target_2.x), y=max(target_1.y, target_2.y)
                )
                board = self._move_to_edge_row(board, block_cell.y, Direction.down)
                board = self._move_to_edge_column(board, block_cell.x, Direction.right)
                board = self._swap_edges(
                    board,
                    Cell(
                        x=board.width - (block_cell.x + 1) + target_1.x,
                        y=target_1.y + board.height - (block_cell.y + 1),
                    ),
                    Cell(
                        x=board.width - (block_cell.x + 1) + target_2.x,
                        y=target_2.y + board.height - (block_cell.y + 1),
                    ),
                )
                board = self._move_to_edge_column(board, board.width - block_cell.x - 1)
                board = self._move_to_edge_row(board, board.height - block_cell.y + 1)
        else:
            if (
                np.array([target_1.y, target_2.y]).mean()
                >= (board.width / board.height)
                * np.array([target_1.x, target_2.x]).mean()
            ):
                # NE
                block_cell = Cell(
                    x=max(target_1.x, target_2.x), y=min(target_1.y, target_2.y)
                )
                board = self._move_to_edge_row(board, block_cell.y)
                board = self._move_to_edge_column(board, block_cell.x, Direction.right)
                board = self._swap_edges(
                    board,
                    Cell(
                        x=board.width - (block_cell.x + 1) + target_1.x,
                        y=target_1.y - block_cell.y,
                    ),
                    Cell(
                        x=board.width - (block_cell.x + 1) + target_2.x,
                        y=target_2.y - block_cell.y,
                    ),
                )
                board = self._move_to_edge_column(board, board.width - block_cell.x - 1)
                board = self._move_to_edge_row(
                    board, board.height - block_cell.y - 1, Direction.down
                )
            else:
                # SW
                block_cell = Cell(
                    x=min(target_1.x, target_2.x), y=max(target_1.y, target_2.y)
                )
                board = self._move_to_edge_row(board, block_cell.y, Direction.down)
                board = self._move_to_edge_column(board, block_cell.x)
                board = self._swap_edges(
                    board,
                    Cell(
                        x=target_1.x - block_cell.x,
                        y=target_1.y + board.height - (block_cell.y + 1),
                    ),
                    Cell(
                        x=target_2.x - block_cell.x,
                        y=target_2.y + board.height - (block_cell.y + 1),
                    ),
                )
                board = self._move_to_edge_column(
                    board, board.width - block_cell.x - 1, Direction.right
                )
                board = self._move_to_edge_row(board, board.height - (block_cell.y + 1))

        return board

    def arrange_edge(self, board: Board, target: Board, edge: int):
        mask = board.field == target.field
        match edge:
            case Direction.up:
                for x, goal in enumerate(target.field[0]):
                    if ~mask[0, x]:
                        swap_target_cells = np.argwhere(
                            ~mask[0] & (board.field[0] == goal)
                        ).flatten()
                        for target_x in swap_target_cells:
                            board = self.swap(board, Cell(x, 0), Cell(int(target_x), 0))
                            mask = board.field == target.field
                            break
            case Direction.down:
                raise NotImplementedError
            case Direction.left:
                for y, goal in enumerate(target.field[:, 0]):
                    if ~mask[y, 0]:
                        swap_target_cells = np.argwhere(
                            ~mask[:, 0] & (board.field[:, 0] == goal)
                        ).flatten()
                        for target_y in swap_target_cells:
                            board = self.swap(board, Cell(0, y), Cell(0, int(target_y)))
                            mask = board.field == target.field
                            break
            case Direction.right:
                raise NotImplementedError

        return board
