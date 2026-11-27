"""Bieu dien trang thai bat bien cho Tro choi Tong bang khong Dau Tang."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable, Mapping, Optional, Tuple

from ..config import (
    DIRECTION_DELTAS,
    DRAW_UTILITY,
    FIRE,
    LOSS_UTILITY,
    MOVE_ACTION_TO_DIR,
    PLAYER_IDS,
    PLAYER_MAX,
    PLAYER_MIN,
    STAY,
    WIN_UTILITY,
)
from .entities import Base, BrickWall, Bullet, Tank

Position = Tuple[int, int]


@dataclass(frozen=True, slots=True, init=False)
class GameState:
    """Ban chup trang thai bat bien bao ve toan ven du lieu truoc bot nhom ngoai."""

    rows: int
    cols: int
    tanks: Mapping[int, Tank]
    bases: Mapping[int, Base]
    brick_walls: Mapping[Position, BrickWall]
    steel_walls: frozenset[Position]
    bullets: tuple[Bullet, ...]
    current_player: int
    ply: int
    max_plies: int

    def __init__(
        self,
        rows: int,
        cols: int,
        tanks: Mapping[int, Tank],
        bases: Mapping[int, Base],
        brick_walls: Mapping[Position, BrickWall],
        steel_walls: Iterable[Position] = frozenset(),
        bullets: Optional[Iterable[Bullet]] = None,
        current_player: int = PLAYER_MAX,
        ply: int = 0,
        max_plies: int = 120,
    ) -> None:
        if rows <= 0 or cols <= 0:
            raise ValueError("Kich thuoc ban do phai la so nguyen duong")
        if current_player not in PLAYER_IDS:
            raise ValueError(f"Nguoi choi hien tai khong hop le: {current_player}")
        if ply < 0 or max_plies < 0:
            raise ValueError("Chi so luot ply va max_plies khong duoc am")
        if set(tanks) != set(PLAYER_IDS) or set(bases) != set(PLAYER_IDS):
            raise ValueError("Trang thai phai co dung 1 xe tang va 1 can cu cho moi phe")

        tank_copy = dict(tanks)
        base_copy = dict(bases)
        wall_copy = dict(brick_walls)
        steel_copy = frozenset(steel_walls)
        bullet_copy = tuple(bullet for bullet in (bullets or ()) if bullet.active)

        for player_id in PLAYER_IDS:
            if tank_copy[player_id].player_id != player_id:
                raise ValueError(f"Thong tin xe tang khong khop phe {player_id}")
            if base_copy[player_id].player_id != player_id:
                raise ValueError(f"Thong tin can cu khong khop phe {player_id}")

        positions = (
            [(tank.row, tank.col) for tank in tank_copy.values()]
            + [(base.row, base.col) for base in base_copy.values()]
            + list(wall_copy)
            + list(steel_copy)
            + [(bullet.row, bullet.col) for bullet in bullet_copy]
        )
        if any(not (0 <= row < rows and 0 <= col < cols) for row, col in positions):
            raise ValueError("Moi thuc the va vien dan phai nam trong bien ban do")
        if any(wall.row != pos[0] or wall.col != pos[1] for pos, wall in wall_copy.items()):
            raise ValueError("Khoa toa do tuong gach khong khop voi thuc the tuong ung")
        if len({bullet.owner_id for bullet in bullet_copy}) != len(bullet_copy):
            raise ValueError("Moi xe tang chi duoc co toi da mot vien dan dang bay")

        object.__setattr__(self, "rows", rows)
        object.__setattr__(self, "cols", cols)
        object.__setattr__(self, "tanks", MappingProxyType(tank_copy))
        object.__setattr__(self, "bases", MappingProxyType(base_copy))
        object.__setattr__(self, "brick_walls", MappingProxyType(wall_copy))
        object.__setattr__(self, "steel_walls", steel_copy)
        object.__setattr__(self, "bullets", bullet_copy)
        object.__setattr__(self, "current_player", current_player)
        object.__setattr__(self, "ply", ply)
        object.__setattr__(self, "max_plies", max_plies)

    def clone(self) -> GameState:
        """Tra ve ban chup hien tai do toan bo truong va tap hop deu bat bien."""
        return self

    @staticmethod
    def opponent(player_id: int) -> int:
        if player_id == PLAYER_MAX:
            return PLAYER_MIN
        if player_id == PLAYER_MIN:
            return PLAYER_MAX
        raise ValueError(f"Ma nguoi choi khong hop le: {player_id}")

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def has_active_bullet(self, player_id: int) -> bool:
        return any(bullet.owner_id == player_id for bullet in self.bullets)

    def is_cell_walkable(self, row: int, col: int) -> bool:
        """Kiem tra o (row, col) co trong de xe tang di chuyen vao hay khong."""
        if not self.in_bounds(row, col) or (row, col) in self.steel_walls:
            return False
        wall = self.brick_walls.get((row, col))
        if wall is not None and wall.hp > 0:
            return False
        if any(base.hp > 0 and (base.row, base.col) == (row, col) for base in self.bases.values()):
            return False
        return not any(
            tank.hp > 0 and (tank.row, tank.col) == (row, col)
            for tank in self.tanks.values()
        )

    def legal_actions(self, player_id: Optional[int] = None) -> list[str]:
        """Tra ve tap hanh dong hop le, loai bo hanh dong du thua cho nguoi choi."""
        pid = self.current_player if player_id is None else player_id
        if pid not in PLAYER_IDS:
            raise ValueError(f"Ma nguoi choi khong hop le: {pid}")
        if self.is_terminal():
            return [STAY]

        tank = self.tanks[pid]
        actions: list[str] = []
        for action, direction in MOVE_ACTION_TO_DIR.items():
            dr, dc = DIRECTION_DELTAS[direction]
            destination = (tank.row + dr, tank.col + dc)
            if self.is_cell_walkable(*destination) or tank.facing != direction:
                actions.append(action)
        if not self.has_active_bullet(pid):
            actions.append(FIRE)
        actions.append(STAY)
        return actions

    def winner(self) -> Optional[int]:
        """Tra ve MAX/MIN neu thang, 0 neu hoa hoac het luot, None neu dang dau."""
        max_alive = self.tanks[PLAYER_MAX].hp > 0 and self.bases[PLAYER_MAX].hp > 0
        min_alive = self.tanks[PLAYER_MIN].hp > 0 and self.bases[PLAYER_MIN].hp > 0
        if not max_alive and not min_alive:
            return 0
        if not min_alive:
            return PLAYER_MAX
        if not max_alive:
            return PLAYER_MIN
        if self.ply >= self.max_plies:
            return 0
        return None

    def is_terminal(self) -> bool:
        return self.winner() is not None

    def utility(self, perspective: int = PLAYER_MAX) -> float:
        """Ham tien ich tong bang khong (+1000 thang, -1000 thua, 0 hoa)."""
        if perspective not in PLAYER_IDS:
            raise ValueError(f"Goc nhin tinh tien ich khong hop le: {perspective}")
        winner = self.winner()
        if winner is None or winner == 0:
            return DRAW_UTILITY
        return WIN_UTILITY if winner == perspective else LOSS_UTILITY

    def state_key(self) -> tuple:
        """Tao khoa bam chuan tac cho bang Transposition Table va phat hien lap."""
        return (
            self.rows,
            self.cols,
            self.current_player,
            tuple(
                (pid, tank.row, tank.col, tank.facing, tank.hp)
                for pid, tank in sorted(self.tanks.items())
            ),
            tuple(
                (pid, base.row, base.col, base.hp)
                for pid, base in sorted(self.bases.items())
            ),
            tuple(sorted((row, col, wall.hp) for (row, col), wall in self.brick_walls.items())),
            tuple(sorted(self.steel_walls)),
            tuple(
                sorted(
                    (bullet.owner_id, bullet.row, bullet.col, bullet.direction)
                    for bullet in self.bullets
                )
            ),
        )

    def to_observation_dict(self) -> dict:
        """Xuat tu dien quan sat doc lap de truyen an toan cho bot chuan Dict."""
        return {
            "rows": self.rows,
            "cols": self.cols,
            "current_player": self.current_player,
            "ply": self.ply,
            "max_plies": self.max_plies,
            "tanks": {
                pid: {
                    "player_id": tank.player_id,
                    "row": tank.row,
                    "col": tank.col,
                    "facing": tank.facing,
                    "hp": tank.hp,
                }
                for pid, tank in self.tanks.items()
            },
            "bases": {
                pid: {
                    "player_id": base.player_id,
                    "row": base.row,
                    "col": base.col,
                    "hp": base.hp,
                }
                for pid, base in self.bases.items()
            },
            "brick_walls": [
                {"row": wall.row, "col": wall.col, "hp": wall.hp}
                for wall in self.brick_walls.values()
                if wall.hp > 0
            ],
            "steel_walls": [{"row": row, "col": col} for row, col in sorted(self.steel_walls)],
            "bullets": [
                {
                    "owner_id": bullet.owner_id,
                    "row": bullet.row,
                    "col": bullet.col,
                    "direction": bullet.direction,
                }
                for bullet in self.bullets
            ],
            "legal_actions": self.legal_actions(),
        }
