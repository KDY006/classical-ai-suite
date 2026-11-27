"""Bo giai SAT Glucose3 (PySAT) cho bai toan N Quan Hau."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from time import perf_counter

from pysat.solvers import Glucose3

from .base_solver import BaseNQueenSolver
from .board import NQueenBoard
from .cnf_encoder import CNFEncodingStats, NQueenCNFEncoder


@dataclass(frozen=True)
class SATSolveResult:
    """Ket qua chi tiet sau khi ma hoa CNF va giai bang Glucose3."""

    n: int
    satisfiable: bool
    num_variables: int
    num_clauses: int
    encoding_stats: CNFEncodingStats
    encoding_time_sec: float
    solve_time_sec: float
    restarts: int
    conflicts: int
    decisions: int
    propagations: int
    board: NQueenBoard | None = None

    @property
    def total_time_sec(self) -> float:
        """Tong thoi gian gom ma hoa CNF va thuc thi Glucose3."""
        return self.encoding_time_sec + self.solve_time_sec


class Glucose3NQueenSolver(BaseNQueenSolver):
    """Cai dat bo giai N-Queen su dung thu vien PySAT Glucose3."""

    def __init__(self, include_col_alo: bool = True) -> None:
        self.include_col_alo: bool = include_col_alo

    @property
    def name(self) -> str:
        return "Glucose3 (SAT - CNF)"

    @property
    def cli_name(self) -> str:
        return "Glucose3 (SAT - CNF)"

    def solve(self, n: int, repeats: int = 1) -> SATSolveResult:
        """Ma hoa va giai N-Queen bang Glucose3, ho tro do trung vi nhieu lan."""
        if n < 1:
            raise ValueError("Kich thuoc ban co phai la so nguyen duong")
        if repeats < 1:
            raise ValueError("So lan lap do thoi gian phai lon hon hoac bang 1")

        enc_times: list[float] = []
        solve_times: list[float] = []
        satisfiable = False
        model: list[int] | None = None
        stats: CNFEncodingStats | None = None
        solver_stats: dict[str, int] = {}

        for _ in range(repeats):
            t_enc_start = perf_counter()
            clauses, stats = NQueenCNFEncoder(n, self.include_col_alo).encode()
            enc_times.append(perf_counter() - t_enc_start)

            t_solve_start = perf_counter()
            with Glucose3(bootstrap_with=clauses) as solver:
                satisfiable = bool(solver.solve())
                model = solver.get_model() if satisfiable else None
                solver_stats = solver.accum_stats()
            solve_times.append(perf_counter() - t_solve_start)

        assert stats is not None
        board = NQueenBoard.from_sat_model(n, model) if model is not None else None

        return SATSolveResult(
            n=n,
            satisfiable=satisfiable,
            num_variables=stats.num_variables,
            num_clauses=stats.total_clauses,
            encoding_stats=stats,
            encoding_time_sec=median(enc_times),
            solve_time_sec=median(solve_times),
            restarts=int(solver_stats.get("restarts", 0)),
            conflicts=int(solver_stats.get("conflicts", 0)),
            decisions=int(solver_stats.get("decisions", 0)),
            propagations=int(solver_stats.get("propagations", 0)),
            board=board,
        )
