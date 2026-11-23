"""Translate N-Queens constraints into clauses understood by a SAT solver."""

from dataclasses import dataclass
from itertools import combinations


class PropositionalVariableMapper:
    def __init__(self, n: int):
        if n < 1:
            raise ValueError("Board size must be positive")
        self.n = n
        self.num_variables = n * n

    def to_var(self, row: int, col: int) -> int:
        if not (0 <= row < self.n and 0 <= col < self.n):
            raise ValueError("Square is outside the board")
        return row * self.n + col + 1

    def to_coord(self, variable: int) -> tuple[int, int]:
        if not 1 <= abs(variable) <= self.num_variables:
            raise ValueError("Variable is outside the board")
        return divmod(abs(variable) - 1, self.n)


@dataclass(frozen=True)
class CNFEncodingStats:
    n: int
    num_variables: int
    row_alo_clauses: int
    col_alo_clauses: int
    row_amo_clauses: int
    col_amo_clauses: int
    diag_amo_clauses: int

    @property
    def total_clauses(self) -> int:
        return (self.row_alo_clauses + self.col_alo_clauses +
                self.row_amo_clauses + self.col_amo_clauses +
                self.diag_amo_clauses)


class NQueenCNFEncoder:
    def __init__(self, n: int, include_col_alo: bool = True):
        self.mapper = PropositionalVariableMapper(n)
        self.n = n
        self.include_col_alo = include_col_alo

    def encode(self) -> tuple[list[list[int]], CNFEncodingStats]:
        n = self.n
        var = self.mapper.to_var
        rows = [[var(r, c) for c in range(n)] for r in range(n)]
        columns = [[var(r, c) for r in range(n)] for c in range(n)]
        diagonals = {}
        antidiagonals = {}
        for r in range(n):
            for c in range(n):
                diagonals.setdefault(r - c, []).append(var(r, c))
                antidiagonals.setdefault(r + c, []).append(var(r, c))

        clauses = list(rows)
        if self.include_col_alo:
            clauses.extend(columns)

        counts = []
        for groups in (rows, columns, list(diagonals.values()) + list(antidiagonals.values())):
            before = len(clauses)
            for group in groups:
                clauses.extend([[-first, -second] for first, second in combinations(group, 2)])
            counts.append(len(clauses) - before)

        stats = CNFEncodingStats(n, n * n, n, n if self.include_col_alo else 0, *counts)
        return clauses, stats

    def theoretical_clause_count(self) -> int:
        n = self.n
        return (n * (2 if self.include_col_alo else 1) + n * n * (n - 1)
                + n * (n - 1) * (2 * n - 1) // 3)
