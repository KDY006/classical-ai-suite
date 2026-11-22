"""Tactical evaluation and move ordering for depth-limited search."""

from __future__ import annotations

from typing import Iterable

from ..config import (
    BULLET_SPEED_PER_CYCLE,
    DIRECTION_DELTAS,
    MOVE_ACTION_TO_DIR,
)
from ..engine.game_state import GameState

TraceResult = tuple[str, int | None, int]


class TacticalEvaluator:
    W_TANK_HP = 125.0
    W_BASE_HP = 155.0
    W_APPROACH = 4.5
    W_LINE_OF_FIRE = 24.0
    W_BULLET_THREAT = 65.0

    @classmethod
    def evaluate(cls, state: GameState, perspective: int) -> float:
        if state.is_terminal():
            return state.utility(perspective)

        opponent = GameState.opponent(perspective)
        my_tank = state.tanks[perspective]
        opp_tank = state.tanks[opponent]
        my_base = state.bases[perspective]
        opp_base = state.bases[opponent]

        score = cls.W_TANK_HP * (my_tank.hp - opp_tank.hp)
        score += cls.W_BASE_HP * (my_base.hp - opp_base.hp)

        my_base_distance = abs(my_tank.row - opp_base.row) + abs(my_tank.col - opp_base.col)
        opp_base_distance = abs(opp_tank.row - my_base.row) + abs(opp_tank.col - my_base.col)
        tank_distance = abs(my_tank.row - opp_tank.row) + abs(my_tank.col - opp_tank.col)
        score += cls.W_APPROACH * (opp_base_distance - my_base_distance)
        score += 1.5 * (state.rows + state.cols - tank_distance)

        score += cls.W_LINE_OF_FIRE * (
            cls._line_of_fire_score(state, perspective)
            - cls._line_of_fire_score(state, opponent)
        )
        score += (
            cls._breach_progress_score(state, perspective)
            - cls._breach_progress_score(state, opponent)
        )

        for bullet in state.bullets:
            kind, target_id, distance = cls.trace_target(
                state,
                bullet.row,
                bullet.col,
                bullet.direction,
            )
            urgency = max(
                0.2,
                1.0 - distance / (BULLET_SPEED_PER_CYCLE * 3.0),
            )
            if target_id == opponent and kind in ("TANK", "BASE"):
                score += cls.W_BULLET_THREAT * urgency
            elif target_id == perspective and kind in ("TANK", "BASE"):
                score -= cls.W_BULLET_THREAT * (urgency + 0.35)
        return score

    @classmethod
    def trace_target(
        cls,
        state: GameState,
        start_row: int,
        start_col: int,
        direction: str,
    ) -> TraceResult:
        dr, dc = DIRECTION_DELTAS[direction]
        row, col = start_row, start_col
        distance = 0
        while True:
            row += dr
            col += dc
            distance += 1
            if not state.in_bounds(row, col) or (row, col) in state.steel_walls:
                return "NONE", None, distance

            wall = state.brick_walls.get((row, col))
            if wall is not None and wall.hp > 0:
                base_distances = [
                    (abs(row - base.row) + abs(col - base.col), player_id)
                    for player_id, base in state.bases.items()
                    if base.hp > 0
                ]
                closer_id = min(base_distances)[1] if base_distances else None
                for player_id, base in state.bases.items():
                    if abs(row - base.row) + abs(col - base.col) == 1:
                        return "WALL_NEAR_BASE", player_id, distance
                return "WALL", closer_id, distance

            for player_id, base in state.bases.items():
                if base.hp > 0 and (base.row, base.col) == (row, col):
                    return "BASE", player_id, distance
            for player_id, tank in state.tanks.items():
                if tank.hp > 0 and (tank.row, tank.col) == (row, col):
                    return "TANK", player_id, distance

    @classmethod
    def _line_of_fire_score(cls, state: GameState, player_id: int) -> float:
        tank = state.tanks[player_id]
        opponent = GameState.opponent(player_id)
        kind, target_id, distance = cls.trace_target(
            state,
            tank.row,
            tank.col,
            tank.facing,
        )
        if target_id == opponent and kind == "TANK":
            return 1.5 / (1.0 + 0.15 * distance)
        if target_id == opponent and kind == "BASE":
            return 1.35 / (1.0 + 0.15 * distance)
        if kind == "WALL_NEAR_BASE":
            return 0.55
        if kind == "WALL":
            return 0.25
        return 0.0

    @classmethod
    def _breach_progress_score(cls, state: GameState, player_id: int) -> float:
        opponent = GameState.opponent(player_id)
        tank = state.tanks[player_id]
        opponent_base = state.bases[opponent]
        dr, dc = DIRECTION_DELTAS[tank.facing]
        row, col = tank.row + dr, tank.col + dc

        while state.in_bounds(row, col) and (row, col) not in state.steel_walls:
            wall = state.brick_walls.get((row, col))
            if wall is not None and wall.hp > 0:
                tank_to_base = abs(tank.row - opponent_base.row) + abs(tank.col - opponent_base.col)
                wall_to_base = abs(row - opponent_base.row) + abs(col - opponent_base.col)
                if wall_to_base < tank_to_base:
                    return 9.0 * (3 - wall.hp)
                return 0.0
            row += dr
            col += dc
        return 0.0

    @classmethod
    def order_actions(cls, state: GameState, actions: Iterable[str]) -> list[str]:
        """Sort promising actions before evaluating their children."""
        player_id = state.current_player
        opponent = GameState.opponent(player_id)
        tank = state.tanks[player_id]
        opponent_base = state.bases[opponent]
        opponent_tank = state.tanks[opponent]

        enemy_bullet_threat = False
        for bullet in state.bullets:
            if bullet.owner_id == player_id:
                continue
            kind, target_id, _ = cls.trace_target(
                state,
                bullet.row,
                bullet.col,
                bullet.direction,
            )
            if kind in ("TANK", "BASE") and target_id == player_id:
                enemy_bullet_threat = True
                break

        def priority(action: str) -> float:
            if action == "FIRE":
                kind, target_id, distance = cls.trace_target(
                    state,
                    tank.row,
                    tank.col,
                    tank.facing,
                )
                if target_id == opponent and kind in ("TANK", "BASE"):
                    return 100.0 - distance
                if kind.startswith("WALL"):
                    return 35.0
                return 10.0

            if action in MOVE_ACTION_TO_DIR:
                direction = MOVE_ACTION_TO_DIR[action]
                dr, dc = DIRECTION_DELTAS[direction]
                next_row, next_col = tank.row + dr, tank.col + dc
                bonus = 45.0 if (
                    enemy_bullet_threat
                    and state.is_cell_walkable(next_row, next_col)
                ) else 0.0
                if state.is_cell_walkable(next_row, next_col):
                    before = min(
                        abs(tank.row - opponent_base.row) + abs(tank.col - opponent_base.col),
                        abs(tank.row - opponent_tank.row) + abs(tank.col - opponent_tank.col),
                    )
                    after = min(
                        abs(next_row - opponent_base.row) + abs(next_col - opponent_base.col),
                        abs(next_row - opponent_tank.row) + abs(next_col - opponent_tank.col),
                    )
                    bonus += 15.0 * (before - after)
                else:
                    kind, target_id, _ = cls.trace_target(
                        state,
                        tank.row,
                        tank.col,
                        direction,
                    )
                    if target_id == opponent and kind in ("TANK", "BASE"):
                        bonus += 28.0
                return bonus

            if action == "STAY":
                return -15.0
            return 0.0

        return sorted(actions, key=priority, reverse=True)
