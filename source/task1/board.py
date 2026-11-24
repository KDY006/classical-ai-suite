"""Board state for a complete assignment with one queen in every column."""

from __future__ import annotations

import random
from collections import Counter


class NQueenBoard:
    def __init__(self, n, queens=None):
        if n < 1:
            raise ValueError("Board size must be positive")
        self.n = n
        self.queens = list(range(n)) if queens is None else list(queens)
        if len(self.queens) != n or any(not 0 <= row < n for row in self.queens):
            raise ValueError("Expected one valid row for each column")
        self.row_counts = Counter()
        self.main_diag_counts = Counter()
        self.anti_diag_counts = Counter()
        for col, row in enumerate(self.queens):
            self.row_counts[row] += 1
            self.main_diag_counts[row - col] += 1
            self.anti_diag_counts[row + col] += 1

    @classmethod
    def from_random(cls, n, rng=None):
        generator = rng or random
        return cls(n, [generator.randrange(n) for _ in range(n)])

    @classmethod
    def from_sat_model(cls, n, model):
        queens = [None] * n
        for literal in model:
            if 1 <= literal <= n * n:
                row, col = divmod(literal - 1, n)
                if queens[col] is not None:
                    raise ValueError("Multiple queens in a column")
                queens[col] = row
        if any(row is None for row in queens):
            raise ValueError("Missing queen in SAT model")
        return cls(n, queens)

    def clone(self):
        return NQueenBoard(self.n, self.queens)

    def conflicts_for_queen(self, col):
        row = self.queens[col]
        return self.row_counts[row] + self.main_diag_counts[row - col] + self.anti_diag_counts[row + col] - 3

    def conflicts_if_placed(self, col, candidate_row):
        if self.queens[col] == candidate_row:
            return self.conflicts_for_queen(col)
        return (self.row_counts[candidate_row] + self.main_diag_counts[candidate_row - col]
                + self.anti_diag_counts[candidate_row + col])

    def move_queen(self, col, new_row):
        if not 0 <= col < self.n or not 0 <= new_row < self.n:
            raise ValueError("Square is outside the board")
        old_row = self.queens[col]
        if old_row == new_row:
            return
        for counts, old_key, new_key in (
            (self.row_counts, old_row, new_row),
            (self.main_diag_counts, old_row - col, new_row - col),
            (self.anti_diag_counts, old_row + col, new_row + col),
        ):
            counts[old_key] -= 1
            if counts[old_key] == 0:
                del counts[old_key]
            counts[new_key] += 1
        self.queens[col] = new_row

    def total_conflicts(self):
        return sum(count * (count - 1) // 2 for counts in
                   (self.row_counts, self.main_diag_counts, self.anti_diag_counts)
                   for count in counts.values())

    def conflicted_columns(self):
        return [col for col in range(self.n) if self.conflicts_for_queen(col)]

    def is_valid_solution(self):
        return all(self.queens[a] != self.queens[b] and
                   abs(self.queens[a] - self.queens[b]) != b - a
                   for a in range(self.n) for b in range(a + 1, self.n))

    def to_boolean_grid(self):
        return [[self.queens[col] == row for col in range(self.n)] for row in range(self.n)]

    def render_ascii(self):
        return "\n".join(" ".join("Q" if occupied else "." for occupied in row)
                         for row in self.to_boolean_grid())

    def queen_coordinates(self):
        return [(row, col) for col, row in enumerate(self.queens)]
