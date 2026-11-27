"""Mo hinh trang thai ban co N Quan Hau voi bang dem xung dot O(1)."""

from __future__ import annotations

import random
from typing import Sequence


class NQueenBoard:
    """Bieu dien trang thai day du voi dung mot quan hau tren moi cot."""

    def __init__(self, n: int, queens: Sequence[int] | None = None) -> None:
        if n < 1:
            raise ValueError("Kich thuoc ban co phai la so nguyen duong")
        self.n: int = n
        self.queens: list[int] = list(range(n)) if queens is None else list(queens)
        if len(self.queens) != n or any(not 0 <= row < n for row in self.queens):
            raise ValueError("Can dung mot chi so hang hop le trong [0, n-1] cho moi cot")

        # Ba mang phang dem so quan hau tren tung hang va hai he duong cheo
        self._row_counts: list[int] = [0] * n
        self._main_diag_counts: list[int] = [0] * (2 * n - 1)
        self._anti_diag_counts: list[int] = [0] * (2 * n - 1)

        offset = n - 1
        for col, row in enumerate(self.queens):
            self._row_counts[row] += 1
            self._main_diag_counts[row - col + offset] += 1
            self._anti_diag_counts[row + col] += 1

        self._total_conflicts: int = self.compute_total_conflicts_direct()

    @classmethod
    def from_random(cls, n: int, rng: random.Random | None = None) -> NQueenBoard:
        """Khoi tao ban co ngau nhien voi mot quan hau o moi cot."""
        generator = rng if rng is not None else random
        return cls(n, [generator.randrange(n) for _ in range(n)])

    @classmethod
    def from_sat_model(cls, n: int, model: Sequence[int]) -> NQueenBoard:
        """Khoi phuc ban co tu tap nghiem DIMACS cua bo giai SAT."""
        if n < 1:
            raise ValueError("Kich thuoc ban co phai la so nguyen duong")
        queens: list[int | None] = [None] * n
        seen_rows: set[int] = set()
        max_var = n * n

        for literal in model:
            if 1 <= literal <= max_var:
                row, col = divmod(literal - 1, n)
                if queens[col] is not None:
                    raise ValueError("Tap nghiem SAT co nhieu hon mot quan hau tren cung mot cot")
                if row in seen_rows:
                    raise ValueError("Tap nghiem SAT co nhieu hon mot quan hau tren cung mot hang")
                queens[col] = row
                seen_rows.add(row)

        if any(row is None for row in queens):
            raise ValueError("Tap nghiem SAT thieu quan hau tren it nhat mot cot")
        return cls(n, [int(row) for row in queens if row is not None])

    def clone(self) -> NQueenBoard:
        """Sao chep nhanh trang thai ban co va ba mang dem xung dot."""
        copy_board = NQueenBoard.__new__(NQueenBoard)
        copy_board.n = self.n
        copy_board.queens = self.queens.copy()
        copy_board._row_counts = self._row_counts.copy()
        copy_board._main_diag_counts = self._main_diag_counts.copy()
        copy_board._anti_diag_counts = self._anti_diag_counts.copy()
        copy_board._total_conflicts = self._total_conflicts
        return copy_board

    def conflicts_for_queen(self, col: int) -> int:
        """Tra ve so quan hau khac dang tan cong quan hau tai cot col."""
        row = self.queens[col]
        offset = self.n - 1
        return (
            self._row_counts[row]
            + self._main_diag_counts[row - col + offset]
            + self._anti_diag_counts[row + col]
            - 3
        )

    def conflicts_if_placed(self, col: int, candidate_row: int) -> int:
        """Tra ve so xung dot neu dat quan hau cua cot col tai hang candidate_row."""
        if self.queens[col] == candidate_row:
            return self.conflicts_for_queen(col)
        offset = self.n - 1
        return (
            self._row_counts[candidate_row]
            + self._main_diag_counts[candidate_row - col + offset]
            + self._anti_diag_counts[candidate_row + col]
        )

    def best_rows_for_column(self, col: int, exclude_current: bool = False) -> tuple[int, list[int]]:
        """Tim so xung dot nho nhat va danh sach hang toi uu cho cot col."""
        rc = self._row_counts
        mc = self._main_diag_counts
        ac = self._anti_diag_counts
        cur_row = self.queens[col]
        m_off = self.n - 1 - col
        skip_cur = exclude_current and self.n > 1

        best_score = self.n * 3
        best_rows: list[int] = []
        for row in range(self.n):
            if skip_cur and row == cur_row:
                continue
            score = rc[row] + mc[row + m_off] + ac[row + col]
            if row == cur_row:
                score -= 3
            if score < best_score:
                best_score = score
                best_rows = [row]
            elif score == best_score:
                best_rows.append(row)
        return best_score, best_rows

    def move_queen(self, col: int, new_row: int) -> int:
        """Di chuyen quan hau o cot col den new_row va cap nhat xung dot O(1)."""
        if not 0 <= col < self.n or not 0 <= new_row < self.n:
            raise ValueError("Vi tri o nam ngoai pham vi ban co")
        old_row = self.queens[col]
        if old_row == new_row:
            return 0

        offset = self.n - 1
        old_main = old_row - col + offset
        old_anti = old_row + col
        new_main = new_row - col + offset
        new_anti = new_row + col

        old_conf = (
            self._row_counts[old_row]
            + self._main_diag_counts[old_main]
            + self._anti_diag_counts[old_anti]
            - 3
        )

        self._row_counts[old_row] -= 1
        self._main_diag_counts[old_main] -= 1
        self._anti_diag_counts[old_anti] -= 1

        new_conf = (
            self._row_counts[new_row]
            + self._main_diag_counts[new_main]
            + self._anti_diag_counts[new_anti]
        )

        self._row_counts[new_row] += 1
        self._main_diag_counts[new_main] += 1
        self._anti_diag_counts[new_anti] += 1

        self.queens[col] = new_row
        delta = new_conf - old_conf
        self._total_conflicts += delta
        return delta

    def compute_total_conflicts_direct(self) -> int:
        """Tinh truc tiep tong so cap quan hau tan cong nhau tu ba bang dem."""
        total = 0
        for counts in (self._row_counts, self._main_diag_counts, self._anti_diag_counts):
            for count in counts:
                if count > 1:
                    total += count * (count - 1) // 2
        return total

    def total_conflicts(self) -> int:
        """Tra ve tong so cap quan hau tan cong nhau hien tai trong O(1)."""
        return self._total_conflicts

    def conflicted_columns(self) -> list[int]:
        """Tra ve danh sach cac cot co quan hau dang bi tan cong."""
        rc = self._row_counts
        mc = self._main_diag_counts
        ac = self._anti_diag_counts
        offset = self.n - 1
        return [
            col
            for col, row in enumerate(self.queens)
            if rc[row] + mc[row - col + offset] + ac[row + col] > 3
        ]

    def attacking_pairs(self) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        """Liet ke tat ca cac cap toa do (hang, cot) cua quan hau tan cong nhau."""
        pairs: list[tuple[tuple[int, int], tuple[int, int]]] = []
        queens = self.queens
        n = self.n
        for c1 in range(n):
            r1 = queens[c1]
            for c2 in range(c1 + 1, n):
                r2 = queens[c2]
                if r1 == r2 or abs(r1 - r2) == (c2 - c1):
                    pairs.append(((r1, c1), (r2, c2)))
        return pairs

    def is_valid_solution(self) -> bool:
        """Kiem chung doc lap xem ban co co phai la nghiem hop le hay khong."""
        queens = self.queens
        n = self.n
        for c1 in range(n):
            r1 = queens[c1]
            for c2 in range(c1 + 1, n):
                r2 = queens[c2]
                if r1 == r2 or abs(r1 - r2) == (c2 - c1):
                    return False
        return True

    def to_boolean_grid(self) -> list[list[bool]]:
        """Chuyen trang thai ban co thanh ma tran logic n x n."""
        return [[self.queens[col] == row for col in range(self.n)] for row in range(self.n)]

    def render_ascii(self) -> str:
        """Xuat ban co dang ky tu ASCII gom Q va dau cham."""
        return "\n".join(
            " ".join("Q" if occupied else "." for occupied in row)
            for row in self.to_boolean_grid()
        )

    def queen_coordinates(self) -> list[tuple[int, int]]:
        """Tra ve danh sach toa do (hang, cot) cua N quan hau theo thu tu cot."""
        return [(row, col) for col, row in enumerate(self.queens)]
