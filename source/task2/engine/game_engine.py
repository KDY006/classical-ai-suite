"""Transition model RESULT(s, a) with cell-by-cell 3-step bullet collision physics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from ..config import (
    BULLET_SPEED_PER_CYCLE,
    DAMAGE_PER_HIT,
    DIRECTION_DELTAS,
    FIRE,
    MOVE_ACTION_TO_DIR,
    STAY,
)
from .entities import Bullet
from .game_state import GameState


@dataclass
class StepEvent:
    """Granular animation and collision metadata emitted during a single turn."""

    player_id: int
    action: str
    bullet_frames: List[List[Tuple[int, int, int, str]]] = field(default_factory=list)
    impacts: List[Tuple[int, int, str]] = field(default_factory=list)


class TankBattleEngine:
    """Stateless transition engine implementing RESULT(s, a) for Tank Battle."""

    @classmethod
    def apply_action(cls, state: GameState, action: str) -> GameState:
        """Compute next state s' = RESULT(s, a) without mutating ``state``."""
        next_state = state.clone()
        cls._step_in_place(next_state, action, record_events=False)
        return next_state

    @classmethod
    def step_with_events(cls, state: GameState, action: str) -> Tuple[GameState, StepEvent]:
        """Compute next state s' plus cell-by-cell bullet trajectory frames for PyGame UI."""
        next_state = state.clone()
        event = cls._step_in_place(next_state, action, record_events=True)
        assert event is not None
        return next_state, event

    @classmethod
    def _step_in_place(
        cls,
        state: GameState,
        action: str,
        record_events: bool = False,
    ) -> Optional[StepEvent]:
        pid = state.current_player
        tank = state.tanks[pid]
        event = StepEvent(player_id=pid, action=action) if record_events else None

        if state.is_terminal():
            return event

        # 1. Execute tank action (movement/rotation, firing, or staying)
        if action in MOVE_ACTION_TO_DIR:
            direction = MOVE_ACTION_TO_DIR[action]
            tank.facing = direction
            dr, dc = DIRECTION_DELTAS[direction]
            nr, nc = tank.row + dr, tank.col + dc
            if state.is_cell_walkable(nr, nc):
                tank.row, tank.col = nr, nc
                # Check if tank stepped directly into an active enemy projectile
                for b in state.bullets:
                    if b.active and b.row == nr and b.col == nc and b.owner_id != pid:
                        tank.take_damage(DAMAGE_PER_HIT)
                        b.active = False
                        if event is not None:
                            event.impacts.append((nr, nc, "TANK"))
                        break

        elif action == FIRE:
            if not state.has_active_bullet(pid):
                state.bullets.append(
                    Bullet(
                        owner_id=pid,
                        row=tank.row,
                        col=tank.col,
                        direction=tank.facing,
                        active=True,
                    )
                )
        elif action == STAY:
            pass

        # 2. Process active bullets belonging to current player for this cycle:
        #    Each bullet advances up to 3 cells, checked cell-by-cell.
        if not state.is_terminal():
            for step_idx in range(BULLET_SPEED_PER_CYCLE):
                any_moved = False
                for bullet in state.bullets:
                    if not bullet.active or bullet.owner_id != pid:
                        continue
                    any_moved = True
                    cls._advance_bullet_one_cell(state, bullet, event)
                    if state.is_terminal():
                        break
                if event is not None and any_moved:
                    snapshot = [
                        (b.owner_id, b.row, b.col, b.direction)
                        for b in state.bullets
                        if b.active
                    ]
                    event.bullet_frames.append(snapshot)
                if state.is_terminal() or not any_moved:
                    break

        # Remove inactive bullets and destroyed brick walls
        state.bullets = [b for b in state.bullets if b.active]
        dead_walls = [pos for pos, w in state.brick_walls.items() if w.hp <= 0]
        for pos in dead_walls:
            del state.brick_walls[pos]

        # Advance turn counter and switch active player
        state.ply += 1
        state.current_player = GameState.opponent(pid)
        return event

    @classmethod
    def _advance_bullet_one_cell(
        cls,
        state: GameState,
        bullet: Bullet,
        event: Optional[StepEvent],
    ) -> None:
        dr, dc = DIRECTION_DELTAS[bullet.direction]
        nr, nc = bullet.row + dr, bullet.col + dc

        # Out of map bounds
        if not state.in_bounds(nr, nc):
            bullet.active = False
            return

        bullet.row, bullet.col = nr, nc

        # Collide with opposing active bullet at same square
        for other in state.bullets:
            if other is not bullet and other.active and other.row == nr and other.col == nc:
                bullet.active = False
                other.active = False
                if event is not None:
                    event.impacts.append((nr, nc, "BULLET"))
                return

        # Collide with indestructible steel wall
        if (nr, nc) in state.steel_walls:
            bullet.active = False
            if event is not None:
                event.impacts.append((nr, nc, "STEEL"))
            return

        # Collide with destructible brick wall
        brick = state.brick_walls.get((nr, nc))
        if brick is not None and brick.hp > 0:
            brick.take_damage(DAMAGE_PER_HIT)
            bullet.active = False
            if event is not None:
                event.impacts.append((nr, nc, "WALL"))
            return

        # Collide with any base
        for base in state.bases.values():
            if base.hp > 0 and base.row == nr and base.col == nc:
                base.take_damage(DAMAGE_PER_HIT)
                bullet.active = False
                if event is not None:
                    event.impacts.append((nr, nc, "BASE"))
                return

        # Collide with any tank (excluding owner at spawn square, handled since bullet moved >=1 cell)
        for tank in state.tanks.values():
            if tank.hp > 0 and tank.row == nr and tank.col == nc:
                tank.take_damage(DAMAGE_PER_HIT)
                bullet.active = False
                if event is not None:
                    event.impacts.append((nr, nc, "TANK"))
                return
