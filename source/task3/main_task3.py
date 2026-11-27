"""Điểm khởi chạy chính cho Nhiệm vụ 3: Bộ giải Kakuro CSP & Giao diện Trực quan hóa PyGame."""

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

    print("=" * 106)
    print("NHIỆM VỤ 3.2: ĐÁNH GIÁ BỘ GIẢI KAKURO CSP TRÊN CÁC BẢNG CÂU ĐỐ VÀ CẤU HÌNH LAN TRUYỀN")
    print("=" * 106)
    print(
        f"{'Bảng câu đố Kakuro':<36} | {'Chế độ giải':<38} | {'Biến':>4} | "
        f"{'Số nút':>6} | {'Quay lui':>8} | {'Thời gian':>10} | {'Hợp lệ':>6}"
    )
    print("-" * 106)

    for fname in map_files:
        csp = KakuroCSP.from_json(maps_dir / fname)
        for mode in (SolverMode.PLAIN_BT, SolverMode.BT_FC, SolverMode.BT_MAC_HEURISTICS):
            res = KakuroSolver(mode=mode).solve(csp)
            valid_vi = "Đúng" if res.valid_verified else "Sai"
            print(
                f"{csp.name[:36]:<36} | {mode.value:<38} | {len(csp.variables):>4} | "
                f"{res.nodes_explored:>6} | {res.backtracks:>8} | {res.elapsed_ms:>7.2f} ms | {valid_vi:>6}"
            )
        print("-" * 106)


def main() -> None:
    parser = argparse.ArgumentParser(description="Nhiệm vụ 3: Bộ giải Kakuro CSP và Trình soạn thảo bảng")
    parser.add_argument("--cli", action="store_true", help="Chạy thực nghiệm đối sánh trên các bảng mẫu")
    parser.add_argument(
        "--headless-screenshot",
        type=str,
        default=None,
        help="Xuất ảnh chụp giao diện PNG trên bảng phức tạp 9x9",
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
        ui.map_idx = 1
        ui.mode_idx = 1
        ui._reload_problem()
        for idx, st in enumerate(ui.result.steps_trace):
            if st.step_type == "PRUNE" and idx >= 12:
                ui.step_idx = idx
                break
        ui.save_screenshot(Path(args.headless_screenshot))
        pygame.quit()
        print(f"Đã lưu ảnh chụp giao diện Kakuro tại: {args.headless_screenshot}")
        return

    from task3.visualizer_ui import KakuroVisualizerUI

    app = KakuroVisualizerUI()
    app.run()


if __name__ == "__main__":
    main()
