"""Backtracking Search solver combining Constraint Propagation with MRV, Degree, and LCV heuristics."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from .csp_model import KakuroCSP
from .propagation import (
    DomainMap,
    ExtendedAC3Propagator,
    ForwardChecker,
    PrunedRecord,
    SumPartitionCatalog,
)


class SolverMode(str, Enum):
    PLAIN_BT = "Baseline Backtracking"
    BT_FC = "BT + Forward Checking + MRV"
    BT_MAC_HEURISTICS = "BT + Extended AC-3 + MRV/Degree/LCV"


@dataclass
class SolverStep:
    """Independent snapshot of a single search/propagation event for the Kakuro UI."""

    step_type: str  # PREPROCESS | SELECT_VAR | ASSIGN | PRUNE | BACKTRACK | SOLVED
    focus_pos: Optional[Tuple[int, int]]
    value: Optional[int]
    assignment: Dict[Tuple[int, int], int]
    domains: Dict[Tuple[int, int], List[int]]
    pruned: Dict[Tuple[int, int], List[int]] = field(default_factory=dict)
    message: str = ""
    nodes_so_far: int = 0
    backtracks_so_far: int = 0


@dataclass
class KakuroSolveResult:
    """Aggregate outcome and performance statistics of a Kakuro solver run."""

    puzzle_name: str
    mode: SolverMode
    solved: bool
    assignment: Dict[Tuple[int, int], int]
    elapsed_ms: float
    nodes_explored: int
    backtracks: int
    pruned_values: int
    valid_verified: bool
    steps_trace: List[SolverStep] = field(default_factory=list)
    status: str = "UNSOLVED"
    trace_truncated: bool = False


class SearchCancelled(Exception):
    """Cooperative cancellation, distinct from UNSAT."""


class KakuroSolver:
    """Object-oriented Kakuro CSP solver supporting 3 configurable propagation/heuristic modes."""

    def __init__(
        self,
        mode: SolverMode = SolverMode.BT_MAC_HEURISTICS,
        record_steps: bool = False,
        max_recorded_steps: int = 2500,
        node_limit: int = 300_000,
        cancel_event=None,
    ) -> None:
        if node_limit < 1 or max_recorded_steps < 1:
            raise ValueError("Limits must be positive.")
        self.mode: SolverMode = mode
        self.record_steps: bool = record_steps
        self.max_recorded_steps: int = max_recorded_steps
        self.node_limit: int = node_limit
        self.cancel_event = cancel_event

        self._nodes: int = 0
        self._backtracks: int = 0
        self._pruned_count: int = 0
        self._steps: List[SolverStep] = []

    def _check_cancel(self):
        if self.cancel_event is not None and self.cancel_event.is_set():
            raise SearchCancelled()

    def solve(self, csp: KakuroCSP) -> KakuroSolveResult:
        t0 = time.perf_counter()
        try:
            return self._solve(csp)
        except SearchCancelled:
            return KakuroSolveResult(csp.name, self.mode, False, dict(csp.givens),
                (time.perf_counter()-t0)*1000, self._nodes, self._backtracks,
                self._pruned_count, False, status='CANCELLED')

    def _solve(self, csp: KakuroCSP) -> KakuroSolveResult:
        self._nodes = 0
        self._backtracks = 0
        self._pruned_count = 0
        self._steps = []

        self._limit_hit = False
        self._trace_truncated = False
        t0 = time.perf_counter()
        assignment: Dict[Tuple[int, int], int] = dict(csp.givens)
        self._emit("INITIAL", None, None, assignment, csp.initial_domains(), {}, "Initial domains before preprocessing.")

        givens_ok = all(run.is_consistent_partial(assignment) for run in csp.runs)
        ok = givens_ok
        if self.mode == SolverMode.PLAIN_BT:
            domains = csp.initial_domains()
            self._emit(
                "PREPROCESS",
                None,
                None,
                assignment,
                domains,
                {},
                "Initialized full domains {1..9} without preprocessing.",
            )
        elif self.mode == SolverMode.BT_FC:
            domains, pre_pruned = SumPartitionCatalog.preprocess_node_domains(csp)
            self._count_pruned(pre_pruned)
            self._emit(
                "PREPROCESS",
                None,
                None,
                assignment,
                domains,
                pre_pruned,
                "Sum-partition node consistency narrowed initial candidate domains.",
            )
        else:
            domains, pre_pruned = SumPartitionCatalog.preprocess_node_domains(csp)
            ok, ac_pruned = ExtendedAC3Propagator.propagate(csp, assignment, domains, seed_pos=None, check_cancel=self._check_cancel) if givens_ok else (False, {})
            merged_pruned = self._merge_pruned(pre_pruned, ac_pruned)
            self._count_pruned(merged_pruned)
            self._emit(
                "PREPROCESS",
                None,
                None,
                assignment,
                domains,
                merged_pruned,
                "Applied Sum-Partition preprocessing + initial Extended AC-3 arc consistency.",
            )
        initial_ok = givens_ok and all(domains.values()) and ok
        if initial_ok and self.mode == SolverMode.BT_FC:
            for pos, value in assignment.items():
                initial_ok, pruned = ForwardChecker.propagate(csp, pos, value, assignment, domains)
                self._count_pruned(pruned)
                if pruned:
                    self._emit("PRUNE", pos, value, assignment, domains, pruned,
                               "Propagate constraints from given digits.")
                if not initial_ok:
                    break
        solved = initial_ok and self._backtrack(csp, assignment, domains)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        verified = csp.verify_solution(assignment) if solved else False

        solved = solved and verified
        status = "SOLVED" if solved else ("NODE_LIMIT" if self._limit_hit else "UNSAT")
        if solved:
            self._emit(
                "SOLVED",
                None,
                None,
                assignment,
                domains,
                {},
                f"Solved all {len(csp.variables)} variables in {self._nodes} nodes ({self._backtracks} backtracks).",
            )

        else:
            self._emit(status, None, None, assignment, domains, {},
                       "Node limit reached; no conclusion about satisfiability." if self._limit_hit else "No solution exists.")

        return KakuroSolveResult(
            puzzle_name=csp.name,
            mode=self.mode,
            solved=solved,
            assignment=dict(assignment),
            elapsed_ms=elapsed_ms,
            nodes_explored=self._nodes,
            backtracks=self._backtracks,
            pruned_values=self._pruned_count,
            valid_verified=verified,
            steps_trace=self._steps,
            status=status,
            trace_truncated=self._trace_truncated,
        )

    def _backtrack(
        self,
        csp: KakuroCSP,
        assignment: Dict[Tuple[int, int], int],
        domains: DomainMap,
    ) -> bool:
        self._check_cancel()
        if len(assignment) == len(csp.variables):
            return csp.verify_solution(assignment)
        if self._nodes >= self.node_limit:
            self._limit_hit = True
            return False

        pos = self._select_unassigned_variable(csp, assignment, domains)
        cand_values = self._order_domain_values(csp, pos, assignment, domains)

        if self.mode == SolverMode.BT_MAC_HEURISTICS:
            msg = f"MRV+Degree selected cell {pos} with domain {sorted(domains[pos])}."
        else:
            msg = f"Selected next unassigned cell {pos} with {len(domains[pos])} candidates."
        self._emit("SELECT_VAR", pos, None, assignment, domains, {}, msg)

        for val in cand_values:
            self._check_cancel()
            if self._nodes >= self.node_limit:
                self._limit_hit = True
                return False
            self._nodes += 1
            if not csp.is_consistent(pos, val, assignment):
                self._emit("REJECT", pos, val, assignment, domains, {},
                           f"Rejected X{pos} = {val}: inconsistent sum or AllDifferent.")
                continue

            saved_domains: DomainMap = {p: set(d) for p, d in domains.items()}
            assignment[pos] = val
            domains[pos] = {val}

            self._emit(
                "ASSIGN",
                pos,
                val,
                assignment,
                domains,
                {},
                f"Assigned X{pos} = {val}.",
            )

            if self.mode == SolverMode.PLAIN_BT:
                prop_ok, pruned_rec = True, {}
            elif self.mode == SolverMode.BT_FC:
                prop_ok, pruned_rec = ForwardChecker.propagate(csp, pos, val, assignment, domains)
            else:
                prop_ok, pruned_rec = ForwardChecker.propagate(csp, pos, val, assignment, domains)
                if prop_ok:
                    prop_ok, ac_pruned = ExtendedAC3Propagator.propagate(csp, assignment, domains, seed_pos=pos, changed_positions=pruned_rec, check_cancel=self._check_cancel)
                    pruned_rec = self._merge_pruned(pruned_rec, ac_pruned)

            if pruned_rec:
                self._count_pruned(pruned_rec)
                self._emit(
                    "PRUNE",
                    pos,
                    val,
                    assignment,
                    domains,
                    pruned_rec,
                    f"Constraint propagation from X{pos}={val} pruned {sum(len(v) for v in pruned_rec.values())} candidate(s)."
                    + ("" if prop_ok else " -> Constraint inconsistency detected!"),
                )

            if not prop_ok:
                self._emit("FAILURE", pos, val, assignment, domains, {}, "Dead end: constraint has no support or a domain is empty.")
            if prop_ok and self._backtrack(csp, assignment, domains):
                return True

            # Undo assignment and restore domains (Backtrack)
            del assignment[pos]
            domains.clear()
            domains.update(saved_domains)
            self._backtracks += 1
            self._emit(
                "BACKTRACK",
                pos,
                val,
                assignment,
                domains,
                {},
                f"Backtracked on X{pos} = {val}; restored domains.",
            )

            if self._limit_hit:
                return False

        return False

    def _select_unassigned_variable(
        self,
        csp: KakuroCSP,
        assignment: Dict[Tuple[int, int], int],
        domains: DomainMap,
    ) -> Tuple[int, int]:
        unassigned = [p for p in csp.ordered_positions if p not in assignment]
        if self.mode != SolverMode.BT_MAC_HEURISTICS:
            # For BT_FC use simple MRV without Degree, for PLAIN_BT static row-major order
            if self.mode == SolverMode.PLAIN_BT:
                return unassigned[0]
            return min(unassigned, key=lambda p: len(domains[p]))

        # Lecture 08 MRV (Minimum Remaining Values) + Degree Heuristic tie-breaker
        def mrv_degree_key(pos: Tuple[int, int]) -> Tuple[int, int, Tuple[int, int]]:
            mrv = len(domains[pos])
            unassigned_degree = sum(1 for peer in csp.peers[pos] if peer not in assignment)
            return (mrv, -unassigned_degree, pos)

        return min(unassigned, key=mrv_degree_key)

    def _order_domain_values(
        self,
        csp: KakuroCSP,
        pos: Tuple[int, int],
        assignment: Dict[Tuple[int, int], int],
        domains: DomainMap,
    ) -> List[int]:
        values = sorted(domains[pos])
        if self.mode != SolverMode.BT_MAC_HEURISTICS or len(values) <= 1:
            return values

        # Estimate LCV by applying the same propagation to a private trial state.
        # Trial pruning is not counted in search statistics or visualized.
        def constraining_impact(val: int) -> Tuple[int, int, int]:
            self._check_cancel()
            if not csp.is_consistent(pos, val, assignment):
                return (1, 0, val)
            trial_assignment = dict(assignment)
            trial_assignment[pos] = val
            trial_domains = {p: set(d) for p, d in domains.items()}
            trial_domains[pos] = {val}
            ok, trial_pruned = ForwardChecker.propagate(csp, pos, val, trial_assignment, trial_domains)
            if ok:
                ok, _ = ExtendedAC3Propagator.propagate(csp, trial_assignment, trial_domains, pos, changed_positions=trial_pruned, check_cancel=self._check_cancel)
            eliminated = sum(len(domains[p]) - len(trial_domains[p])
                             for p in domains if p not in trial_assignment)
            return (0 if ok else 1, eliminated, val)

        return sorted(values, key=constraining_impact)

    def _count_pruned(self, pruned: PrunedRecord) -> None:
        for vals in pruned.values():
            self._pruned_count += len(vals)

    @staticmethod
    def _merge_pruned(a: PrunedRecord, b: PrunedRecord) -> PrunedRecord:
        merged: PrunedRecord = {k: list(v) for k, v in a.items()}
        for k, vals in b.items():
            existing = set(merged.get(k, []))
            existing.update(vals)
            merged[k] = sorted(existing)
        return merged

    def _emit(
        self,
        step_type: str,
        focus_pos: Optional[Tuple[int, int]],
        value: Optional[int],
        assignment: Dict[Tuple[int, int], int],
        domains: DomainMap,
        pruned: PrunedRecord,
        message: str,
    ) -> None:
        self._check_cancel()
        if not self.record_steps:
            return
        terminal = step_type in {"SOLVED", "UNSAT", "NODE_LIMIT"}
        if not terminal and len(self._steps) >= self.max_recorded_steps - 1:
            self._trace_truncated = True
            return
        if terminal and self._trace_truncated:
            message = "Trace limit: intermediate events omitted. " + message
        self._steps.append(
            SolverStep(
                step_type=step_type,
                focus_pos=focus_pos,
                value=value,
                assignment=dict(assignment),
                domains={p: sorted(d) for p, d in domains.items()},
                pruned={p: list(vals) for p, vals in pruned.items()},
                message=message,
                nodes_so_far=self._nodes,
                backtracks_so_far=self._backtracks,
            )
        )
