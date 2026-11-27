"""Điểm khởi chạy chính cho Nhiệm vụ 2: Đấu Tăng Đối Kháng (PyGame Arena & CLI)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_SOURCE = Path(__file__).resolve().parents[1]
if str(PROJECT_SOURCE) not in sys.path:
    sys.path.insert(0, str(PROJECT_SOURCE))

ACTION_VI = {
    "MOVE_UP": "LÊN",
    "MOVE_DOWN": "XUỐNG",
    "MOVE_LEFT": "TRÁI",
    "MOVE_RIGHT": "PHẢI",
    "FIRE": "BẮN",
    "STAY": "ĐỨNG YÊN",
}


def run_cli_benchmark() -> None:
    from task2.agents import (
        AlphaBetaAgent,
        HeuristicAlphaBetaAgent,
        HeuristicMinimaxAgent,
        MinimaxAgent,
        discover_external_agents,
    )
    from task2.engine import TankBattleEngine, get_all_scenarios

    print("=" * 94)
    print("NHIỆM VỤ 2.2: ĐỐI SÁNH CÔNG BẰNG 4 CẤU HÌNH THUẬT TOÁN TRÊN KỊCH BẢN TÀN CUỘC (TẦNG 1)")
    print("=" * 94)
    print(f"{'Kịch bản bản đồ':<30} | {'Cấu hình thuật toán':<26} | {'Nước đi':<10} | {'Số nút':>8} | {'Thời gian':>10}")
    print("-" * 94)

    for scen in get_all_scenarios(tier="tier1"):
        s0 = scen.builder()
        agents = [
            MinimaxAgent(max_ply_cap=6, name="Minimax thuần"),
            AlphaBetaAgent(max_ply_cap=6, name="Alpha-Beta thuần"),
            HeuristicMinimaxAgent(max_depth=4, name="Heuristic Minimax (d=4)"),
            HeuristicAlphaBetaAgent(max_depth=4, name="Heuristic Alpha-Beta (d=4)"),
        ]
        for ag in agents:
            act = ag.safe_choose_action(s0)
            m = ag.last_metrics
            act_vi = ACTION_VI.get(act, act)
            print(
                f"{scen.title:<30} | {ag.name:<26} | {act_vi:<10} | "
                f"{m.explored_states:>8,} | {m.elapsed_ms:>7.2f} ms"
            )
        print("-" * 94)

    ext = discover_external_agents()
    print(f"Đã phát hiện {len(ext)} bot nhóm ngoài: {[b.name for b in ext]}")

    state = get_all_scenarios(tier="tier2")[1].builder()
    p1 = HeuristicAlphaBetaAgent(max_depth=4, name="Heuristic Alpha-Beta (d=4)")
    p2 = ext[0] if ext else HeuristicMinimaxAgent(max_depth=2, name="Heuristic Minimax (d=2)")
    while not state.is_terminal() and state.ply < 60:
        bot = p1 if state.current_player == 1 else p2
        move = bot.safe_choose_action(state)
        state = TankBattleEngine.apply_action(state, move)
    w = state.winner()
    ket_qua = "Phe MAX thắng" if w == 1 else ("Phe MIN thắng" if w == 2 else "Chưa phân thắng bại / Hòa")
    print(f"Trận đấu mẫu ({p1.name} vs {p2.name}): dừng ở lượt {state.ply}, kết quả: {ket_qua}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Nhiệm vụ 2: Trò chơi Đấu Tăng Tìm kiếm Đối kháng")
    parser.add_argument("--cli", action="store_true", help="Chạy đối sánh 4 thuật toán trên dòng lệnh")
    parser.add_argument(
        "--headless-screenshot",
        type=str,
        default=None,
        help="Chụp ảnh giao diện trận đấu mẫu ra đường dẫn file PNG",
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
        print(f"Đã lưu ảnh chụp giao diện Đấu Tăng tại: {args.headless_screenshot}")
        return

    from task2.ui import TankBattleArenaUI

    arena = TankBattleArenaUI()
    arena.run()


if __name__ == "__main__":
    main()
