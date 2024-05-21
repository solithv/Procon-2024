import json

import numpy as np

from .data import Cell, CuttingInfo, Direction
from .patterns import Board, CuttingDie


class Game:
    def __init__(self, game_input: dict) -> None:
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

        self.make_standard_dies()
        for i, pattern in enumerate(game_input["general"]["patterns"], len(self.dies)):
            self.dies.append(
                CuttingDie(
                    i, pattern["width"], pattern["height"], pattern=pattern["cells"]
                )
            )

    def make_standard_dies(self) -> None:
        """定型抜き型を作成"""
        self.dies: list[CuttingDie] = []
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
            {"n": len(self.logs), "ops": [log.to_dict() for log in self.logs]}
        )

    def check_board(self) -> np.ndarray:
        """現在盤面と最終盤面を比較

        Returns:
            np.ndarray: 一致箇所がTrueのbool map
        """
        return self.board.field == self.goal.field

    def search_static_die(self, size: int, type: int) -> CuttingDie:
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

    def apply_die(self, die: CuttingDie, cell: Cell, direction: int) -> None:
        """抜き型を適用

        Args:
            die (CuttingDie): 適用する抜き型
            cell (Cell): 適用する座標
            direction (int): 適用する方向(Directionで定義)
        """
        self.logs.append(self.board._apply_die(die=die, cell=cell, direction=direction))

    def row_two_pieces_replace(self, corner_target: Cell, target: Cell) -> None:
        """横方向に角との2点交換

        Args:
            corner_target (Cell): 角の座標
            target (Cell): 交換対象の座標
        """

        def get_margin():
            match corner:
                case self.board.corners.nw:
                    return target.x - corner_target.x - 1
                case self.board.corners.ne:
                    return corner_target.x - target.x - 1
                case self.board.corners.sw:
                    return target.x - corner_target.x - 1
                case self.board.corners.se:
                    return corner_target.x - target.x - 1

        def get_offset_x():
            match corner:
                case self.board.corners.nw:
                    return -size
                case self.board.corners.ne:
                    return 1
                case self.board.corners.sw:
                    return -size
                case self.board.corners.se:
                    return 1

        def get_offset_y():
            match corner:
                case self.board.corners.nw:
                    return -size + 1
                case self.board.corners.ne:
                    return -size + 1
                case self.board.corners.sw:
                    return 0
                case self.board.corners.se:
                    return 0

        corner = corner_target.copy()
        match corner:
            case self.board.corners.nw:
                direction = Direction.right
            case self.board.corners.ne:
                direction = Direction.left
            case self.board.corners.sw:
                direction = Direction.right
            case self.board.corners.se:
                direction = Direction.left
            case _:
                raise ValueError(
                    f"corner_target must be corner cell but input {corner_target}."
                )

        for i in reversed(range(9)):
            size = 2**i
            while size <= get_margin():
                self.apply_die(
                    self.search_static_die(size, 1),
                    Cell(target.x + get_offset_x(), target.y + get_offset_y()),
                    direction,
                )
                corner_target.x += size
        if target.x - corner_target.x == 1:
            self.apply_die(
                self.search_static_die(size, 1),
                Cell(target.x, target.y + get_offset_y()),
                direction,
            )

    def column_two_pieces_replace(self, corner_target: Cell, target: Cell) -> None:
        """縦方向に角との2点交換

        Args:
            corner_target (Cell): 角の座標
            target (Cell): 交換対象の座標
        """

        def get_margin():
            match corner:
                case self.board.corners.nw:
                    return target.y - corner_target.y - 1
                case self.board.corners.ne:
                    return target.y - corner_target.y - 1
                case self.board.corners.sw:
                    return corner_target.y - target.y - 1
                case self.board.corners.se:
                    return corner_target.y - target.y - 1
                case _:
                    raise ValueError

        def get_offset_x():
            match corner:
                case self.board.corners.nw:
                    return -size + 1
                case self.board.corners.ne:
                    return 0
                case self.board.corners.sw:
                    return -size + 1
                case self.board.corners.se:
                    return 0
                case _:
                    raise ValueError

        def get_offset_y():
            match corner:
                case self.board.corners.nw:
                    return -size
                case self.board.corners.ne:
                    return -size
                case self.board.corners.sw:
                    return 1
                case self.board.corners.se:
                    return 1
                case _:
                    raise ValueError

        corner = corner_target.copy()
        match corner:
            case self.board.corners.nw:
                direction = Direction.down
            case self.board.corners.ne:
                direction = Direction.up
            case self.board.corners.sw:
                direction = Direction.down
            case self.board.corners.se:
                direction = Direction.up
            case _:
                raise ValueError(
                    f"corner_target must be corner cell but input {corner_target}"
                )

        for i in reversed(range(9)):
            size = 2**i
            while size <= get_margin():
                self.apply_die(
                    self.search_static_die(size, 1),
                    Cell(target.x + get_offset_x(), target.y + get_offset_y()),
                    direction,
                )
                corner_target.y += size
        if target.y - corner_target.y == 1:
            self.apply_die(
                self.search_static_die(size, 1),
                Cell(target.x + get_offset_x(), target.y),
                direction,
            )
