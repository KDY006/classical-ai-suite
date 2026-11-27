"""Diem khoi chay chinh cho Nhiem vu 2: Dau Tang doi khang (PyGame UI & CLI)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from statistics import median

PROJECT_SOURCE = Path(__file__).resolve().parents[1]
if str(PROJECT_SOURCE) not in sys.path:
    sys.path.insert(0, str(PROJECT_SOURCE))

from task2.agents import (
    AlphaBetaAgent,
    BaseTankAgent,
    HeuristicAlphaBetaAgent,
    HeuristicMinimaxAgent,
    MinimaxAgent,
    TacticalEvaluator,
    discover_external_agents,
)
from task2.config import (
    ACTION_LABELS_CLI,
    ALL_ACTIONS,
    BASE_INITIAL_HP,
    BULLET_SPEED_PER_CYCLE,
    DAMAGE_PER_HIT,
    DIR_RIGHT,
    FIRE,
    PLAYER_MAX,
    PLAYER_MIN,
    STAY,
    TANK_INITIAL_HP,
    WALL_INITIAL_HP,
)
from task2.engine import (
    Base,
    BrickWall,
    Bullet,
    GameState,
    Tank,
    TankBattleEngine,
    get_all_scenarios,
    get_scenario,
)


class Task2ExperimentRunner:
    """Lop OOP dieu phoi mo hinh hoa, thuc nghiem 2 tang va kiem chung cho Task 2."""

    def run_model_summary(self) -> None:
        """In tom tat mo hinh 6 thanh phan Zero-Sum Game va minh hoa dan bay tung o."""
        print("=" * 94)
        print("NHIEM VU 2.1: MO HINH TRO CHOI TONG BANG KHONG (ZERO-SUM GAME) - DAU TANG")
        print("=" * 94)
        print(
            f"- Thong so de bai: Tank HP={TANK_INITIAL_HP}, Base HP={BASE_INITIAL_HP}, "
            f"Wall HP={WALL_INITIAL_HP}, Sat thuong={DAMAGE_PER_HIT}, "
            f"Toc do dan={BULLET_SPEED_PER_CYCLE} o/chu ky (kiem tra va cham tung o mot)"
        )
        print(f"- Tap 6 hanh dong: {', '.join(ALL_ACTIONS)}")
        print("- Ham tien ich: +1000 (MAX thang), -1000 (MIN thang), 0 (Hoa / Het luot)")

        # Minh hoa nhanh vat ly dan bay 3 o dung ngay tai o tuong gach thu 2
        demo_state = GameState(
            rows=5,
            cols=7,
            tanks={
                PLAYER_MAX: Tank(PLAYER_MAX, 2, 1, facing=DIR_RIGHT, hp=6),
                PLAYER_MIN: Tank(PLAYER_MIN, 2, 5, facing="LEFT", hp=6),
            },
            bases={
                PLAYER_MAX: Base(PLAYER_MAX, 4, 0, hp=9),
                PLAYER_MIN: Base(PLAYER_MIN, 0, 6, hp=9),
            },
            brick_walls={(2, 3): BrickWall(2, 3, hp=3)},
            current_player=PLAYER_MAX,
        )
        nxt, ev = TankBattleEngine.step_with_events(demo_state, FIRE)
        print(
            f"- Minh hoa vat ly: MAX o (2,1) ban ve PHAI qua tuong gach (2,3) HP=3 -> "
            f"va cham {ev.impacts}, tuong con HP={nxt.brick_walls[(2, 3)].hp}, "
            f"dan con lai={len(nxt.bullets)} (dung ngay khi trung vat can)"
        )

    def run_tier1_benchmark(self, repeats: int = 3) -> None:
        """Doi sanh cong bang ca 4 cau hinh thuat toan tren 3 kich ban Tan cuoc 7x7."""
        print("\n" + "=" * 102)
        print(f"NHIEM VU 2.2 (TANG 1): DOI SANH 4 CAU HINH TREN TAN CUOC 7x7 (TRUNG VI {repeats} LAN)")
        print("=" * 102)
        print(
            f"{'Kich ban ban do':<30} | {'Cau hinh thuat toan':<26} | {'Nuoc di':<7} | "
            f"{'So nut':>8} | {'Cat tia':>7} | {'TT':>4} | {'TG (ms)':>8}"
        )
        print("-" * 102)

        for scen in get_all_scenarios(tier="tier1"):
            s0 = scen.builder()
            agents: list[BaseTankAgent] = [
                MinimaxAgent(max_ply_cap=6, name="Minimax thuần", cli_name="Minimax thuan"),
                AlphaBetaAgent(max_ply_cap=6, name="Alpha-Beta thuần", cli_name="Alpha-Beta thuan"),
                HeuristicMinimaxAgent(max_depth=4, name="Heuristic Minimax (d=4)", cli_name="Heuristic Minimax (d=4)"),
                HeuristicAlphaBetaAgent(max_depth=4, name="Heuristic Alpha-Beta (d=4)", cli_name="Heuristic Alpha-Beta (d=4)"),
            ]
            for ag in agents:
                times: list[float] = []
                act = STAY
                for _ in range(repeats):
                    act = ag.safe_choose_action(s0)
                    times.append(ag.last_metrics.elapsed_ms)
                m = ag.last_metrics
                act_cli = ACTION_LABELS_CLI.get(act, act)
                print(
                    f"{scen.cli_title:<30} | {ag.cli_name:<26} | {act_cli:<7} | "
                    f"{m.explored_states:>8,} | {m.pruned_branches:>7,} | {m.tt_hits:>4} | {median(times):>8.2f}"
                )
            print("-" * 102)

    def run_tier2_benchmark(self, repeats: int = 3) -> None:
        """Doi sanh Heuristic Minimax va Heuristic Alpha-Beta tren ban do day mau 9x9 & 11x11."""
        print("\n" + "=" * 100)
        print(f"NHIEM VU 2.2 (TANG 2): DAU TRUONG DAY MAU 9x9 & 11x11 (DO SAU d = 2, 3, 4)")
        print("=" * 100)
        print(
            f"{'Ban do':<28} | {'d':>2} | {'Thuat toan':<24} | {'Nuoc di':<7} | "
            f"{'So nut':>8} | {'Cat tia':>7} | {'TT':>4} | {'TG (ms)':>8}"
        )
        print("-" * 100)

        for key in ("classic_9x9", "fortress_11x11"):
            scen = get_scenario(key)
            s0 = scen.builder()
            for depth in (2, 3, 4):
                for ag in (
                    HeuristicMinimaxAgent(max_depth=depth, cli_name="Heuristic Minimax"),
                    HeuristicAlphaBetaAgent(max_depth=depth, cli_name="Heuristic Alpha-Beta"),
                ):
                    times: list[float] = []
                    act = STAY
                    for _ in range(repeats):
                        act = ag.safe_choose_action(s0)
                        times.append(ag.last_metrics.elapsed_ms)
                    m = ag.last_metrics
                    print(
                        f"{scen.cli_title:<28} | {depth:>2} | {ag.cli_name:<24} | "
                        f"{ACTION_LABELS_CLI.get(act, act):<7} | {m.explored_states:>8,} | "
                        f"{m.pruned_branches:>7,} | {m.tt_hits:>4} | {median(times):>8.2f}"
                    )
            print("-" * 100)

    def run_match_showcase(self) -> None:
        """Chay tran dau kiem thu tich hop bot nhom ngoai va giao tranh truc tiep."""
        ext = discover_external_agents()
        print(f"\nDa phat hien {len(ext)} bot nhom ngoai: {[b.cli_name for b in ext]}")
        print("=" * 100)
        print("NHIEM VU 2.3: TRAN DAU DOI KHANG DAY MAU (GIAO LO HOA LUC 9x9)")
        print("=" * 100)
        print(
            f"{'Phe MAX':<28} | {'Phe MIN':<30} | {'Luot':>4} | "
            f"{'Mau cuoi (M vs N)':<18} | {'Ket qua'}"
        )
        print("-" * 100)

        s0 = get_scenario("crossfire_9x9").builder()
        matchups: list[tuple[BaseTankAgent, BaseTankAgent]] = [
            (
                HeuristicAlphaBetaAgent(max_depth=4, cli_name="Heuristic Alpha-Beta (d=4)"),
                HeuristicMinimaxAgent(max_depth=2, cli_name="Heuristic Minimax (d=2)"),
            )
        ]
        for bot in ext:
            matchups.append(
                (
                    HeuristicAlphaBetaAgent(max_depth=4, cli_name="Heuristic Alpha-Beta (d=4)"),
                    bot,
                )
            )

        for p1, p2 in matchups:
            final_state = s0
            for snap in TankBattleEngine.iter_match(s0, p1, p2):
                final_state = snap.state
            w = final_state.winner()
            kq = "MAX thang" if w == PLAYER_MAX else ("MIN thang" if w == PLAYER_MIN else "Hoa (Het luot)")
            hp_str = (
                f"{final_state.tanks[1].hp}/{final_state.bases[1].hp} vs "
                f"{final_state.tanks[2].hp}/{final_state.bases[2].hp}"
            )
            print(f"{p1.cli_name:<28} | {p2.cli_name:<30} | {final_state.ply:>4} | {hp_str:<18} | {kq}")

    def run_verification_suite(self) -> bool:
        """Bo kiem chung tu dong 6 nhom bat bien cho Task 2."""
        print("=" * 82)
        print("KIEM CHUNG TU DONG NHIEM VU 2 (VAT LY, BAT BIEN, 4 THUAT TOAN, BOT NGOAI)")
        print("=" * 82)

        # 1. Kiem chung thong so HP 6/9/3, sat thuong 1 va dan bay 3 o dung tai vat can dau tien
        s_phys = GameState(
            rows=5,
            cols=7,
            tanks={
                PLAYER_MAX: Tank(PLAYER_MAX, 2, 1, facing=DIR_RIGHT),
                PLAYER_MIN: Tank(PLAYER_MIN, 2, 4, facing="LEFT"),
            },
            bases={
                PLAYER_MAX: Base(PLAYER_MAX, 4, 0),
                PLAYER_MIN: Base(PLAYER_MIN, 0, 6),
            },
            brick_walls={(2, 3): BrickWall(2, 3)},
            current_player=PLAYER_MAX,
        )
        assert s_phys.tanks[PLAYER_MAX].hp == 6
        assert s_phys.bases[PLAYER_MAX].hp == 9
        assert s_phys.brick_walls[(2, 3)].hp == 3
        s_after, ev = TankBattleEngine.step_with_events(s_phys, FIRE)
        assert s_after.brick_walls[(2, 3)].hp == 2, "Tuong gach phai mat dung 1 HP"
        assert s_after.tanks[PLAYER_MIN].hp == 6, "Dan phai dung ngay khi trung tuong, khong xuyen qua xe"
        assert len(s_after.bullets) == 0 and ev.impacts == [(2, 3, "WALL")]

        # Kiem tra dan triet tieu giua 2 vien dan doi dau
        s_clash = GameState(
            rows=5,
            cols=7,
            tanks={
                PLAYER_MAX: Tank(PLAYER_MAX, 2, 0, facing=DIR_RIGHT),
                PLAYER_MIN: Tank(PLAYER_MIN, 2, 6, facing="LEFT"),
            },
            bases={
                PLAYER_MAX: Base(PLAYER_MAX, 4, 0),
                PLAYER_MIN: Base(PLAYER_MIN, 0, 6),
            },
            brick_walls={},
            bullets=[Bullet(PLAYER_MIN, 2, 2, "LEFT")],
            current_player=PLAYER_MAX,
        )
        s_clash_next, ev_clash = TankBattleEngine.step_with_events(s_clash, FIRE)
        assert len(s_clash_next.bullets) == 0 and any(i[2] == "BULLET" for i in ev_clash.impacts)
        print("[DAT] 1. Thong so HP (6/9/3), sat thuong 1 va vat ly dan 3 o tung buoc chinh xac.")

        # 2. Kiem chung bat bien GameState va cach ly bot loi
        mutated = False
        try:
            s_phys.tanks[PLAYER_MAX] = Tank(PLAYER_MAX, 0, 0)  # type: ignore[index]
            mutated = True
        except TypeError:
            pass
        assert not mutated, "GameState.tanks phai bat bien (MappingProxyType)"

        class _BrokenBot(BaseTankAgent):
            def __init__(self) -> None:
                super().__init__("Bot loi")

            def choose_action(self, state: GameState) -> str:
                raise RuntimeError("Loi gia lap")

        assert _BrokenBot().safe_choose_action(s_phys) == STAY
        print("[DAT] 2. GameState bat bien va safe_choose_action cach ly an toan bot nhom ngoai.")

        # 3. Kiem chung tuong duong tuyet doi giua Minimax thuan va Alpha-Beta thuan (Tang 1)
        for scen in get_all_scenarios(tier="tier1"):
            s0 = scen.builder()
            mm = MinimaxAgent(max_ply_cap=6)
            ab = AlphaBetaAgent(max_ply_cap=6)
            act_mm = mm.safe_choose_action(s0)
            act_ab = ab.safe_choose_action(s0)
            assert abs(mm.last_metrics.best_value - ab.last_metrics.best_value) < 1e-6, (
                f"Gia tri Minimax != Alpha-Beta tai {scen.key}"
            )
            assert act_mm == act_ab, f"Nuoc di Minimax != Alpha-Beta tai {scen.key}"
            assert ab.last_metrics.explored_states < mm.last_metrics.explored_states
        print("[DAT] 3. Alpha-Beta thuan giu nguyen gia tri/nuoc di toi uu cua Minimax va cat tia manh.")

        # 4. Kiem chung tinh phan doi xung EVAL(s) va tuong duong Heuristic Minimax vs Heuristic Alpha-Beta
        for key in ("classic_9x9", "crossfire_9x9", "fortress_11x11"):
            s0 = get_scenario(key).builder()
            e_max = TacticalEvaluator.evaluate(s0, PLAYER_MAX)
            e_min = TacticalEvaluator.evaluate(s0, PLAYER_MIN)
            assert abs(e_max + e_min) < 1e-6, f"EVAL(s) khong phan doi xung tai {key}"

            hm = HeuristicMinimaxAgent(max_depth=3)
            hab = HeuristicAlphaBetaAgent(max_depth=3)
            hm.safe_choose_action(s0)
            hab.safe_choose_action(s0)
            assert abs(hm.last_metrics.best_value - hab.last_metrics.best_value) < 1e-6, (
                f"Heuristic Alpha-Beta lech gia tri so voi Heuristic Minimax tai {key}: "
                f"{hab.last_metrics.best_value} vs {hm.last_metrics.best_value}"
            )
            assert hab.last_metrics.explored_states < hm.last_metrics.explored_states
        print("[DAT] 4. EVAL(s) phan doi xung va Heuristic Alpha-Beta khop tuyet doi Heuristic Minimax.")

        # 5. Kiem chung nap dong bot nhom ngoai va khong ban mu vao tuong thep
        ext = discover_external_agents()
        assert len(ext) >= 2, f"Can it nhat 2 bot mau nhom ngoai, tim thay {len(ext)}"
        s_cf = get_scenario("crossfire_9x9").builder()
        for bot in ext:
            act = bot.safe_choose_action(s_cf)
            assert act in ALL_ACTIONS
            assert act != FIRE, f"Bot {bot.cli_name} khong duoc ban mu vao tuong thep phia truoc"
        print("[DAT] 5. Nap dong 2 bot ngoai (OOP + Dict) thanh cong, khong ban mu vao tuong thep.")

        # 6. Kiem chung tran dau day mau co giao tranh gay sat thuong thuc su (khong hoa thu dong 6/9 vs 6/9)
        p1 = HeuristicAlphaBetaAgent(max_depth=4)
        p2 = ext[0]
        final_s = s_cf
        for snap in TankBattleEngine.iter_match(s_cf, p1, p2):
            final_s = snap.state
        total_hp_lost = (
            (TANK_INITIAL_HP - final_s.tanks[1].hp)
            + (TANK_INITIAL_HP - final_s.tanks[2].hp)
            + (BASE_INITIAL_HP - final_s.bases[1].hp)
            + (BASE_INITIAL_HP - final_s.bases[2].hp)
        )
        assert total_hp_lost > 0, "Tran dau mau phai co giao tranh gay sat thuong thuc te"
        print(
            f"[DAT] 6. Tran dau day mau giao tranh tich cuc (tong HP mat={total_hp_lost}, "
            f"ket thuc luot {final_s.ply}, winner={final_s.winner()})."
        )
        print("KET LUAN: TAT CA 6 NHOM KIEM CHUNG DEU DAT.")
        return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Nhiem vu 2: Tro choi Dau Tang Tim kiem Doi khang (PyGame UI & CLI)"
    )
    parser.add_argument("--cli", action="store_true", help="Chay tron bo thuc nghiem tren terminal")
    parser.add_argument("--explain-model", action="store_true", help="In tom tat mo hinh Zero-Sum Game")
    parser.add_argument("--repeats", type=int, default=3, help="So lan lap do trung vi thoi gian")
    parser.add_argument("--verify", action="store_true", help="Chay bo kiem chung tu dong 6 nhom")
    parser.add_argument(
        "--headless-screenshot",
        type=str,
        default=None,
        help="Xuat anh chup giao dien PyGame ra file PNG o che do khong cua so",
    )
    parser.add_argument(
        "--map",
        type=str,
        default="classic_9x9",
        help="Ma ban do khoi dau cho giao dien hoac chup anh (classic_9x9, crossfire_9x9, ...)",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=6,
        help="So luot chay truoc khi chup anh headless",
    )
    args = parser.parse_args()

    runner = Task2ExperimentRunner()

    if args.verify:
        runner.run_verification_suite()
        return

    if args.headless_screenshot:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        import pygame
        from task2.ui import TankBattleArenaUI

        ui = TankBattleArenaUI(initial_scenario_key=args.map)
        for _ in range(max(0, args.turns)):
            ui.execute_turn()
        ui.save_screenshot(Path(args.headless_screenshot))
        pygame.quit()
        print(f"Da luu anh chup giao dien Dau Tang tai: {args.headless_screenshot}")
        return

    if args.explain_model and not args.cli:
        runner.run_model_summary()
        return

    if args.cli:
        runner.run_model_summary()
        runner.run_tier1_benchmark(repeats=max(1, args.repeats))
        runner.run_tier2_benchmark(repeats=max(1, args.repeats))
        runner.run_match_showcase()
        return

    from task2.ui import TankBattleArenaUI

    TankBattleArenaUI(initial_scenario_key=args.map).run()


if __name__ == "__main__":
    main()
