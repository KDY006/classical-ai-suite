"""Thuat toan tim kiem cuc bo Min-Conflicts va cac chien luoc chon bien."""

from __future__ import annotations

import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterator

from .base_solver import BaseNQueenSolver
from .board import NQueenBoard


@dataclass(frozen=True)
class StepSnapshot:
    """Anh chup bat bien nhe o moi buoc giai phuc vu giao dien truc quan."""

    step: int
    queens: tuple[int, ...]
    selected_col: int | None
    old_row: int | None
    new_row: int | None
    total_conflicts: int
    solved: bool


@dataclass
class LocalSearchResult:
    """Ket qua tong hop sau khi chay thuat toan Min-Conflicts."""

    n: int
    strategy_name: str
    strategy_cli_name: str
    solved: bool
    steps: int
    elapsed_sec: float
    remaining_conflicts: int
    board: NQueenBoard
    conflict_history: list[int] = field(default_factory=list)


class VariableSelectionStrategy(ABC):
    """Lop truu tuong cho ham heuristic chon cot dang co xung dot."""

    def reset(self, n: int) -> None:
        """Khoi tao lai trang thai bo nho phu cua chien luoc theo kich thuoc n."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Ten hien thi co dau cho giao dien va bieu do."""

    @property
    @abstractmethod
    def cli_name(self) -> str:
        """Ten hien thi khong dau cho terminal CLI."""

    @abstractmethod
    def select_column(
        self,
        board: NQueenBoard,
        conflicted_cols: list[int],
        step: int,
        rng: random.Random,
        total_conflicts: int,
    ) -> int:
        """Chon mot cot dang co xung dot de sua trong buoc hien tai."""

    def notify_move(self, col: int, step: int, improved: bool) -> None:
        """Cap nhat trang thai noi bo sau khi di chuyen quan hau tai cot col."""


class RandomConflictedSelector(VariableSelectionStrategy):
    """Chien luoc Min-Conflicts tieu chuan (Lecture 08): chon ngau nhien deu."""

    @property
    def name(self) -> str:
        return "Min-Conflicts tiêu chuẩn (Ngẫu nhiên)"

    @property
    def cli_name(self) -> str:
        return "Min-Conflicts tieu chuan (Ngau nhien)"

    def select_column(
        self,
        board: NQueenBoard,
        conflicted_cols: list[int],
        step: int,
        rng: random.Random,
        total_conflicts: int,
    ) -> int:
        return rng.choice(conflicted_cols)


class PureMaxConflictSelector(VariableSelectionStrategy):
    """Chien luoc doi chung: luon chon cot nhieu xung dot nhat (khong Tabu)."""

    @property
    def name(self) -> str:
        return "Max-Conflict thuần (Đối chứng)"

    @property
    def cli_name(self) -> str:
        return "Max-Conflict thuan (Doi chung)"

    def select_column(
        self,
        board: NQueenBoard,
        conflicted_cols: list[int],
        step: int,
        rng: random.Random,
        total_conflicts: int,
    ) -> int:
        queens = board.queens
        rc = board._row_counts
        mc = board._main_diag_counts
        ac = board._anti_diag_counts
        offset = board.n - 1

        best_score = -1
        best_cols: list[int] = []
        for col in conflicted_cols:
            row = queens[col]
            score = rc[row] + mc[row - col + offset] + ac[row + col] - 3
            if score > best_score:
                best_score = score
                best_cols = [col]
            elif score == best_score:
                best_cols.append(col)
        return best_cols[0] if len(best_cols) == 1 else rng.choice(best_cols)


class AdaptiveTabuMaxConflictSelector(VariableSelectionStrategy):
    """Heuristic de xuat: uu tien xung dot cuc dai ket hop Tabu thich nghi va an xa."""

    def __init__(self, tenure_ratio: float = 0.10) -> None:
        if tenure_ratio < 0.0:
            raise ValueError("He so thoi han cam Tabu khong duoc am")
        self.tenure_ratio: float = tenure_ratio
        self._base_tenure: int = 2
        self._last_moved: list[int] = []
        self._stagnation_limit: int = 6
        self._best_conflicts: int = 0
        self._stagnation: int = 0
        self._consecutive_escapes: int = 0

    @property
    def name(self) -> str:
        return "Max-Conflict + Tabu thích nghi (Đề xuất)"

    @property
    def cli_name(self) -> str:
        return "Max-Conflict + Tabu thich nghi (De xuat)"

    def reset(self, n: int) -> None:
        self._base_tenure = max(2, min(6, round(n * self.tenure_ratio)))
        self._last_moved = [-1000] * n
        self._stagnation_limit = max(4, min(12, n // 2 + 1))
        self._best_conflicts = n * n
        self._stagnation = 0
        self._consecutive_escapes = 0

    def select_column(
        self,
        board: NQueenBoard,
        conflicted_cols: list[int],
        step: int,
        rng: random.Random,
        total_conflicts: int,
    ) -> int:
        # Theo doi su dinh tre de thoat nhanh khoi cuc tri cuc bo hoac binh nguyen
        if total_conflicts < self._best_conflicts:
            self._best_conflicts = total_conflicts
            self._stagnation = 0
            self._consecutive_escapes = 0
        else:
            self._stagnation += 1

        if self._stagnation >= self._stagnation_limit:
            self._stagnation = 0
            self._best_conflicts = total_conflicts
            self._consecutive_escapes += 1
            # Chi nhieu dong cot chua xung dot khi ket o cuc tri chat (1 cap) hoac dinh tre 3 chu ky
            if (total_conflicts == 1 or self._consecutive_escapes >= 3) and len(conflicted_cols) < board.n:
                conflicted_set = set(conflicted_cols)
                non_conflicted = [c for c in range(board.n) if c not in conflicted_set]
                return rng.choice(non_conflicted)
            return rng.choice(conflicted_cols)

        k = len(conflicted_cols)
        if k <= 2:
            # Khi chi con 2 cot xung dot, tat cam cung de tranh lap 2 buoc tren ban co nho
            if k == 1:
                return conflicted_cols[0]
            if self._stagnation >= 2:
                return rng.choice(conflicted_cols)
            c0, c1 = conflicted_cols[0], conflicted_cols[1]
            if self._last_moved[c0] == self._last_moved[c1]:
                return rng.choice(conflicted_cols)
            return c0 if self._last_moved[c0] < self._last_moved[c1] else c1

        # Thoi han cam thich nghi dam bao luon con it nhat mot nua tap xung dot kha dung
        effective_tenure = min(self._base_tenure, k // 2)

        queens = board.queens
        rc = board._row_counts
        mc = board._main_diag_counts
        ac = board._anti_diag_counts
        offset = board.n - 1
        last_moved = self._last_moved

        best_score = -1
        best_age = -1
        best_cols: list[int] = []

        fallback_score = -1
        fallback_cols: list[int] = []

        for col in conflicted_cols:
            row = queens[col]
            score = rc[row] + mc[row - col + offset] + ac[row + col] - 3
            age = step - last_moved[col]

            if age <= effective_tenure:
                # Dieu kien an xa nhe chi kich hoat khi sap dat nghiem (tong xung dot <= 2)
                if total_conflicts <= 2 and score == total_conflicts:
                    min_sc, _ = board.best_rows_for_column(col)
                    if min_sc == 0:
                        return col
                if score > fallback_score:
                    fallback_score = score
                    fallback_cols = [col]
                elif score == fallback_score:
                    fallback_cols.append(col)
                continue

            # Trong tap khong bi cam: uu tien bac xung dot cao nhat, pha hoa theo tuoi
            if score > best_score:
                best_score = score
                best_age = age
                best_cols = [col]
            elif score == best_score:
                if age > best_age:
                    best_age = age
                    best_cols = [col]
                elif age == best_age:
                    best_cols.append(col)

        candidates = best_cols or fallback_cols or conflicted_cols
        return candidates[0] if len(candidates) == 1 else rng.choice(candidates)

    def notify_move(self, col: int, step: int, improved: bool) -> None:
        self._last_moved[col] = step


# Giu ten bi danh de tuong thich nguoc voi ma nguon cu
TabuMaxConflictSelector = AdaptiveTabuMaxConflictSelector


class MinConflictsSolver(BaseNQueenSolver):
    """Bo giai tim kiem cuc bo Min-Conflicts ho tro chay nhanh va sinh tung buoc."""

    def __init__(
        self,
        strategy: VariableSelectionStrategy | None = None,
        max_steps: int = 5000,
        record_history: bool = False,
    ) -> None:
        if max_steps < 0:
            raise ValueError("So buoc toi da max_steps khong duoc am")
        self.strategy: VariableSelectionStrategy = strategy or RandomConflictedSelector()
        self.max_steps: int = max_steps
        self.record_history: bool = record_history

    @property
    def name(self) -> str:
        return self.strategy.name

    @property
    def cli_name(self) -> str:
        return self.strategy.cli_name

    def _prepare_run(
        self,
        n: int,
        initial_board: NQueenBoard | None,
        seed: int | None,
    ) -> tuple[NQueenBoard, random.Random]:
        if n < 1:
            raise ValueError("Kich thuoc ban co phai la so nguyen duong")
        if initial_board is not None and initial_board.n != n:
            raise ValueError("Kich thuoc ban co khoi tao khong khop voi tham so n")
        rng = random.Random(seed)
        board = initial_board.clone() if initial_board is not None else NQueenBoard.from_random(n, rng)
        self.strategy.reset(n)
        return board, rng

    def _choose_best_row(
        self,
        board: NQueenBoard,
        col: int,
        rng: random.Random,
    ) -> tuple[int, int]:
        """Chon hang lam cuc tieu hoa xung dot cho cot col, uu tien doi vi tri."""
        # Neu chien luoc chu dong chon cot chua xung dot de pha cuc tri cuc bo, bat buoc doi hang
        force_different = board.conflicts_for_queen(col) == 0
        min_score, best_rows = board.best_rows_for_column(col, exclude_current=force_different)
        cur_row = board.queens[col]
        if len(best_rows) == 1:
            return best_rows[0], min_score
        other_rows = [row for row in best_rows if row != cur_row]
        chosen = rng.choice(other_rows if other_rows else best_rows)
        return chosen, min_score

    def solve(
        self,
        n: int,
        initial_board: NQueenBoard | None = None,
        seed: int | None = None,
    ) -> LocalSearchResult:
        """Chay nhanh khong giao dien cho thuc nghiem CLI va Jupyter Notebook."""
        board, rng = self._prepare_run(n, initial_board, seed)
        start = time.perf_counter()

        conflicts = board.total_conflicts()
        history = [conflicts] if self.record_history else []
        steps = 0

        while conflicts > 0 and steps < self.max_steps:
            steps += 1
            conflicted_cols = board.conflicted_columns()
            col = self.strategy.select_column(board, conflicted_cols, steps, rng, conflicts)
            new_row, _ = self._choose_best_row(board, col, rng)
            delta = board.move_queen(col, new_row)
            conflicts = board.total_conflicts()
            self.strategy.notify_move(col, steps, delta < 0)
            if self.record_history:
                history.append(conflicts)

        return LocalSearchResult(
            n=n,
            strategy_name=self.strategy.name,
            strategy_cli_name=self.strategy.cli_name,
            solved=(conflicts == 0),
            steps=steps,
            elapsed_sec=time.perf_counter() - start,
            remaining_conflicts=conflicts,
            board=board,
            conflict_history=history,
        )

    def iter_solve(
        self,
        n: int,
        initial_board: NQueenBoard | None = None,
        seed: int | None = None,
    ) -> Iterator[StepSnapshot]:
        """Generator tra ve anh chup tung buoc giai phuc vu giao dien PyGame."""
        board, rng = self._prepare_run(n, initial_board, seed)
        conflicts = board.total_conflicts()
        yield StepSnapshot(
            step=0,
            queens=tuple(board.queens),
            selected_col=None,
            old_row=None,
            new_row=None,
            total_conflicts=conflicts,
            solved=(conflicts == 0),
        )

        steps = 0
        while conflicts > 0 and steps < self.max_steps:
            steps += 1
            conflicted_cols = board.conflicted_columns()
            col = self.strategy.select_column(board, conflicted_cols, steps, rng, conflicts)
            old_row = board.queens[col]
            new_row, _ = self._choose_best_row(board, col, rng)
            delta = board.move_queen(col, new_row)
            conflicts = board.total_conflicts()
            self.strategy.notify_move(col, steps, delta < 0)
            yield StepSnapshot(
                step=steps,
                queens=tuple(board.queens),
                selected_col=col,
                old_row=old_row,
                new_row=new_row,
                total_conflicts=conflicts,
                solved=(conflicts == 0),
            )
