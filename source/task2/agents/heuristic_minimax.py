"""Configuration 3: Heuristic Minimax Search agent (depth cutoff + EVAL(s), no pruning)."""

from __future__ import annotations

import math
import time
from typing import Tuple

from ..config import STAY
from ..engine.game_engine import TankBattleEngine
from ..engine.game_state import GameState
from .base_agent import BaseTankAgent, SearchMetrics
from .evaluation import TacticalEvaluator


class HeuristicMinimaxAgent(BaseTankAgent):
    """Depth-limited Minimax Search replacing CUTOFF-TEST leaves with EVAL(s)."""

    def __init__(self, max_depth: int = 4, name: str = "Heuristic Minimax") -> None:
        super().__init__(name=name)
        self.max_depth: int = max_depth
        self._explored: int = 0
        self._max_depth_seen: int = 0

    def choose_action(self, state: GameState) -> str:
        t0 = time.perf_counter()
        self._explored = 0
        self._max_depth_seen = 0
        root_player = state.current_player

        best_val, best_act = self._search(state, depth=0, root_player=root_player)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        self.last_metrics = SearchMetrics(
            explored_states=self._explored,
            elapsed_ms=elapsed_ms,
            depth_reached=self._max_depth_seen,
            pruned_branches=0,
            tt_hits=0,
            best_value=best_val,
            chosen_action=best_act,
        )
        return best_act

    def _search(self, state: GameState, depth: int, root_player: int) -> Tuple[float, str]:
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

        legal = state.legal_actions()
        maximizing = state.current_player == root_player

        if maximizing:
            best_val = -math.inf
            best_act = legal[0]
            for act in legal:
                child = TankBattleEngine.apply_action(state, act)
                val, _ = self._search(child, depth + 1, root_player)
                if val > best_val:
                    best_val = val
                    best_act = act
            return best_val, best_act
        else:
            best_val = math.inf
            best_act = legal[0]
            for act in legal:
                child = TankBattleEngine.apply_action(state, act)
                val, _ = self._search(child, depth + 1, root_player)
                if val < best_val:
                    best_val = val
                    best_act = act
            return best_val, best_act
