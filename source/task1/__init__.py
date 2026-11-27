"""Nhiem vu 1: Bo giai N Quan Hau bang Logic menh de (Glucose3) va Min-Conflicts."""

from .base_solver import BaseNQueenSolver
from .board import NQueenBoard
from .cnf_encoder import (
    CNFEncodingStats,
    NQueenCNFEncoder,
    PropositionalRule,
    PropositionalVariableMapper,
)
from .min_conflicts import (
    AdaptiveTabuMaxConflictSelector,
    LocalSearchResult,
    MinConflictsSolver,
    PureMaxConflictSelector,
    RandomConflictedSelector,
    StepSnapshot,
    TabuMaxConflictSelector,
    VariableSelectionStrategy,
)
from .sat_solver import Glucose3NQueenSolver, SATSolveResult

__all__ = [
    "BaseNQueenSolver",
    "NQueenBoard",
    "PropositionalVariableMapper",
    "PropositionalRule",
    "CNFEncodingStats",
    "NQueenCNFEncoder",
    "Glucose3NQueenSolver",
    "SATSolveResult",
    "VariableSelectionStrategy",
    "RandomConflictedSelector",
    "PureMaxConflictSelector",
    "AdaptiveTabuMaxConflictSelector",
    "TabuMaxConflictSelector",
    "StepSnapshot",
    "LocalSearchResult",
    "MinConflictsSolver",
]
