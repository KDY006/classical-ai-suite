"""Trinh soan thao bang Kakuro dung chung mo hinh CSP va bo kiem tra hop le."""

from __future__ import annotations

import json
import random
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .csp_model import CellSpec, KakuroCSP


class BoardEditor:
    """Quan ly ban nhap bang Kakuro tuy chinh, sua hang loat, sinh de va luu JSON."""

    def __init__(self, csp: KakuroCSP) -> None:
        self.name: str = csp.name
        self.grid: List[List[CellSpec]] = deepcopy(csp.raw_grid)
        self.givens: Dict[Tuple[int, int], int] = dict(csp.givens)

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return len(self.grid[0])

    def run_cells(self, pos: Tuple[int, int], direction: str) -> List[Tuple[int, int]]:
        """Liet ke cac o trang lien tiep xuat phat tu o goi y pos theo huong direction."""
        r, c = pos
        dr, dc = (0, 1) if direction == "across" else (1, 0)
        r, c = r + dr, c + dc
        cells: List[Tuple[int, int]] = []
        while r < self.rows and c < self.cols and self.grid[r][c] == "W":
            cells.append((r, c))
            r, c = r + dr, c + dc
        return cells

    def synchronize_clues(self) -> None:
        """Dong bo lai cac o goi y theo cau truc day o trang hien tai."""
        for r in range(self.rows):
            for c in range(self.cols):
                old = self.grid[r][c]
                if old == "W":
                    continue
                clues: Dict[str, int] = {}
                for direction in ("across", "down"):
                    cells = self.run_cells((r, c), direction)
                    if cells:
                        default_sum = sum((rr + cc) % 9 + 1 for rr, cc in cells)
                        clues[direction] = (
                            old.get(direction, default_sum) if isinstance(old, dict) else default_sum
                        )
                self.grid[r][c] = clues if clues else "B"

    def set_cell_type(self, pos: Tuple[int, int], white: bool) -> None:
        """Chuyen doi mot o thanh o trang hoac o den va dong bo goi y."""
        r, c = pos
        if white and (r == 0 or c == 0):
            raise ValueError("Hang dau tien va cot dau tien bat buoc la o den hoac o goi y")
        if (self.grid[r][c] == "W") == white:
            return
        self.grid[r][c] = "W" if white else "B"
        self.givens.pop(pos, None)
        self.synchronize_clues()

    def set_clue(self, pos: Tuple[int, int], direction: str, value: int) -> None:
        """Cap nhat tong goi y ngang hoac doc tai o goi y pos."""
        if direction not in ("across", "down") or not self.run_cells(pos, direction):
            raise ValueError("Khong co day o trang nao theo huong nay")
        r, c = pos
        if self.grid[r][c] == "W" or type(value) is not int or not 1 <= value <= 45:
            raise ValueError("Tong goi y phai la so nguyen tu 1 den 45")
        cell = self.grid[r][c]
        clues = dict(cell) if isinstance(cell, dict) else {}
        clues[direction] = value
        self.grid[r][c] = clues

    def set_given(self, pos: Tuple[int, int], value: int) -> None:
        """Gan chu so cho truoc (1..9) cho o trang pos; nhap 0 de xoa."""
        r, c = pos
        if self.grid[r][c] != "W" or type(value) is not int or not 0 <= value <= 9:
            raise ValueError("O trang chi nhan chu so tu 1 den 9; nhap 0 de xoa")
        if value:
            self.givens[pos] = value
        else:
            self.givens.pop(pos, None)

    @classmethod
    def new(cls, size: int) -> "BoardEditor":
        """Tao ban nhap Kakuro vuong moi kich thuoc tu 3x3 den 9x9."""
        if not 3 <= size <= 9:
            raise ValueError("Kich thuoc bang phai nam trong khoang tu 3 den 9")
        grid: List[List[CellSpec]] = [
            ["B" if r == 0 or c == 0 else "W" for c in range(size)]
            for r in range(size)
        ]
        for i in range(1, size):
            grid[0][i] = {"down": sum((r + i) % 9 + 1 for r in range(1, size))}
            grid[i][0] = {"across": sum((i + c) % 9 + 1 for c in range(1, size))}
        return cls(KakuroCSP(f"Bảng tùy chỉnh {size}x{size}", grid))

    def bulk_rows(self) -> List[str]:
        """Xuat dang van ban moi o 1 ky hieu: #, 0, 1..9 hoac ngang/doc."""
        out: List[str] = []
        for r, row in enumerate(self.grid):
            tokens: List[str] = []
            for c, cell in enumerate(row):
                if cell == "W":
                    tokens.append(str(self.givens.get((r, c), 0)))
                elif isinstance(cell, dict):
                    tokens.append(f"{cell.get('across', 0)}/{cell.get('down', 0)}")
                else:
                    tokens.append("#")
            out.append(" ".join(tokens))
        return out

    def apply_bulk_rows(self, rows: List[str]) -> None:
        """Thay the nguyen tu toan bo luoi va so cho truoc tu danh sach dong."""
        if len(rows) != self.rows:
            raise ValueError(f"Can nhap dung {self.rows} hang")
        grid: List[List[CellSpec]] = []
        givens: Dict[Tuple[int, int], int] = {}

        for r, line in enumerate(rows):
            tokens = line.split()
            if len(tokens) != self.cols:
                raise ValueError(f"Hang {r + 1}: can dung {self.cols} o cach nhau boi dau cach")
            row: List[CellSpec] = []
            for c, token in enumerate(tokens):
                if token == "#":
                    row.append("B")
                elif token in "0123456789" and len(token) == 1:
                    row.append("W")
                    if token != "0":
                        givens[(r, c)] = int(token)
                elif "/" in token:
                    parts = token.split("/")
                    if len(parts) != 2 or not all(x.isascii() and x.isdigit() and len(x) <= 2 for x in parts):
                        raise ValueError(f"O ({r + 1},{c + 1}): nhap theo dang ngang/doc, vi du 17/0")
                    a, d = int(parts[0]), int(parts[1])
                    if not (0 <= a <= 45 and 0 <= d <= 45):
                        raise ValueError(f"O ({r + 1},{c + 1}): tong goi y phai tu 0 den 45")
                    clues = {k: v for k, v in (("across", a), ("down", d)) if v}
                    row.append(clues if clues else "B")
                else:
                    raise ValueError(f"O ({r + 1},{c + 1}): ky hieu khong hop le {token!r}")
            grid.append(row)

        candidate = KakuroCSP(self.name, grid, givens=givens)
        self.grid = deepcopy(candidate.raw_grid)
        self.givens = dict(candidate.givens)

    def randomize_clues(self, rng: Optional[random.Random] = None) -> None:
        """Giu nguyen bo cuc luoi, sinh bo tong goi y moi tu mot mau dien hop le."""
        generator = rng if rng is not None else random.Random()
        csp = self.to_csp()
        old = self.grid
        grid = deepcopy(old)
        for _ in range(100):
            digits = list(range(1, 10))
            generator.shuffle(digits)
            ro = list(range(9))
            co = list(range(9))
            generator.shuffle(ro)
            generator.shuffle(co)
            assignment = {(r, c): digits[(ro[r] + co[c]) % 9] for r, c in csp.variables}
            grid = deepcopy(old)
            for run in csp.runs:
                r, c = run.clue_pos
                key = "across" if run.orientation == "ACROSS" else "down"
                cell = grid[r][c]
                if isinstance(cell, dict):
                    cell[key] = sum(assignment[v.pos] for v in run.variables)
            if grid != old:
                break
        self.grid = grid
        self.givens = {}

    def to_csp(self) -> KakuroCSP:
        return KakuroCSP(self.name, self.grid, givens=self.givens)

    def validate(self) -> KakuroCSP:
        """Kiem tra tinh hop le cua cau truc luoi va tinh nhat quan cua givens."""
        csp = self.to_csp()
        for run in csp.runs:
            if not run.is_consistent_partial(csp.givens):
                r, c = run.clue_pos
                direction = "ngang" if run.orientation == "ACROSS" else "doc"
                raise ValueError(
                    f"Mau thuan tai goi y {direction} ({r + 1}, {c + 1}): tong hoac so cho truoc khong hop le"
                )
        return csp

    def save(self, path: Path | str) -> None:
        """Luu ban nhap hop le ra file JSON."""
        self.to_csp()
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "name": self.name,
            "grid": self.grid,
            "givens": [
                {"row": r, "col": c, "value": v}
                for (r, c), v in sorted(self.givens.items())
            ],
        }
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path | str) -> "BoardEditor":
        """Nap mot file JSON Kakuro vao trinh soan thao."""
        return cls(KakuroCSP.from_json(Path(path)))
