"""PySAT Glucose3 solver wrapper for the N-Queen CNF formulation."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from pysat.solvers import Glucose3

from .board import NQueenBoard
from .cnf_encoder import CNFEncodingStats, NQueenCNFEncoder


@dataclass
class SATSolveResult:
    """Stores results and timing metrics of a Glucose3 N-Queen run."""

    n: int
    satisfiable: bool
    num_variables: int
    num_clauses: int
    encoding_stats: CNFEncodingStats
    encoding_time_sec: float
    solve_time_sec: float
    board: Optional[NQueenBoard] = None

    @property
    def total_time_sec(self) -> float:
        return self.encoding_time_sec + self.solve_time_sec


class Glucose3NQueenSolver:
    """Solves the N-Queen problem by encoding constraints into CNF and invoking Glucose3."""

    def __init__(self, include_col_alo: bool = True) -> None:
        self.include_col_alo: bool = include_col_alo

    def solve(self, n: int) -> SATSolveResult:
        """Encode and solve the N-Queen instance of size ``n`` using Glucose3."""
        t0 = time.perf_counter()
        encoder = NQueenCNFEncoder(n=n, include_col_alo=self.include_col_alo)
        clauses, stats = encoder.encode()
        encoding_time = time.perf_counter() - t0

        t1 = time.perf_counter()
        with Glucose3(bootstrap_with=clauses) as solver:
            is_sat = solver.solve()
            model = solver.get_model() if is_sat else None
        solve_time = time.perf_counter() - t1

        board = NQueenBoard.from_sat_model(n, model) if (is_sat and model is not None) else None
        return SATSolveResult(
            n=n,
            satisfiable=is_sat,
            num_variables=stats.num_variables,
            num_clauses=stats.total_clauses,
            encoding_stats=stats,
            encoding_time_sec=encoding_time,
            solve_time_sec=solve_time,
            board=board,
        )
