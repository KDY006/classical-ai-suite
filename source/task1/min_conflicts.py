"""Min-conflicts search with interchangeable queen-selection policies."""

from __future__ import annotations

import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .board import NQueenBoard


@dataclass
class LocalSearchResult:
    n: int
    strategy_name: str
    solved: bool
    steps: int
    elapsed_sec: float
    remaining_conflicts: int
    board: NQueenBoard
    conflict_history: list[int] = field(default_factory=list)


class VariableSelectionStrategy(ABC):
    def reset(self, n):
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def select_column(self, board, conflicted_cols, step, rng, total_conflicts):
        pass

    def notify_move(self, col, step, improved):
        pass


class RandomConflictedSelector(VariableSelectionStrategy):
    @property
    def name(self):
        return "Standard Min-Conflicts (Random Variable)"

    def select_column(self, board, conflicted_cols, step, rng, total_conflicts):
        return rng.choice(conflicted_cols)


class TabuMaxConflictSelector(VariableSelectionStrategy):
    """Select a highly conflicted queen, avoiding recently selected columns."""

    def __init__(self, tenure_ratio=0.12, stagnation_limit=16):
        self.tenure_ratio = tenure_ratio
        self.stagnation_limit = stagnation_limit

    @property
    def name(self):
        return "Proposed Heuristic (Max-Conflict + Tabu)"

    def reset(self, n):
        self.tenure = max(2, min(8, round(n * self.tenure_ratio)))
        self.tabu_until = [0] * n
        self.best_conflicts = float("inf")
        self.stagnation = 0

    def select_column(self, board, conflicted_cols, step, rng, total_conflicts):
        if total_conflicts < self.best_conflicts:
            self.best_conflicts = total_conflicts
            self.stagnation = 0
        else:
            self.stagnation += 1
        if self.stagnation >= self.stagnation_limit:
            self.stagnation = 0
            self.best_conflicts = total_conflicts
            self.tabu_until = [0] * board.n
            return rng.choice(conflicted_cols)

        available = []
        for col in conflicted_cols:
            score = board.conflicts_for_queen(col)
            if (self.tabu_until[col] > step and score == total_conflicts and
                    any(board.conflicts_if_placed(col, row) == 0 for row in range(board.n))):
                return col
            if self.tabu_until[col] <= step:
                available.append(col)
        candidates = available or conflicted_cols
        best = max(board.conflicts_for_queen(col) for col in candidates)
        return rng.choice([col for col in candidates if board.conflicts_for_queen(col) == best])

    def notify_move(self, col, step, improved):
        self.tabu_until[col] = step + self.tenure


class MinConflictsSolver:
    def __init__(self, strategy=None, max_steps=5000, record_history=False):
        if max_steps < 0:
            raise ValueError("max_steps must be non-negative")
        self.strategy = strategy or RandomConflictedSelector()
        self.max_steps = max_steps
        self.record_history = record_history

    def solve(self, n, initial_board=None, seed=None):
        if initial_board is not None and initial_board.n != n:
            raise ValueError("Initial board size does not match n")
        rng = random.Random(seed)
        board = initial_board.clone() if initial_board is not None else NQueenBoard.from_random(n, rng)
        self.strategy.reset(n)
        start = time.perf_counter()
        conflicts = board.total_conflicts()
        history = [conflicts] if self.record_history else []
        steps = 0
        while conflicts and steps < self.max_steps:
            steps += 1
            col = self.strategy.select_column(board, board.conflicted_columns(), steps, rng, conflicts)
            scores = [board.conflicts_if_placed(col, row) for row in range(n)]
            minimum = min(scores)
            rows = [row for row, score in enumerate(scores) if score == minimum]
            other_rows = [row for row in rows if row != board.queens[col]]
            row = rng.choice(other_rows or rows)
            old_conflicts = board.conflicts_for_queen(col)
            board.move_queen(col, row)
            conflicts += minimum - old_conflicts
            self.strategy.notify_move(col, steps, minimum < old_conflicts)
            if self.record_history:
                history.append(conflicts)
        return LocalSearchResult(n, self.strategy.name, conflicts == 0, steps,
                                 time.perf_counter() - start, conflicts, board, history)
