"""Zero-Sum game state representation for Tank Battle."""

from __future__ import annotations

from typing import Dict, FrozenSet, List, Optional, Tuple

from ..config import (
    ALL_ACTIONS,
    DIRECTION_DELTAS,
    DRAW_UTILITY,
    FIRE,
    LOSS_UTILITY,
    MOVE_ACTION_TO_DIR,
    PLAYER_MAX,
    PLAYER_MIN,
    STAY,
    WIN_UTILITY,
)
from .entities import Base, BrickWall, Bullet, SteelWall, Tank


class GameState:
    """Encapsulates a complete snapshot of the Tank Battle Zero-Sum Game.

    Components correspond directly to Lecture 07 formalization:
      - ``current_player``: PLAYER(s) in {PLAYER_MAX, PLAYER_MIN}
      - ``legal_actions()``: ACTIONS(s)
      - ``is_terminal()``: TERMINAL-TEST(s)
      - ``utility(perspective)``: UTILITY(s, p)
    """

    def __init__(
        self,
        rows: int,
        cols: int,
        tanks: Dict[int, Tank],
        bases: Dict[int, Base],
        brick_walls: Dict[Tuple[int, int], BrickWall],
        steel_walls: FrozenSet[Tuple[int, int]] = frozenset(),
        bullets: Optional[List[Bullet]] = None,
        current_player: int = PLAYER_MAX,
        ply: int = 0,
        max_plies: int = 120,
    ) -> None:
        self.rows: int = rows
        self.cols: int = cols
        self.tanks: Dict[int, Tank] = tanks
        self.bases: Dict[int, Base] = bases
        self.brick_walls: Dict[Tuple[int, int], BrickWall] = brick_walls
        self.steel_walls: FrozenSet[Tuple[int, int]] = steel_walls
        self.bullets: List[Bullet] = bullets if bullets is not None else []
        self.current_player: int = current_player
        self.ply: int = ply
        self.max_plies: int = max_plies

    def clone(self) -> "GameState":
        """Fast deep copy of mutable game entities while sharing immutable steel wall coords."""
        return GameState(
            rows=self.rows,
            cols=self.cols,
            tanks={pid: t.clone() for pid, t in self.tanks.items()},
            bases={pid: b.clone() for pid, b in self.bases.items()},
            brick_walls={pos: w.clone() for pos, w in self.brick_walls.items() if w.hp > 0},
            steel_walls=self.steel_walls,
            bullets=[b.clone() for b in self.bullets if b.active],
            current_player=self.current_player,
            ply=self.ply,
            max_plies=self.max_plies,
        )

    @staticmethod
    def opponent(player_id: int) -> int:
        return PLAYER_MIN if player_id == PLAYER_MAX else PLAYER_MAX

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def has_active_bullet(self, player_id: int) -> bool:
        return any(b.active and b.owner_id == player_id for b in self.bullets)

    def is_cell_walkable(self, row: int, col: int) -> bool:
        if not self.in_bounds(row, col):
            return False
        if (row, col) in self.steel_walls:
            return False
        wall = self.brick_walls.get((row, col))
        if wall is not None and wall.hp > 0:
            return False
        for base in self.bases.values():
            if base.hp > 0 and base.row == row and base.col == col:
                return False
        for tank in self.tanks.values():
            if tank.hp > 0 and tank.row == row and tank.col == col:
                return False
        return True

    def legal_actions(self, player_id: Optional[int] = None) -> List[str]:
        """Return legal non-redundant actions for ``player_id`` in state ``s``."""
        pid = self.current_player if player_id is None else player_id
        tank = self.tanks[pid]
        if tank.hp <= 0:
            return [STAY]

        actions: List[str] = []
        for move_act, direction in MOVE_ACTION_TO_DIR.items():
            dr, dc = DIRECTION_DELTAS[direction]
            nr, nc = tank.row + dr, tank.col + dc
            # Legal if cell is walkable OR rotating tank orientation in place
            if self.is_cell_walkable(nr, nc) or tank.facing != direction:
                actions.append(move_act)

        if not self.has_active_bullet(pid):
            actions.append(FIRE)

        actions.append(STAY)
        return actions if actions else list(ALL_ACTIONS)

    def winner(self) -> Optional[int]:
        """Return winning player ID, 0 for draw/timeout, or None if game is ongoing."""
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
        """TERMINAL-TEST(s): True when either a tank/base is destroyed or ply limit reached."""
        return self.winner() is not None

    def utility(self, perspective: int = PLAYER_MAX) -> float:
        """UTILITY(s, p): Zero-sum payoff (+1000 win, -1000 loss, 0 draw)."""
        w = self.winner()
        if w is None or w == 0:
            return DRAW_UTILITY
        return WIN_UTILITY if w == perspective else LOSS_UTILITY

    def state_key(self) -> tuple:
        """Hashable canonical key for Transposition Table lookups."""
        t1 = self.tanks[PLAYER_MAX]
        t2 = self.tanks[PLAYER_MIN]
        b1 = self.bases[PLAYER_MAX]
        b2 = self.bases[PLAYER_MIN]
        walls_key = tuple(
            sorted((pos[0], pos[1], w.hp) for pos, w in self.brick_walls.items() if w.hp > 0)
        )
        bullets_key = tuple(
            (b.owner_id, b.row, b.col, b.direction) for b in self.bullets if b.active
        )
        return (
            self.current_player,
            (t1.row, t1.col, t1.facing, t1.hp),
            (t2.row, t2.col, t2.facing, t2.hp),
            (b1.hp, b2.hp),
            walls_key,
            bullets_key,
        )

    def to_observation_dict(self) -> dict:
        """Export a pure-Python dictionary snapshot for external group bot adapters."""
        return {
            "rows": self.rows,
            "cols": self.cols,
            "current_player": self.current_player,
            "ply": self.ply,
            "max_plies": self.max_plies,
            "tanks": {
                pid: {
                    "player_id": t.player_id,
                    "row": t.row,
                    "col": t.col,
                    "facing": t.facing,
                    "hp": t.hp,
                }
                for pid, t in self.tanks.items()
            },
            "bases": {
                pid: {
                    "player_id": b.player_id,
                    "row": b.row,
                    "col": b.col,
                    "hp": b.hp,
                }
                for pid, b in self.bases.items()
            },
            "brick_walls": [
                {"row": w.row, "col": w.col, "hp": w.hp}
                for w in self.brick_walls.values()
                if w.hp > 0
            ],
            "steel_walls": [{"row": r, "col": c} for (r, c) in self.steel_walls],
            "bullets": [
                {
                    "owner_id": b.owner_id,
                    "row": b.row,
                    "col": b.col,
                    "direction": b.direction,
                }
                for b in self.bullets
                if b.active
            ],
            "legal_actions": self.legal_actions(),
        }
