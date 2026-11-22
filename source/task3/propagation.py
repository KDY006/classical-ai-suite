"""Constraint propagation techniques for Kakuro: Sum Partitions, Forward Checking, and Extended AC-3."""

from __future__ import annotations

from collections import deque
from itertools import combinations
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from .csp_model import KakuroCSP, RunConstraint

DomainMap = Dict[Tuple[int, int], Set[int]]
PrunedRecord = Dict[Tuple[int, int], List[int]]


class SumPartitionCatalog:
    """Precomputes all valid duplicate-free digit combinations (1..9) for every (length, sum)."""

    _CACHE: Dict[Tuple[int, int], List[FrozenSet[int]]] = {}
    _INITIALIZED: bool = False

    @classmethod
    def initialize(cls) -> None:
        if cls._INITIALIZED:
            return
        digits = range(1, 10)
        for length in range(1, 10):
            for comb in combinations(digits, length):
                key = (length, sum(comb))
                cls._CACHE.setdefault(key, []).append(frozenset(comb))
        cls._INITIALIZED = True

    @classmethod
    def allowed_digits(
        cls,
        length: int,
        target_sum: int,
        forbidden: Set[int],
    ) -> Set[int]:
        """Return union of digits participating in at least one valid partition of (length, target_sum)
        that avoids all ``forbidden`` digits.
        """
        cls.initialize()
        if length <= 0 or target_sum <= 0:
            return set()
        partitions = cls._CACHE.get((length, target_sum), [])
        valid_union: Set[int] = set()
        for part in partitions:
            if part.isdisjoint(forbidden):
                valid_union.update(part)
        return valid_union

    @classmethod
    def preprocess_node_domains(cls, csp: KakuroCSP) -> Tuple[DomainMap, PrunedRecord]:
        """Apply initial sum-partition node consistency across every horizontal and vertical run."""
        cls.initialize()
        domains = csp.initial_domains()
        pruned: PrunedRecord = {}

        for pos, var in csp.variables.items():
            allowed = set(range(1, 10))
            if var.across_run is not None:
                allowed &= cls.allowed_digits(var.across_run.length, var.across_run.target_sum, set())
            if var.down_run is not None:
                allowed &= cls.allowed_digits(var.down_run.length, var.down_run.target_sum, set())
            removed = sorted(domains[pos] - allowed)
            if removed:
                pruned[pos] = removed
            domains[pos] = allowed

        return domains, pruned


class ForwardChecker:
    """Implements Forward Checking on unassigned neighbors after assigning X_pos = value."""

    @staticmethod
    def propagate(
        csp: KakuroCSP,
        pos: Tuple[int, int],
        value: int,
        assignment: Dict[Tuple[int, int], int],
        domains: DomainMap,
    ) -> Tuple[bool, PrunedRecord]:
        var = csp.variables[pos]
        pruned: PrunedRecord = {}

        for run in (var.across_run, var.down_run):
            if run is None:
                continue
            assigned_vals = {assignment[v.pos] for v in run.variables if v.pos in assignment}
            unassigned_vars = [v for v in run.variables if v.pos not in assignment]
            k_rem = len(unassigned_vars)
            sum_rem = run.target_sum - sum(assigned_vals)

            if k_rem == 0:
                if sum_rem != 0:
                    return False, pruned
                continue

            valid_for_run = SumPartitionCatalog.allowed_digits(k_rem, sum_rem, assigned_vals)
            if not valid_for_run:
                return False, pruned

            for u_var in unassigned_vars:
                u_pos = u_var.pos
                to_remove = [d for d in domains[u_pos] if d not in valid_for_run]
                if to_remove:
                    for d in to_remove:
                        domains[u_pos].remove(d)
                    pruned.setdefault(u_pos, []).extend(sorted(to_remove))
                if not domains[u_pos]:
                    return False, pruned

        return True, pruned


class ExtendedAC3Propagator:
    """Generalized Arc Consistency (MAC) over Kakuro AllDiff + Exact-Sum run constraints.

    Maintains a worklist of RunConstraints. For each run:
      1. Eliminates digits already fixed in assigned or singleton cells of the same run.
      2. Prunes candidate value ``v`` for unassigned cell ``X_i`` if no valid tuple of
         distinct remaining values from the other unassigned cells' current domains can
         sum to ``target_sum - sum(assigned) - v`` (verified via fast domain-aware DP/DFS
         since run length <= 8).
    """

    @classmethod
    def propagate(
        cls,
        csp: KakuroCSP,
        assignment: Dict[Tuple[int, int], int],
        domains: DomainMap,
        seed_pos: Optional[Tuple[int, int]] = None,
    ) -> Tuple[bool, PrunedRecord]:
        pruned: PrunedRecord = {}
        queue: deque[RunConstraint] = deque()
        in_queue: Set[int] = set()

        if seed_pos is None:
            initial_runs = csp.runs
        else:
            v = csp.variables[seed_pos]
            initial_runs = [r for r in (v.across_run, v.down_run) if r is not None]

        for r in initial_runs:
            if r.run_id not in in_queue:
                queue.append(r)
                in_queue.add(r.run_id)

        while queue:
            run = queue.popleft()
            in_queue.remove(run.run_id)

            ok, changed_positions = cls._revise_run(run, assignment, domains, pruned)
            if not ok:
                return False, pruned

            for ch_pos in changed_positions:
                ch_var = csp.variables[ch_pos]
                for neighbor_run in (ch_var.across_run, ch_var.down_run):
                    if (
                        neighbor_run is not None
                        and neighbor_run.run_id != run.run_id
                        and neighbor_run.run_id not in in_queue
                    ):
                        queue.append(neighbor_run)
                        in_queue.add(neighbor_run.run_id)

        return True, pruned

    @classmethod
    def _revise_run(
        cls,
        run: RunConstraint,
        assignment: Dict[Tuple[int, int], int],
        domains: DomainMap,
        pruned: PrunedRecord,
    ) -> Tuple[bool, List[Tuple[int, int]]]:
        changed: List[Tuple[int, int]] = []
        used_assigned: Set[int] = set()
        for v in run.variables:
            if v.pos in assignment:
                val = assignment[v.pos]
                if val in used_assigned:
                    return False, changed
                used_assigned.add(val)

        unassigned = [v.pos for v in run.variables if v.pos not in assignment]
        rem_sum = run.target_sum - sum(used_assigned)

        if not unassigned:
            return (rem_sum == 0), changed
        if rem_sum <= 0:
            return False, changed

        other_domains = [domains[p] - used_assigned for p in unassigned]
        if any(not d for d in other_domains):
            for p, d in zip(unassigned, other_domains):
                removed = sorted(domains[p] - d)
                if removed:
                    domains[p] = d
                    pruned.setdefault(p, []).extend(removed)
            return False, changed

        # Check generalized arc support for each candidate value of each unassigned variable
        k = len(unassigned)
        for idx, pos in enumerate(unassigned):
            current_dom = list(domains[pos])
            supported_vals: Set[int] = set()
            peer_doms = [domains[unassigned[j]] for j in range(k) if j != idx]

            for cand in current_dom:
                if cand in used_assigned:
                    continue
                if cls._has_support(peer_doms, 0, rem_sum - cand, used_assigned | {cand}):
                    supported_vals.add(cand)

            if len(supported_vals) < len(current_dom):
                removed = sorted(domains[pos] - supported_vals)
                domains[pos] = supported_vals
                pruned.setdefault(pos, []).extend(removed)
                changed.append(pos)
                if not supported_vals:
                    return False, changed

        return True, changed

    @classmethod
    def _has_support(
        cls,
        peer_doms: List[Set[int]],
        idx: int,
        target_rem: int,
        used: Set[int],
    ) -> bool:
        rem_vars = len(peer_doms) - idx
        if rem_vars == 0:
            return target_rem == 0

        # Quick min/max residual sum bound check
        min_rem = rem_vars * (rem_vars + 1) // 2
        max_rem = rem_vars * (19 - rem_vars) // 2
        if target_rem < min_rem or target_rem > max_rem:
            return False

        for val in peer_doms[idx]:
            if val not in used and val <= target_rem:
                if cls._has_support(peer_doms, idx + 1, target_rem - val, used | {val}):
                    return True
        return False
