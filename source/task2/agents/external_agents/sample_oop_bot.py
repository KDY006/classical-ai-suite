"""Bot mau nhom ngoai chuan 1 (OOP): ke thua lop BaseTankAgent."""

from __future__ import annotations

import time

from task2.agents.base_agent import BaseTankAgent, SearchMetrics
from task2.agents.evaluation import TacticalEvaluator
from task2.engine.game_engine import TankBattleEngine
from task2.engine.game_state import GameState


class ExternalGreedyStrikerBot(BaseTankAgent):
    """Bot tham lam nhin truoc 1 nuoc minh hoa tich hop chuan OOP."""

    def __init__(self) -> None:
        super().__init__(
            name="Bot ngoài: Xung kích (OOP)",
            cli_name="Bot ngoai: Xung kich (OOP)",
        )

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
