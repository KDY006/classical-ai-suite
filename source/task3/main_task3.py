"""Main entry point for Task 3: Kakuro CSP Solver Benchmark & PyGame Visualizer UI."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_SOURCE = Path(__file__).resolve().parents[1]
if str(PROJECT_SOURCE) not in sys.path:
    sys.path.insert(0, str(PROJECT_SOURCE))


def run_cli_evaluation() -> None:
    from task3 import KakuroCSP, KakuroSolver, SolverMode

    maps_dir = Path(__file__).resolve().parent / "maps"
    map_files = [
        "board_5x5_example.json",
        "board_6x6_medium.json",
        "board_8x8_hard.json",
        "board_9x9_complex.json",
    ]

    print("=" * 98)
    print("TASK 3.2: KAKURO CSP SOLVER EVALUATION")
    print("=" * 98)
    print(
        f"{'Kakuro Board':<36} | {'Algorithm':<34} | {'Vars':>4} | "
        f"{'Nodes':>6} | {'Backtracks':>10} | {'Time (ms)':>9} | {'Valid':>5}"
    )
    print("-" * 98)

    for fname in map_files:
        csp = KakuroCSP.from_json(maps_dir / fname)
        for mode in (SolverMode.PLAIN_BT, SolverMode.BT_FC, SolverMode.BT_MAC_HEURISTICS):
            res = KakuroSolver(mode=mode).solve(csp)
            print(
                f"{csp.name[:36]:<36} | {mode.value:<34} | {len(csp.variables):>4} | "
                f"{res.nodes_explored:>6} | {res.backtracks:>10} | {res.elapsed_ms:>9.2f} | {str(res.valid_verified):>5}"
            )
        print("-" * 98)


def main() -> None:
    parser = argparse.ArgumentParser(description="Task 3: Kakuro CSP solver and board editor")
    parser.add_argument("--cli", action="store_true", help="Run benchmark on preset boards")
    parser.add_argument(
        "--headless-screenshot",
        type=str,
        default=None,
        help="Save a PNG screenshot of the 9x9 board",
    )
    args = parser.parse_args()

    if args.cli:
        run_cli_evaluation()
        return

    if args.headless_screenshot:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        import pygame
        from task3.visualizer_ui import KakuroVisualizerUI

        ui = KakuroVisualizerUI()
        # Switch to 9x9 Complex Board (index 1) and Forward Checking (mode 1) to show active pruning & domains
        ui.map_idx = 1
        ui.mode_idx = 1
        ui._reload_problem()
        # Advance to a PRUNE step for clear visual demonstration
        for idx, st in enumerate(ui.result.steps_trace):
            if st.step_type == "PRUNE" and idx >= 12:
                ui.step_idx = idx
                break
        ui.save_screenshot(Path(args.headless_screenshot))
        pygame.quit()
        print(f"Screenshot saved to {args.headless_screenshot}")
        return

    from task3.visualizer_ui import KakuroVisualizerUI

    app = KakuroVisualizerUI()
    app.run()


if __name__ == "__main__":
    main()
