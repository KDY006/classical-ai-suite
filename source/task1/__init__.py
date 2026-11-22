"""Task 1: N-Queen Solver using Propositional Logic (Glucose3) and Local Search (Min-Conflicts)."""

from .board import NQueenBoard
from .cnf_encoder import NQueenCNFEncoder, PropositionalVariableMapper
from .sat_solver import Glucose3NQueenSolver, SATSolveResult
from .min_conflicts import (
    LocalSearchResult,
    MinConflictsSolver,
    RandomConflictedSelector,
    TabuMaxConflictSelector,
)

__all__ = [
    "NQueenBoard",
    "PropositionalVariableMapper",
    "NQueenCNFEncoder",
    "Glucose3NQueenSolver",
    "SATSolveResult",
    "MinConflictsSolver",
    "RandomConflictedSelector",
    "TabuMaxConflictSelector",
    "LocalSearchResult",
]
