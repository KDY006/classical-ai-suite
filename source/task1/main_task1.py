"""Command-line entry point for Task 1: N-Queen (Glucose3 SAT & Min-Conflicts)."""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

PROJECT_SOURCE = Path(__file__).resolve().parents[1]
if str(PROJECT_SOURCE) not in sys.path:
    sys.path.insert(0, str(PROJECT_SOURCE))

from task1.board import NQueenBoard
from task1.min_conflicts import (
    MinConflictsSolver,
    RandomConflictedSelector,
    TabuMaxConflictSelector,
)
from task1.sat_solver import Glucose3NQueenSolver


def run_sat_demo(sizes: list[int]) -> None:
    print("=" * 72)
    print("TASK 1.1 & 1.2: PROPOSITIONAL LOGIC CNF + PYSAT GLUCOSE3 SOLVER")
    print("=" * 72)
    print(f"{'N':>5} | {'Vars':>8} | {'CNF Clauses':>13} | {'Encode (ms)':>12} | {'Solve (ms)':>11} | {'Valid':>6}")
    print("-" * 72)

    solver = Glucose3NQueenSolver(include_col_alo=True)
    for n in sizes:
        res = solver.solve(n)
        is_valid = res.board.is_valid_solution() if res.board else False
        print(
            f"{n:>5} | {res.num_variables:>8} | {res.num_clauses:>13,} | "
            f"{res.encoding_time_sec * 1000:>12.2f} | {res.solve_time_sec * 1000:>11.2f} | {str(is_valid):>6}"
        )
        if n == 8 and res.board is not None:
            sample_board = res.board

    if "sample_board" in locals():
        print("\nSample 8-Queen solution found by Glucose3:")
        print(sample_board.render_ascii())


def run_min_conflicts_comparison(sizes: list[int], trials: int, max_steps: int) -> None:
    print("\n" + "=" * 86)
    print(f"TASK 1.3: MIN-CONFLICTS BENCHMARK ({trials} shared random initial states per N, max_steps={max_steps})")
    print("=" * 86)
    header = (
        f"{'N':>5} | {'Algorithm':<40} | {'Success':>9} | "
        f"{'Avg Steps':>10} | {'Avg Time (ms)':>13}"
    )
    print(header)
    print("-" * 86)

    std_solver = MinConflictsSolver(RandomConflictedSelector(), max_steps=max_steps)
    tabu_solver = MinConflictsSolver(TabuMaxConflictSelector(), max_steps=max_steps)

    for n in sizes:
        initial_boards = [NQueenBoard.from_random(n, random.Random(1000 + n * 97 + t)) for t in range(trials)]
        for solver in (std_solver, tabu_solver):
            successes = 0
            total_steps = 0
            total_time = 0.0
            for t, init_b in enumerate(initial_boards):
                res = solver.solve(n=n, initial_board=init_b, seed=5000 + t)
                if res.solved and res.board.is_valid_solution():
                    successes += 1
                total_steps += res.steps
                total_time += res.elapsed_sec

            rate = 100.0 * successes / trials
            avg_steps = total_steps / trials
            avg_ms = (total_time / trials) * 1000.0
            print(
                f"{n:>5} | {solver.strategy.name:<40} | {rate:>8.1f}% | "
                f"{avg_steps:>10.1f} | {avg_ms:>13.2f}"
            )
        print("-" * 86)


def main() -> None:
    parser = argparse.ArgumentParser(description="Task 1: N-Queen SAT & Min-Conflicts Solver")
    parser.add_argument("--sat-sizes", nargs="+", type=int, default=[4, 8, 12, 16, 20, 30, 40, 50])
    parser.add_argument("--mc-sizes", nargs="+", type=int, default=[8, 16, 32, 64, 100])
    parser.add_argument("--trials", type=int, default=25)
    parser.add_argument("--max-steps", type=int, default=2000)
    args = parser.parse_args()

    run_sat_demo(args.sat_sizes)
    run_min_conflicts_comparison(args.mc_sizes, trials=args.trials, max_steps=args.max_steps)


if __name__ == "__main__":
    main()
