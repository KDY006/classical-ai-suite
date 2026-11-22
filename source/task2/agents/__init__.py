"""Tank Battle agents and external bot discovery."""

from .alphabeta_agent import AlphaBetaAgent
from .base_agent import (
    BaseTankAgent,
    DictAdapterTankAgent,
    SearchMetrics,
    discover_external_agents,
)
from .evaluation import TacticalEvaluator
from .heuristic_ab import EXACT, LOWER, TTEntry, UPPER, HeuristicAlphaBetaAgent
from .heuristic_minimax import HeuristicMinimaxAgent
from .minimax_agent import MinimaxAgent

__all__ = [
    "BaseTankAgent",
    "DictAdapterTankAgent",
    "SearchMetrics",
    "discover_external_agents",
    "TacticalEvaluator",
    "MinimaxAgent",
    "AlphaBetaAgent",
    "HeuristicMinimaxAgent",
    "HeuristicAlphaBetaAgent",
    "TTEntry",
    "EXACT",
    "LOWER",
    "UPPER",
]
