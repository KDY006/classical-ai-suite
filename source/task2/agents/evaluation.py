"""Heuristic state evaluation EVAL(s) and tactical move ordering for Tank Battle."""

from __future__ import annotations

from typing import List, Tuple

from ..config import (
    BULLET_SPEED_PER_CYCLE,
    DIRECTION_DELTAS,
    FIRE,
    MOVE_ACTION_TO_DIR,
    STAY,
)
from ..engine.game_state import GameState


class TacticalEvaluator:
    """Balances offensive pressure, base defense, line-of-fire, and projectile evasion."""

    W_TANK_HP: float = 125.0
    W_BASE_HP: float = 155.0
    W_APPROACH: float = 4.5
    W_LINE_OF_FIRE: float = 24.0
    W_BULLET_THREAT: float = 65.0

    @classmethod
    def evaluate(cls, state: GameState, perspective: int) -> float:
        """Compute heuristic value EVAL(s) from ``perspective`` player's viewpoint."""
        if state.is_terminal():
            return state.utility(perspective)

        opp = GameState.opponent(perspective)
        my_tank = state.tanks[perspective]
        opp_tank = state.tanks[opp]
        my_base = state.bases[perspective]
        opp_base = state.bases[opp]

        # 1. Material / Health advantage
        score = cls.W_TANK_HP * (my_tank.hp - opp_tank.hp)
        score += cls.W_BASE_HP * (my_base.hp - opp_base.hp)

        # 2. Positional pressure toward enemy base and enemy tank
        max_dist = state.rows + state.cols
        my_dist_base = abs(my_tank.row - opp_base.row) + abs(my_tank.col - opp_base.col)
        opp_dist_base = abs(opp_tank.row - my_base.row) + abs(opp_tank.col - my_base.col)
        my_dist_tank = abs(my_tank.row - opp_tank.row) + abs(my_tank.col - opp_tank.col)

        score += cls.W_APPROACH * (opp_dist_base - my_dist_base)
        score += 1.5 * (max_dist - my_dist_tank)

        # 3. Line-of-fire alignment and wall-breaching progress toward opponent
        score += cls.W_LINE_OF_FIRE * (
            cls._line_of_fire_score(state, perspective)
            - cls._line_of_fire_score(state, opp)
        )
        score += cls._breach_progress_score(state, perspective) - cls._breach_progress_score(state, opp)

        # 4. Active projectile trajectories (reward our accurate shots, penalize incoming danger)
        for bullet in state.bullets:
            if not bullet.active:
                continue
            impact_kind, dist_steps = cls._trace_bullet_target(state, bullet.row, bullet.col, bullet.direction)
            urgency = max(0.2, 1.0 - (dist_steps / (BULLET_SPEED_PER_CYCLE * 3.0)))
            if impact_kind == ("TANK", opp) or impact_kind == ("BASE", opp):
                score += cls.W_BULLET_THREAT * urgency
            elif impact_kind == ("TANK", perspective) or impact_kind == ("BASE", perspective):
                score -= cls.W_BULLET_THREAT * (urgency + 0.35)

        return score

    @classmethod
    def _line_of_fire_score(cls, state: GameState, player_id: int) -> float:
        tank = state.tanks[player_id]
        opp = GameState.opponent(player_id)
        impact_kind, dist = cls._trace_bullet_target(state, tank.row, tank.col, tank.facing)
        if impact_kind == ("TANK", opp):
            return 1.5 / (1.0 + 0.15 * dist)
        if impact_kind == ("BASE", opp):
            return 1.35 / (1.0 + 0.15 * dist)
        if impact_kind == ("WALL_NEAR_OPP_BASE", opp):
            return 0.55
        if impact_kind == ("WALL_TOWARD_OPP", opp):
            return 0.25
        return 0.0

    @classmethod
    def _breach_progress_score(cls, state: GameState, player_id: int) -> float:
        """Reward damaging brick walls that stand along the corridor toward the enemy base."""
        opp = GameState.opponent(player_id)
        my_tank = state.tanks[player_id]
        opp_base = state.bases[opp]
        dr, dc = DIRECTION_DELTAS[my_tank.facing]
        r, c = my_tank.row + dr, my_tank.col + dc
        while state.in_bounds(r, c) and (r, c) not in state.steel_walls:
            wall = state.brick_walls.get((r, c))
            if wall is not None and wall.hp > 0:
                d_tank = abs(my_tank.row - opp_base.row) + abs(my_tank.col - opp_base.col)
                d_wall = abs(r - opp_base.row) + abs(c - opp_base.col)
                if d_wall < d_tank:
                    return 9.0 * (3 - wall.hp)
                return 0.0
            r += dr
            c += dc
        return 0.0

    @classmethod
    def _trace_bullet_target(
        cls,
        state: GameState,
        start_r: int,
        start_c: int,
        direction: str,
    ) -> Tuple[Tuple[str, int], int]:
        dr, dc = DIRECTION_DELTAS[direction]
        r, c = start_r, start_c
        steps = 0
        while True:
            r += dr
            c += dc
            steps += 1
            if not state.in_bounds(r, c) or (r, c) in state.steel_walls:
                return (("NONE", 0), steps)
            wall = state.brick_walls.get((r, c))
            if wall is not None and wall.hp > 0:
                for pid, base in state.bases.items():
                    if abs(r - base.row) + abs(c - base.col) == 1:
                        return (("WALL_NEAR_OPP_BASE", pid), steps)
                # Check which base this wall is closer to
                d1 = abs(r - state.bases[1].row) + abs(c - state.bases[1].col)
                d2 = abs(r - state.bases[2].row) + abs(c - state.bases[2].col)
                closer_pid = 1 if d1 < d2 else 2
                return (("WALL_TOWARD_OPP", closer_pid), steps)
            for pid, base in state.bases.items():
                if base.hp > 0 and base.row == r and base.col == c:
                    return (("BASE", pid), steps)
            for pid, tank in state.tanks.items():
                if tank.hp > 0 and tank.row == r and tank.col == c:
                    return (("TANK", pid), steps)

    @classmethod
    def order_actions(cls, state: GameState, actions: List[str]) -> List[str]:
        """Order candidate moves so promising tactical actions are searched first."""
        pid = state.current_player
        opp = GameState.opponent(pid)
        tank = state.tanks[pid]
        opp_base = state.bases[opp]
        opp_tank = state.tanks[opp]

        # Check if tank is currently standing in an enemy bullet corridor
        in_bullet_corridor = False
        for b in state.bullets:
            if b.active and b.owner_id != pid:
                kind, _ = cls._trace_bullet_target(state, b.row, b.col, b.direction)
                if kind == ("TANK", pid):
                    in_bullet_corridor = True
                    break

        def move_priority(action: str) -> float:
            if action == FIRE:
                kind, dist = cls._trace_bullet_target(state, tank.row, tank.col, tank.facing)
                if kind in (("TANK", opp), ("BASE", opp)):
                    return 100.0 - dist
                if kind[0].startswith("WALL"):
                    return 35.0
                return 10.0

            if action in MOVE_ACTION_TO_DIR:
                direction = MOVE_ACTION_TO_DIR[action]
                dr, dc = DIRECTION_DELTAS[direction]
                nr, nc = tank.row + dr, tank.col + dc
                bonus = 45.0 if in_bullet_corridor and state.is_cell_walkable(nr, nc) else 0.0
                if state.is_cell_walkable(nr, nc):
                    d_before = min(
                        abs(tank.row - opp_base.row) + abs(tank.col - opp_base.col),
                        abs(tank.row - opp_tank.row) + abs(tank.col - opp_tank.col),
                    )
                    d_after = min(
                        abs(nr - opp_base.row) + abs(nc - opp_base.col),
                        abs(nr - opp_tank.row) + abs(nc - opp_tank.col),
                    )
                    bonus += 15.0 * (d_before - d_after)
                else:
                    # Pure rotation toward enemy
                    kind, _ = cls._trace_bullet_target(state, tank.row, tank.col, direction)
                    if kind in (("TANK", opp), ("BASE", opp)):
                        bonus += 28.0
                return bonus

            if action == STAY:
                return -15.0
            return 0.0

        return sorted(actions, key=move_priority, reverse=True)
