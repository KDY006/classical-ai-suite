"""Configuration 4: Heuristic Minimax with Alpha-Beta Pruning, Move Ordering & Transposition Table."""

from __future__ import annotations

import math
import time
from typing import Dict, Tuple

from ..config import STAY
from ..engine.game_engine import TankBattleEngine
from ..engine.game_state import GameState
from .base_agent import BaseTankAgent, SearchMetrics
from .evaluation import TacticalEvaluator

TT_EXACT = 0
TT_LOWER = 1
TT_UPPER = 2


class HeuristicAlphaBetaAgent(BaseTankAgent):
    """Real-time optimized Adversarial Search combining Heuristic Minimax, Alpha-Beta Pruning,
    Tactical Move Ordering, and a Transposition Table.
    """

    def __init__(
        self,
        max_depth: int = 4,
        use_move_ordering: bool = True,
        use_transposition_table: bool = True,
        name: str = "Heuristic Alpha-Beta",
    ) -> None:
        super().__init__(name=name)
        self.max_depth: int = max_depth
        self.use_move_ordering: bool = use_move_ordering
        self.use_transposition_table: bool = use_transposition_table

        self._explored: int = 0
        self._pruned: int = 0
        self._tt_hits: int = 0
        self._max_depth_seen: int = 0
        self._tt: Dict[tuple, Tuple[int, float, int, str]] = {}

    def choose_action(self, state: GameState) -> str:
        t0 = time.perf_counter()
        self._explored = 0
        self._pruned = 0
        self._tt_hits = 0
        self._max_depth_seen = 0
        self._tt.clear()
        root_player = state.current_player

        best_val, best_act = self._alphabeta(
            state=state,
            depth=0,
            alpha=-math.inf,
            beta=math.inf,
            root_player=root_player,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        self.last_metrics = SearchMetrics(
            explored_states=self._explored,
            elapsed_ms=elapsed_ms,
            depth_reached=self._max_depth_seen,
            pruned_branches=self._pruned,
            tt_hits=self._tt_hits,
            best_value=best_val,
            chosen_action=best_act,
        )
        return best_act

    def _alphabeta(
        self,
        state: GameState,
        depth: int,
        alpha: float,
        beta: float,
        root_player: int,
    ) -> Tuple[float, str]:
        self._explored += 1
        if depth > self._max_depth_seen:
            self._max_depth_seen = depth

        if state.is_terminal():
            u = state.utility(root_player)
            if u > 0:
                u -= 0.01 * depth
            elif u < 0:
                u += 0.01 * depth
            return u, STAY

        if depth >= self.max_depth:
            return TacticalEvaluator.evaluate(state, root_player), STAY

        rem_depth = self.max_depth - depth
        alpha_orig = alpha
        beta_orig = beta
        tt_key = state.state_key()

        if self.use_transposition_table and tt_key in self._tt:
            stored_rem, stored_val, flag, stored_act = self._tt[tt_key]
            if stored_rem >= rem_depth:
                self._tt_hits += 1
                if flag == TT_EXACT:
                    return stored_val, stored_act
                elif flag == TT_LOWER:
                    alpha = max(alpha, stored_val)
                elif flag == TT_UPPER:
                    beta = min(beta, stored_val)
                if alpha >= beta:
                    self._pruned += 1
                    return stored_val, stored_act

        legal = state.legal_actions()
        if self.use_move_ordering and len(legal) > 1:
            legal = TacticalEvaluator.order_actions(state, legal)

        maximizing = state.current_player == root_player

        if maximizing:
            best_val = -math.inf
            best_act = legal[0]
            for act in legal:
                child = TankBattleEngine.apply_action(state, act)
                val, _ = self._alphabeta(child, depth + 1, alpha, beta, root_player)
                if val > best_val:
                    best_val = val
                    best_act = act
                alpha = max(alpha, best_val)
                if beta <= alpha:
                    self._pruned += 1
                    break
        else:
            best_val = math.inf
            best_act = legal[0]
            for act in legal:
                child = TankBattleEngine.apply_action(state, act)
                val, _ = self._alphabeta(child, depth + 1, alpha, beta, root_player)
                if val < best_val:
                    best_val = val
                    best_act = act
                beta = min(beta, best_val)
                if beta <= alpha:
                    self._pruned += 1
                    break

        if self.use_transposition_table:
            if best_val <= alpha_orig:
                flag = TT_UPPER
            elif best_val >= beta_orig:
                flag = TT_LOWER
            else:
                flag = TT_EXACT
            self._tt[tt_key] = (rem_depth, best_val, flag, best_act)

        return best_val, best_act
