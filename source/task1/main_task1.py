"""Run reproducible SAT and local-search experiments from the command line."""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from task1.board import NQueenBoard
from task1.min_conflicts import MinConflictsSolver, RandomConflictedSelector, TabuMaxConflictSelector
from task1.sat_solver import Glucose3NQueenSolver


def positive_integer(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("expected a positive integer")
    return number


def run_sat_demo(sizes):
    solver = Glucose3NQueenSolver()
    sample = None
    print("\nGlucose3 - propositional logic")
    print(f"{'N':>5} {'Variables':>10} {'Clauses':>12} {'Encode ms':>12} {'Solver ms':>12} {'Valid':>8}")
    for n in sizes:
        result = solver.solve(n)
        valid = result.board is not None and result.board.is_valid_solution()
        print(f"{n:5} {result.num_variables:10} {result.num_clauses:12,} "
              f"{result.encoding_time_sec * 1000:12.2f} {result.solve_time_sec * 1000:12.2f} "
              f"{str(valid):>8}")
        if n == 8 and valid:
            sample = result.board
    if sample is not None:
        print("\nExample solution for N=8")
        print(sample.render_ascii())


def run_min_conflicts_comparison(sizes, trials, max_steps):
    print(f"\nMin-Conflicts - {trials} shared starting boards, limit {max_steps} steps")
    print(f"{'N':>5} {'Method':<28} {'Success':>9} {'Mean steps':>12} {'Mean ms':>10}")
    for n in sizes:
        boards = [NQueenBoard.from_random(n, random.Random(2026 + n * 131 + trial))
                  for trial in range(trials)]
        for name, strategy in (("Random", RandomConflictedSelector()),
                               ("Max-conflict + Tabu", TabuMaxConflictSelector())):
            solver = MinConflictsSolver(strategy, max_steps=max_steps)
            results = [solver.solve(n, initial_board=board, seed=9000 + trial)
                       for trial, board in enumerate(boards)]
            success = sum(result.solved and result.board.is_valid_solution() for result in results)
            print(f"{n:5} {name:<28} {100 * success / trials:8.1f}% "
                  f"{mean(result.steps for result in results):12.1f} "
                  f"{1000 * mean(result.elapsed_sec for result in results):10.2f}")


def main():
    parser = argparse.ArgumentParser(description="N-Queen experiments")
    parser.add_argument("--sat-sizes", nargs="+", type=positive_integer, default=[4, 8, 12, 16, 20, 30, 40, 50])
    parser.add_argument("--mc-sizes", nargs="+", type=positive_integer, default=[8, 16, 32, 64, 100])
    parser.add_argument("--trials", type=positive_integer, default=25)
    parser.add_argument("--max-steps", type=positive_integer, default=2000)
    args = parser.parse_args()
    run_sat_demo(args.sat_sizes)
    run_min_conflicts_comparison(args.mc_sizes, args.trials, args.max_steps)


if __name__ == "__main__":
    main()
