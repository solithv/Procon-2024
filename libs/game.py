import json

import numpy as np

from .data import Cell, CuttingInfo, Direction, StaticDieTypes, GameSpecification
from .patterns import Board, CuttingDie


class Game:
    def __init__(
        self, game_input: dict, debug: Cell = None, debug_seed: int = 0
    ) -> None:
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
            size=GameSpecification.MAX_SIZE, type=StaticDieTypes.FULL
        )

        if debug:
            np.random.seed(debug_seed)
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

    def format_log(self) -> dict:
        """回答フォーマットを作成

        Returns:
            dict: JSON形式データ
        """
        return {"n": len(self.logs), "ops": [log.dict() for log in self.logs]}

    def log_to_json(self) -> str:
        """回答フォーマットを作成

        Returns:
            str: JSON形式データ
        """
        return json.dumps(self.format_log())

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
                direction = Direction.RIGHT
            case board.corners.ne:
                direction = Direction.LEFT
            case board.corners.sw:
                direction = Direction.RIGHT
            case board.corners.se:
                direction = Direction.LEFT
            case _:
                raise ValueError(
                    f"corner_target must be corner cell but input {corner_target}."
                )

        while margin := get_margin():
            size = int(np.power(2, np.floor(np.log2(margin))))
            self.apply_die(
                board,
                self.get_static_die(size, StaticDieTypes.FULL),
                Cell(target.x + get_offset_x(), target.y + get_offset_y()),
                direction,
            )
            if direction == Direction.RIGHT:
                corner_target.x += size
            else:
                corner_target.x -= size

        size = 1
        self.apply_die(
            board,
            self.get_static_die(size, StaticDieTypes.FULL),
            Cell(target.x, target.y + get_offset_y()),
            direction,
        )

    def _swap_edge_vertical(
        self, board: Board, corner_target: Cell, target: Cell
    ) -> None:
        """縦方向に角との2点交換

        Args:
            board (Board): 対象のboard
            corner_target (Cell): 角の座標
            target (Cell): 交換対象の座標
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
                direction = Direction.DOWN
            case board.corners.ne:
                direction = Direction.DOWN
            case board.corners.sw:
                direction = Direction.UP
            case board.corners.se:
                direction = Direction.UP
            case _:
                raise ValueError(
                    f"corner_target must be corner cell but input {corner_target}"
                )

        while margin := get_margin():
            size = int(np.power(2, np.floor(np.log2(margin))))
            self.apply_die(
                board,
                self.get_static_die(size, StaticDieTypes.FULL),
                Cell(target.x + get_offset_x(), target.y + get_offset_y()),
                direction,
            )
            if direction == Direction.DOWN:
                corner_target.y += size
            else:
                corner_target.y -= size

        size = 1
        self.apply_die(
            board,
            self.get_static_die(size, StaticDieTypes.FULL),
            Cell(target.x + get_offset_x(), target.y),
            direction,
        )

    def _swap_edges(
        self, board: Board, corner: Cell, target_1: Cell, target_2: Cell
    ) -> None:
        """角のブロック内で任意の2点を交換

        Args:
            board (Board): 対象のboard
            target_1 (Cell): 交換対象
            target_2 (Cell): 交換対象
        """
        if target_1.x == target_2.x:
            if target_1.y in (0, board.height - 1):
                self._swap_edge_vertical(board, target_1, target_2)
                return
            elif target_2.y in (0, board.height - 1):
                self._swap_edge_vertical(board, target_2, target_1)
                return
            else:
                raise ValueError("non swappable targets")
        elif target_1.y == target_2.y:
            if target_1.x in (0, board.width - 1):
                self._swap_edge_horizontal(board, target_1, target_2)
                return
            elif target_2.x in (0, board.width - 1):
                self._swap_edge_horizontal(board, target_2, target_1)
                return
            else:
                raise ValueError("non swappable targets")

        if target_1.y > target_2.y:
            target_1, target_2 = target_2, target_1
        if not (target_1.y == 0 and target_2.x in (0, board.width - 1)) and not (
            target_2.y == board.height - 1 and target_1.x in (0, board.width - 1)
        ):
            raise ValueError(f"targets are not in corner block: {target_1}, {target_2}")

        if corner.y == target_1.y:
            target_1, target_2 = target_2, target_1
        self._swap_edge_vertical(board, corner, target_1)
        self._swap_edge_horizontal(board, corner, target_2)
        self._swap_edge_vertical(board, corner, target_1)

    def _move_to_edge_row(self, board: Board, target_row: int, direction: int) -> None:
        """行を辺に移動

        Args:
            board (Board): 対象のboard
            target_row (int): 辺に移動させたい行のindex
            direction (int): 移動方向(up or down)
        """
        match direction:
            case Direction.UP:
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
            case Direction.DOWN:
                if 0 < target_row + 1 < self.board.height:
                    self.apply_die(
                        board,
                        self.full_die,
                        Cell(x=0, y=target_row + 1),
                        direction,
                    )
            case _:
                raise ValueError("unsupported direction")

    def _move_to_edge_column(
        self, board: Board, target_column: int, direction: int
    ) -> None:
        """列を辺に移動

        Args:
            board (Board): 対象のboard
            target_column (int): 辺に移動させたい列のindex
            direction (int): 移動方向(left or right)
        """
        match direction:
            case Direction.LEFT:
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
            case Direction.RIGHT:
                if 0 < target_column + 1 < self.board.width:
                    self.apply_die(
                        board,
                        self.full_die,
                        Cell(x=target_column + 1, y=0),
                        direction,
                    )
            case _:
                raise ValueError("unsupported direction")

    def swap(self, board: Board, target_1: Cell, target_2: Cell) -> None:
        """任意の2点を交換

        Args:
            board (Board): 対象のboard
            target_1 (Cell): 交換対象
            target_2 (Cell): 交換対象
        """

        def nw():
            block_cell = Cell(
                x=min(target_1.x, target_2.x), y=min(target_1.y, target_2.y)
            )
            self._move_to_edge_row(board, block_cell.y, Direction.UP)
            self._move_to_edge_column(board, block_cell.x, Direction.LEFT)
            self._swap_edges(
                board,
                board.corners.nw,
                Cell(x=target_1.x - block_cell.x, y=target_1.y - block_cell.y),
                Cell(x=target_2.x - block_cell.x, y=target_2.y - block_cell.y),
            )
            self._move_to_edge_column(
                board, board.width - block_cell.x - 1, Direction.RIGHT
            )
            self._move_to_edge_row(
                board, board.height - block_cell.y - 1, Direction.DOWN
            )

        def se():
            block_cell = Cell(
                x=max(target_1.x, target_2.x), y=max(target_1.y, target_2.y)
            )
            self._move_to_edge_row(board, block_cell.y, Direction.DOWN)
            self._move_to_edge_column(board, block_cell.x, Direction.RIGHT)
            self._swap_edges(
                board,
                board.corners.se,
                Cell(
                    x=board.width - (block_cell.x + 1) + target_1.x,
                    y=target_1.y + board.height - (block_cell.y + 1),
                ),
                Cell(
                    x=board.width - (block_cell.x + 1) + target_2.x,
                    y=target_2.y + board.height - (block_cell.y + 1),
                ),
            )
            self._move_to_edge_column(
                board, board.width - block_cell.x - 1, Direction.LEFT
            )
            self._move_to_edge_row(
                board, board.height - (block_cell.y + 1), Direction.UP
            )

        def ne():
            block_cell = Cell(
                x=max(target_1.x, target_2.x), y=min(target_1.y, target_2.y)
            )
            self._move_to_edge_row(board, block_cell.y, Direction.UP)
            self._move_to_edge_column(board, block_cell.x, Direction.RIGHT)
            self._swap_edges(
                board,
                board.corners.ne,
                Cell(
                    x=board.width - (block_cell.x + 1) + target_1.x,
                    y=target_1.y - block_cell.y,
                ),
                Cell(
                    x=board.width - (block_cell.x + 1) + target_2.x,
                    y=target_2.y - block_cell.y,
                ),
            )
            self._move_to_edge_column(
                board, board.width - block_cell.x - 1, Direction.LEFT
            )
            self._move_to_edge_row(
                board, board.height - block_cell.y - 1, Direction.DOWN
            )

        def sw():
            block_cell = Cell(
                x=min(target_1.x, target_2.x), y=max(target_1.y, target_2.y)
            )
            self._move_to_edge_row(board, block_cell.y, Direction.DOWN)
            self._move_to_edge_column(board, block_cell.x, Direction.LEFT)
            self._swap_edges(
                board,
                board.corners.sw,
                Cell(
                    x=target_1.x - block_cell.x,
                    y=target_1.y + board.height - (block_cell.y + 1),
                ),
                Cell(
                    x=target_2.x - block_cell.x,
                    y=target_2.y + board.height - (block_cell.y + 1),
                ),
            )
            self._move_to_edge_column(
                board, board.width - block_cell.x - 1, Direction.RIGHT
            )
            self._move_to_edge_row(
                board, board.height - (block_cell.y + 1), Direction.UP
            )

        block_size = max(abs(target_1.x - target_2.x), abs(target_1.y - target_2.y))
        block_size = int(np.power(2, np.ceil(np.log2(block_size))))

        if np.sign(target_1.x - target_2.x) != np.sign(target_1.y - target_2.y):
            if target_1.x < target_2.x and target_1.y > target_2.y:
                target_1, target_2 = target_2, target_1

            if target_1.x == board.width - 1 and target_2.y == board.height - 1:
                se()
            elif (
                target_1 not in board.corners.members()
                or target_2.y != board.height - 1
            ):
                nw()
            else:
                se()
        else:
            if target_1.x > target_2.x and target_1.y > target_2.y:
                target_1, target_2 = target_2, target_1

            if target_1.y == 0 and target_2.x == board.width - 1:
                ne()
            elif target_1.x == 0 and target_2.y == board.height - 1:
                sw()
            elif (
                target_1 not in board.corners.members()
                or target_2.y != board.height - 1
            ):
                ne()
            else:
                sw()

    def arrange_edge(self, board: Board, target: Board, edge: int) -> None:
        """辺を対象に揃える

        Args:
            board (Board): 対象のboard
            target (Board): 目的の状態
            edge (int): 揃える辺
        """
        mask = board.field == target.field
        match edge:
            case Direction.UP:
                for x, goal in enumerate(target.field[0]):
                    if ~mask[0, x]:
                        swap_target_cells = np.argwhere(
                            ~mask[0]
                            & (board.field[0] == goal)
                            & (board.field[0, x] == target.field[0])
                        ).flatten()
                        if not swap_target_cells:
                            swap_target_cells = np.argwhere(
                                ~mask[0]
                                & (board.field[0] == goal)
                                & (board.field[0, x] != target.field[0])
                            ).flatten()
                        for target_x in swap_target_cells:
                            self.swap(board, Cell(x, 0), Cell(int(target_x), 0))
                            mask = board.field == target.field
                            break
            case Direction.DOWN:
                for x, goal in enumerate(target.field[-1]):
                    if ~mask[-1, x]:
                        swap_target_cells = np.argwhere(
                            ~mask[-1]
                            & (board.field[-1] == goal)
                            & (board.field[-1, x] == target.field[-1])
                        ).flatten()
                        if not swap_target_cells:
                            swap_target_cells = np.argwhere(
                                ~mask[-1]
                                & (board.field[-1] == goal)
                                & (board.field[-1, x] != target.field[-1])
                            ).flatten()
                        for target_x in swap_target_cells:
                            self.swap(
                                board,
                                Cell(x, board.height - 1),
                                Cell(int(target_x), board.height - 1),
                            )
                            mask = board.field == target.field
                            break
            case Direction.LEFT:
                for y, goal in enumerate(target.field[:, 0]):
                    if ~mask[y, 0]:
                        swap_target_cells = np.argwhere(
                            ~mask[:, 0]
                            & (board.field[:, 0] == goal)
                            & (board.field[y, 0] == target.field[:, 0])
                        ).flatten()
                        if not swap_target_cells:
                            swap_target_cells = np.argwhere(
                                ~mask[:, 0]
                                & (board.field[:, 0] == goal)
                                & (board.field[y, 0] != target.field[:, 0])
                            ).flatten()
                        for target_y in swap_target_cells:
                            self.swap(board, Cell(0, y), Cell(0, int(target_y)))
                            mask = board.field == target.field
                            break
            case Direction.RIGHT:
                for y, goal in enumerate(target.field[:, -1]):
                    if ~mask[y, -1]:
                        swap_target_cells = np.argwhere(
                            ~mask[:, -1]
                            & (board.field[:, -1] == goal)
                            & (board.field[y, -1] == target.field[:, -1])
                        ).flatten()
                        if not swap_target_cells:
                            swap_target_cells = np.argwhere(
                                ~mask[:, -1]
                                & (board.field[:, -1] == goal)
                                & (board.field[y, -1] != target.field[:, -1])
                            ).flatten()
                        for target_y in swap_target_cells:
                            self.swap(
                                board,
                                Cell(board.width - 1, y),
                                Cell(board.width - 1, int(target_y)),
                            )
                            mask = board.field == target.field
                            break

    def arrange_rows(self) -> None:
        """行単位で揃える"""
        target = self.goal.copy()
        for _ in range(self.board.height // 2):
            self.arrange_edge(self.board, target, edge=Direction.UP)
            self.arrange_edge(self.board, target, edge=Direction.DOWN)
            self._move_to_edge_row(self.board, 2, Direction.UP)
            self._move_to_edge_row(target, 2, Direction.UP)
        if self.board.height % 2:
            self._move_to_edge_row(self.board, 1, Direction.UP)
            self._move_to_edge_row(target, 1, Direction.UP)

    def arrange_columns(self) -> None:
        """列単位で揃える"""
        target = self.goal.copy()
        for _ in range(self.board.width // 2):
            self.arrange_edge(self.board, target, edge=Direction.LEFT)
            self.arrange_edge(self.board, target, edge=Direction.RIGHT)
            self._move_to_edge_column(self.board, 2, Direction.LEFT)
            self._move_to_edge_column(target, 2, Direction.LEFT)
        if self.board.width % 2:
            self._move_to_edge_column(self.board, 1, Direction.LEFT)
            self._move_to_edge_column(target, 1, Direction.LEFT)

    def rough_arrange(self, limit: int = None) -> None:
        """行列単位で揃える

        Args:
            limit (int, optional): 試行回数の上限. Defaults to None.
        """
        count = 0
        while limit is None or count < limit:
            previous = self.board.field.copy()
            self.arrange_rows()
            self.arrange_columns()
            if (previous == self.board.field).all():
                return
            count += 1

    def arrange(self) -> None:
        """揃える"""
        while not self.check_board().all():
            mask = self.check_board()
            target = np.argwhere(~mask)[0]
            swap_targets = np.argwhere(
                ~mask & (self.board.field[*target] == self.goal.field)
            )
            if not swap_targets:
                swap_targets = np.argwhere(~mask)
            for y, x in swap_targets:
                self.swap(self.board, Cell(*target[::-1]), Cell(x, y))
                break
