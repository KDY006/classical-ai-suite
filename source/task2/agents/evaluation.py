"""Ham luong gia chien thuat EVAL(s) va sap xep nuoc di cho tim kiem cat do sau."""

from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, Optional, Tuple

from ..config import (
    BULLET_SPEED_PER_CYCLE,
    DIRECTION_DELTAS,
    DIRECTIONS,
    MOVE_ACTION_TO_DIR,
)
from ..engine.game_state import GameState

TraceResult = tuple[str, int | None, int]
Coord = Tuple[int, int]


class TacticalEvaluator:
    """Luong gia trang thai tong bang khong (antisymmetric) va uu tien nuoc di."""

    W_TANK_HP = 130.0
    W_BASE_HP = 165.0
    W_SHIELD_HP = 7.5
    W_APPROACH_BASE = 6.0
    W_APPROACH_TANK = 3.0
    W_LINE_OF_FIRE = 28.0
    W_AXIS_ALIGN = 9.0
    W_BULLET_THREAT = 70.0
    W_STEEL_BLOCK_PENALTY = 5.0

    # Cache khoang cach ngan nhat ne tuong thep tinh cho moi cau hinh ban do (O(1) khi tra cuu)
    _STEEL_DIST_CACHE: Dict[Tuple[int, int, frozenset[Coord], Coord], Dict[Coord, int]] = {}

    @classmethod
    def _steel_distance_map(cls, state: GameState, target: Coord) -> Dict[Coord, int]:
        """Tinh BFS khoang cach ngan nhat den target co tranh cac o tuong thep bat tu."""
        key = (state.rows, state.cols, state.steel_walls, target)
        cached = cls._STEEL_DIST_CACHE.get(key)
        if cached is not None:
            return cached

        dist: Dict[Coord, int] = {target: 0}
        queue: deque[Coord] = deque([target])
        steel = state.steel_walls
        rows, cols = state.rows, state.cols

        while queue:
            r, c = queue.popleft()
            d_next = dist[(r, c)] + 1
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                pos = (nr, nc)
                if 0 <= nr < rows and 0 <= nc < cols and pos not in steel and pos not in dist:
                    dist[pos] = d_next
                    queue.append(pos)

        cls._STEEL_DIST_CACHE[key] = dist
        return dist

    @classmethod
    def steel_aware_distance(cls, state: GameState, src: Coord, dst: Coord) -> int:
        """Tra ve khoang cach ngan nhat co ne tuong thep giua src va dst."""
        dist_map = cls._steel_distance_map(state, dst)
        return dist_map.get(src, abs(src[0] - dst[0]) + abs(src[1] - dst[1]) + 4)

    @classmethod
    def evaluate(cls, state: GameState, perspective: int) -> float:
        """Tinh diem luong gia doi xung: evaluate(s, MAX) == -evaluate(s, MIN)."""
        if state.is_terminal():
            return state.utility(perspective)

        opponent = GameState.opponent(perspective)
        my_tank = state.tanks[perspective]
        opp_tank = state.tanks[opponent]
        my_base = state.bases[perspective]
        opp_base = state.bases[opponent]

        # 1. Chenh lech sinh luc xe tang va can cu
        score = cls.W_TANK_HP * (my_tank.hp - opp_tank.hp)
        score += cls.W_BASE_HP * (my_base.hp - opp_base.hp)

        # 2. Chenh lech do ben lop tuong gach bao ve quanh hai can cu (khuyen khich pha tuong dich)
        my_shield = cls._base_shield_hp(state, my_base.row, my_base.col)
        opp_shield = cls._base_shield_hp(state, opp_base.row, opp_base.col)
        score += cls.W_SHIELD_HP * (my_shield - opp_shield)

        # 3. Khoang cach tiep can can cu co ne tuong thep (tranh ket sau tru thep trung tam)
        my_to_opp_base = cls.steel_aware_distance(
            state, (my_tank.row, my_tank.col), (opp_base.row, opp_base.col)
        )
        opp_to_my_base = cls.steel_aware_distance(
            state, (opp_tank.row, opp_tank.col), (my_base.row, my_base.col)
        )
        score += cls.W_APPROACH_BASE * (opp_to_my_base - my_to_opp_base)

        # 4. Diem tuyen ban truc dien, can truc tan cong thong thoang va phat quay vao tuong thep
        score += cls._positional_offense_score(state, perspective) - cls._positional_offense_score(
            state, opponent
        )

        # 5. Moi de doa tu cac vien dan dang bay tren san
        for bullet in state.bullets:
            kind, target_id, distance = cls.trace_target(
                state,
                bullet.row,
                bullet.col,
                bullet.direction,
            )
            urgency = max(0.25, 1.0 - distance / (BULLET_SPEED_PER_CYCLE * 3.0))
            if target_id == opponent and kind in ("TANK", "BASE"):
                score += cls.W_BULLET_THREAT * urgency
            elif target_id == perspective and kind in ("TANK", "BASE"):
                score -= cls.W_BULLET_THREAT * urgency
        return score

    @staticmethod
    def _base_shield_hp(state: GameState, base_row: int, base_col: int) -> int:
        """Tong HP cac o tuong gach trong ban kinh 2 o bao quanh can cu."""
        total = 0
        for (r, c), wall in state.brick_walls.items():
            if wall.hp > 0 and abs(r - base_row) + abs(c - base_col) <= 2:
                total += wall.hp
        return total

    @classmethod
    def _positional_offense_score(cls, state: GameState, player_id: int) -> float:
        """Tinh diem chiem tuyen ban va can truc tan cong cho mot phe."""
        tank = state.tanks[player_id]
        opponent = GameState.opponent(player_id)
        opp_base = state.bases[opponent]

        # Kiem tra muc tieu theo huong nong dang quay
        kind, target_id, distance = cls.trace_target(state, tank.row, tank.col, tank.facing)
        score = 0.0
        if target_id == opponent and kind == "TANK":
            score += cls.W_LINE_OF_FIRE * (1.6 / (1.0 + 0.14 * distance))
        elif target_id == opponent and kind == "BASE":
            score += cls.W_LINE_OF_FIRE * (1.5 / (1.0 + 0.14 * distance))
        elif kind == "WALL_NEAR_BASE" and target_id == opponent:
            score += cls.W_LINE_OF_FIRE * 0.75
        elif kind == "WALL":
            score += cls.W_LINE_OF_FIRE * 0.25
        elif kind == "STEEL" and distance == 1:
            score -= cls.W_STEEL_BLOCK_PENALTY

        # Thuong khi dung tren truc ngang/doc thong thoang (khong bi thep chan) toi dich
        best_axis = 0.0
        for direction in DIRECTIONS:
            d_kind, d_target, d_dist = cls.trace_target(state, tank.row, tank.col, direction)
            if d_target == opponent and d_kind in ("TANK", "BASE"):
                best_axis = max(best_axis, cls.W_AXIS_ALIGN / (1.0 + 0.12 * d_dist))
            elif d_kind == "WALL_NEAR_BASE" and d_target == opponent:
                best_axis = max(best_axis, cls.W_AXIS_ALIGN * 0.55)
        score += best_axis

        # Thuong tien gan hon den tuong gach che chan can cu dich
        dr, dc = DIRECTION_DELTAS[tank.facing]
        r, c = tank.row + dr, tank.col + dc
        while state.in_bounds(r, c) and (r, c) not in state.steel_walls:
            wall = state.brick_walls.get((r, c))
            if wall is not None and wall.hp > 0:
                tank_dist = abs(tank.row - opp_base.row) + abs(tank.col - opp_base.col)
                wall_dist = abs(r - opp_base.row) + abs(c - opp_base.col)
                if wall_dist < tank_dist:
                    score += 8.0 * (3 - wall.hp)
                break
            r += dr
            c += dc

        return score

    @classmethod
    def trace_target(
        cls,
        state: GameState,
        start_row: int,
        start_col: int,
        direction: str,
    ) -> TraceResult:
        """Do tia theo huong direction tra ve (loai vat can dau tien, ma phe, khoang cach)."""
        dr, dc = DIRECTION_DELTAS[direction]
        row, col = start_row, start_col
        distance = 0
        while True:
            row += dr
            col += dc
            distance += 1
            if not state.in_bounds(row, col):
                return "NONE", None, distance
            if (row, col) in state.steel_walls:
                return "STEEL", None, distance

            wall = state.brick_walls.get((row, col))
            if wall is not None and wall.hp > 0:
                for player_id, base in state.bases.items():
                    if base.hp > 0 and abs(row - base.row) + abs(col - base.col) <= 2:
                        return "WALL_NEAR_BASE", player_id, distance
                return "WALL", None, distance

            for player_id, base in state.bases.items():
                if base.hp > 0 and (base.row, base.col) == (row, col):
                    return "BASE", player_id, distance
            for player_id, tank in state.tanks.items():
                if tank.hp > 0 and (tank.row, tank.col) == (row, col):
                    return "TANK", player_id, distance

    @classmethod
    def order_actions(
        cls,
        state: GameState,
        actions: Iterable[str],
        tt_best_action: Optional[str] = None,
    ) -> list[str]:
        """Sap xep nuoc di trien vong len truoc de toi da hoa ty le cat tia Alpha-Beta."""
        player_id = state.current_player
        opponent = GameState.opponent(player_id)
        tank = state.tanks[player_id]
        opponent_base = state.bases[opponent]
        opponent_tank = state.tanks[opponent]

        enemy_bullet_threat = False
        for bullet in state.bullets:
            if bullet.owner_id == player_id:
                continue
            kind, target_id, _ = cls.trace_target(state, bullet.row, bullet.col, bullet.direction)
            if kind in ("TANK", "BASE") and target_id == player_id:
                enemy_bullet_threat = True
                break

        base_dist_now = cls.steel_aware_distance(
            state, (tank.row, tank.col), (opponent_base.row, opponent_base.col)
        )
        tank_dist_now = cls.steel_aware_distance(
            state, (tank.row, tank.col), (opponent_tank.row, opponent_tank.col)
        )

        def priority(action: str) -> float:
            if tt_best_action is not None and action == tt_best_action:
                return 1000.0

            if action == "FIRE":
                kind, target_id, distance = cls.trace_target(
                    state, tank.row, tank.col, tank.facing
                )
                if target_id == opponent and kind in ("TANK", "BASE"):
                    return 120.0 - distance
                if kind == "WALL_NEAR_BASE" and target_id == opponent:
                    return 65.0
                if kind == "WALL":
                    return 30.0
                if kind == "STEEL":
                    return -25.0
                return 5.0

            if action in MOVE_ACTION_TO_DIR:
                direction = MOVE_ACTION_TO_DIR[action]
                dr, dc = DIRECTION_DELTAS[direction]
                next_row, next_col = tank.row + dr, tank.col + dc
                walkable = state.is_cell_walkable(next_row, next_col)
                bonus = 50.0 if (enemy_bullet_threat and walkable) else 0.0

                if walkable:
                    base_dist_next = cls.steel_aware_distance(
                        state, (next_row, next_col), (opponent_base.row, opponent_base.col)
                    )
                    tank_dist_next = cls.steel_aware_distance(
                        state, (next_row, next_col), (opponent_tank.row, opponent_tank.col)
                    )
                    bonus += 18.0 * (base_dist_now - base_dist_next)
                    bonus += 8.0 * (tank_dist_now - tank_dist_next)
                else:
                    kind, target_id, _ = cls.trace_target(state, tank.row, tank.col, direction)
                    if target_id == opponent and kind in ("TANK", "BASE"):
                        bonus += 40.0
                    elif kind == "WALL_NEAR_BASE" and target_id == opponent:
                        bonus += 20.0
                return bonus

            if action == "STAY":
                return -18.0
            return 0.0

        return sorted(actions, key=priority, reverse=True)
