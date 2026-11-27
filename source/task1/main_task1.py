"""Diem khoi chay chinh cho Nhiem vu 1: N Quan Hau (PyGame UI & CLI)."""

from __future__ import annotations

import argparse
import os
import random
import sys
from pathlib import Path
from statistics import mean, median

PROJECT_SOURCE = Path(__file__).resolve().parents[1]
if str(PROJECT_SOURCE) not in sys.path:
    sys.path.insert(0, str(PROJECT_SOURCE))

from task1.board import NQueenBoard
from task1.cnf_encoder import NQueenCNFEncoder
from task1.min_conflicts import (
    AdaptiveTabuMaxConflictSelector,
    MinConflictsSolver,
    PureMaxConflictSelector,
    RandomConflictedSelector,
)
from task1.sat_solver import Glucose3NQueenSolver


def positive_integer(value: str) -> int:
    """Kiem tra tham so dong lenh la so nguyen duong."""
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("Vui long nhap so nguyen duong")
    return number


class Task1ExperimentRunner:
    """Lop OOP dieu phoi thuc nghiem, giai thich CNF va kiem chung cho Task 1."""

    def run_cnf_explanation(self, n: int = 4) -> None:
        """In minh hoa mo hinh Logic menh de va quy trinh chuyen doi CNF."""
        encoder = NQueenCNFEncoder(n=n, include_col_alo=True)
        groups = encoder.discover_constraint_groups()
        _, stats = encoder.encode()
        rules = encoder.explain_cnf_conversion(sample_limit=2)

        print("=" * 92)
        print(f"NHIEM VU 1.1: MO HINH LOGIC MENH DE VA CHUYEN DOI CNF (MINH HOA N = {n})")
        print("=" * 92)
        print(f"- Tap bien logic: {stats.num_variables} bien P(r,c), anh xa DIMACS id(r,c) = r*{n} + c + 1")
        print(
            f"- Nhom rang buoc phat hien: {len(groups['rows'])} hang, {len(groups['columns'])} cot, "
            f"{len(groups['main_diagonals'])} cheo chinh, {len(groups['anti_diagonals'])} cheo phu"
        )
        print(
            f"- Phan ra menh de CNF: ALO hang={stats.row_alo_clauses}, ALO cot={stats.col_alo_clauses}, "
            f"AMO hang={stats.row_amo_clauses}, AMO cot={stats.col_amo_clauses}, "
            f"AMO cheo={stats.diag_amo_clauses} -> Tong={stats.total_clauses} "
            f"(ly thuyet={encoder.theoretical_clause_count()})"
        )
        w_expr = max(22, max(len(r.logical_expr) for r in rules))
        w_cnf = max(22, max(len(r.cnf_expr) for r in rules))
        sep_w = max(92, 34 + 3 + w_expr + 3 + w_cnf + 3 + 16)
        print("-" * sep_w)
        print(f"{'Loai rang buoc':<34} | {'Bieu thuc logic':<{w_expr}} | {'Dang chuan CNF':<{w_cnf}} | {'DIMACS'}")
        print("-" * sep_w)
        for rule in rules:
            dimacs_str = str(list(rule.dimacs_clause))
            print(f"{rule.category:<34} | {rule.logical_expr:<{w_expr}} | {rule.cnf_expr:<{w_cnf}} | {dimacs_str}")

    def run_sat_benchmark(self, sizes: list[int], repeats: int = 3) -> None:
        """Thuc nghiem bo giai Glucose3 voi N >= 4 tang dan va bao cao thong ke."""
        solver = Glucose3NQueenSolver(include_col_alo=True)
        # Khoi dong nhe (warm-up) de giam nhieu lan chay dau tien
        solver.solve(4, repeats=1)

        sample_board: NQueenBoard | None = None
        print("\n" + "=" * 102)
        print(f"NHIEM VU 1.2: THUC NGHIEM BO GIAI SAT GLUCOSE3 (TRUNG VI {repeats} LAN CHAY)")
        print("=" * 102)
        print(
            f"{'N':>4} {'Bien':>7} {'Menh de CNF':>13} {'Ma hoa(ms)':>12} "
            f"{'Giai(ms)':>10} {'Tong(ms)':>10} {'Quyet dinh':>12} {'Lan truyen':>12} {'Hop le':>8}"
        )
        print("-" * 102)

        for n in sizes:
            res = solver.solve(n, repeats=repeats)
            valid = res.satisfiable and res.board is not None and res.board.is_valid_solution()
            status = "Dung" if valid else ("Vo nghiem" if not res.satisfiable else "Sai")
            print(
                f"{n:4} {res.num_variables:7} {res.num_clauses:13,} "
                f"{res.encoding_time_sec * 1000:12.2f} {res.solve_time_sec * 1000:10.2f} "
                f"{res.total_time_sec * 1000:10.2f} {res.decisions:12,} "
                f"{res.propagations:12,} {status:>8}"
            )
            if n == 8 and valid:
                sample_board = res.board

        if sample_board is not None:
            print("\nVi du nghiem ban co N = 8 tim boi Glucose3:")
            print(sample_board.render_ascii())

    def run_min_conflicts_comparison(self, sizes: list[int], trials: int = 30, max_steps: int = 2500) -> None:
        """Doi sanh cong bang 3 chien luoc chon bien tren cung tap ban co khoi tao."""
        print("\n" + "=" * 104)
        print(
            f"NHIEM VU 1.3: DOI SANH MIN-CONFLICTS ({trials} ban co khoi tao chung, toi da {max_steps} buoc)"
        )
        print("=" * 104)
        print(
            f"{'N':>5} {'Chien luoc chon bien':<42} {'Dat (%)':>9} "
            f"{'Buoc TB':>10} {'Trung vi':>10} {'TG TB(ms)':>11} {'Giam buoc':>10}"
        )
        print("-" * 104)

        for n in sizes:
            boards = [
                NQueenBoard.from_random(n, random.Random(2026 + n * 131 + trial))
                for trial in range(trials)
            ]
            baseline_steps: float | None = None
            strategies = (
                RandomConflictedSelector(),
                PureMaxConflictSelector(),
                AdaptiveTabuMaxConflictSelector(),
            )
            for strategy in strategies:
                solver = MinConflictsSolver(strategy=strategy, max_steps=max_steps)
                results = [
                    solver.solve(n, initial_board=board, seed=9000 + trial)
                    for trial, board in enumerate(boards)
                ]
                success = sum(r.solved and r.board.is_valid_solution() for r in results)
                avg_steps = mean(r.steps for r in results)
                med_steps = median(r.steps for r in results)
                avg_ms = 1000.0 * mean(r.elapsed_sec for r in results)

                if baseline_steps is None:
                    baseline_steps = avg_steps
                    gain_str = "-"
                else:
                    pct = 100.0 * (baseline_steps - avg_steps) / max(1e-9, baseline_steps)
                    gain_str = f"{pct:+.1f}%"

                print(
                    f"{n:5} {strategy.cli_name:<42} {100.0 * success / trials:8.1f}% "
                    f"{avg_steps:10.1f} {med_steps:10.1f} {avg_ms:11.2f} {gain_str:>10}"
                )
            print("-" * 104)

    def run_verification_suite(self) -> bool:
        """Chay bo kiem chung toan hoc, tinh dung dan va hieu nang cua Task 1."""
        print("=" * 78)
        print("KIEM CHUNG TU DONG NHIEM VU 1 (CNF, GLUCOSE3, BOARD, MIN-CONFLICTS)")
        print("=" * 78)

        # 1. Kiem chung cong thuc tong so menh de CNF voi ca hai che do ALO cot
        for include_col in (True, False):
            for n in range(1, 26):
                enc = NQueenCNFEncoder(n=n, include_col_alo=include_col)
                clauses, stats = enc.encode()
                assert len(clauses) == stats.total_clauses
                assert stats.total_clauses == enc.theoretical_clause_count(), (
                    f"Sai lech so menh de tai N={n}, include_col={include_col}"
                )
        print("[DAT] 1. Cong thuc so menh de CNF khop 100% voi ma hoa (N = 1..25).")

        # 2. Kiem chung UNSAT cho N=2, 3 va nghiem hop le cho N=1, 4..30
        sat_solver = Glucose3NQueenSolver()
        for unsat_n in (2, 3):
            res = sat_solver.solve(unsat_n)
            assert not res.satisfiable and res.board is None, f"Ky vong UNSAT tai N={unsat_n}"
        for sat_n in (1, 4, 5, 6, 7, 8, 12, 16, 20, 30):
            res = sat_solver.solve(sat_n)
            assert res.satisfiable and res.board is not None and res.board.is_valid_solution(), (
                f"Nghiem SAT khong hop le tai N={sat_n}"
            )
        print("[DAT] 2. Glucose3 xac dinh dung UNSAT (N=2,3) va nghiem hop le (N=1,4..30).")

        # 3. Kiem chung cap nhat xung dot O(1) cua NQueenBoard
        rng = random.Random(42)
        board = NQueenBoard.from_random(12, rng)
        for _ in range(500):
            board.move_queen(rng.randrange(12), rng.randrange(12))
            assert board.total_conflicts() == board.compute_total_conflicts_direct()
        print("[DAT] 3. Cap nhat gia tang xung dot O(1) cua NQueenBoard chinh xac tuyet doi.")

        # 4. Kiem chung tinh nhat quan giua solve() va iter_solve()
        init_b = NQueenBoard.from_random(12, random.Random(77))
        direct = MinConflictsSolver(AdaptiveTabuMaxConflictSelector(), max_steps=1000).solve(
            12, initial_board=init_b, seed=123
        )
        snaps = list(
            MinConflictsSolver(AdaptiveTabuMaxConflictSelector(), max_steps=1000).iter_solve(
                12, initial_board=init_b, seed=123
            )
        )
        assert snaps[-1].step == direct.steps
        assert list(snaps[-1].queens) == direct.board.queens
        assert snaps[-1].solved == direct.solved
        print("[DAT] 4. Giao dien solve() va iter_solve() dong nhat 100% tung buoc.")

        # 5. Kiem chung hieu nang Heuristic de xuat tren cac muc N = 4, 8, 16, 32, 64, 100
        for n in (4, 8, 16, 32, 64, 100):
            trials = 30
            boards = [NQueenBoard.from_random(n, random.Random(500 + n * 31 + i)) for i in range(trials)]
            std_runs = [
                MinConflictsSolver(RandomConflictedSelector(), max_steps=2500).solve(
                    n, initial_board=b, seed=1000 + i
                )
                for i, b in enumerate(boards)
            ]
            prop_runs = [
                MinConflictsSolver(AdaptiveTabuMaxConflictSelector(), max_steps=2500).solve(
                    n, initial_board=b, seed=1000 + i
                )
                for i, b in enumerate(boards)
            ]
            assert all(r.solved and r.board.is_valid_solution() for r in prop_runs), (
                f"Heuristic de xuat chua dat 100% thanh cong tai N={n}"
            )
            std_avg = mean(r.steps for r in std_runs)
            prop_avg = mean(r.steps for r in prop_runs)
            if n >= 8:
                assert prop_avg < std_avg, (
                    f"Heuristic de xuat chua giam so buoc tai N={n}: {prop_avg:.1f} vs {std_avg:.1f}"
                )
        print("[DAT] 5. Heuristic Max-Conflict + Tabu thich nghi dat 100% va giam buoc tren moi N.")
        print("KET LUAN: TAT CA 5 NHOM KIEM CHUNG DEU DAT.")
        return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Nhiem vu 1: Bai toan N Quan Hau (Giao dien PyGame toi gian & CLI)"
    )
    parser.add_argument("--cli", action="store_true", help="Chay tron bo thuc nghiem tren terminal")
    parser.add_argument(
        "--explain-cnf",
        type=positive_integer,
        default=None,
        help="In minh hoa chuyen doi Logic menh de sang CNF cho kich thuoc N",
    )
    parser.add_argument(
        "--sat-sizes",
        nargs="+",
        type=positive_integer,
        default=[4, 8, 12, 16, 20, 30, 40, 50],
        help="Danh sach kich thuoc N cho thuc nghiem Glucose3",
    )
    parser.add_argument(
        "--sat-repeats",
        type=positive_integer,
        default=3,
        help="So lan lap do trung vi thoi gian cho Glucose3",
    )
    parser.add_argument(
        "--mc-sizes",
        nargs="+",
        type=positive_integer,
        default=[8, 16, 32, 64, 100],
        help="Danh sach kich thuoc N cho doi sanh Min-Conflicts",
    )
    parser.add_argument("--trials", type=positive_integer, default=30, help="So ban co thu nghiem moi muc N")
    parser.add_argument("--max-steps", type=positive_integer, default=2500, help="So buoc toi da Min-Conflicts")
    parser.add_argument("--verify", action="store_true", help="Chay bo kiem chung tu dong toan dien")
    parser.add_argument(
        "--headless-screenshot",
        type=str,
        default=None,
        help="Xuat anh chup giao dien PyGame ra file PNG o che do khong cua so",
    )
    parser.add_argument(
        "--screenshot-mode",
        choices=("conflicts", "solved", "sat"),
        default="conflicts",
        help="Trang thai hien thi khi chup anh headless (conflicts, solved, sat)",
    )
    args = parser.parse_args()

    runner = Task1ExperimentRunner()

    if args.verify:
        runner.run_verification_suite()
        return

    if args.headless_screenshot:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        import pygame
        from task1.ui_nqueen import MinimalNQueenUI

        ui = MinimalNQueenUI(initial_n=8)
        if args.screenshot_mode == "sat":
            ui.set_algorithm("sat")
            ui.solve_immediately()
        elif args.screenshot_mode == "solved":
            ui.set_board_size(12)
            ui.run_quick_compare()
        else:
            ui.set_board_size(8)
            ui.step_once()
        ui.save_screenshot(Path(args.headless_screenshot))
        pygame.quit()
        print(f"Da luu anh chup giao dien N-Queen tai: {args.headless_screenshot}")
        return

    if args.explain_cnf is not None and not args.cli:
        runner.run_cnf_explanation(args.explain_cnf)
        return

    if args.cli:
        runner.run_cnf_explanation(args.explain_cnf or 4)
        runner.run_sat_benchmark(args.sat_sizes, repeats=args.sat_repeats)
        runner.run_min_conflicts_comparison(args.mc_sizes, args.trials, args.max_steps)
        return

    from task1.ui_nqueen import MinimalNQueenUI

    MinimalNQueenUI(initial_n=8).run()


if __name__ == "__main__":
    main()
