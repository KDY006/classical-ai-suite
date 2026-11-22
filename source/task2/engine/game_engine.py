"""Pure state transitions and deterministic cell-by-cell projectile collisions."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Tuple

from ..config import (
    ALL_ACTIONS,
    BULLET_SPEED_PER_CYCLE,
    DAMAGE_PER_HIT,
    DIRECTION_DELTAS,
    FIRE,
    MOVE_ACTION_TO_DIR,
    PLAYER_MAX,
    PLAYER_MIN,
    STAY,
)
from .entities import Base, BrickWall, Bullet, Tank
from .game_state import GameState

BulletFrame = Tuple[int, int, int, str]
Impact = Tuple[int, int, str]


@dataclass
class StepEvent:
    """Animation data for a completed action and its projectile substeps."""

    player_id: int
    action: str
    bullet_frames: List[List[BulletFrame]] = field(default_factory=list)
    impacts: List[Impact] = field(default_factory=list)


class TankBattleEngine:
    """Stateless transition engine implementing RESULT(state, action)."""

    @classmethod
    def apply_action(cls, state: GameState, action: str) -> GameState:
        """Return the next immutable state without changing ``state``."""
        next_state, _ = cls._transition(state, action, record_events=False)
        return next_state

    @classmethod
    def step_with_events(cls, state: GameState, action: str) -> tuple[GameState, StepEvent]:
        """Return the next state and per-cell projectile animation events."""
        next_state, event = cls._transition(state, action, record_events=True)
        if event is None:
            raise RuntimeError("Event recording did not produce a StepEvent.")
        return next_state, event

    @classmethod
    def _transition(
        cls,
        state: GameState,
        action: str,
        record_events: bool,
    ) -> tuple[GameState, Optional[StepEvent]]:
        if action not in ALL_ACTIONS:
            raise ValueError(f"Unknown action: {action!r}")

        player_id = state.current_player
        event = StepEvent(player_id=player_id, action=action) if record_events else None
        if state.is_terminal():
            return state, event

        tanks: Dict[int, Tank] = dict(state.tanks)
        bases: Dict[int, Base] = dict(state.bases)
        brick_walls: Dict[tuple[int, int], BrickWall] = dict(state.brick_walls)
        bullets: List[Bullet] = list(state.bullets)
        steel_walls = state.steel_walls
        tank = tanks[player_id]

        if action in MOVE_ACTION_TO_DIR:
            direction = MOVE_ACTION_TO_DIR[action]
            dr, dc = DIRECTION_DELTAS[direction]
            destination = (tank.row + dr, tank.col + dc)
            tank = replace(tank, facing=direction)
            if cls._is_walkable(
                destination[0],
                destination[1],
                state.rows,
                state.cols,
                tanks,
                bases,
                brick_walls,
                steel_walls,
            ):
                tank = replace(tank, row=destination[0], col=destination[1])
                for index, bullet in enumerate(bullets):
                    if (
                        bullet.owner_id != player_id
                        and (bullet.row, bullet.col) == destination
                    ):
                        tank, _ = tank.damaged(DAMAGE_PER_HIT)
                        bullets[index] = replace(bullet, active=False)
                        if event is not None:
                            event.impacts.append((destination[0], destination[1], "TANK"))
                        break
            tanks[player_id] = tank
        elif action == FIRE and not any(b.owner_id == player_id for b in bullets):
            bullets.append(
                Bullet(
                    owner_id=player_id,
                    row=tank.row,
                    col=tank.col,
                    direction=tank.facing,
                )
            )
        elif action == STAY:
            pass

        if not cls._is_combat_terminal(tanks, bases):
            for _ in range(BULLET_SPEED_PER_CYCLE):
                moved_any = False
                for index, bullet in enumerate(bullets):
                    if not bullet.active or bullet.owner_id != player_id:
                        continue
                    moved_any = True
                    cls._advance_bullet_one_cell(
                        index,
                        bullets,
                        tanks,
                        bases,
                        brick_walls,
                        steel_walls,
                        state.rows,
                        state.cols,
                        event,
                    )
                    if cls._is_combat_terminal(tanks, bases):
                        break

                if event is not None and moved_any:
                    event.bullet_frames.append(
                        [
                            (bullet.owner_id, bullet.row, bullet.col, bullet.direction)
                            for bullet in bullets
                            if bullet.active
                        ]
                    )
                if not moved_any or cls._is_combat_terminal(tanks, bases):
                    break

        next_state = GameState(
            rows=state.rows,
            cols=state.cols,
            tanks=tanks,
            bases=bases,
            brick_walls={
                position: wall for position, wall in brick_walls.items() if wall.hp > 0
            },
            steel_walls=steel_walls,
            bullets=(bullet for bullet in bullets if bullet.active),
            current_player=GameState.opponent(player_id),
            ply=state.ply + 1,
            max_plies=state.max_plies,
        )
        return next_state, event

    @staticmethod
    def _is_walkable(
        row: int,
        col: int,
        rows: int,
        cols: int,
        tanks: Dict[int, Tank],
        bases: Dict[int, Base],
        brick_walls: Dict[tuple[int, int], BrickWall],
        steel_walls: frozenset[tuple[int, int]],
    ) -> bool:
        if not (0 <= row < rows and 0 <= col < cols) or (row, col) in steel_walls:
            return False
        wall = brick_walls.get((row, col))
        if wall is not None and wall.hp > 0:
            return False
        if any(base.hp > 0 and (base.row, base.col) == (row, col) for base in bases.values()):
            return False
        return not any(
            tank.hp > 0 and (tank.row, tank.col) == (row, col)
            for tank in tanks.values()
        )

    @staticmethod
    def _is_combat_terminal(tanks: Dict[int, Tank], bases: Dict[int, Base]) -> bool:
        max_alive = tanks[PLAYER_MAX].hp > 0 and bases[PLAYER_MAX].hp > 0
        min_alive = tanks[PLAYER_MIN].hp > 0 and bases[PLAYER_MIN].hp > 0
        return not max_alive or not min_alive

    @classmethod
    def _advance_bullet_one_cell(
        cls,
        bullet_index: int,
        bullets: List[Bullet],
        tanks: Dict[int, Tank],
        bases: Dict[int, Base],
        brick_walls: Dict[tuple[int, int], BrickWall],
        steel_walls: frozenset[tuple[int, int]],
        rows: int,
        cols: int,
        event: Optional[StepEvent],
    ) -> None:
        bullet = bullets[bullet_index]
        dr, dc = DIRECTION_DELTAS[bullet.direction]
        next_row, next_col = bullet.row + dr, bullet.col + dc
        if not (0 <= next_row < rows and 0 <= next_col < cols):
            bullets[bullet_index] = replace(bullet, active=False)
            return

        bullets[bullet_index] = replace(bullet, row=next_row, col=next_col)
        for other_index, other in enumerate(bullets):
            if (
                other_index != bullet_index
                and other.active
                and other.owner_id != bullet.owner_id
                and (other.row, other.col) == (next_row, next_col)
            ):
                bullets[bullet_index] = replace(bullets[bullet_index], active=False)
                bullets[other_index] = replace(other, active=False)
                cls._record_impact(event, next_row, next_col, "BULLET")
                return

        if (next_row, next_col) in steel_walls:
            bullets[bullet_index] = replace(bullets[bullet_index], active=False)
            cls._record_impact(event, next_row, next_col, "STEEL")
            return

        wall = brick_walls.get((next_row, next_col))
        if wall is not None and wall.hp > 0:
            brick_walls[(next_row, next_col)], _ = wall.damaged(DAMAGE_PER_HIT)
            bullets[bullet_index] = replace(bullets[bullet_index], active=False)
            cls._record_impact(event, next_row, next_col, "WALL")
            return

        for player_id in (PLAYER_MAX, PLAYER_MIN):
            base = bases[player_id]
            if base.hp > 0 and (base.row, base.col) == (next_row, next_col):
                bases[player_id], _ = base.damaged(DAMAGE_PER_HIT)
                bullets[bullet_index] = replace(bullets[bullet_index], active=False)
                cls._record_impact(event, next_row, next_col, "BASE")
                return

        for player_id in (PLAYER_MAX, PLAYER_MIN):
            tank = tanks[player_id]
            if tank.hp > 0 and (tank.row, tank.col) == (next_row, next_col):
                tanks[player_id], _ = tank.damaged(DAMAGE_PER_HIT)
                bullets[bullet_index] = replace(bullets[bullet_index], active=False)
                cls._record_impact(event, next_row, next_col, "TANK")
                return

    @staticmethod
    def _record_impact(
        event: Optional[StepEvent],
        row: int,
        col: int,
        impact_type: str,
    ) -> None:
        if event is not None:
            event.impacts.append((row, col, impact_type))
