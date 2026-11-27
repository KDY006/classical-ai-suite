"""Giao dien PyGame toi gian cho Nhien vu 1 (N Quan Hau) tuan thu UI.md."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random
from typing import Iterator

import pygame

from .board import NQueenBoard
from .min_conflicts import (
    AdaptiveTabuMaxConflictSelector,
    MinConflictsSolver,
    PureMaxConflictSelector,
    RandomConflictedSelector,
    StepSnapshot,
    VariableSelectionStrategy,
)
from .sat_solver import Glucose3NQueenSolver, SATSolveResult


# Bang mau gioi han 3 tong chu dao theo quy uoc UI.md
BG_CANVAS = (250, 250, 250)
SURFACE = (255, 255, 255)
SURFACE_SUBTLE = (243, 244, 246)
SURFACE_ACTIVE = (229, 231, 235)
BORDER = (229, 231, 235)
BORDER_STRONG = (156, 163, 175)
TEXT_PRIMARY = (17, 24, 39)
TEXT_SECONDARY = (107, 114, 128)

ACCENT_PRIMARY = (15, 118, 110)
ACCENT_PRIMARY_HOVER = (17, 94, 89)
ACCENT_PRIMARY_SOFT = (230, 244, 241)

ACCENT_ALERT = (200, 62, 55)
ACCENT_ALERT_SOFT = (252, 235, 234)

WINDOW_W = 1160
WINDOW_H = 720
HEADER_H = 56
SIDEBAR_X = 760
SIDEBAR_W = WINDOW_W - SIDEBAR_X
PRESET_SIZES = (4, 8, 12, 16, 20, 32, 50)

SANS_FONTS = ("SF Pro Display", "Helvetica Neue", "Segoe UI", "Arial", "DejaVu Sans")
MONO_FONTS = ("SF Mono", "Menlo", "Consolas", "Courier New", "DejaVu Sans Mono")


@dataclass
class ButtonSpec:
    """Mo ta hinh hoc va trang thai hien thi cua mot nut bam toi gian."""

    key: str
    label: str
    rect: pygame.Rect
    primary: bool = False
    active: bool = False


class MinimalNQueenUI:
    """Giao dien PyGame phong cach toi gian (Minimalism) cho bai toan N-Queen."""

    ALGO_OPTIONS: tuple[tuple[str, str], ...] = (
        ("sat", "Glucose3 (SAT - CNF)"),
        ("mc_std", "Min-Conflicts tiêu chuẩn"),
        ("mc_pure", "Max-Conflict thuần (Đối chứng)"),
        ("mc_tabu", "Max-Conflict + Tabu thích nghi (Đề xuất)"),
    )

    def __init__(self, initial_n: int = 8) -> None:
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("Bài Toán N Quân Hậu | Nhiệm Vụ 1")
        self.clock = pygame.time.Clock()

        # Khoi tao bo font da nen tang ho tro tieng Viet co dau
        self.font_h1 = self._load_font(SANS_FONTS, 20, bold=True)
        self.font_h2 = self._load_font(SANS_FONTS, 12, bold=True)
        self.font_body = self._load_font(SANS_FONTS, 13, bold=False)
        self.font_body_bold = self._load_font(SANS_FONTS, 13, bold=True)
        self.font_caption = self._load_font(SANS_FONTS, 12, bold=False)
        self.font_mono = self._load_font(MONO_FONTS, 13, bold=False)
        self.font_mono_bold = self._load_font(MONO_FONTS, 13, bold=True)
        self.font_coord = self._load_font(MONO_FONTS, 11, bold=False)

        # Trang thai bai toan va bo dieu khien mo phong
        self.n: int = max(4, min(100, initial_n))
        self.algo_key: str = "mc_tabu"
        self.seed_counter: int = 1
        self.initial_board: NQueenBoard = NQueenBoard.from_random(self.n, random.Random(2026))
        self.board: NQueenBoard = self.initial_board.clone()

        self.step_iter: Iterator[StepSnapshot] | None = None
        self.auto_play: bool = False
        self.speed_sps: int = 12
        self._step_accum_ms: float = 0.0
        self._dragging_slider: bool = False

        self.steps_count: int = 0
        self.selected_col: int | None = None
        self.last_elapsed_ms: float | None = None
        self.sat_result: SATSolveResult | None = None
        self.compare_summary: tuple[str, str] | None = None
        self.status_text: str = "Sẵn sàng"
        self.status_tone: str = "neutral"
        self.footer_note: str = "Nhấn Giải ngay, Từng bước hoặc Phát để quan sát thuật toán."

        self.slider_rect = pygame.Rect(SIDEBAR_X + 24, 464, SIDEBAR_W - 48, 16)
        self.buttons: list[ButtonSpec] = []
        self._rebuild_buttons()
        self._sync_status_from_board()

    @staticmethod
    def _load_font(candidates: tuple[str, ...], size: int, bold: bool = False) -> pygame.font.Font:
        """Tim font he thong co san ho tro day du tieng Viet co dau."""
        for family in candidates:
            path = pygame.font.match_font(family, bold=bold)
            if path:
                return pygame.font.Font(path, size)
        return pygame.font.SysFont(",".join(candidates), size, bold=bold)

    def _rebuild_buttons(self) -> None:
        """Xay dung danh sach nut tuong tac trong sidebar theo bo cuc UI.md."""
        x0 = SIDEBAR_X + 24
        w = SIDEBAR_W - 48
        buttons: list[ButtonSpec] = []

        # Nut tang giam kich thuoc N
        buttons.append(ButtonSpec("n_dec", "-", pygame.Rect(x0 + w - 110, 92, 30, 28)))
        buttons.append(ButtonSpec("n_inc", "+", pygame.Rect(x0 + w - 30, 92, 30, 28)))

        # Hang chon nhanh cac kich thuoc N pho bien
        gap = 6
        pill_w = (w - gap * (len(PRESET_SIZES) - 1)) // len(PRESET_SIZES)
        for idx, size in enumerate(PRESET_SIZES):
            rx = x0 + idx * (pill_w + gap)
            buttons.append(
                ButtonSpec(
                    key=f"size_{size}",
                    label=str(size),
                    rect=pygame.Rect(rx, 128, pill_w, 28),
                    active=(self.n == size),
                )
            )

        # Bon nut chon thuat toan
        for idx, (key, label) in enumerate(self.ALGO_OPTIONS):
            ry = 186 + idx * 32
            buttons.append(
                ButtonSpec(
                    key=f"algo_{key}",
                    label=label,
                    rect=pygame.Rect(x0, ry, w, 28),
                    active=(self.algo_key == key),
                )
            )

        # Hang nut hanh dong chinh
        half_w = (w - 8) // 2
        buttons.append(ButtonSpec("solve", "Giải ngay", pygame.Rect(x0, 356, half_w, 36), primary=True))
        buttons.append(ButtonSpec("random", "Ngẫu nhiên", pygame.Rect(x0 + half_w + 8, 356, w - half_w - 8, 36)))

        # Hang dieu khien mo phong va so sanh
        tri_w = (w - 16) // 3
        play_label = "Tạm dừng" if self.auto_play else "Phát"
        buttons.append(ButtonSpec("step", "Từng bước", pygame.Rect(x0, 400, tri_w, 32)))
        buttons.append(ButtonSpec("play", play_label, pygame.Rect(x0 + tri_w + 8, 400, tri_w, 32), active=self.auto_play))
        buttons.append(ButtonSpec("compare", "So sánh", pygame.Rect(x0 + 2 * (tri_w + 8), 400, w - 2 * (tri_w + 8), 32)))

        self.buttons = buttons

    def _make_strategy(self, key: str) -> VariableSelectionStrategy:
        """Tao doi tuong chien luoc chon bien tuong ung voi ma lua chon."""
        if key == "mc_std":
            return RandomConflictedSelector()
        if key == "mc_pure":
            return PureMaxConflictSelector()
        return AdaptiveTabuMaxConflictSelector()

    def _sync_status_from_board(self) -> None:
        """Cap nhat nhan trang thai o thanh tieu de dua tren so xung dot hien tai."""
        conflicts = self.board.total_conflicts()
        if conflicts == 0 and self.board.is_valid_solution():
            self.status_text = "Đã tìm thấy nghiệm"
            self.status_tone = "success"
        elif self.auto_play:
            self.status_text = f"Đang chạy ({conflicts} xung đột)"
            self.status_tone = "neutral"
        else:
            self.status_text = f"Còn {conflicts} cặp xung đột"
            self.status_tone = "alert"

    def set_board_size(self, new_n: int) -> None:
        """Thay doi kich thuoc ban co N trong khoang [4, 100] va khoi tao lai."""
        clamped = max(4, min(100, new_n))
        if clamped == self.n:
            return
        self.n = clamped
        self.randomize_board()

    def set_algorithm(self, algo_key: str) -> None:
        """Chuyen doi thuat toan hien tai va dat lai trinh phat tung buoc."""
        if algo_key == self.algo_key:
            return
        self.algo_key = algo_key
        self.auto_play = False
        self.step_iter = None
        self.selected_col = None
        self.sat_result = None
        self.steps_count = 0
        self.last_elapsed_ms = None
        self.board = self.initial_board.clone()
        self._sync_status_from_board()
        self._rebuild_buttons()

    def randomize_board(self) -> None:
        """Tao ban co khoi tao ngau nhien moi cho ca so sanh lan chay tung buoc."""
        self.auto_play = False
        self.step_iter = None
        self.seed_counter += 1
        self.initial_board = NQueenBoard.from_random(self.n, random.Random(2026 + self.n * 97 + self.seed_counter))
        self.board = self.initial_board.clone()
        self.steps_count = 0
        self.selected_col = None
        self.last_elapsed_ms = None
        self.sat_result = None
        self.compare_summary = None
        self.footer_note = f"Đã tạo bàn cờ ngẫu nhiên {self.n} × {self.n} với {self.board.total_conflicts()} cặp xung đột."
        self._sync_status_from_board()
        self._rebuild_buttons()

    def solve_immediately(self) -> None:
        """Chay ngay thuat toan dang chon den khi co ket qua cuoi cung."""
        self.auto_play = False
        self.step_iter = None
        self.selected_col = None

        if self.algo_key == "sat":
            res = Glucose3NQueenSolver().solve(self.n, repeats=1)
            self.sat_result = res
            self.last_elapsed_ms = res.solve_time_sec * 1000.0
            self.steps_count = 0
            if res.board is not None:
                self.board = res.board
                self.footer_note = (
                    f"Glucose3 giải xong {self.n} × {self.n} với {res.num_clauses:,} mệnh đề CNF "
                    f"trong {self.last_elapsed_ms:.2f} ms."
                )
            else:
                self.footer_note = f"Glucose3 xác định N = {self.n} không có nghiệm."
            self._sync_status_from_board()
            self._rebuild_buttons()
            return

        self.sat_result = None
        strategy = self._make_strategy(self.algo_key)
        solver = MinConflictsSolver(strategy=strategy, max_steps=5000)
        res = solver.solve(self.n, initial_board=self.initial_board, seed=9000 + self.seed_counter)
        self.board = res.board
        self.steps_count = res.steps
        self.last_elapsed_ms = res.elapsed_sec * 1000.0
        if res.solved:
            self.footer_note = (
                f"{strategy.name} tìm ra nghiệm sau {res.steps:,} bước ({self.last_elapsed_ms:.2f} ms)."
            )
        else:
            self.footer_note = (
                f"{strategy.name} dừng ở {res.steps:,} bước, còn {res.remaining_conflicts} cặp xung đột."
            )
        self._sync_status_from_board()
        self._rebuild_buttons()

    def step_once(self) -> None:
        """Thuc hien dung 1 buoc sua xung dot cua thuat toan Min-Conflicts."""
        if self.algo_key == "sat":
            self.solve_immediately()
            return

        if self.step_iter is None:
            self.sat_result = None
            strategy = self._make_strategy(self.algo_key)
            solver = MinConflictsSolver(strategy=strategy, max_steps=5000)
            self.step_iter = solver.iter_solve(
                self.n,
                initial_board=self.initial_board,
                seed=9000 + self.seed_counter,
            )
            # Bo qua anh chup khoi tao buoc 0 de tien ngay toi buoc 1
            first = next(self.step_iter, None)
            if first is not None:
                self.board = NQueenBoard(self.n, first.queens)
                self.steps_count = first.step

        snap = next(self.step_iter, None)
        if snap is None:
            self.auto_play = False
            self._sync_status_from_board()
            self._rebuild_buttons()
            return

        self.board = NQueenBoard(self.n, snap.queens)
        self.steps_count = snap.step
        self.selected_col = snap.selected_col
        self.last_elapsed_ms = None
        if snap.selected_col is not None:
            self.footer_note = (
                f"Bước {snap.step}: dời cột {snap.selected_col} từ hàng {snap.old_row} sang hàng {snap.new_row} "
                f"(còn {snap.total_conflicts} xung đột)."
            )
        if snap.solved or snap.step >= 5000:
            self.auto_play = False
            self.step_iter = None
        self._sync_status_from_board()
        self._rebuild_buttons()

    def toggle_autoplay(self) -> None:
        """Bat hoac tam dung che do phat tu dong cho Min-Conflicts."""
        if self.algo_key == "sat":
            self.solve_immediately()
            return
        if self.board.total_conflicts() == 0:
            self.randomize_board()
        self.auto_play = not self.auto_play
        self._step_accum_ms = 0.0
        self._sync_status_from_board()
        self._rebuild_buttons()

    def run_quick_compare(self) -> None:
        """So sanh truc tiep Min-Conflicts chuan va Heuristic de xuat tren cung ban co."""
        self.auto_play = False
        self.step_iter = None
        self.sat_result = None
        seed = 9000 + self.seed_counter

        std_res = MinConflictsSolver(RandomConflictedSelector(), max_steps=5000).solve(
            self.n, initial_board=self.initial_board, seed=seed
        )
        prop_res = MinConflictsSolver(AdaptiveTabuMaxConflictSelector(), max_steps=5000).solve(
            self.n, initial_board=self.initial_board, seed=seed
        )

        self.board = prop_res.board
        self.steps_count = prop_res.steps
        self.selected_col = None
        self.last_elapsed_ms = prop_res.elapsed_sec * 1000.0
        self.compare_summary = (
            f"{std_res.steps} bước ({std_res.elapsed_sec * 1000:.2f} ms)",
            f"{prop_res.steps} bước ({prop_res.elapsed_sec * 1000:.2f} ms)",
        )
        if std_res.steps > 0:
            diff_pct = 100.0 * (std_res.steps - prop_res.steps) / std_res.steps
            self.footer_note = (
                f"So sánh cùng bàn cờ {self.n} × {self.n}: Chuẩn {std_res.steps} bước vs "
                f"Đề xuất {prop_res.steps} bước ({diff_pct:+.1f}%)."
            )
        else:
            self.footer_note = "Bàn cờ khởi tạo đã là nghiệm hợp lệ."
        self._sync_status_from_board()
        self._rebuild_buttons()

    def _update_slider_from_x(self, mouse_x: int) -> None:
        """Cap nhat toc do phat tu dong theo vi tri keo chuot tren thanh truot."""
        ratio = (mouse_x - self.slider_rect.left) / max(1, self.slider_rect.width)
        ratio = max(0.0, min(1.0, ratio))
        self.speed_sps = max(1, min(60, int(round(1 + ratio * 59))))

    def _handle_button_click(self, key: str) -> None:
        if key == "n_dec":
            self.set_board_size(self.n - 1)
        elif key == "n_inc":
            self.set_board_size(self.n + 1)
        elif key.startswith("size_"):
            self.set_board_size(int(key.split("_", 1)[1]))
        elif key.startswith("algo_"):
            self.set_algorithm(key.split("_", 1)[1])
        elif key == "solve":
            self.solve_immediately()
        elif key == "random":
            self.randomize_board()
        elif key == "step":
            self.auto_play = False
            self.step_once()
        elif key == "play":
            self.toggle_autoplay()
        elif key == "compare":
            self.run_quick_compare()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Xu ly su kien chuot va phim tat; tra ve False khi dong cua so."""
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key == pygame.K_SPACE:
                self.toggle_autoplay()
            elif event.key in (pygame.K_RIGHT, pygame.K_s):
                self.auto_play = False
                self.step_once()
            elif event.key == pygame.K_r:
                self.randomize_board()
            elif event.key == pygame.K_RETURN:
                self.solve_immediately()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.slider_rect.inflate(8, 12).collidepoint(event.pos):
                self._dragging_slider = True
                self._update_slider_from_x(event.pos[0])
            else:
                for btn in self.buttons:
                    if btn.rect.collidepoint(event.pos):
                        self._handle_button_click(btn.key)
                        break
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging_slider = False
        elif event.type == pygame.MOUSEMOTION and self._dragging_slider:
            self._update_slider_from_x(event.pos[0])
        return True

    def update(self, dt_ms: float) -> None:
        """Cap nhat bo dem thoi gian cho che do phat tu dong Min-Conflicts."""
        if not self.auto_play:
            return
        self._step_accum_ms += dt_ms
        interval_ms = 1000.0 / max(1, self.speed_sps)
        max_steps_per_frame = 4
        ran = 0
        while self._step_accum_ms >= interval_ms and self.auto_play and ran < max_steps_per_frame:
            self._step_accum_ms -= interval_ms
            self.step_once()
            ran += 1

    def _draw_dashed_line(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        color: tuple[int, int, int],
        width: int = 2,
        dash_len: float = 7.0,
        gap_len: float = 5.0,
    ) -> None:
        """Ve duong net dut noi cap quan hau dang tan cong nhau."""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist = (dx * dx + dy * dy) ** 0.5
        if dist < 1e-6:
            return
        ux, uy = dx / dist, dy / dist
        pos = 0.0
        while pos < dist:
            seg_end = min(pos + dash_len, dist)
            p1 = (int(round(start[0] + ux * pos)), int(round(start[1] + uy * pos)))
            p2 = (int(round(start[0] + ux * seg_end)), int(round(start[1] + uy * seg_end)))
            pygame.draw.line(self.screen, color, p1, p2, width)
            pos += dash_len + gap_len

    def _draw_queen_crown(
        self,
        x: float,
        y: float,
        cell: float,
        color: tuple[int, int, int],
    ) -> None:
        """Ve bieu tuong vuong mien vector toi gian tu dong co gian theo o."""
        if cell < 16.0:
            cx = int(round(x + cell * 0.5))
            cy = int(round(y + cell * 0.5))
            radius = max(2, int(round(cell * 0.28)))
            pygame.draw.circle(self.screen, color, (cx, cy), radius)
            return

        def pt(hx: float, vy: float) -> tuple[int, int]:
            return int(round(x + cell * hx)), int(round(y + cell * vy))

        crown = [
            pt(0.22, 0.32),
            pt(0.29, 0.66),
            pt(0.71, 0.66),
            pt(0.78, 0.32),
            pt(0.63, 0.50),
            pt(0.65, 0.24),
            pt(0.54, 0.47),
            pt(0.50, 0.19),
            pt(0.46, 0.47),
            pt(0.35, 0.24),
            pt(0.37, 0.50),
        ]
        pygame.draw.polygon(self.screen, color, crown)

        dot_r = max(2, int(round(cell * 0.045)))
        for hx, vy in ((0.22, 0.29), (0.35, 0.22), (0.50, 0.17), (0.65, 0.22), (0.78, 0.29)):
            pygame.draw.circle(self.screen, color, pt(hx, vy), dot_r)

        base_rect = pygame.Rect(
            int(round(x + cell * 0.28)),
            int(round(y + cell * 0.70)),
            max(4, int(round(cell * 0.44))),
            max(3, int(round(cell * 0.09))),
        )
        pygame.draw.rect(self.screen, color, base_rect, border_radius=2)

    def _draw_header(self) -> None:
        """Ve thanh tieu de toi gian phia tren cung."""
        pygame.draw.rect(self.screen, SURFACE, (0, 0, WINDOW_W, HEADER_H))
        pygame.draw.line(self.screen, BORDER, (0, HEADER_H - 1), (WINDOW_W, HEADER_H - 1), 1)

        title_surf = self.font_h1.render("Bài Toán N Quân Hậu", True, TEXT_PRIMARY)
        self.screen.blit(title_surf, (28, (HEADER_H - title_surf.get_height()) // 2))

        sub_surf = self.font_caption.render(
            "Nhiệm vụ 1  |  Logic Mệnh Đề (Glucose3) & Tìm Kiếm Cục Bộ (Min-Conflicts)",
            True,
            TEXT_SECONDARY,
        )
        self.screen.blit(
            sub_surf,
            (28 + title_surf.get_width() + 18, (HEADER_H - sub_surf.get_height()) // 2 + 2),
        )

        # Nhan trang thai dang vien pill gon ben phai
        if self.status_tone == "success":
            pill_bg, pill_fg, pill_border = ACCENT_PRIMARY_SOFT, ACCENT_PRIMARY, ACCENT_PRIMARY
        elif self.status_tone == "alert":
            pill_bg, pill_fg, pill_border = ACCENT_ALERT_SOFT, ACCENT_ALERT, ACCENT_ALERT
        else:
            pill_bg, pill_fg, pill_border = SURFACE_SUBTLE, TEXT_PRIMARY, BORDER_STRONG

        st_surf = self.font_caption.render(self.status_text, True, pill_fg)
        pill_w = st_surf.get_width() + 24
        pill_rect = pygame.Rect(WINDOW_W - 28 - pill_w, (HEADER_H - 26) // 2, pill_w, 26)
        pygame.draw.rect(self.screen, pill_bg, pill_rect, border_radius=13)
        pygame.draw.rect(self.screen, pill_border, pill_rect, width=1, border_radius=13)
        self.screen.blit(
            st_surf,
            (pill_rect.centerx - st_surf.get_width() // 2, pill_rect.centery - st_surf.get_height() // 2),
        )

    def _draw_board_area(self) -> None:
        """Ve ban co N x N can giua voi khoang trang rong va duong xung dot."""
        pygame.draw.rect(self.screen, BG_CANVAS, (0, HEADER_H, SIDEBAR_X, WINDOW_H - HEADER_H))

        n = self.board.n
        show_coords = n <= 20
        coord_pad = 22 if show_coords else 0
        board_side = 544
        cell = board_side / n

        origin_x = (SIDEBAR_X - board_side) // 2 + (coord_pad // 2)
        origin_y = HEADER_H + (WINDOW_H - HEADER_H - board_side - 28) // 2 + (coord_pad // 2)

        solved = self.board.total_conflicts() == 0

        # Ve tung o ban co xen ke trang va xam rat nhe
        for row in range(n):
            y0 = int(round(origin_y + row * cell))
            y1 = int(round(origin_y + (row + 1) * cell))
            for col in range(n):
                x0 = int(round(origin_x + col * cell))
                x1 = int(round(origin_x + (col + 1) * cell))
                rect = pygame.Rect(x0, y0, max(1, x1 - x0), max(1, y1 - y0))

                is_queen = self.board.queens[col] == row
                if is_queen and not solved and self.board.conflicts_for_queen(col) > 0:
                    fill = ACCENT_ALERT_SOFT
                elif is_queen and solved:
                    fill = ACCENT_PRIMARY_SOFT
                else:
                    fill = SURFACE if (row + col) % 2 == 0 else SURFACE_SUBTLE
                pygame.draw.rect(self.screen, fill, rect)

        # Khung vien 1px manh bao ngoai ban co
        outer_rect = pygame.Rect(origin_x, origin_y, board_side, board_side)
        pygame.draw.rect(self.screen, BORDER_STRONG, outer_rect, width=1)

        # Chi so hang va cot khi N <= 20
        if show_coords:
            for i in range(n):
                lbl = self.font_coord.render(str(i), True, TEXT_SECONDARY)
                cx = int(round(origin_x + (i + 0.5) * cell)) - lbl.get_width() // 2
                self.screen.blit(lbl, (cx, origin_y - 18))
                cy = int(round(origin_y + (i + 0.5) * cell)) - lbl.get_height() // 2
                self.screen.blit(lbl, (origin_x - lbl.get_width() - 8, cy))

        # Ve tia net dut noi cac cap quan hau tan cong nhau khi N <= 20
        if not solved and n <= 20:
            for (r1, c1), (r2, c2) in self.board.attacking_pairs():
                p1 = (origin_x + (c1 + 0.5) * cell, origin_y + (r1 + 0.5) * cell)
                p2 = (origin_x + (c2 + 0.5) * cell, origin_y + (r2 + 0.5) * cell)
                self._draw_dashed_line(p1, p2, ACCENT_ALERT, width=2)

        # Ve quan hau va danh dau cot vua di chuyen
        for col, row in enumerate(self.board.queens):
            x0 = origin_x + col * cell
            y0 = origin_y + row * cell
            if self.selected_col == col:
                hl_rect = pygame.Rect(
                    int(round(x0)),
                    int(round(y0)),
                    max(2, int(round(cell))),
                    max(2, int(round(cell))),
                )
                pygame.draw.rect(self.screen, TEXT_PRIMARY, hl_rect, width=2)

            if solved:
                q_color = ACCENT_PRIMARY
            elif self.board.conflicts_for_queen(col) > 0:
                q_color = ACCENT_ALERT
            else:
                q_color = TEXT_PRIMARY
            self._draw_queen_crown(x0, y0, cell, q_color)

        # Ghi chu 1 dong nhe phia duoi ban co
        note_surf = self.font_caption.render(self.footer_note, True, TEXT_SECONDARY)
        self.screen.blit(
            note_surf,
            (SIDEBAR_X // 2 - note_surf.get_width() // 2, origin_y + board_side + 16),
        )

    def _draw_button(self, btn: ButtonSpec, mouse_pos: tuple[int, int]) -> None:
        hovered = btn.rect.collidepoint(mouse_pos)
        if btn.primary:
            bg = ACCENT_PRIMARY_HOVER if hovered else ACCENT_PRIMARY
            fg = SURFACE
            border_color = None
        elif btn.active:
            bg = ACCENT_PRIMARY_SOFT
            fg = ACCENT_PRIMARY
            border_color = ACCENT_PRIMARY
        else:
            bg = SURFACE_SUBTLE if hovered else SURFACE
            fg = TEXT_PRIMARY
            border_color = BORDER_STRONG if hovered else BORDER

        pygame.draw.rect(self.screen, bg, btn.rect, border_radius=6)
        if border_color is not None:
            pygame.draw.rect(self.screen, border_color, btn.rect, width=1, border_radius=6)

        font = self.font_body_bold if (btn.primary or btn.active) else self.font_body
        text_surf = font.render(btn.label, True, fg)
        if btn.key.startswith("algo_"):
            tx = btn.rect.left + 12
        else:
            tx = btn.rect.centerx - text_surf.get_width() // 2
        ty = btn.rect.centery - text_surf.get_height() // 2
        self.screen.blit(text_surf, (tx, ty))

    def _telemetry_rows(self) -> list[tuple[str, str]]:
        """Tao 6 dong thong so truc quan tuy theo che do SAT hay Min-Conflicts."""
        if self.sat_result is not None:
            r = self.sat_result
            st = r.encoding_stats
            alo = st.row_alo_clauses + st.col_alo_clauses
            amo = st.row_amo_clauses + st.col_amo_clauses + st.diag_amo_clauses
            return [
                ("Kích thước / Biến", f"{r.n} × {r.n} ({r.num_variables:,})"),
                ("Tổng mệnh đề CNF", f"{r.num_clauses:,}"),
                ("Phân rã ALO / AMO", f"{alo:,} / {amo:,}"),
                ("Mã hóa / Giải SAT", f"{r.encoding_time_sec * 1000:.2f} / {r.solve_time_sec * 1000:.2f} ms"),
                ("Quyết định / Lan truyền", f"{r.decisions:,} / {r.propagations:,}"),
                ("Xung đột / Khởi động lại", f"{r.conflicts:,} / {r.restarts:,}"),
            ]

        elapsed_str = f"{self.last_elapsed_ms:.2f} ms" if self.last_elapsed_ms is not None else "Từng bước"
        std_cmp = self.compare_summary[0] if self.compare_summary else "Nhấn So sánh"
        prop_cmp = self.compare_summary[1] if self.compare_summary else "Nhấn So sánh"
        return [
            ("Kích thước bàn cờ", f"{self.n} × {self.n}"),
            ("Số bước đã chạy", f"{self.steps_count:,} bước"),
            ("Cặp xung đột hiện tại", f"{self.board.total_conflicts():,} cặp"),
            ("Thời gian thực thi", elapsed_str),
            ("Đối chiếu (Chuẩn)", std_cmp),
            ("Đối chiếu (Đề xuất)", prop_cmp),
        ]

    def _draw_sidebar(self, mouse_pos: tuple[int, int]) -> None:
        """Ve thanh dieu khien va thong so ben phai theo bo cuc 3 nhom."""
        pygame.draw.rect(self.screen, SURFACE, (SIDEBAR_X, HEADER_H, SIDEBAR_W, WINDOW_H - HEADER_H))
        pygame.draw.line(self.screen, BORDER, (SIDEBAR_X, HEADER_H), (SIDEBAR_X, WINDOW_H), 1)

        x0 = SIDEBAR_X + 24
        x1 = WINDOW_W - 24

        # Nhom 1: Cau hinh
        self.screen.blit(self.font_h2.render("CẤU HÌNH", True, TEXT_SECONDARY), (x0, 72))
        self.screen.blit(self.font_body.render("Kích thước bàn cờ N", True, TEXT_PRIMARY), (x0, 97))
        n_val = self.font_mono_bold.render(f"N = {self.n}", True, TEXT_PRIMARY)
        self.screen.blit(n_val, (x1 - 55 - n_val.get_width() // 2, 98))
        self.screen.blit(self.font_caption.render("Thuật toán giải", True, TEXT_SECONDARY), (x0, 166))

        pygame.draw.line(self.screen, BORDER, (x0, 324), (x1, 324), 1)

        # Nhom 2: Dieu khien
        self.screen.blit(self.font_h2.render("ĐIỀU KHIỂN", True, TEXT_SECONDARY), (x0, 336))

        # Ve tat ca cac nut trong Nhom 1 va Nhom 2
        for btn in self.buttons:
            self._draw_button(btn, mouse_pos)

        # Thanh truot toc do hoat anh
        self.screen.blit(self.font_caption.render("Tốc độ hoạt ảnh", True, TEXT_SECONDARY), (x0, 444))
        spd_lbl = self.font_mono.render(f"{self.speed_sps} bước/giây", True, TEXT_PRIMARY)
        self.screen.blit(spd_lbl, (x1 - spd_lbl.get_width(), 444))

        track_y = self.slider_rect.centery
        pygame.draw.line(self.screen, BORDER, (self.slider_rect.left, track_y), (self.slider_rect.right, track_y), 4)
        ratio = (self.speed_sps - 1) / 59.0
        knob_x = int(round(self.slider_rect.left + ratio * self.slider_rect.width))
        pygame.draw.line(self.screen, ACCENT_PRIMARY, (self.slider_rect.left, track_y), (knob_x, track_y), 4)
        pygame.draw.circle(self.screen, SURFACE, (knob_x, track_y), 7)
        pygame.draw.circle(self.screen, ACCENT_PRIMARY, (knob_x, track_y), 7, 2)

        pygame.draw.line(self.screen, BORDER, (x0, 492), (x1, 492), 1)

        # Nhom 3: Thong so va chu giai
        self.screen.blit(self.font_h2.render("THÔNG SỐ", True, TEXT_SECONDARY), (x0, 504))
        for idx, (label, value) in enumerate(self._telemetry_rows()):
            ry = 528 + idx * 24
            lbl_surf = self.font_caption.render(label, True, TEXT_SECONDARY)
            val_surf = self.font_mono.render(value, True, TEXT_PRIMARY)
            self.screen.blit(lbl_surf, (x0, ry))
            self.screen.blit(val_surf, (x1 - val_surf.get_width(), ry))

        # Dong chu giai mau toi gian o day sidebar
        legend_y = 684
        items = (
            (ACCENT_PRIMARY, "Hợp lệ"),
            (TEXT_PRIMARY, "An toàn"),
            (ACCENT_ALERT, "Xung đột"),
        )
        lx = x0
        for color, text in items:
            pygame.draw.circle(self.screen, color, (lx + 5, legend_y + 7), 5)
            surf = self.font_caption.render(text, True, TEXT_SECONDARY)
            self.screen.blit(surf, (lx + 16, legend_y))
            lx += surf.get_width() + 34

    def render(self) -> None:
        """Ve toan bo khung hinh hien tai."""
        mouse_pos = pygame.mouse.get_pos()
        self._draw_header()
        self._draw_board_area()
        self._draw_sidebar(mouse_pos)
        pygame.display.flip()

    def save_screenshot(self, output_path: Path) -> None:
        """Xuat anh chup man hinh PNG phuc vu kiem thu va minh hoa."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.render()
        pygame.image.save(self.screen, str(output_path))

    def run(self) -> None:
        """Vong lap su kien chinh cua cua so PyGame."""
        running = True
        while running:
            dt_ms = float(self.clock.tick(60))
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False
                    break
            self.update(dt_ms)
            self.render()
        pygame.quit()
