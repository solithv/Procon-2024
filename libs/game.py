import json

import numpy as np

from .data import Cell, CuttingInfo, Direction, StaticDieTypes, GameSpecification
from .patterns import Board, CuttingDie


class Game:
    def __init__(
        self, game_input: dict, debug: Cell = None, debug_seed: int = None
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
        standard_dies_count = len(self.dies)
        for pattern in game_input["general"]["patterns"]:
            self.dies.append(
                CuttingDie(
                    pattern["p"],
                    pattern["width"],
                    pattern["height"],
                    pattern=pattern["cells"],
                )
            )
        assert len(self.dies) - standard_dies_count == game_input["general"]["n"]

        self.full_die = self.get_static_die(
            size=GameSpecification.MAX_SIZE, type=StaticDieTypes.FULL
        )
        self.full_even_row = self.get_static_die(
            size=GameSpecification.MAX_SIZE, type=StaticDieTypes.EVEN_ROW
        )
        self.full_even_colum = self.get_static_die(
            size=GameSpecification.MAX_SIZE, type=StaticDieTypes.EVEN_COLUMN
        )

        if debug:
            np.random.seed(debug_seed)
            pattern = np.random.randint(0, 4, (debug.y, debug.x))
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
        log = board._apply_die(die=die, cell=cell, direction=direction)
        if board is self.board:
            self.logs.append(log)
        # print(board.field)

    def decompose_to_powers_of_two(self, x: int) -> list[int]:
        """入力を2^nの和に分解

        Args:
            x (int): 入力値

        Returns:
            list[int]: 分解結果(降順)
        """
        result = []
        power = 0
        while x > 0:
            if x & 1:
                result.append(2**power)
            x >>= 1
            power += 1

        return result[::-1]

    def _swap_edge_fixed_turn(self, board: Board, corner: Cell, target: Cell):
        """確定4手で角と直線上2点交換

        Args:
            board (Board): ボード
            corner (Cell): 角
            target (Cell): 交換対象
        """

        def _vertical():
            if board.corners.is_n(corner):
                direction = Direction.DOWN
                _, _target = self._line_move_to_corner_vertical(
                    board, corner, Cell(target.x, target.y + 1)
                )
                self.apply_die(
                    board,
                    self.get_static_die(1, StaticDieTypes.FULL),
                    Cell(_target.x, _target.y + 1),
                    direction,
                )
                _, _target = self._line_move_to_corner_vertical(
                    board, corner, Cell(_target.x, _target.y + 2)
                )
                self.apply_die(
                    board,
                    self.get_static_die(1, StaticDieTypes.FULL),
                    _target,
                    direction,
                )
            else:
                direction = Direction.UP
                _, _target = self._line_move_to_corner_vertical(
                    board, corner, Cell(target.x, target.y - 1)
                )
                self.apply_die(
                    board,
                    self.get_static_die(1, StaticDieTypes.FULL),
                    Cell(_target.x, _target.y - 1),
                    direction,
                )
                _, _target = self._line_move_to_corner_vertical(
                    board, corner, Cell(_target.x, _target.y - 2)
                )
                self.apply_die(
                    board,
                    self.get_static_die(1, StaticDieTypes.FULL),
                    _target,
                    direction,
                )

        def _horizontal():
            if board.corners.is_w(corner):
                direction = Direction.RIGHT
                _, _target = self._line_move_to_corner_horizontal(
                    board, corner, Cell(target.x + 1, target.y)
                )
                self.apply_die(
                    board,
                    self.get_static_die(1, StaticDieTypes.FULL),
                    Cell(_target.x + 1, _target.y),
                    direction,
                )
                _, _target = self._line_move_to_corner_horizontal(
                    board, corner, Cell(_target.x + 2, _target.y)
                )
                self.apply_die(
                    board,
                    self.get_static_die(1, StaticDieTypes.FULL),
                    _target,
                    direction,
                )
            else:
                direction = Direction.LEFT
                _, _target = self._line_move_to_corner_horizontal(
                    board, corner, Cell(target.x - 1, target.y)
                )
                self.apply_die(
                    board,
                    self.get_static_die(1, StaticDieTypes.FULL),
                    Cell(_target.x - 1, _target.y),
                    direction,
                )
                _, _target = self._line_move_to_corner_horizontal(
                    board, corner, Cell(_target.x - 2, _target.y)
                )
                self.apply_die(
                    board,
                    self.get_static_die(1, StaticDieTypes.FULL),
                    _target,
                    direction,
                )

        if corner.x == target.x:
            _vertical()
        elif corner.y == target.y:
            _horizontal()
        else:
            raise ValueError(f"{corner=} and {target=} are not on a line")

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
            if board.corners.is_w(corner):
                return target.x - corner_target.x - 1
            elif board.corners.is_e(corner):
                return corner_target.x - target.x - 1
            else:
                raise ValueError(f"{corner} is not corner cell")

        def get_offset_x():
            if board.corners.is_w(corner):
                return -size
            elif board.corners.is_e(corner):
                return 1
            else:
                raise ValueError(f"{corner} is not corner cell")

        def get_offset_y():
            if board.corners.is_n(corner):
                return -size + 1
            elif board.corners.is_s(corner):
                return 0
            else:
                raise ValueError(f"{corner} is not corner cell")

        corner = corner_target.copy()
        corner_target = corner_target.copy()  # id被り対策
        if board.corners.is_w(corner):
            direction = Direction.RIGHT
        elif board.corners.is_e(corner):
            direction = Direction.LEFT
        else:
            raise ValueError(
                f"corner_target must be corner cell but input {corner_target}."
            )

        margins = self.decompose_to_powers_of_two(get_margin())
        if len(margins) < 4:
            for size in margins:
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
        else:
            self._swap_edge_fixed_turn(board, corner, target)

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
            if board.corners.is_n(corner):
                return target.y - corner_target.y - 1
            elif board.corners.is_s(corner):
                return corner_target.y - target.y - 1
            else:
                raise ValueError(f"{corner} is not corner cell")

        def get_offset_x():
            if board.corners.is_w(corner):
                return -size + 1
            elif board.corners.is_e(corner):
                return 0
            else:
                raise ValueError(f"{corner} is not corner cell")

        def get_offset_y():
            if board.corners.is_n(corner):
                return -size
            elif board.corners.is_s(corner):
                return 1
            else:
                raise ValueError(f"{corner} is not corner cell")

        corner = corner_target.copy()
        corner_target = corner_target.copy()  # id被り対策
        if board.corners.is_n(corner):
            direction = Direction.DOWN
        elif board.corners.is_s(corner):
            direction = Direction.UP
        else:
            raise ValueError(
                f"corner_target must be corner cell but input {corner_target}"
            )

        margins = self.decompose_to_powers_of_two(get_margin())
        if len(margins) < 4:
            for size in margins:
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
        else:
            self._swap_edge_fixed_turn(board, corner, target)

    def _line_move_to_corner_vertical(
        self, board: Board, corner: Cell, target: Cell
    ) -> tuple[Cell, Cell]:
        """縦方向に対象が角に移動するように列を移動

        Args:
            board (Board): 対象のBoard
            corner (Cell): 移動先の角
            target (Cell): 角に移動させるCell

        Returns:
            tuple[Cell, Cell]: 逆操作のためのcorner, target
        """
        assert corner.x == target.x
        x = (
            corner.x - self.full_die.width + 1
            if board.corners.is_w(corner)
            else corner.x
        )
        restore_target = Cell(target.x, board.height - target.y - 1)
        if board.corners.is_n(corner):
            y = target.y - self.full_die.height
            self.apply_die(board, self.full_die, Cell(x, y), Direction.UP)
            restore_corner = Cell(corner.x, board.corners.s)
        elif board.corners.is_s(corner):
            y = target.y + 1
            self.apply_die(board, self.full_die, Cell(x, y), Direction.DOWN)
            restore_corner = Cell(corner.x, board.corners.n)
        else:
            raise ValueError(f"{corner=} is not corner cell.")
        return restore_corner, restore_target

    def _line_move_to_corner_horizontal(self, board: Board, corner: Cell, target: Cell):
        """横方向に対象が角に移動するように行を移動

        Args:
            board (Board): 対象のBoard
            corner (Cell): 移動先の角
            target (Cell): 角に移動させるCell

        Returns:
            tuple[Cell, Cell]: 逆操作のためのcorner, target
        """
        assert corner.y == target.y
        y = (
            corner.y - self.full_die.height + 1
            if board.corners.is_n(corner)
            else corner.y
        )
        restore_target = Cell(board.width - target.x - 1, corner.y)
        if board.corners.is_w(corner):
            x = target.x - self.full_die.width
            self.apply_die(board, self.full_die, Cell(x, y), Direction.LEFT)
            restore_corner = Cell(board.corners.e, corner.y)
        elif board.corners.is_e(corner):
            x = target.x + 1
            self.apply_die(board, self.full_die, Cell(x, y), Direction.RIGHT)
            restore_corner = Cell(board.corners.w, corner.y)
        else:
            raise ValueError(f"{corner=} is not corner cell.")
        return restore_corner, restore_target

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

        restore_corner, restore_target = self._line_move_to_corner_vertical(
            board, corner, target_1
        )
        self._swap_edge_horizontal(board, corner, target_2)
        self._line_move_to_corner_vertical(board, restore_corner, restore_target)

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
                not board.corners.is_corner(target_1) or target_2.y != board.height - 1
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
                not board.corners.is_corner(target_1) or target_2.y != board.height - 1
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
        mask: np.ndarray = board.field == target.field
        match edge:
            case Direction.UP:
                for x, goal in enumerate(target.field[0]):
                    if ~mask[0, x]:
                        swap_target_cells = np.argwhere(
                            ~mask[0]
                            & (board.field[0] == goal)
                            & (board.field[0, x] == target.field[0])
                        ).flatten()
                        if not swap_target_cells.size:
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
                        if not swap_target_cells.size:
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
                        if not swap_target_cells.size:
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
                        if not swap_target_cells.size:
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

    def is_arrangeable(self, vec: np.ndarray, target: np.ndarray) -> bool:
        """揃えられるか判定

        Args:
            vec (np.ndarray): 対象行・列
            target (np.ndarray): 対象行・列の完成状態

        Returns:
            bool: 判定結果
        """
        mask: np.ndarray = vec == target
        if mask.all() or np.count_nonzero(~mask) <= 1:
            return False
        for i, goal in enumerate(target):
            if ~mask[i] and goal in vec[~mask]:
                return True
        return False

    def is_arrangeable_row(self) -> np.ndarray:
        """行単位で揃えられるか判定

        Returns:
            np.ndarray: 揃えられる行がTrueのベクトル
        """
        return np.array(
            [
                self.is_arrangeable(vec, target)
                for vec, target in zip(self.board.field, self.goal.field)
            ]
        )

    def is_arrangeable_column(self) -> np.ndarray:
        """列単位で揃えられるか判定

        Returns:
            np.ndarray: 揃えられる列がTrueのベクトル
        """
        return np.array(
            [
                self.is_arrangeable(vec, target)
                for vec, target in zip(self.board.field.T, self.goal.field.T)
            ]
        ).T

    def arrange_rows(self) -> None:
        """行単位で揃える"""
        target = self.goal.copy()
        self.arrange_edge(self.board, target, edge=Direction.UP)
        self.arrange_edge(self.board, target, edge=Direction.DOWN)
        arrangeable_rows = np.argwhere(self.is_arrangeable_row()).flatten()
        row_indexes = np.arange(target.height)

        for index in arrangeable_rows:
            if index in row_indexes[[0, -1]]:
                continue
            move_to = index - row_indexes[0] + 1
            self._move_to_edge_row(self.board, move_to, Direction.UP)
            self._move_to_edge_row(target, move_to, Direction.UP)
            row_indexes = np.roll(row_indexes, -move_to)
            self.arrange_edge(self.board, target, edge=Direction.UP)
            self.arrange_edge(self.board, target, edge=Direction.DOWN)

        move_to = np.argwhere(row_indexes == 0).flatten()[0]
        self._move_to_edge_row(self.board, move_to, Direction.UP)
        self._move_to_edge_row(target, move_to, Direction.UP)
        row_indexes = np.roll(row_indexes, -move_to)

        assert (self.goal.field == target.field).all()

    def arrange_columns(self) -> None:
        """列単位で揃える"""
        target = self.goal.copy()

        self.arrange_edge(self.board, target, edge=Direction.LEFT)
        self.arrange_edge(self.board, target, edge=Direction.RIGHT)
        arrangeable_columns = np.argwhere(self.is_arrangeable_column()).flatten()
        column_indexes = np.arange(target.width)

        for index in arrangeable_columns:
            if index in column_indexes[[0, -1]]:
                continue
            move_to = index - column_indexes[0] + 1
            self._move_to_edge_column(self.board, move_to, Direction.LEFT)
            self._move_to_edge_column(target, move_to, Direction.LEFT)
            column_indexes = np.roll(column_indexes, -move_to)
            self.arrange_edge(self.board, target, edge=Direction.LEFT)
            self.arrange_edge(self.board, target, edge=Direction.RIGHT)

        move_to = np.argwhere(column_indexes == 0).flatten()[0]
        self._move_to_edge_column(self.board, move_to, Direction.LEFT)
        self._move_to_edge_column(target, move_to, Direction.LEFT)
        column_indexes = np.roll(column_indexes, -move_to)

        assert (self.goal.field == target.field).all()

    def rough_arrange(self, limit: int = None) -> None:
        """行列単位で揃える

        Args:
            limit (int, optional): 試行回数の上限. Defaults to None.
        """
        while self.is_arrangeable_row().any() or self.is_arrangeable_column().any():
            self.arrange_rows()
            self.arrange_columns()

    def arrange(self) -> None:
        """揃える"""
        while not self.check_board().all():
            mask = self.check_board()
            target = np.argwhere(~mask)[0]
            swap_targets = np.argwhere(
                ~mask & (self.board.field[*target] == self.goal.field)
            )
            if not swap_targets.size:
                swap_targets = np.argwhere(~mask)
            for y, x in swap_targets:
                self.swap(self.board, Cell(*target[::-1]), Cell(x, y))
                break
