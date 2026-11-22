"""Min-Conflicts local search solver and variable-selection heuristics for N-Queen."""

from __future__ import annotations

import abc
import random
import time
from dataclasses import dataclass, field
from typing import List, Optional

from .board import NQueenBoard


@dataclass
class LocalSearchResult:
    """Outcome and performance metrics of a Min-Conflicts run."""

    n: int
    strategy_name: str
    solved: bool
    steps: int
    elapsed_sec: float
    remaining_conflicts: int
    board: NQueenBoard
    conflict_history: List[int] = field(default_factory=list)


class VariableSelectionStrategy(abc.ABC):
    """Strategy interface for choosing which conflicted column to repair at step t."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Human-readable identifier of the heuristic."""

    def reset(self, n: int) -> None:
        """Reset any internal memory before starting a new search episode."""

    @abc.abstractmethod
    def select_column(
        self,
        board: NQueenBoard,
        conflicted_cols: List[int],
        step: int,
        rng: random.Random,
        total_conflicts: int,
    ) -> int:
        """Return the column index of the queen to relocate."""

    def notify_move(self, col: int, step: int, improved: bool) -> None:
        """Update internal heuristic memory after moving ``col`` at ``step``."""


class RandomConflictedSelector(VariableSelectionStrategy):
    """Standard Lecture 08 Min-Conflicts variable selector: uniform random conflicted column."""

    @property
    def name(self) -> str:
        return "Standard Min-Conflicts (Random Variable)"

    def select_column(
        self,
        board: NQueenBoard,
        conflicted_cols: List[int],
        step: int,
        rng: random.Random,
        total_conflicts: int,
    ) -> int:
        return rng.choice(conflicted_cols)


class TabuMaxConflictSelector(VariableSelectionStrategy):
    """Proposed heuristic: Max-Conflict variable selection with short-term Tabu list and Aspiration.

    Design rationale:
      1. Prioritizing the queen involved in the highest number of conflicts resolves
         dense bottlenecks earlier than uniform random selection.
      2. Naive Max-Conflict gets trapped in 2-cycles on plateaus. Maintaining a short-term
         Tabu tenure prevents re-selecting recently moved columns for ``tenure`` steps.
      3. Aspiration criterion: if any tabu column accounts for all remaining conflicts
         on the board and has a conflict-free row available, override tabu immediately.
      4. Plateau diversification: if total conflicts fail to decrease for ``stagnation_limit``
         consecutive steps, clear short-term tabu locks and pick a random conflicted column.
    """

    def __init__(self, tenure_ratio: float = 0.12, stagnation_limit: int = 16) -> None:
        self.tenure_ratio: float = tenure_ratio
        self.stagnation_limit: int = stagnation_limit
        self._tabu_until: List[int] = []
        self._tenure: int = 2
        self._stagnant_steps: int = 0
        self._best_seen_conflicts: int = 10**9

    @property
    def name(self) -> str:
        return "Proposed Heuristic (Max-Conflict + Tabu)"

    def reset(self, n: int) -> None:
        self._tenure = max(2, min(8, int(round(n * self.tenure_ratio))))
        self._tabu_until = [0] * n
        self._stagnant_steps = 0
        self._best_seen_conflicts = 10**9

    def select_column(
        self,
        board: NQueenBoard,
        conflicted_cols: List[int],
        step: int,
        rng: random.Random,
        total_conflicts: int,
    ) -> int:
        if total_conflicts < self._best_seen_conflicts:
            self._best_seen_conflicts = total_conflicts
            self._stagnant_steps = 0
        else:
            self._stagnant_steps += 1

        if self._stagnant_steps >= self.stagnation_limit:
            self._stagnant_steps = 0
            self._best_seen_conflicts = total_conflicts
            return rng.choice(conflicted_cols)

        tabu_until = self._tabu_until
        best_non_tabu_score = -1
        best_non_tabu_cols: List[int] = []
        best_any_score = -1
        best_any_cols: List[int] = []

        for col in conflicted_cols:
            c_score = board.conflicts_for_queen(col)

            if c_score == total_conflicts and tabu_until[col] > step:
                for r in range(board.n):
                    if board.conflicts_if_placed(col, r) == 0:
                        return col

            if c_score > best_any_score:
                best_any_score = c_score
                best_any_cols = [col]
            elif c_score == best_any_score:
                best_any_cols.append(col)

            if tabu_until[col] <= step:
                if c_score > best_non_tabu_score:
                    best_non_tabu_score = c_score
                    best_non_tabu_cols = [col]
                elif c_score == best_non_tabu_score:
                    best_non_tabu_cols.append(col)

        if best_non_tabu_cols:
            return rng.choice(best_non_tabu_cols)
        return rng.choice(best_any_cols)

    def notify_move(self, col: int, step: int, improved: bool) -> None:
        self._tabu_until[col] = step + self._tenure


class MinConflictsSolver:
    """Implements the Lecture 08 Min-Conflicts algorithm parameterized by VariableSelectionStrategy."""

    def __init__(
        self,
        strategy: Optional[VariableSelectionStrategy] = None,
        max_steps: int = 5000,
        record_history: bool = False,
    ) -> None:
        self.strategy: VariableSelectionStrategy = strategy or RandomConflictedSelector()
        self.max_steps: int = max_steps
        self.record_history: bool = record_history

    def solve(
        self,
        n: int,
        initial_board: Optional[NQueenBoard] = None,
        seed: Optional[int] = None,
    ) -> LocalSearchResult:
        """Run Min-Conflicts starting from ``initial_board`` (or a random board using ``seed``)."""
        rng = random.Random(seed)
        board = initial_board.clone() if initial_board is not None else NQueenBoard.from_random(n, rng)
        self.strategy.reset(n)

        history: List[int] = []
        t0 = time.perf_counter()
        current_total = board.total_conflicts()
        if self.record_history:
            history.append(current_total)

        for step in range(1, self.max_steps + 1):
            if current_total == 0:
                elapsed = time.perf_counter() - t0
                return LocalSearchResult(
                    n=n,
                    strategy_name=self.strategy.name,
                    solved=True,
                    steps=step - 1,
                    elapsed_sec=elapsed,
                    remaining_conflicts=0,
                    board=board,
                    conflict_history=history,
                )

            conflicted = board.conflicted_columns()
            col = self.strategy.select_column(board, conflicted, step, rng, current_total)

            # Value selection: pick row minimizing conflicts (break ties randomly, preferring
            # a different row when tied so sideways moves explore plateaus effectively).
            current_row = board.queens[col]
            min_conf = board.n * 4
            best_other_rows: List[int] = []
            current_row_ties = False

            for candidate_row in range(board.n):
                c_val = board.conflicts_if_placed(col, candidate_row)
                if c_val < min_conf:
                    min_conf = c_val
                    if candidate_row == current_row:
                        best_other_rows = []
                        current_row_ties = True
                    else:
                        best_other_rows = [candidate_row]
                        current_row_ties = False
                elif c_val == min_conf:
                    if candidate_row == current_row:
                        current_row_ties = True
                    else:
                        best_other_rows.append(candidate_row)

            if best_other_rows:
                chosen_row = rng.choice(best_other_rows)
            elif current_row_ties:
                chosen_row = current_row
            else:
                chosen_row = current_row

            old_queen_conf = board.conflicts_for_queen(col)
            board.move_queen(col, chosen_row)
            current_total += min_conf - old_queen_conf
            self.strategy.notify_move(col, step, improved=(min_conf < old_queen_conf))

            if self.record_history:
                history.append(current_total)

        elapsed = time.perf_counter() - t0
        return LocalSearchResult(
            n=n,
            strategy_name=self.strategy.name,
            solved=(current_total == 0),
            steps=self.max_steps,
            elapsed_sec=elapsed,
            remaining_conflicts=current_total,
            board=board,
            conflict_history=history,
        )
