"""Cau hinh 1: Thuat toan Minimax thuan tuy (khong cat tia, khong heuristic)."""

from __future__ import annotations

import math
import time
from typing import Optional

from ..config import STAY
from ..engine.game_engine import TankBattleEngine
from ..engine.game_state import GameState
from .base_agent import BaseTankAgent, SearchMetrics


class MinimaxAgent(BaseTankAgent):
    """Tac tu Minimax thuan tuy duyet toan bo cay den trang thai ket thuc hoac gioi han ply."""

    def __init__(
        self,
        max_ply_cap: Optional[int] = 6,
        name: str = "Minimax thuần",
        cli_name: Optional[str] = None,
    ) -> None:
        super().__init__(name=name, cli_name=cli_name)
        self.max_ply_cap = max_ply_cap
        self._explored = 0
        self._max_depth_seen = 0

    def choose_action(self, state: GameState) -> str:
        started = time.perf_counter()
        self._explored = 0
        self._max_depth_seen = 0
        root = state.current_player
        best_value, best_action = self._search(state, 0, root)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        self.last_metrics = SearchMetrics(
            explored_states=self._explored,
            elapsed_ms=elapsed_ms,
            depth_reached=self._max_depth_seen,
            pruned_branches=0,
            tt_hits=0,
            best_value=best_value,
            chosen_action=best_action,
        )
        return best_action

    def _search(
        self,
        state: GameState,
        depth: int,
        root_player: int,
    ) -> tuple[float, str]:
        self._explored += 1
        self._max_depth_seen = max(self._max_depth_seen, depth)
        if state.is_terminal():
            return self._terminal_value(state, root_player, depth), STAY
        if self.max_ply_cap is not None and depth >= self.max_ply_cap:
            return 0.0, STAY

        legal = state.legal_actions()
        maximizing = state.current_player == root_player
        best_value = -math.inf if maximizing else math.inf
        best_action = legal[0]
        for action in legal:
            child = TankBattleEngine.apply_action(state, action)
            value, _ = self._search(child, depth + 1, root_player)
            if maximizing and value > best_value:
                best_value, best_action = value, action
            elif not maximizing and value < best_value:
                best_value, best_action = value, action
        return best_value, best_action
