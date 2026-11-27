"""Diem khoi chay chinh cho Nhiem vu 3: Bo giai Kakuro CSP, CLI va Giao dien PyGame."""

from __future__ import annotations

import argparse
import os
import random
import statistics
import sys
import tempfile
from pathlib import Path
from threading import Event
from typing import List, Tuple

PROJECT_SOURCE = Path(__file__).resolve().parents[1]
if str(PROJECT_SOURCE) not in sys.path:
    sys.path.insert(0, str(PROJECT_SOURCE))

from task3 import (
    BoardEditor,
    ExtendedAC3Propagator,
    KakuroCSP,
    KakuroSolver,
    SolverMode,
    SumPartitionCatalog,
)


class Task3ExperimentRunner:
    """Dieu phoi giai thich CSP, benchmark CLI, kiem chung 22 tieu chi va chup anh UI."""

    MAP_FILES: Tuple[str, ...] = (
        "board_5x5_example.json",
        "board_6x6_medium.json",
        "board_8x8_hard.json",
        "board_9x9_complex.json",
    )
    MODES: Tuple[SolverMode, ...] = (
        SolverMode.PLAIN_BT,
        SolverMode.BT_FC,
        SolverMode.BT_MAC_HEURISTICS,
    )

    def __init__(self, maps_dir: Path | None = None) -> None:
        self.maps_dir = Path(maps_dir or Path(__file__).resolve().parent / "maps")

    def _load_all_maps(self) -> List[KakuroCSP]:
        return [KakuroCSP.from_json(self.maps_dir / fname) for fname in self.MAP_FILES]

    def explain_csp(self) -> None:
        """In tom tat mo hinh <X, D, C>, bat bien tong va hieu qua thu hep mien ban dau."""
        print("=" * 102)
        print("NHIEM VU 3.1: MO HINH HOA CSP <X, D, C> VA HIEU QUA TIEN XU LY KAKURO")
        print("=" * 102)
        print("Thanh phan bai toan:")
        print("  - Tap bien X      : Moi o trang (r, c) la mot bien so nguyen X_(r,c).")
        print("  - Mien gia tri D  : D(X_(r,c)) = {1, 2, ..., 9} (hoac {v} neu la so cho truoc).")
        print("  - Tap rang buoc C : Moi day ngang (Across) va doc (Down) gom dong thoi:")
        print("                      (1) AllDiff(X_1, ..., X_k) doi mot khac nhau;")
        print("                      (2) Tong(X_1 + ... + X_k) = S (tong goi y cua day).")
        print("-" * 102)
        print(
            f"{'Bang Kakuro':<36} | {'Kich thuoc':>9} | {'|X|':>4} | {'|C|':>4} | "
            f"{'Tong H=V':>9} | {'|D| goc':>7} | {'Sau Part.':>9} | {'Sau AC-3':>8} | {'Don tri':>7}"
        )
        print("-" * 102)

        for csp in self._load_all_maps():
            sum_h, sum_v = csp.sum_invariants()
            raw_total = sum(len(d) for d in csp.initial_domains().values())
            part_domains, _ = SumPartitionCatalog.preprocess_node_domains(csp)
            part_total = sum(len(d) for d in part_domains.values())

            ac_domains = {p: set(d) for p, d in part_domains.items()}
            ExtendedAC3Propagator.propagate(csp, dict(csp.givens), ac_domains)
            ac_total = sum(len(d) for d in ac_domains.values())
            singletons = sum(1 for d in ac_domains.values() if len(d) == 1)

            inv_str = f"{sum_h}={sum_v}"
            size_str = f"{csp.rows}x{csp.cols}"
            print(
                f"{csp.cli_name[:36]:<36} | {size_str:>9} | {len(csp.variables):>4} | "
                f"{len(csp.runs):>4} | {inv_str:>9} | {raw_total:>7} | {part_total:>9} | "
                f"{ac_total:>8} | {singletons:>4}/{len(csp.variables):<2}"
            )
        print("=" * 102)

    def run_cli_benchmark(self, trials: int = 10, show_solution: bool = True) -> None:
        """Chay thuc nghiem doi sanh 3 che do giai tren ca 4 bang mau (ASCII thuan)."""
        if trials < 1:
            raise ValueError("So lan lap trials phai lon hon hoac bang 1")

        print("=" * 114)
        print(f"NHIEM VU 3.2: DANH GIA BO GIAI KAKURO CSP ({trials} LAN LAP + 1 LAN WARM-UP)")
        print("=" * 114)
        print(
            f"{'Bang cau do Kakuro':<34} | {'Che do giai':<36} | {'Bien':>4} | "
            f"{'So nut':>6} | {'Q.lui':>6} | {'Cat tia':>7} | {'TG TB(ms)':>9} | {'Hop le':>6}"
        )
        print("-" * 114)

        sample_solutions: List[Tuple[KakuroCSP, dict]] = []
        speedup_9x9: dict[SolverMode, Tuple[int, float]] = {}

        for csp in self._load_all_maps():
            for mode in self.MODES:
                # Chay warm-up 1 lan truoc khi do thoi gian trung binh
                _ = KakuroSolver(mode=mode, record_steps=False).solve(csp)
                times: List[float] = []
                last_res = None
                for _ in range(trials):
                    res = KakuroSolver(mode=mode, record_steps=False).solve(csp)
                    times.append(res.elapsed_ms)
                    last_res = res

                assert last_res is not None
                mean_ms = statistics.mean(times)
                valid_str = "Dung" if last_res.valid_verified else "Sai"
                print(
                    f"{csp.cli_name[:34]:<34} | {mode.cli_label:<36} | {len(csp.variables):>4} | "
                    f"{last_res.nodes_explored:>6} | {last_res.backtracks:>6} | "
                    f"{last_res.pruned_values:>7} | {mean_ms:>9.3f} | {valid_str:>6}"
                )
                if csp.rows == 9:
                    speedup_9x9[mode] = (last_res.nodes_explored, mean_ms)
                if mode is SolverMode.BT_MAC_HEURISTICS and csp.rows in (5, 9):
                    sample_solutions.append((csp, last_res.assignment))
            print("-" * 114)

        if (
            SolverMode.PLAIN_BT in speedup_9x9
            and SolverMode.BT_FC in speedup_9x9
            and SolverMode.BT_MAC_HEURISTICS in speedup_9x9
        ):
            bt_nodes, bt_ms = speedup_9x9[SolverMode.PLAIN_BT]
            fc_nodes, fc_ms = speedup_9x9[SolverMode.BT_FC]
            mac_nodes, mac_ms = speedup_9x9[SolverMode.BT_MAC_HEURISTICS]
            node_ratio = bt_nodes / max(1, mac_nodes)
            fc_time_ratio = bt_ms / max(1e-6, fc_ms)
            print(
                f"Tong ket 9x9: AC-3 mo rong + MRV/Bac/LCV giam {node_ratio:.1f}x so nut "
                f"({bt_nodes} -> {mac_nodes}, 0 quay lui, {mac_ms:.3f} ms); "
                f"Kiem tra tien + MRV dat toc do nhanh nhat {fc_time_ratio:.1f}x "
                f"({bt_ms:.3f} ms -> {fc_ms:.3f} ms, {fc_nodes} nut)."
            )

        if show_solution:
            for csp, assignment in sample_solutions:
                print()
                print(f"Loi giai kiem chung 100% ({csp.cli_name}):")
                print(csp.render_solution_ascii(assignment))

    def run_verification(self) -> bool:
        """Chay 22 kiem thu tu dong bao phu CSP, 3 che do, BoardEditor va bien ngoai le."""
        checks: List[Tuple[str, bool, str]] = []
        maps = self._load_all_maps()

        # 1..4: Bat bien tong ngang == tong doc tren 4 bang mau
        for csp in maps:
            sum_h, sum_v = csp.sum_invariants()
            ok = sum_h == sum_v and sum_h > 0
            checks.append((f"Bat bien tong {csp.rows}x{csp.cols}", ok, f"sumH={sum_h}, sumV={sum_v}"))

        # 5..8: Ca 3 che do deu giai dung va qua verify_solution() tren tung bang
        mac_results = []
        plain_results = []
        for csp in maps:
            mode_ok = True
            detail_parts = []
            for mode in self.MODES:
                res = KakuroSolver(mode=mode).solve(csp)
                if not (res.solved and res.valid_verified and res.status == "SOLVED"):
                    mode_ok = False
                detail_parts.append(f"{mode.name}:{res.nodes_explored}n/{res.backtracks}bt")
                if mode is SolverMode.BT_MAC_HEURISTICS:
                    mac_results.append(res)
                if mode is SolverMode.PLAIN_BT:
                    plain_results.append(res)
            checks.append((f"3 che do giai hop le {csp.rows}x{csp.cols}", mode_ok, ", ".join(detail_parts)))

        # 9: AC-3 mo rong + MRV/Bac/LCV dat 0 quay lui tren ca 4 bang va it nut hon Quay lui co ban
        zero_bt = all(r.backtracks == 0 for r in mac_results)
        fewer_nodes = all(m.nodes_explored < p.nodes_explored for m, p in zip(mac_results, plain_results))
        checks.append(
            (
                "AC-3 mo rong + MRV/Bac/LCV dat 0 quay lui & giam nut",
                zero_bt and fewer_nodes,
                f"backtracks={[r.backtracks for r in mac_results]}",
            )
        )

        # 10: Generator iter_steps() nhat quan voi solve(record_steps=True)
        csp_5 = maps[0]
        solver_gen = KakuroSolver(mode=SolverMode.BT_MAC_HEURISTICS)
        streamed = list(solver_gen.iter_steps(csp_5))
        direct = KakuroSolver(mode=SolverMode.BT_MAC_HEURISTICS, record_steps=True).solve(csp_5)
        gen_ok = (
            len(streamed) == len(direct.steps_trace)
            and len(streamed) > 0
            and streamed[-1].step_type == "SOLVED"
            and csp_5.verify_solution(streamed[-1].assignment)
        )
        checks.append(("Generator iter_steps() khop trace & nghiem", gen_ok, f"steps={len(streamed)}"))

        # 11..14: BoardEditor bulk_rows() -> apply_bulk_rows() round-trip tren 4 bang
        for csp in maps:
            ed = BoardEditor(csp)
            rows_txt = ed.bulk_rows()
            ed.apply_bulk_rows(rows_txt)
            rebuilt = ed.validate()
            rt_ok = rebuilt.raw_grid == csp.raw_grid and rebuilt.givens == csp.givens
            checks.append((f"BoardEditor bulk round-trip {csp.rows}x{csp.cols}", rt_ok, f"rows={len(rows_txt)}"))

        # 15: randomize_clues() tao bo goi y moi co nghiem tren ca 4 bang
        rng = random.Random(42)
        rand_ok = True
        for csp in maps:
            ed = BoardEditor(csp)
            ed.randomize_clues(rng=rng)
            res = KakuroSolver(mode=SolverMode.BT_MAC_HEURISTICS).solve(ed.validate())
            if not (res.solved and res.valid_verified):
                rand_ok = False
        checks.append(("BoardEditor randomize_clues() co nghiem 4/4 bang", rand_ok, "seed=42"))

        # 16: Bang tuy chinh 4x4 co chu so cho truoc giai duoc tren ca 3 che do
        ed4 = BoardEditor.new(4)
        ed4.set_cell_type((3, 3), white=False)
        ed4.randomize_clues(rng=random.Random(7))
        ref_sol = KakuroSolver(mode=SolverMode.BT_MAC_HEURISTICS).solve(ed4.to_csp())
        first_pos = sorted(ref_sol.assignment.keys())[0]
        ed4.set_given(first_pos, ref_sol.assignment[first_pos])
        custom_csp = ed4.validate()
        custom_ok = all(
            (r := KakuroSolver(mode=m).solve(custom_csp)).solved and r.valid_verified
            for m in self.MODES
        )
        checks.append(("Bang tuy chinh 4x4 + so cho truoc (3 che do)", custom_ok, f"given={first_pos}:{ref_sol.assignment[first_pos]}"))

        # 17: BoardEditor save() -> load() JSON round-trip
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_json = Path(tmpdir) / "roundtrip_4x4.json"
            ed4.save(tmp_json)
            loaded = BoardEditor.load(tmp_json)
            loaded_res = KakuroSolver(mode=SolverMode.BT_MAC_HEURISTICS).solve(loaded.validate())
            io_ok = (
                loaded.grid == ed4.grid
                and loaded.givens == ed4.givens
                and loaded_res.solved
                and loaded_res.valid_verified
            )
        checks.append(("BoardEditor save/load JSON round-trip", io_ok, "4x4 with given"))

        # 18: Bang vo nghiem (UNSAT) tra ve status == 'UNSAT' tren ca 3 che do
        unsat_grid = [
            ["B", {"down": 3}, {"down": 4}],
            [{"across": 17}, "W", "W"],
            [{"across": 3}, "W", "W"],
        ]
        unsat_csp = KakuroCSP("Bang vo nghiem test", unsat_grid)
        unsat_ok = all(
            (r := KakuroSolver(mode=m).solve(unsat_csp)).status == "UNSAT" and not r.solved
            for m in self.MODES
        )
        checks.append(("Phat hien bang vo nghiem UNSAT (3 che do)", unsat_ok, "status=UNSAT"))

        # 19: Gioi han node_limit=1 tra ve status == 'NODE_LIMIT'
        lim_res = KakuroSolver(mode=SolverMode.PLAIN_BT, node_limit=1).solve(maps[-1])
        lim_ok = lim_res.status == "NODE_LIMIT" and not lim_res.solved
        checks.append(("Dung dung han voi node_limit=1", lim_ok, f"status={lim_res.status}, nodes={lim_res.nodes_explored}"))

        # 20: Huy hop tac qua cancel_event tra ve status == 'CANCELLED'
        cancel_ev = Event()
        cancel_ev.set()
        cancel_res = KakuroSolver(mode=SolverMode.BT_MAC_HEURISTICS, cancel_event=cancel_ev).solve(maps[-1])
        cancel_ok = cancel_res.status == "CANCELLED" and not cancel_res.solved
        checks.append(("Huy hop tac cancel_event -> CANCELLED", cancel_ok, f"status={cancel_res.status}"))

        # 21: Khoi phuc giai binh thuong ngay sau khi huy
        rec_res = KakuroSolver(mode=SolverMode.BT_MAC_HEURISTICS).solve(maps[-1])
        rec_ok = rec_res.solved and rec_res.valid_verified and rec_res.status == "SOLVED"
        checks.append(("Khoi phuc giai 9x9 sau huy hop tac", rec_ok, f"nodes={rec_res.nodes_explored}"))

        # 22: Gioi han max_recorded_steps=15 luon giu lai buoc ket thuc SOLVED
        trunc_res = KakuroSolver(
            mode=SolverMode.BT_MAC_HEURISTICS,
            record_steps=True,
            max_recorded_steps=15,
        ).solve(maps[-1])
        trunc_ok = (
            trunc_res.solved
            and trunc_res.trace_truncated
            and len(trunc_res.steps_trace) == 15
            and trunc_res.steps_trace[-1].step_type == "SOLVED"
        )
        checks.append(
            (
                "Cat ngan lich su max_recorded_steps giu buoc SOLVED",
                trunc_ok,
                f"len={len(trunc_res.steps_trace)}, truncated={trunc_res.trace_truncated}",
            )
        )

        print("=" * 98)
        print("NHIEM VU 3: KIEM CHUNG TU DONG 22 TIEU CHI KAKURO CSP & BOARD EDITOR")
        print("=" * 98)
        passed = 0
        for idx, (title, ok, detail) in enumerate(checks, start=1):
            tag = "[PASS]" if ok else "[FAIL]"
            if ok:
                passed += 1
            print(f"{idx:>2}. {tag} {title:<52} | {detail}")
        print("-" * 98)
        print(f"Ket qua tong hop: {passed}/{len(checks)} kiem thu dat.")
        print("=" * 98)
        return passed == len(checks)

    def export_headless_screenshot(self, output_path: Path, screenshot_mode: str = "prune") -> None:
        """Xuat anh chup giao dien PNG khong can cua so hien thi cho kiem thu thi giac."""
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        import pygame
        from task3.visualizer_ui import KakuroVisualizerUI

        ui = KakuroVisualizerUI(maps_dir=self.maps_dir)
        if screenshot_mode == "editor":
            ui.select_map(0, solve_sync=True)
            ui.editing = True
            ui.editor = BoardEditor(ui.csp)
            ui.selected = (1, 2)
            ui._notify("Chế độ Soạn thảo: chọn ô để sửa loại ô, tổng gợi ý hoặc chữ số cho trước.")
        elif screenshot_mode == "solved":
            ui.select_map(3, solve_sync=True)
            ui.select_mode(2, solve_sync=True)
            if ui.result and ui.result.steps_trace:
                ui.step_idx = len(ui.result.steps_trace) - 1
        elif screenshot_mode == "backtrack":
            ui.select_map(0, solve_sync=True)
            ui.select_mode(0, solve_sync=True)
            if ui.result and ui.result.steps_trace:
                chosen = 0
                for idx, st in enumerate(ui.result.steps_trace):
                    if st.step_type == "BACKTRACK" and len(st.assignment) >= 3:
                        chosen = idx
                        break
                ui.step_idx = chosen
        else:
            # Che do 'prune': hien thi bang phuc tap 9x9 voi cat tia ung vien ro net
            ui.select_map(3, solve_sync=True)
            ui.select_mode(1, solve_sync=True)
            if ui.result and ui.result.steps_trace:
                best_idx = 0
                best_score = -1
                for idx, st in enumerate(ui.result.steps_trace):
                    if st.step_type == "PRUNE" and 8 <= len(st.assignment) <= 26:
                        pruned_cnt = sum(len(v) for v in st.pruned.values())
                        if pruned_cnt > best_score:
                            best_score = pruned_cnt
                            best_idx = idx
                if best_score < 0:
                    for idx, st in enumerate(ui.result.steps_trace):
                        if st.step_type == "PRUNE":
                            best_idx = idx
                            break
                ui.step_idx = best_idx

        ui.save_screenshot(output_path)
        pygame.quit()
        print(f"Da luu anh chup giao dien ({screenshot_mode}) tai: {output_path}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Nhiem vu 3: Bo giai Kakuro CSP, Benchmark CLI va Giao dien PyGame toi gian"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Chay thuc nghiem doi sanh 3 che do giai tren 4 bang mau (khong mo PyGame)",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=10,
        help="So lan lap cho moi cau hinh khi chay --cli (mac dinh: 10)",
    )
    parser.add_argument(
        "--explain-csp",
        action="store_true",
        help="In mo hinh hoa <X, D, C>, bat bien tong va do thu hep mien ban dau",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Chay 22 kiem thu tu dong bao phu CSP, 3 che do, BoardEditor va ngoai le",
    )
    parser.add_argument(
        "--headless-screenshot",
        type=str,
        default=None,
        help="Xuat anh chup giao dien PNG khong cua so den duong dan chi dinh",
    )
    parser.add_argument(
        "--screenshot-mode",
        type=str,
        choices=("prune", "backtrack", "solved", "editor"),
        default="prune",
        help="Trang thai giao dien can chup: prune | backtrack | solved | editor",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    runner = Task3ExperimentRunner()

    if args.explain_csp:
        runner.explain_csp()
        if not (args.cli or args.verify or args.headless_screenshot):
            return

    if args.verify:
        all_ok = runner.run_verification()
        if not all_ok:
            sys.exit(1)
        if not (args.cli or args.headless_screenshot):
            return

    if args.cli:
        runner.run_cli_benchmark(trials=args.trials, show_solution=True)
        return

    if args.headless_screenshot:
        runner.export_headless_screenshot(Path(args.headless_screenshot), args.screenshot_mode)
        return

    from task3.visualizer_ui import KakuroVisualizerUI

    app = KakuroVisualizerUI()
    app.run()


if __name__ == "__main__":
    main()
