"""Configuration 2: Pure Alpha-Beta Pruning Search agent (no heuristic cutoff)."""

from __future__ import annotations

import math
import time
from typing import Optional, Tuple

from ..config import STAY
from ..engine.game_engine import TankBattleEngine
from ..engine.game_state import GameState
from .base_agent import BaseTankAgent, SearchMetrics


class AlphaBetaAgent(BaseTankAgent):
    """Exact Alpha-Beta Search returning the identical minimax decision with fewer states."""

    def __init__(self, max_ply_cap: Optional[int] = 7, name: str = "Alpha-Beta Search") -> None:
        super().__init__(name=name)
        self.max_ply_cap: Optional[int] = max_ply_cap
        self._explored: int = 0
        self._pruned: int = 0
        self._max_depth_seen: int = 0

    def choose_action(self, state: GameState) -> str:
        t0 = time.perf_counter()
        self._explored = 0
        self._pruned = 0
        self._max_depth_seen = 0
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
            tt_hits=0,
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

        if state.is_terminal() or (self.max_ply_cap is not None and depth >= self.max_ply_cap):
            u = state.utility(root_player)
            if u > 0:
                u -= 0.01 * depth
            elif u < 0:
                u += 0.01 * depth
            return u, STAY

        legal = state.legal_actions()
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
            return best_val, best_act
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
            return best_val, best_act
