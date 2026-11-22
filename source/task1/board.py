"""Chessboard representation and O(1) incremental conflict tracking for N-Queen."""

from __future__ import annotations

import random
from typing import Iterable, List, Optional, Sequence, Tuple


class NQueenBoard:
    """Represents an N x N chessboard for both SAT decoding and Local Search.

    In complete-state local search mode, exactly one queen is placed in each column c
    at row ``queens[c]``. Row, main-diagonal, and anti-diagonal occupancy counts are
    maintained incrementally so conflict queries run in O(1) time.
    """

    def __init__(self, n: int, queens: Optional[Sequence[int]] = None) -> None:
        if n < 1:
            raise ValueError(f"Board size n must be positive, got {n}.")
        self.n: int = n
        if queens is not None:
            if len(queens) != n:
                raise ValueError(f"Expected {n} queen positions, got {len(queens)}.")
            for r in queens:
                if not (0 <= r < n):
                    raise ValueError(f"Row index {r} out of range [0, {n - 1}].")
            self.queens: List[int] = list(queens)
        else:
            self.queens = list(range(n))

        self.row_counts: List[int] = [0] * n
        self.main_diag_counts: List[int] = [0] * (2 * n - 1)
        self.anti_diag_counts: List[int] = [0] * (2 * n - 1)
        self._rebuild_counts()

    def _rebuild_counts(self) -> None:
        n = self.n
        self.row_counts = [0] * n
        self.main_diag_counts = [0] * (2 * n - 1)
        self.anti_diag_counts = [0] * (2 * n - 1)
        for col, row in enumerate(self.queens):
            self.row_counts[row] += 1
            self.main_diag_counts[row - col + n - 1] += 1
            self.anti_diag_counts[row + col] += 1

    @classmethod
    def from_random(cls, n: int, rng: Optional[random.Random] = None) -> "NQueenBoard":
        """Create a complete-state board with one queen placed at a random row per column."""
        generator = rng if rng is not None else random
        queens = [generator.randrange(n) for _ in range(n)]
        return cls(n, queens)

    @classmethod
    def from_sat_model(cls, n: int, model: Iterable[int]) -> "NQueenBoard":
        """Construct an NQueenBoard from a PySAT truth assignment over variables 1..N^2."""
        positive_vars = {lit for lit in model if lit > 0 and lit <= n * n}
        queens = [-1] * n
        placed_count = 0
        for var in sorted(positive_vars):
            idx = var - 1
            row, col = divmod(idx, n)
            if queens[col] != -1:
                raise ValueError(f"Multiple queens assigned in column {col}.")
            queens[col] = row
            placed_count += 1
        if placed_count != n or any(r == -1 for r in queens):
            raise ValueError(f"SAT model placed {placed_count} queens across columns, expected {n}.")
        return cls(n, queens)

    def clone(self) -> "NQueenBoard":
        """Return a deep copy of the board."""
        return NQueenBoard(self.n, self.queens)

    def conflicts_for_queen(self, col: int) -> int:
        """Return the number of other queens currently attacking the queen in ``col``."""
        row = self.queens[col]
        n = self.n
        return (
            (self.row_counts[row] - 1)
            + (self.main_diag_counts[row - col + n - 1] - 1)
            + (self.anti_diag_counts[row + col] - 1)
        )

    def conflicts_if_placed(self, col: int, candidate_row: int) -> int:
        """Return how many other queens would attack ``(candidate_row, col)`` if moved there."""
        current_row = self.queens[col]
        if candidate_row == current_row:
            return self.conflicts_for_queen(col)
        n = self.n
        return (
            self.row_counts[candidate_row]
            + self.main_diag_counts[candidate_row - col + n - 1]
            + self.anti_diag_counts[candidate_row + col]
        )

    def move_queen(self, col: int, new_row: int) -> None:
        """Move the queen in ``col`` to ``new_row`` and update conflict counters in O(1)."""
        old_row = self.queens[col]
        if old_row == new_row:
            return
        n = self.n
        self.row_counts[old_row] -= 1
        self.main_diag_counts[old_row - col + n - 1] -= 1
        self.anti_diag_counts[old_row + col] -= 1

        self.queens[col] = new_row
        self.row_counts[new_row] += 1
        self.main_diag_counts[new_row - col + n - 1] += 1
        self.anti_diag_counts[new_row + col] += 1

    def total_conflicts(self) -> int:
        """Return total number of attacking queen pairs on the board."""
        pairs = 0
        for count in self.row_counts:
            if count > 1:
                pairs += count * (count - 1) // 2
        for count in self.main_diag_counts:
            if count > 1:
                pairs += count * (count - 1) // 2
        for count in self.anti_diag_counts:
            if count > 1:
                pairs += count * (count - 1) // 2
        return pairs

    def conflicted_columns(self) -> List[int]:
        """Return all columns whose queen is currently attacked by at least one other queen."""
        return [col for col in range(self.n) if self.conflicts_for_queen(col) > 0]

    def is_valid_solution(self) -> bool:
        """Verify independently that N queens are placed with zero attacking pairs."""
        if len(self.queens) != self.n:
            return False
        for c1 in range(self.n):
            r1 = self.queens[c1]
            if not (0 <= r1 < self.n):
                return False
            for c2 in range(c1 + 1, self.n):
                r2 = self.queens[c2]
                if r1 == r2 or abs(r1 - r2) == abs(c1 - c2):
                    return False
        return True

    def to_boolean_grid(self) -> List[List[bool]]:
        """Convert the board to an N x N 2D boolean matrix (True = queen, False = empty)."""
        grid = [[False] * self.n for _ in range(self.n)]
        for col, row in enumerate(self.queens):
            grid[row][col] = True
        return grid

    def render_ascii(self) -> str:
        """Return a readable text representation of the chessboard."""
        grid = self.to_boolean_grid()
        lines: List[str] = []
        for r in range(self.n):
            row_str = " ".join("Q" if grid[r][c] else "." for c in range(self.n))
            lines.append(row_str)
        return "\n".join(lines)

    def queen_coordinates(self) -> List[Tuple[int, int]]:
        """Return list of (row, col) positions of all queens."""
        return [(self.queens[col], col) for col in range(self.n)]
