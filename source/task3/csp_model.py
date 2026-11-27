"""Mo hinh hoa huong doi tuong CSP <X, D, C> cho cau do Kakuro."""

from __future__ import annotations

import json
import unicodedata
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

CellSpec = Union[str, Dict[str, int]]


def to_ascii_label(text: str) -> str:
    """Chuyen chuoi tieng Viet co dau sang khong dau ASCII an toan cho CLI."""
    replaced = text.replace("đ", "d").replace("Đ", "D")
    normalized = unicodedata.normalize("NFD", replaced)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn").encode(
        "ascii", "ignore"
    ).decode("ascii")


@dataclass
class CellVariable:
    """Dai dien mot bien o trang X_(r,c) can dien chu so 1..9 tren bang Kakuro."""

    row: int
    col: int
    initial_domain: Set[int] = field(default_factory=lambda: set(range(1, 10)))
    across_run: Optional["RunConstraint"] = None
    down_run: Optional["RunConstraint"] = None

    @property
    def pos(self) -> Tuple[int, int]:
        return (self.row, self.col)

    def peer_positions(self) -> Set[Tuple[int, int]]:
        """Tra ve toa do cac bien hang xom cung day ngang hoac cung day doc."""
        peers: Set[Tuple[int, int]] = set()
        if self.across_run is not None:
            for v in self.across_run.variables:
                if v.pos != self.pos:
                    peers.add(v.pos)
        if self.down_run is not None:
            for v in self.down_run.variables:
                if v.pos != self.pos:
                    peers.add(v.pos)
        return peers


@dataclass
class RunConstraint:
    """Rang buoc dong thoi AllDiff va tong chinh xac tren mot day o trang lien tiep."""

    run_id: int
    orientation: str
    clue_pos: Tuple[int, int]
    target_sum: int
    variables: List[CellVariable]

    @property
    def length(self) -> int:
        return len(self.variables)

    def is_consistent_partial(self, assignment: Dict[Tuple[int, int], int]) -> bool:
        """Kiem tra phep gan bo phan co vi pham AllDiff hoac can tong min/max khong."""
        assigned_vals: List[int] = []
        unassigned_count = 0

        for var in self.variables:
            val = assignment.get(var.pos)
            if val is not None:
                if val in assigned_vals:
                    return False
                assigned_vals.append(val)
            else:
                unassigned_count += 1

        current_sum = sum(assigned_vals)
        if unassigned_count == 0:
            return current_sum == self.target_sum

        rem_sum = self.target_sum - current_sum
        if rem_sum <= 0:
            return False

        # Tinh can tong nho nhat va lon nhat tu cac chu so 1..9 chua dung
        used = set(assigned_vals)
        available = [d for d in range(1, 10) if d not in used]
        if len(available) < unassigned_count:
            return False

        min_possible = sum(available[:unassigned_count])
        max_possible = sum(available[-unassigned_count:])
        return min_possible <= rem_sum <= max_possible

    def is_satisfied_complete(self, assignment: Dict[Tuple[int, int], int]) -> bool:
        """Kiem tra toan bo day da gan day du, doi mot khac nhau va dung tong."""
        vals = [assignment.get(v.pos) for v in self.variables]
        if any(v is None for v in vals):
            return False
        int_vals = [int(v) for v in vals if v is not None]
        return len(set(int_vals)) == len(int_vals) and sum(int_vals) == self.target_sum


class KakuroCSP:
    """Dong goi tron ven bai toan thoa man rang buoc Kakuro <X, D, C>."""

    def __init__(
        self,
        name: str,
        raw_grid: List[List[CellSpec]],
        description: str = "",
        givens: Optional[Dict[Tuple[int, int], int]] = None,
    ) -> None:
        if not isinstance(raw_grid, list) or not raw_grid or not isinstance(raw_grid[0], list) or not raw_grid[0]:
            raise ValueError("Bang phai la mot luoi chu nhat khac rong")
        for row in raw_grid:
            if not isinstance(row, list) or len(row) != len(raw_grid[0]):
                raise ValueError("Tat ca cac hang trong bang phai co cung do dai")
            for cell in row:
                if cell in ("W", "B"):
                    continue
                if not isinstance(cell, dict) or not cell or not set(cell) <= {"across", "down"}:
                    raise ValueError(f"O du lieu khong hop le: {cell!r}")
                if any(type(v) is not int or not 1 <= v <= 45 for v in cell.values()):
                    raise ValueError(f"Tong goi y khong hop le (can tu 1 den 45): {cell!r}")

        self.name: str = name
        self.cli_name: str = to_ascii_label(name)
        self.description: str = description
        self.raw_grid: List[List[CellSpec]] = deepcopy(raw_grid)
        self.rows: int = len(raw_grid)
        self.cols: int = len(raw_grid[0])

        self.variables: Dict[Tuple[int, int], CellVariable] = {}
        self.ordered_positions: List[Tuple[int, int]] = []
        self.runs: List[RunConstraint] = []
        self.peers: Dict[Tuple[int, int], Set[Tuple[int, int]]] = {}

        self._build_csp()
        self.givens: Dict[Tuple[int, int], int] = dict(givens or {})
        for pos, value in self.givens.items():
            if pos not in self.variables or type(value) is not int or not 1 <= value <= 9:
                raise ValueError(f"Chu so cho truoc khong hop le tai {pos}: {value!r}")

    @classmethod
    def from_json(cls, path: Path) -> "KakuroCSP":
        with Path(path).open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls.from_dict(data, Path(path).stem)

    @classmethod
    def from_dict(cls, data: Any, default_name: str = "Kakuro") -> "KakuroCSP":
        if not isinstance(data, dict) or "grid" not in data or not isinstance(data.get("givens", []), list):
            raise ValueError("File JSON phai chua luoi grid va danh sach givens hop le")
        givens: Dict[Tuple[int, int], int] = {}
        for item in data.get("givens", []):
            if not isinstance(item, dict) or not {"row", "col", "value"} <= set(item):
                raise ValueError("Moi chu so cho truoc can co du row, col va value")
            r, c, value = item["row"], item["col"], item["value"]
            if type(r) is not int or type(c) is not int or (r, c) in givens:
                raise ValueError("Toa do chu so cho truoc bi trung hoac khong hop le")
            givens[(r, c)] = value
        return cls(
            name=str(data.get("name", default_name)),
            raw_grid=data["grid"],
            description=str(data.get("description", "")),
            givens=givens,
        )

    def _build_csp(self) -> None:
        # 1. Phat hien toan bo cac bien o trang X_(r, c)
        for r in range(self.rows):
            for c in range(self.cols):
                if self.raw_grid[r][c] == "W":
                    var = CellVariable(row=r, col=c)
                    self.variables[(r, c)] = var
                    self.ordered_positions.append((r, c))

        # 2. Phat hien cac day rang buoc ngang (ACROSS) va doc (DOWN) tu cac o goi y
        run_counter = 0
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.raw_grid[r][c]
                if not isinstance(cell, dict):
                    continue

                if "across" in cell:
                    target = int(cell["across"])
                    run_vars: List[CellVariable] = []
                    cc = c + 1
                    while cc < self.cols and (r, cc) in self.variables:
                        run_vars.append(self.variables[(r, cc)])
                        cc += 1
                    if not run_vars:
                        raise ValueError(f"Goi y ngang tai ({r + 1}, {c + 1}) khong co o trang nao")
                    rc = RunConstraint(run_counter, "ACROSS", (r, c), target, run_vars)
                    run_counter += 1
                    self.runs.append(rc)
                    for v in run_vars:
                        v.across_run = rc

                if "down" in cell:
                    target = int(cell["down"])
                    run_vars = []
                    rr = r + 1
                    while rr < self.rows and (rr, c) in self.variables:
                        run_vars.append(self.variables[(rr, c)])
                        rr += 1
                    if not run_vars:
                        raise ValueError(f"Goi y doc tai ({r + 1}, {c + 1}) khong co o trang nao")
                    rc = RunConstraint(run_counter, "DOWN", (r, c), target, run_vars)
                    run_counter += 1
                    self.runs.append(rc)
                    for v in run_vars:
                        v.down_run = rc

        if not self.variables:
            raise ValueError("Bang khong co o trang nao de giai")
        for run in self.runs:
            if not 1 <= run.length <= 9:
                raise ValueError(f"Do dai day o trang tai {run.clue_pos} vuot qua gioi han 1..9")
        for pos, var in self.variables.items():
            if var.across_run is None or var.down_run is None:
                raise ValueError(f"O trang {pos} bat buoc phai thuoc ca day ngang va day doc")
            self.peers[pos] = var.peer_positions()

    def sum_invariants(self) -> Tuple[int, int]:
        """Tra ve (tong tat ca goi y ngang, tong tat ca goi y doc) de kiem chung."""
        across_total = sum(r.target_sum for r in self.runs if r.orientation == "ACROSS")
        down_total = sum(r.target_sum for r in self.runs if r.orientation == "DOWN")
        return across_total, down_total

    def initial_domains(self) -> Dict[Tuple[int, int], Set[int]]:
        """Tra ve mien gia tri ban dau {1..9} (hoac don tri neu la chu so cho truoc)."""
        return {
            pos: {self.givens[pos]} if pos in self.givens else set(range(1, 10))
            for pos in self.ordered_positions
        }

    def is_consistent(
        self,
        pos: Tuple[int, int],
        value: int,
        assignment: Dict[Tuple[int, int], int],
    ) -> bool:
        """Kiem tra gan X_pos = value co nhat quan voi hai day ngang/doc hay khong."""
        var = self.variables[pos]
        if type(value) is not int or not 1 <= value <= 9:
            return False
        if pos in self.givens and self.givens[pos] != value:
            return False
        old = assignment.get(pos)
        assignment[pos] = value
        ok = True
        if var.across_run is not None and not var.across_run.is_consistent_partial(assignment):
            ok = False
        if ok and var.down_run is not None and not var.down_run.is_consistent_partial(assignment):
            ok = False
        if old is None:
            del assignment[pos]
        else:
            assignment[pos] = old
        return ok

    def verify_solution(self, assignment: Dict[Tuple[int, int], int]) -> bool:
        """Kiem chung doc lap toan bo bien thuoc 1..9, khop givens va dung moi day."""
        if set(assignment.keys()) != set(self.variables.keys()):
            return False
        for val in assignment.values():
            if type(val) is not int or not (1 <= val <= 9):
                return False
        if any(assignment.get(pos) != value for pos, value in self.givens.items()):
            return False
        return all(run.is_satisfied_complete(assignment) for run in self.runs)

    def render_solution_ascii(self, assignment: Dict[Tuple[int, int], int]) -> str:
        """Xuat bang loi giai dang ky tu ASCII ro rang cho terminal."""
        lines: List[str] = []
        for r in range(self.rows):
            tokens: List[str] = []
            for c in range(self.cols):
                cell = self.raw_grid[r][c]
                if cell == "W":
                    val = assignment.get((r, c))
                    tokens.append(f"{val:>5}" if val is not None else "    .")
                elif isinstance(cell, dict):
                    d_str = str(cell.get("down", ""))
                    a_str = str(cell.get("across", ""))
                    tokens.append(f"{d_str}\\{a_str}".rjust(5))
                else:
                    tokens.append("    #")
            lines.append(" ".join(tokens))
        return "\n".join(lines)
