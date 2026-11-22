"""Propositional Logic formulation and CNF encoding for the N-Queen problem."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


class PropositionalVariableMapper:
    """Bijective mapping between 2D board squares (row, col) and DIMACS variables 1..N^2."""

    def __init__(self, n: int) -> None:
        if n < 1:
            raise ValueError(f"Board size n must be >= 1, got {n}.")
        self.n: int = n

    @property
    def num_variables(self) -> int:
        return self.n * self.n

    def to_var(self, row: int, col: int) -> int:
        """Map square (row, col) to positive integer variable in [1, N^2]."""
        if not (0 <= row < self.n and 0 <= col < self.n):
            raise ValueError(f"Coordinates ({row}, {col}) out of bounds for N={self.n}.")
        return row * self.n + col + 1

    def to_coord(self, variable: int) -> Tuple[int, int]:
        """Map positive or negative literal back to board square (row, col)."""
        var_id = abs(variable)
        if not (1 <= var_id <= self.num_variables):
            raise ValueError(f"Variable {var_id} out of range [1, {self.num_variables}].")
        return divmod(var_id - 1, self.n)


@dataclass(frozen=True)
class CNFEncodingStats:
    """Breakdown of generated propositional variables and CNF clauses."""

    n: int
    num_variables: int
    row_alo_clauses: int
    col_alo_clauses: int
    row_amo_clauses: int
    col_amo_clauses: int
    diag_amo_clauses: int

    @property
    def total_clauses(self) -> int:
        return (
            self.row_alo_clauses
            + self.col_alo_clauses
            + self.row_amo_clauses
            + self.col_amo_clauses
            + self.diag_amo_clauses
        )


class NQueenCNFEncoder:
    """Discovers N-Queen propositional constraints and converts them into CNF clauses.

    Propositional formulation:
      - Variables: P(r, c) is True iff square (r, c) contains a queen.
      - Existence (At-Least-One):
          For every row r: P(r, 0) v P(r, 1) v ... v P(r, N-1)
          (Optionally for every column c as well to strengthen unit propagation.)
      - Non-attacking (At-Most-One via pairwise implication):
          For every pair of distinct attacking cells (r1, c1) and (r2, c2) sharing a row,
          column, main diagonal (r1 - c1 = r2 - c2), or anti-diagonal (r1 + c1 = r2 + c2):
              P(r1, c1) => ~P(r2, c2)
          Eliminating implication (alpha => beta  ===  ~alpha v beta) directly yields
          the binary CNF clause:
              (~P(r1, c1) v ~P(r2, c2))
    """

    def __init__(self, n: int, include_col_alo: bool = True) -> None:
        if n < 1:
            raise ValueError(f"N-Queen requires n >= 1, got {n}.")
        self.n: int = n
        self.include_col_alo: bool = include_col_alo
        self.mapper = PropositionalVariableMapper(n)

    def encode(self) -> Tuple[List[List[int]], CNFEncodingStats]:
        """Generate all CNF clauses and exact structural statistics for board size N."""
        n = self.n
        to_var = self.mapper.to_var
        clauses: List[List[int]] = []

        # 1. Row At-Least-One clauses: each row has at least one queen
        for r in range(n):
            clauses.append([to_var(r, c) for c in range(n)])
        row_alo_count = n

        # 2. Optional Column At-Least-One clauses: each column has at least one queen
        col_alo_count = 0
        if self.include_col_alo:
            for c in range(n):
                clauses.append([to_var(r, c) for r in range(n)])
            col_alo_count = n

        # 3. Row At-Most-One binary clauses: ~P(r, c1) v ~P(r, c2)
        row_amo_count = 0
        for r in range(n):
            for c1 in range(n):
                v1 = -to_var(r, c1)
                for c2 in range(c1 + 1, n):
                    clauses.append([v1, -to_var(r, c2)])
                    row_amo_count += 1

        # 4. Column At-Most-One binary clauses: ~P(r1, c) v ~P(r2, c)
        col_amo_count = 0
        for c in range(n):
            for r1 in range(n):
                v1 = -to_var(r1, c)
                for r2 in range(r1 + 1, n):
                    clauses.append([v1, -to_var(r2, c)])
                    col_amo_count += 1

        # 5. Diagonal At-Most-One binary clauses (main and anti-diagonals)
        diag_amo_count = 0
        main_diags: Dict[int, List[int]] = {}
        anti_diags: Dict[int, List[int]] = {}
        for r in range(n):
            for c in range(n):
                v = to_var(r, c)
                main_diags.setdefault(r - c, []).append(v)
                anti_diags.setdefault(r + c, []).append(v)

        for diag_vars in main_diags.values():
            k = len(diag_vars)
            for i in range(k):
                vi = -diag_vars[i]
                for j in range(i + 1, k):
                    clauses.append([vi, -diag_vars[j]])
                    diag_amo_count += 1

        for diag_vars in anti_diags.values():
            k = len(diag_vars)
            for i in range(k):
                vi = -diag_vars[i]
                for j in range(i + 1, k):
                    clauses.append([vi, -diag_vars[j]])
                    diag_amo_count += 1

        stats = CNFEncodingStats(
            n=n,
            num_variables=self.mapper.num_variables,
            row_alo_clauses=row_alo_count,
            col_alo_clauses=col_alo_count,
            row_amo_clauses=row_amo_count,
            col_amo_clauses=col_amo_count,
            diag_amo_clauses=diag_amo_count,
        )
        return clauses, stats

    def theoretical_clause_count(self) -> int:
        """Closed-form verification of the total number of generated CNF clauses."""
        n = self.n
        alo = 2 * n if self.include_col_alo else n
        row_col_amo = n * n * (n - 1)
        diag_amo = n * (n - 1) * (2 * n - 1) // 3
        return alo + row_col_amo + diag_amo
