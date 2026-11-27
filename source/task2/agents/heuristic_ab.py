"""Heuristic Alpha-Beta with move ordering and transposition table."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass

from ..config import STAY
from ..engine.game_engine import TankBattleEngine
from ..engine.game_state import GameState
from .base_agent import BaseTankAgent, SearchMetrics
from .evaluation import TacticalEvaluator

EXACT = "exact"
LOWER = "lower"
UPPER = "upper"


@dataclass(frozen=True, slots=True)
class TTEntry:
    remaining_depth: int
    value: float
    bound: str
    action: str


class HeuristicAlphaBetaAgent(BaseTankAgent):
    def __init__(
        self,
        max_depth: int = 4,
        use_move_ordering: bool = True,
        use_transposition_table: bool = True,
        name: str = "Heuristic Alpha-Beta",
    ) -> None:
        super().__init__(name=name)
        if max_depth < 1:
            raise ValueError("max_depth must be at least 1.")
        self.max_depth = max_depth
        self.use_move_ordering = use_move_ordering
        self.use_transposition_table = use_transposition_table
        self._explored = 0
        self._pruned = 0
        self._tt_hits = 0
        self._max_depth_seen = 0
        self._tt: dict[tuple, TTEntry] = {}

    def choose_action(self, state: GameState) -> str:
        started = time.perf_counter()
        self._explored = 0
        self._pruned = 0
        self._tt_hits = 0
        self._max_depth_seen = 0
        self._tt.clear()
        root = state.current_player
        best_value, best_action = self._search(
            state,
            0,
            -math.inf,
            math.inf,
            root,
        )
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        self.last_metrics = SearchMetrics(
            explored_states=self._explored,
            elapsed_ms=elapsed_ms,
            depth_reached=self._max_depth_seen,
            pruned_branches=self._pruned,
            tt_hits=self._tt_hits,
            best_value=best_value,
            chosen_action=best_action,
        )
        return best_action

    def _search(
        self,
        state: GameState,
        depth: int,
        alpha: float,
        beta: float,
        root_player: int,
    ) -> tuple[float, str]:
        self._explored += 1
        self._max_depth_seen = max(self._max_depth_seen, depth)
        if state.is_terminal():
            return self._terminal_value(state, root_player, depth), STAY
        if depth >= self.max_depth:
            return TacticalEvaluator.evaluate(state, root_player), STAY

        alpha_original = alpha
        beta_original = beta
        remaining_depth = self.max_depth - depth
        tt_key = state.state_key()
        tt_entry: TTEntry | None = None

        if self.use_transposition_table:
            tt_entry = self._tt.get(tt_key)
            if tt_entry is not None and tt_entry.remaining_depth >= remaining_depth:
                self._tt_hits += 1
                if tt_entry.bound == EXACT:
                    return tt_entry.value, tt_entry.action
                if tt_entry.bound == LOWER:
                    alpha = max(alpha, tt_entry.value)
                elif tt_entry.bound == UPPER:
                    beta = min(beta, tt_entry.value)
                if alpha >= beta:
                    self._pruned += 1
                    return tt_entry.value, tt_entry.action

        legal = state.legal_actions()
        if self.use_move_ordering and len(legal) > 1:
            legal = TacticalEvaluator.order_actions(state, legal)

        maximizing = state.current_player == root_player
        best_value = -math.inf if maximizing else math.inf
        best_action = legal[0]

        for action in legal:
            child = TankBattleEngine.apply_action(state, action)
            value, _ = self._search(
                child,
                depth + 1,
                alpha,
                beta,
                root_player,
            )
            if maximizing:
                if value > best_value:
                    best_value, best_action = value, action
                alpha = max(alpha, best_value)
            else:
                if value < best_value:
                    best_value, best_action = value, action
                beta = min(beta, best_value)
            if beta <= alpha:
                self._pruned += 1
                break

        if self.use_transposition_table:
            if best_value <= alpha_original:
                bound = UPPER
            elif best_value >= beta_original:
                bound = LOWER
            else:
                bound = EXACT
            self._tt[tt_key] = TTEntry(
                remaining_depth,
                best_value,
                bound,
                best_action,
            )
        return best_value, best_action
