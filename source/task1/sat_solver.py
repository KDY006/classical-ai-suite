"""Run the Glucose3 SAT solver on an encoded N-Queens instance."""

from dataclasses import dataclass
from time import perf_counter

from pysat.solvers import Glucose3

from .board import NQueenBoard
from .cnf_encoder import CNFEncodingStats, NQueenCNFEncoder


@dataclass
class SATSolveResult:
    n: int
    satisfiable: bool
    num_variables: int
    num_clauses: int
    encoding_stats: CNFEncodingStats
    encoding_time_sec: float
    solve_time_sec: float
    board: NQueenBoard | None = None

    @property
    def total_time_sec(self):
        return self.encoding_time_sec + self.solve_time_sec


class Glucose3NQueenSolver:
    def __init__(self, include_col_alo=True):
        self.include_col_alo = include_col_alo

    def solve(self, n):
        started = perf_counter()
        clauses, stats = NQueenCNFEncoder(n, self.include_col_alo).encode()
        encoding_time = perf_counter() - started
        started = perf_counter()
        with Glucose3(bootstrap_with=clauses) as solver:
            satisfiable = solver.solve()
            model = solver.get_model() if satisfiable else None
        solve_time = perf_counter() - started
        board = NQueenBoard.from_sat_model(n, model) if model is not None else None
        return SATSolveResult(n, satisfiable, stats.num_variables, stats.total_clauses,
                              stats, encoding_time, solve_time, board)
