"""Object-oriented CSP formulation <X, D, C> for Kakuro puzzles."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

CellSpec = Union[str, Dict[str, int]]


@dataclass
class CellVariable:
    """Represents a single playable white square X_(r,c) on a Kakuro board."""

    row: int
    col: int
    initial_domain: Set[int] = field(default_factory=lambda: set(range(1, 10)))
    across_run: Optional["RunConstraint"] = None
    down_run: Optional["RunConstraint"] = None

    @property
    def pos(self) -> Tuple[int, int]:
        return (self.row, self.col)

    def peer_positions(self) -> Set[Tuple[int, int]]:
        """Return coordinates of all variables sharing a horizontal or vertical run."""
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
    """Simultaneous AllDiff and exact-sum constraint over a contiguous line of white cells."""

    run_id: int
    orientation: str  # "ACROSS" or "DOWN"
    clue_pos: Tuple[int, int]
    target_sum: int
    variables: List[CellVariable]

    @property
    def length(self) -> int:
        return len(self.variables)

    def is_consistent_partial(self, assignment: Dict[Tuple[int, int], int]) -> bool:
        """Check whether ``assignment`` violates AllDiff or sum bounds on this run."""
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

        # Compute minimum and maximum achievable sums using distinct unused digits in 1..9
        used = set(assigned_vals)
        available = [d for d in range(1, 10) if d not in used]
        if len(available) < unassigned_count:
            return False

        min_possible = sum(available[:unassigned_count])
        max_possible = sum(available[-unassigned_count:])
        return min_possible <= rem_sum <= max_possible

    def is_satisfied_complete(self, assignment: Dict[Tuple[int, int], int]) -> bool:
        vals = [assignment.get(v.pos) for v in self.variables]
        if any(v is None for v in vals):
            return False
        int_vals = [int(v) for v in vals if v is not None]
        return len(set(int_vals)) == len(int_vals) and sum(int_vals) == self.target_sum


class KakuroCSP:
    """Encapsulates the Kakuro Constraint Satisfaction Problem <X, D, C>."""

    def __init__(
        self,
        name: str,
        raw_grid: List[List[CellSpec]],
        description: str = "",
        givens: Optional[Dict[Tuple[int, int], int]] = None,
    ) -> None:
        if not isinstance(raw_grid, list) or not raw_grid or not isinstance(raw_grid[0], list) or not raw_grid[0]:
            raise ValueError("The board must be a non-empty rectangular grid.")
        for row in raw_grid:
            if not isinstance(row, list) or len(row) != len(raw_grid[0]):
                raise ValueError("All rows must have the same length.")
            for cell in row:
                if cell in ("W", "B"):
                    continue
                if not isinstance(cell, dict) or not cell or not set(cell) <= {"across", "down"}:
                    raise ValueError(f"Invalid cell: {cell!r}")
                if any(type(v) is not int or not 1 <= v <= 45 for v in cell.values()):
                    raise ValueError(f"Invalid clue sum: {cell!r}")
        self.name: str = name
        self.description: str = description
        self.raw_grid: List[List[CellSpec]] = deepcopy(raw_grid)
        self.rows: int = len(raw_grid)
        self.cols: int = len(raw_grid[0]) if self.rows > 0 else 0

        self.variables: Dict[Tuple[int, int], CellVariable] = {}
        self.ordered_positions: List[Tuple[int, int]] = []
        self.runs: List[RunConstraint] = []
        self.peers: Dict[Tuple[int, int], Set[Tuple[int, int]]] = {}

        self._build_csp()
        self.givens = dict(givens or {})
        for pos, value in self.givens.items():
            if pos not in self.variables or type(value) is not int or not 1 <= value <= 9:
                raise ValueError(f"Invalid given digit at {pos}: {value!r}")

    @classmethod
    def from_json(cls, path: Path) -> "KakuroCSP":
        with Path(path).open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls.from_dict(data, Path(path).stem)

    @classmethod
    def from_dict(cls, data, default_name="Kakuro") -> "KakuroCSP":
        if not isinstance(data, dict) or "grid" not in data or not isinstance(data.get("givens", []), list):
            raise ValueError("JSON must contain a grid and a valid givens list.")
        givens = {}
        for item in data.get("givens", []):
            if not isinstance(item, dict) or not {"row", "col", "value"} <= set(item):
                raise ValueError("Each given requires row, col and value.")
            r, c, value = item["row"], item["col"], item["value"]
            if type(r) is not int or type(c) is not int or (r, c) in givens:
                raise ValueError("Invalid or duplicate given coordinates.")
            givens[(r, c)] = value
        return cls(
            name=data.get("name", default_name),
            raw_grid=data["grid"],
            description=data.get("description", ""),
            givens=givens,
        )

    def _build_csp(self) -> None:
        # 1. Identify all white cells X_(r, c)
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.raw_grid[r][c]
                if cell == "W":
                    var = CellVariable(row=r, col=c)
                    self.variables[(r, c)] = var
                    self.ordered_positions.append((r, c))

        # 2. Discover horizontal (ACROSS) and vertical (DOWN) runs from clue cells
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
                        raise ValueError(f"Across clue at ({r+1}, {c+1}) has no white cells.")
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
                        raise ValueError(f"Down clue at ({r+1}, {c+1}) has no white cells.")
                    rc = RunConstraint(run_counter, "DOWN", (r, c), target, run_vars)
                    run_counter += 1
                    self.runs.append(rc)
                    for v in run_vars:
                        v.down_run = rc

        if not self.variables:
            raise ValueError("The board has no white cells.")
        for run in self.runs:
            if not 1 <= run.length <= 9:
                raise ValueError(f"Invalid run length at {run.clue_pos}.")
        for pos, var in self.variables.items():
            if var.across_run is None or var.down_run is None:
                raise ValueError(f"White cell {pos} requires both across and down clues.")
            self.peers[pos] = var.peer_positions()

    def initial_domains(self) -> Dict[Tuple[int, int], Set[int]]:
        return {pos: {self.givens[pos]} if pos in self.givens else set(range(1, 10)) for pos in self.ordered_positions}

    def is_consistent(
        self,
        pos: Tuple[int, int],
        value: int,
        assignment: Dict[Tuple[int, int], int],
    ) -> bool:
        """Check whether assigning ``X_pos = value`` stays consistent with its two runs."""
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
        """Independently verify that every variable is assigned in 1..9 and all runs hold."""
        if set(assignment.keys()) != set(self.variables.keys()):
            return False
        for val in assignment.values():
            if type(val) is not int or not (1 <= val <= 9):
                return False
        if any(assignment.get(pos) != value for pos, value in self.givens.items()):
            return False
        return all(run.is_satisfied_complete(assignment) for run in self.runs)
