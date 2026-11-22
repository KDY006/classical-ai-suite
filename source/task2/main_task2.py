"""Main entry point for Task 2: Tank Battle PyGame Arena & CLI Benchmark."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_SOURCE = Path(__file__).resolve().parents[1]
if str(PROJECT_SOURCE) not in sys.path:
    sys.path.insert(0, str(PROJECT_SOURCE))


def run_cli_benchmark() -> None:
    from task2.agents import (
        AlphaBetaAgent,
        HeuristicAlphaBetaAgent,
        HeuristicMinimaxAgent,
        MinimaxAgent,
        discover_external_agents,
    )
    from task2.engine import TankBattleEngine, get_all_scenarios

    print("=" * 88)
    print("TASK 2.2: FAIR 4-ALGORITHM COMPARISON ON TIER-1 ENDGAME SCENARIOS")
    print("=" * 88)
    print(f"{'Scenario':<26} | {'Algorithm':<24} | {'Action':<10} | {'States':>8} | {'Time (ms)':>9}")
    print("-" * 88)

    for scen in get_all_scenarios(tier="tier1"):
        s0 = scen.builder()
        agents = [
            MinimaxAgent(max_ply_cap=6, name="Minimax Search"),
            AlphaBetaAgent(max_ply_cap=6, name="Alpha-Beta Search"),
            HeuristicMinimaxAgent(max_depth=4, name="Heuristic Minimax (d=4)"),
            HeuristicAlphaBetaAgent(max_depth=4, name="Heuristic Alpha-Beta (d=4)"),
        ]
        for ag in agents:
            act = ag.safe_choose_action(s0)
            m = ag.last_metrics
            print(f"{scen.title:<26} | {ag.name:<24} | {act:<10} | {m.explored_states:>8,} | {m.elapsed_ms:>9.2f}")
        print("-" * 88)

    ext = discover_external_agents()
    print(f"Discovered {len(ext)} external bot plugin(s): {[b.name for b in ext]}")

    # Simulate a quick match between Heuristic Alpha-Beta and an external bot
    state = get_all_scenarios(tier="tier2")[1].builder()
    p1 = HeuristicAlphaBetaAgent(max_depth=4)
    p2 = ext[0] if ext else HeuristicMinimaxAgent(max_depth=2)
    while not state.is_terminal() and state.ply < 60:
        bot = p1 if state.current_player == 1 else p2
        move = bot.safe_choose_action(state)
        state = TankBattleEngine.apply_action(state, move)
    print(f"Sample Match ({p1.name} vs {p2.name}): ended at ply {state.ply}, winner={state.winner()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Task 2: Tank Battle Adversarial Search")
    parser.add_argument("--cli", action="store_true", help="Run headless 4-algorithm benchmark in terminal")
    parser.add_argument(
        "--headless-screenshot",
        type=str,
        default=None,
        help="Render a sample match state headlessly and save UI screenshot to path",
    )
    args = parser.parse_args()

    if args.cli:
        run_cli_benchmark()
        return

    if args.headless_screenshot:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        from task2.ui import TankBattleArenaUI

        ui = TankBattleArenaUI()
        for _ in range(6):
            ui.execute_turn()
        ui.save_screenshot(Path(args.headless_screenshot))
        import pygame

        pygame.quit()
        print(f"Saved Tank Battle UI screenshot to {args.headless_screenshot}")
        return

    from task2.ui import TankBattleArenaUI

    arena = TankBattleArenaUI()
    arena.run()


if __name__ == "__main__":
    main()
