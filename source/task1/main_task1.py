"""Chương trình dòng lệnh chạy thực nghiệm N-Queen với Glucose3 SAT và Min-Conflicts."""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from task1.board import NQueenBoard
from task1.min_conflicts import (
    MinConflictsSolver,
    RandomConflictedSelector,
    TabuMaxConflictSelector,
)
from task1.sat_solver import Glucose3NQueenSolver


def positive_integer(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("vui lòng nhập số nguyên dương")
    return number


def run_sat_demo(sizes: list[int]) -> None:
    solver = Glucose3NQueenSolver()
    sample = None
    print("=" * 76)
    print("NHIỆM VỤ 1.1 & 1.2: LOGIC MỆNH ĐỀ CNF + BỘ GIẢI GLUCOSE3 (PYSAT)")
    print("=" * 76)
    print(f"{'N':>5} {'Số biến':>10} {'Số mệnh đề':>14} {'Mã hóa (ms)':>13} {'Giải (ms)':>12} {'Hợp lệ':>10}")
    print("-" * 76)
    for n in sizes:
        result = solver.solve(n)
        valid = result.board is not None and result.board.is_valid_solution()
        valid_str = "Đúng" if valid else "Sai"
        print(
            f"{n:5} {result.num_variables:10} {result.num_clauses:14,} "
            f"{result.encoding_time_sec * 1000:13.2f} {result.solve_time_sec * 1000:12.2f} "
            f"{valid_str:>10}"
        )
        if n == 8 and valid:
            sample = result.board
    if sample is not None:
        print("\nVí dụ nghiệm bàn cờ N = 8 tìm bởi Glucose3:")
        print(sample.render_ascii())


def run_min_conflicts_comparison(sizes: list[int], trials: int, max_steps: int) -> None:
    print("\n" + "=" * 86)
    print(f"NHIỆM VỤ 1.3: ĐỐI SÁNH MIN-CONFLICTS ({trials} bàn cờ khởi tạo chung, tối đa {max_steps} bước)")
    print("=" * 86)
    print(f"{'N':>5} {'Phương pháp chọn biến':<42} {'Tỷ lệ đạt':>10} {'Bước TB':>11} {'Thời gian TB':>13}")
    print("-" * 86)
    for n in sizes:
        boards = [
            NQueenBoard.from_random(n, random.Random(2026 + n * 131 + trial))
            for trial in range(trials)
        ]
        for strategy in (RandomConflictedSelector(), TabuMaxConflictSelector()):
            solver = MinConflictsSolver(strategy, max_steps=max_steps)
            results = [
                solver.solve(n, initial_board=board, seed=9000 + trial)
                for trial, board in enumerate(boards)
            ]
            success = sum(result.solved and result.board.is_valid_solution() for result in results)
            print(
                f"{n:5} {strategy.name:<42} {100 * success / trials:9.1f}% "
                f"{mean(result.steps for result in results):11.1f} "
                f"{1000 * mean(result.elapsed_sec for result in results):10.2f} ms"
            )
        print("-" * 86)


def main() -> None:
    parser = argparse.ArgumentParser(description="Thực nghiệm bài toán N Quân Hậu (Task 1)")
    parser.add_argument("--sat-sizes", nargs="+", type=positive_integer, default=[4, 8, 12, 16, 20, 30, 40, 50])
    parser.add_argument("--mc-sizes", nargs="+", type=positive_integer, default=[8, 16, 32, 64, 100])
    parser.add_argument("--trials", type=positive_integer, default=25)
    parser.add_argument("--max-steps", type=positive_integer, default=2000)
    args = parser.parse_args()
    run_sat_demo(args.sat_sizes)
    run_min_conflicts_comparison(args.mc_sizes, args.trials, args.max_steps)


if __name__ == "__main__":
    main()
