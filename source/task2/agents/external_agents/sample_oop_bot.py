"""Example external student group bot using Protocol 1: subclassing BaseTankAgent."""

from __future__ import annotations

import time

from task2.agents.base_agent import BaseTankAgent, SearchMetrics
from task2.agents.evaluation import TacticalEvaluator
from task2.engine.game_engine import TankBattleEngine
from task2.engine.game_state import GameState


class ExternalGreedyStrikerBot(BaseTankAgent):
    """Sample 1-ply greedy lookahead bot illustrating OOP external integration."""

    def __init__(self) -> None:
        super().__init__(name="Ext: GreedyStriker (OOP)")

    def choose_action(self, state: GameState) -> str:
        t0 = time.perf_counter()
        me = state.current_player
        legal = state.legal_actions()
        best_action = legal[0]
        best_score = float("-inf")

        for act in legal:
            nxt = TankBattleEngine.apply_action(state, act)
            score = TacticalEvaluator.evaluate(nxt, me)
            if score > best_score:
                best_score = score
                best_action = act

        elapsed = (time.perf_counter() - t0) * 1000.0
        self.last_metrics = SearchMetrics(
            explored_states=len(legal),
            elapsed_ms=elapsed,
            depth_reached=1,
            best_value=best_score,
            chosen_action=best_action,
        )
        return best_action
