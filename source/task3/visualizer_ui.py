"""Giao dien PyGame phong cach toi gian (Minimalism) cho Nhien vu 3 (Kakuro CSP)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Thread
from typing import Dict, List, Optional, Tuple

import pygame

from .board_editor import BoardEditor
from .csp_model import KakuroCSP
from .solver import KakuroSolveResult, KakuroSolver, SolverMode, SolverStep


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

SANS_FONTS = ("SF Pro Display", "Helvetica Neue", "Segoe UI", "Arial", "DejaVu Sans")
MONO_FONTS = ("SF Mono", "Menlo", "Consolas", "Courier New", "DejaVu Sans Mono")


@dataclass
class ControlButton:
    """Mo ta hinh hoc va trang thai hien thi cua mot nut bam toi gian."""

    rect: pygame.Rect
    label: str
    action_id: str
    enabled: bool = True
    primary: bool = False
    active: bool = False


class KakuroVisualizerUI:
    """Giao dien PyGame toi gian truc quan hoa mien gia tri, AC-3, quay lui va soan thao."""

    GRID_BOX = pygame.Rect(40, 120, 680, 514)
    MAX_CELL_SIZE = 94

    MODES: Tuple[SolverMode, ...] = (
        SolverMode.PLAIN_BT,
        SolverMode.BT_FC,
        SolverMode.BT_MAC_HEURISTICS,
    )
    MODE_LABELS: Tuple[str, ...] = (
        "Quay lui cơ bản",
        "Kiểm tra tiến + MRV",
        "AC-3 mở rộng + MRV/Bậc/LCV",
    )
    MAP_SHORT_LABELS: Tuple[str, ...] = ("5×5", "6×6", "8×8", "9×9")

    EVENT_TITLES: Dict[str, str] = {
        "INITIAL": "Khởi tạo miền giá trị",
        "PREPROCESS": "Tiền xử lý thu hẹp miền",
        "SELECT_VAR": "Chọn biến ưu tiên",
        "ASSIGN": "Thử gán chữ số",
        "PRUNE": "Lan truyền cắt tỉa miền",
        "REJECT": "Từ chối ứng viên",
        "FAILURE": "Phát hiện ngõ cụt",
        "BACKTRACK": "Quay lui khôi phục miền",
        "SOLVED": "Đã tìm thấy nghiệm hợp lệ",
        "UNSAT": "Bảng vô nghiệm",
        "NODE_LIMIT": "Chạm giới hạn nút duyệt",
    }

    def __init__(self, maps_dir: Optional[Path] = None) -> None:
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Câu Đố Kakuro (CSP) | Nhiệm Vụ 3")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock = pygame.time.Clock()
        self._font_cache: Dict[Tuple[str, int, bool], pygame.font.Font] = {}

        self.maps_dir = Path(maps_dir or Path(__file__).resolve().parent / "maps")
        preferred = (
            "board_5x5_example.json",
            "board_6x6_medium.json",
            "board_8x8_hard.json",
            "board_9x9_complex.json",
        )
        self.map_files = [self.maps_dir / name for name in preferred if (self.maps_dir / name).exists()]
        if not self.map_files:
            raise ValueError("Khong tim thay bang mau nao trong thu muc maps/")

        self.map_idx: int = 0
        self.mode_idx: int = 2
        self.csp: KakuroCSP = KakuroCSP.from_json(self.map_files[self.map_idx])
        self.editor: BoardEditor = BoardEditor(self.csp)
        self.editing: bool = False
        self.custom: bool = False

        self.result: Optional[KakuroSolveResult] = None
        self._pruned_prefix: List[int] = []
        self.step_idx: int = 0
        self.auto_play: bool = False
        self.step_delay_ms: int = 240
        self.last_tick: int = 0

        self.selected: Optional[Tuple[int, int]] = None
        self.field: Optional[str] = None
        self.buffer: str = ""
        self.path_text: str = "custom_board.json"
        self.new_size: int = 5
        self.bulk: Optional[List[str]] = None

        self.notice: str = "Chọn bảng mẫu bên phải hoặc nhấn Sửa bảng để tự tạo câu đố mới."
        self.notice_error: bool = False
        self.buttons: List[ControlButton] = []
        self.fields: Dict[str, pygame.Rect] = {}

        self.busy: bool = False
        self.jobs: Queue[Tuple[Optional[KakuroSolveResult], Optional[str]]] = Queue()
        self.cancel_event: Event = Event()

        self.speed_slider = pygame.Rect(SIDEBAR_X + 24, 376, SIDEBAR_W - 48, 16)
        self.drag_speed: bool = False

        self._set_result(self._compute_trace())

    # ------------------------------------------------------------------
    # Tien ich font chu va ve co ban
    # ------------------------------------------------------------------

    def _font(self, size: int, bold: bool = False, mono: bool = False) -> pygame.font.Font:
        family_key = "mono" if mono else "sans"
        cache_key = (family_key, size, bold)
        if cache_key not in self._font_cache:
            candidates = MONO_FONTS if mono else SANS_FONTS
            font_path = None
            for family in candidates:
                matched = pygame.font.match_font(family, bold=bold)
                if matched:
                    font_path = matched
                    break
            if font_path:
                self._font_cache[cache_key] = pygame.font.Font(font_path, size)
            else:
                self._font_cache[cache_key] = pygame.font.SysFont(",".join(candidates), size, bold=bold)
        return self._font_cache[cache_key]

    def _draw_text(
        self,
        value: object,
        x: int,
        y: int,
        size: int = 13,
        color: Tuple[int, int, int] = TEXT_PRIMARY,
        bold: bool = False,
        mono: bool = False,
        max_width: Optional[int] = None,
        align: str = "left",
    ) -> int:
        font = self._font(size, bold=bold, mono=mono)
        text = str(value)
        if max_width is not None and font.size(text)[0] > max_width:
            ellipsis = "..."
            while text and font.size(text + ellipsis)[0] > max_width:
                text = text[:-1]
            text = (text + ellipsis) if text else ""
        surf = font.render(text, True, color)
        if align == "right":
            draw_x = x - surf.get_width()
        elif align == "center":
            draw_x = x - surf.get_width() // 2
        else:
            draw_x = x
        self.screen.blit(surf, (draw_x, y))
        return surf.get_width()

    def _draw_centered(
        self,
        value: object,
        rect: pygame.Rect,
        size: int = 14,
        color: Tuple[int, int, int] = TEXT_PRIMARY,
        bold: bool = False,
        mono: bool = False,
    ) -> None:
        text = str(value)
        cur_size = size
        font = self._font(cur_size, bold=bold, mono=mono)
        while cur_size > 9 and font.size(text)[0] > rect.width - 8:
            cur_size -= 1
            font = self._font(cur_size, bold=bold, mono=mono)
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def _draw_wrapped(
        self,
        value: str,
        x: int,
        y: int,
        width: int,
        size: int = 12,
        color: Tuple[int, int, int] = TEXT_SECONDARY,
        max_lines: int = 3,
        line_gap: int = 5,
    ) -> None:
        font = self._font(size)
        lines: List[str] = []
        current = ""
        for word in str(value).split():
            trial = f"{current} {word}".strip()
            if current and font.size(trial)[0] > width:
                lines.append(current)
                current = word
            else:
                current = trial
        if current:
            lines.append(current)
        for idx, line in enumerate(lines[:max_lines]):
            self._draw_text(line, x, y + idx * (size + line_gap), size=size, color=color, max_width=width)

    def _draw_button(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        label: str,
        action_id: str,
        enabled: bool = True,
        primary: bool = False,
        active: bool = False,
        font_size: int = 13,
    ) -> None:
        can_click = enabled and (not self.busy or action_id == "EDIT")
        rect = pygame.Rect(x, y, w, h)
        btn = ControlButton(rect, label, action_id, can_click, primary, active)
        self.buttons.append(btn)

        hovered = can_click and rect.collidepoint(pygame.mouse.get_pos())
        if not can_click:
            bg = SURFACE_SUBTLE
            fg = BORDER_STRONG
            border_color: Optional[Tuple[int, int, int]] = BORDER
        elif primary:
            bg = ACCENT_PRIMARY_HOVER if hovered else ACCENT_PRIMARY
            fg = SURFACE
            border_color = None
        elif active:
            bg = ACCENT_PRIMARY_SOFT
            fg = ACCENT_PRIMARY
            border_color = ACCENT_PRIMARY
        else:
            bg = SURFACE_SUBTLE if hovered else SURFACE
            fg = TEXT_PRIMARY
            border_color = BORDER_STRONG if hovered else BORDER

        pygame.draw.rect(self.screen, bg, rect, border_radius=6)
        if border_color is not None:
            pygame.draw.rect(self.screen, border_color, rect, 1, border_radius=6)
        self._draw_centered(label, rect, size=font_size, color=fg, bold=(primary or active))

    def _draw_input_box(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        key: str,
        value: str,
        mono: bool = True,
    ) -> None:
        rect = pygame.Rect(x, y, w, h)
        self.fields[key] = rect
        focused = self.field == key
        pygame.draw.rect(self.screen, SURFACE, rect, border_radius=6)
        pygame.draw.rect(
            self.screen,
            ACCENT_PRIMARY if focused else BORDER_STRONG,
            rect,
            2 if focused else 1,
            border_radius=6,
        )
        display_val = self.buffer if focused else value
        if focused:
            display_val = display_val + "|"
        self._draw_text(
            display_val,
            x + 10,
            y + (h - 15) // 2,
            size=13,
            color=TEXT_PRIMARY,
            mono=mono,
            max_width=w - 20,
        )

    def _notify(self, message: str, error: bool = False) -> None:
        self.notice = message
        self.notice_error = error

    @staticmethod
    def _localize_error(exc: Exception) -> str:
        """Chuyen thong bao loi ASCII tu tang loi sang tieng Viet co dau cho UI."""
        raw = str(exc)
        mapping = {
            "Hang dau tien va cot dau tien bat buoc la o den hoac o goi y": (
                "Hàng đầu tiên và cột đầu tiên bắt buộc là ô đen hoặc ô gợi ý."
            ),
            "Khong co day o trang nao theo huong nay": "Không có dãy ô trắng nào theo hướng này.",
            "Tong goi y phai la so nguyen tu 1 den 45": "Tổng gợi ý phải là số nguyên từ 1 đến 45.",
            "O trang chi nhan chu so tu 1 den 9; nhap 0 de xoa": (
                "Ô trắng chỉ nhận chữ số từ 1 đến 9; nhập 0 để xóa."
            ),
            "Kich thuoc bang phai nam trong khoang tu 3 den 9": "Kích thước bảng phải từ 3 đến 9.",
            "Bang khong co o trang nao de giai": "Bảng không có ô trắng nào để giải.",
            "File JSON phai chua luoi grid va danh sach givens hop le": (
                "Tệp JSON phải chứa lưới hợp lệ và danh sách số cho trước đúng định dạng."
            ),
        }
        if raw in mapping:
            return mapping[raw]
        if raw.startswith("Mau thuan tai goi y"):
            return "Mâu thuẫn tổng gợi ý hoặc chữ số cho trước trong một dãy."
        if raw.startswith("O trang") and "day ngang" in raw:
            return "Mỗi ô trắng bắt buộc phải thuộc đồng thời một dãy ngang và một dãy dọc."
        if raw.startswith("Can nhap dung"):
            return "Số dòng nhập nhanh không khớp với số hàng của bảng."
        if raw.startswith("Hang "):
            return "Một hàng nhập nhanh thiếu hoặc thừa số cột; các ô cần cách nhau bằng dấu cách."
        if raw.startswith("O ("):
            return "Ký hiệu ô không hợp lệ (chỉ dùng #, 0, 1–9 hoặc tổng ngang/dọc như 17/0)."
        return raw

    # ------------------------------------------------------------------
    # Quan ly trang thai bai toan va luong giai nen
    # ------------------------------------------------------------------

    def _set_result(self, result: Optional[KakuroSolveResult]) -> None:
        self.result = result
        self._pruned_prefix = []
        if result is None:
            return
        running = 0
        for st in result.steps_trace:
            running += sum(len(vals) for vals in st.pruned.values())
            self._pruned_prefix.append(running)

    def _compute_trace(self) -> KakuroSolveResult:
        return KakuroSolver(
            mode=self.MODES[self.mode_idx],
            record_steps=True,
            max_recorded_steps=30_000,
        ).solve(self.csp)

    def select_map(self, idx: int, solve_sync: bool = False) -> None:
        """Nap bang mau theo chi so va giai lai (dong bo neu dung cho screenshot)."""
        self.map_idx = idx % len(self.map_files)
        self.csp = KakuroCSP.from_json(self.map_files[self.map_idx])
        self.editor = BoardEditor(self.csp)
        self.custom = False
        self.selected = None
        self.field = None
        self.bulk = None
        self.auto_play = False
        if self.editing:
            self._notify(f"Đã nạp {self.csp.name} vào trình soạn thảo.")
            return
        if solve_sync:
            self._set_result(self._compute_trace())
            self.step_idx = 0
            self._notify(f"Đã nạp {self.csp.name}.")
        else:
            self.start_solve()

    def select_mode(self, idx: int, solve_sync: bool = False) -> None:
        """Doi che do giai CSP theo chi so 0..2."""
        self.mode_idx = idx % len(self.MODES)
        if self.editing:
            self._notify(f"Chế độ giải đã chọn: {self.MODE_LABELS[self.mode_idx]}.")
            return
        if solve_sync:
            self._set_result(self._compute_trace())
            self.step_idx = 0
            self._notify(f"Đã chuyển sang: {self.MODE_LABELS[self.mode_idx]}.")
        else:
            self.start_solve()

    def start_solve(self) -> None:
        """Khoi chay luong nen giai Kakuro de giao dien khong bi treo."""
        if self.busy:
            return
        self.commit_field()
        self.csp = self.editor.to_csp() if self.editing else self.csp
        if not (3 <= self.csp.rows <= 9 and 3 <= self.csp.cols <= 9):
            raise ValueError("Giao diện hỗ trợ kích thước bảng từ 3 đến 9 hàng và cột.")
        self.editing = False
        self.bulk = None
        self.auto_play = False
        self.busy = True
        self.step_idx = 0
        self._set_result(None)
        self._notify("Đang tìm nghiệm... Nhấn Dừng & Sửa hoặc phím Esc để hủy.")

        csp = self.csp
        mode = self.MODES[self.mode_idx]
        self.cancel_event = Event()
        self.jobs = Queue()
        jobs, cancel = self.jobs, self.cancel_event

        def worker() -> None:
            try:
                res = KakuroSolver(
                    mode=mode,
                    record_steps=True,
                    max_recorded_steps=30_000,
                    cancel_event=cancel,
                ).solve(csp)
                jobs.put((res, None))
            except Exception as exc:
                jobs.put((None, str(exc)))

        Thread(target=worker, daemon=True).start()

    def _poll_worker(self) -> None:
        if not self.busy:
            return
        try:
            res, error = self.jobs.get_nowait()
        except Empty:
            return
        self.busy = False
        if res is not None and res.status == "CANCELLED":
            self._set_result(None)
            self.editing = True
            self._notify("Đã hủy phiên tìm kiếm và quay lại chế độ Soạn thảo.")
            return
        if error:
            self._set_result(None)
            self.editing = True
            self._notify(f"Lỗi bộ giải: {error}", error=True)
            return
        self._set_result(res)
        self.step_idx = 0
        if res and res.solved:
            self._notify(
                f"Đã giải xong sau {res.nodes_explored:,} nút ({res.backtracks:,} lần quay lui, {res.elapsed_ms:.2f} ms)."
            )
        elif res and res.status == "NODE_LIMIT":
            self._notify("Đã chạm giới hạn nút duyệt; hãy thử chế độ AC-3 mở rộng.", error=True)
        else:
            self._notify("Bảng hiện tại vô nghiệm; nhấn Sửa bảng để điều chỉnh gợi ý.", error=True)

    # ------------------------------------------------------------------
    # Ve thanh tieu de va luoi Kakuro ben trai
    # ------------------------------------------------------------------

    def _cell_rect(self, r: int, c: int) -> pygame.Rect:
        rows, cols = (self.editor.rows, self.editor.cols) if self.editing else (self.csp.rows, self.csp.cols)
        cell_size = min(self.GRID_BOX.width // cols, self.GRID_BOX.height // rows, self.MAX_CELL_SIZE)
        left = self.GRID_BOX.x + (self.GRID_BOX.width - cols * cell_size) // 2
        top = self.GRID_BOX.y + (self.GRID_BOX.height - rows * cell_size) // 2
        return pygame.Rect(left + c * cell_size, top + r * cell_size, cell_size, cell_size)

    def _draw_header(self, step: Optional[SolverStep]) -> None:
        pygame.draw.rect(self.screen, SURFACE, (0, 0, WINDOW_W, HEADER_H))
        pygame.draw.line(self.screen, BORDER, (0, HEADER_H - 1), (WINDOW_W, HEADER_H - 1), 1)

        self._draw_text("Câu Đố Kakuro (CSP)", 24, 15, size=20, color=TEXT_PRIMARY, bold=True)
        self._draw_text("Nhiệm vụ 3 · Lan truyền ràng buộc & Quay lui", 236, 21, size=13, color=TEXT_SECONDARY)

        # Nhan trang thai nho gon ben phai vung luoi
        if self.busy:
            badge_text, badge_bg, badge_fg = "Đang giải...", SURFACE_SUBTLE, TEXT_PRIMARY
        elif self.bulk is not None:
            badge_text, badge_bg, badge_fg = "Sửa nhanh toàn bảng", SURFACE_SUBTLE, TEXT_PRIMARY
        elif self.editing:
            badge_text, badge_bg, badge_fg = "Chế độ Soạn thảo", SURFACE_SUBTLE, TEXT_PRIMARY
        elif step and step.step_type == "SOLVED":
            badge_text, badge_bg, badge_fg = "Nghiệm hợp lệ", ACCENT_PRIMARY_SOFT, ACCENT_PRIMARY
        elif step and step.step_type in ("UNSAT", "FAILURE", "BACKTRACK", "REJECT", "NODE_LIMIT"):
            badge_text, badge_bg, badge_fg = self.EVENT_TITLES[step.step_type], ACCENT_ALERT_SOFT, ACCENT_ALERT
        else:
            badge_text, badge_bg, badge_fg = "Chế độ Giải", ACCENT_PRIMARY_SOFT, ACCENT_PRIMARY

        badge_font = self._font(12, bold=True)
        bw = badge_font.size(badge_text)[0] + 24
        badge_rect = pygame.Rect(SIDEBAR_X - bw - 20, 14, bw, 28)
        pygame.draw.rect(self.screen, badge_bg, badge_rect, border_radius=14)
        self._draw_centered(badge_text, badge_rect, size=12, color=badge_fg, bold=True)

        # Nut chuyen che do o goc phai thanh tieu de (nut phu, giu 1 nut chinh duy nhat)
        if self.bulk is not None:
            top_label, top_action = "Quay lại Soạn thảo", "BULK_CANCEL"
        elif self.editing:
            top_label, top_action = "Quay lại Chế độ Giải", "CANCEL_EDIT"
        elif self.busy or self.auto_play:
            top_label, top_action = "Dừng & Sửa bảng", "EDIT"
        else:
            top_label, top_action = "Sửa bảng", "EDIT"
        self._draw_button(WINDOW_W - 184, 12, 160, 32, top_label, top_action, font_size=13)

    def _draw_canvas_header(self) -> None:
        rows, cols = (self.editor.rows, self.editor.cols) if self.editing else (self.csp.rows, self.csp.cols)
        title = f"Bảng tùy chỉnh {rows}×{cols}" if self.custom else self.csp.name
        cx = SIDEBAR_X // 2
        self._draw_text(title, cx, 70, size=15, color=TEXT_PRIMARY, bold=True, align="center", max_width=700)

        if self.editing:
            white_cnt = sum(1 for row in self.editor.grid for c in row if c == "W")
            given_cnt = len(self.editor.givens)
            meta = f"Lưới {rows}×{cols}  ·  {white_cnt} ô trắng  ·  {given_cnt} số cho trước"
        else:
            sum_h, sum_v = self.csp.sum_invariants()
            meta = (
                f"Lưới {rows}×{cols}  ·  {len(self.csp.variables)} biến ô trắng  ·  "
                f"{len(self.csp.runs)} dãy tổng  ·  Tổng ngang = Tổng dọc = {sum_h}"
            )
            if sum_h != sum_v:
                meta = f"Lưới {rows}×{cols}  ·  Tổng ngang ({sum_h}) ≠ Tổng dọc ({sum_v})"
        self._draw_text(meta, cx, 93, size=12, color=TEXT_SECONDARY, align="center", max_width=700)

    def _draw_grid(self, step: Optional[SolverStep]) -> None:
        grid = self.editor.grid if self.editing else self.csp.raw_grid
        givens = self.editor.givens if self.editing else self.csp.givens
        rows, cols = len(grid), len(grid[0])

        top_left_rect = self._cell_rect(0, 0)
        cell_n = top_left_rect.width
        board_rect = pygame.Rect(top_left_rect.x, top_left_rect.y, cols * cell_n, rows * cell_n)

        for r, row in enumerate(grid):
            for c, cell in enumerate(row):
                pos = (r, c)
                rect = self._cell_rect(r, c)
                n = rect.width

                if cell == "W":
                    self._draw_white_cell(rect, pos, step, givens)
                elif isinstance(cell, dict):
                    self._draw_clue_cell(rect, cell)
                else:
                    pygame.draw.rect(self.screen, TEXT_PRIMARY, rect)
                    pygame.draw.rect(self.screen, TEXT_SECONDARY, rect, 1)

        # Vien ngoai khung luoi ro net 1px
        pygame.draw.rect(self.screen, BORDER_STRONG, board_rect, 1)

        # Vien nhan o dang chon / o dang xet (ve sau cung de khong bi de)
        if self.editing and self.selected is not None:
            sel_rect = self._cell_rect(*self.selected)
            pygame.draw.rect(self.screen, TEXT_PRIMARY, sel_rect, 2)
        elif not self.editing and step is not None and step.focus_pos is not None:
            focus_rect = self._cell_rect(*step.focus_pos)
            is_alert = step.step_type in ("BACKTRACK", "FAILURE", "REJECT")
            border_col = ACCENT_ALERT if is_alert else TEXT_PRIMARY
            pygame.draw.rect(self.screen, border_col, focus_rect, 2)

    def _draw_clue_cell(self, rect: pygame.Rect, cell: Dict[str, int]) -> None:
        n = rect.width
        pygame.draw.rect(self.screen, SURFACE_SUBTLE, rect)
        pygame.draw.line(self.screen, BORDER_STRONG, rect.topleft, rect.bottomright, 1)
        pygame.draw.rect(self.screen, BORDER_STRONG, rect, 1)

        clue_size = max(11, min(16, int(n * 0.23)))
        clue_font = self._font(clue_size, bold=True, mono=True)

        if "across" in cell:
            surf = clue_font.render(str(cell["across"]), True, TEXT_PRIMARY)
            cx = rect.x + int(n * 0.72)
            cy = rect.y + int(n * 0.27)
            self.screen.blit(surf, surf.get_rect(center=(cx, cy)))

        if "down" in cell:
            surf = clue_font.render(str(cell["down"]), True, TEXT_PRIMARY)
            cx = rect.x + int(n * 0.28)
            cy = rect.y + int(n * 0.73)
            self.screen.blit(surf, surf.get_rect(center=(cx, cy)))

    def _draw_white_cell(
        self,
        rect: pygame.Rect,
        pos: Tuple[int, int],
        step: Optional[SolverStep],
        givens: Dict[Tuple[int, int], int],
    ) -> None:
        n = rect.width
        is_focus = (not self.editing) and (step is not None) and (pos == step.focus_pos)
        is_alert_focus = is_focus and step is not None and step.step_type in ("BACKTRACK", "FAILURE", "REJECT")
        candidates = step.domains.get(pos, []) if (step is not None and not self.editing) else []
        removed = step.pruned.get(pos, []) if (step is not None and not self.editing) else []
        empty_domain = (step is not None and not self.editing and pos not in step.assignment and not candidates)

        # Quyet dinh mau nen tuan thu nghiem 3 tong UI.md
        if self.editing and pos == self.selected:
            bg = SURFACE_SUBTLE
        elif step is not None and not self.editing and step.step_type == "SOLVED":
            bg = ACCENT_PRIMARY_SOFT
        elif is_alert_focus or empty_domain:
            bg = ACCENT_ALERT_SOFT
        elif is_focus:
            bg = SURFACE_SUBTLE
        else:
            bg = SURFACE

        pygame.draw.rect(self.screen, bg, rect)
        pygame.draw.rect(self.screen, BORDER, rect, 1)

        value = givens.get(pos) if (self.editing or step is None) else step.assignment.get(pos)
        if value is not None:
            is_given = pos in givens
            val_color = TEXT_PRIMARY if is_given else ACCENT_PRIMARY
            val_size = max(19, int(n * 0.44))
            self._draw_centered(value, rect, size=val_size, color=val_color, bold=True, mono=True)
            if is_given:
                self._draw_text("G", rect.x + 4, rect.y + 2, size=10, color=TEXT_SECONDARY, bold=True, mono=True)
            return

        if step is None or self.editing:
            return

        if empty_domain:
            self._draw_centered("×", rect, size=max(20, int(n * 0.45)), color=ACCENT_ALERT, bold=True)
            return

        # Hien thi luoi ung vien 3x3 cho bien chua gan
        pad = 3
        inner = max(12, n - 2 * pad)
        cand_size = max(10, min(14, int(n * 0.19)))
        cand_set = set(candidates)
        removed_set = set(removed)
        alert_digit = (
            step.value
            if (is_alert_focus and step.value is not None)
            else None
        )

        for d in range(1, 10):
            if d not in cand_set and d not in removed_set and d != alert_digit:
                continue
            slot_col = (d - 1) % 3
            slot_row = (d - 1) // 3
            cx = rect.x + pad + int((slot_col + 0.5) * inner / 3.0)
            cy = rect.y + pad + int((slot_row + 0.5) * inner / 3.0)
            is_pruned = d in removed_set
            is_rejected = d == alert_digit

            if is_pruned or is_rejected:
                color = ACCENT_ALERT
                bold_digit = True
            else:
                color = TEXT_SECONDARY
                bold_digit = False

            font = self._font(cand_size, bold=bold_digit, mono=True)
            surf = font.render(str(d), True, color)
            self.screen.blit(surf, surf.get_rect(center=(cx, cy)))

            if is_pruned or (is_rejected and step.step_type == "REJECT"):
                # Gach cheo mau ACCENT_ALERT len chu so bi loai theo UI.md
                delta = max(4, cand_size // 2)
                pygame.draw.line(
                    self.screen,
                    ACCENT_ALERT,
                    (cx - delta, cy + delta - 1),
                    (cx + delta, cy - delta + 1),
                    2,
                )

    def _draw_canvas_footer(self) -> None:
        # Chu giai 3 tong ngan gon ngay duoi luoi
        y_leg = 648
        items = [
            ("teal", "Đã gán hợp lệ"),
            ("focus", "Đang xét (MRV)"),
            ("prune", "Ứng viên bị loại"),
            ("alert", "Quay lui / Ngõ cụt"),
            ("given", "G: Cho trước"),
        ]
        font = self._font(12)
        total_w = sum(16 + font.size(label)[0] + 18 for _, label in items) - 18
        cur_x = max(24, (SIDEBAR_X - total_w) // 2)

        for kind, label in items:
            sw = pygame.Rect(cur_x, y_leg + 2, 11, 11)
            if kind == "teal":
                pygame.draw.rect(self.screen, ACCENT_PRIMARY, sw, border_radius=2)
            elif kind == "focus":
                pygame.draw.rect(self.screen, SURFACE_SUBTLE, sw, border_radius=2)
                pygame.draw.rect(self.screen, TEXT_PRIMARY, sw, 2, border_radius=2)
            elif kind == "prune":
                pygame.draw.rect(self.screen, SURFACE, sw, border_radius=2)
                pygame.draw.rect(self.screen, BORDER_STRONG, sw, 1, border_radius=2)
                pygame.draw.line(self.screen, ACCENT_ALERT, (sw.x + 2, sw.bottom - 2), (sw.right - 2, sw.y + 2), 2)
            elif kind == "alert":
                pygame.draw.rect(self.screen, ACCENT_ALERT_SOFT, sw, border_radius=2)
                pygame.draw.rect(self.screen, ACCENT_ALERT, sw, 1, border_radius=2)
            else:
                pygame.draw.rect(self.screen, SURFACE, sw, border_radius=2)
                pygame.draw.rect(self.screen, TEXT_PRIMARY, sw, 1, border_radius=2)
            cur_x += 16
            cur_x += self._draw_text(label, cur_x, y_leg, size=12, color=TEXT_SECONDARY) + 18

        # Dong thong bao trang thai / loi (toi da 2 dong)
        notice_color = ACCENT_ALERT if self.notice_error else TEXT_SECONDARY
        self._draw_text(
            self.notice,
            SIDEBAR_X // 2,
            678,
            size=12,
            color=notice_color,
            align="center",
            max_width=708,
        )

    # ------------------------------------------------------------------
    # Ve Sidebar ben phai (3 che do: Giai / Soan thao / Sua nhanh)
    # ------------------------------------------------------------------

    def _draw_sidebar_shell(self) -> None:
        pygame.draw.rect(self.screen, SURFACE, (SIDEBAR_X, HEADER_H, SIDEBAR_W, WINDOW_H - HEADER_H))
        pygame.draw.line(self.screen, BORDER, (SIDEBAR_X, HEADER_H), (SIDEBAR_X, WINDOW_H), 1)

    def _step_description(self, step: SolverStep) -> str:
        pos_str = f"ô ({step.focus_pos[0] + 1}, {step.focus_pos[1] + 1})" if step.focus_pos else ""
        kind = step.step_type
        if kind == "INITIAL":
            return "Khởi tạo miền {1..9} cho mọi ô trắng và cố định các chữ số cho trước."
        if kind == "PREPROCESS":
            if self.mode_idx == 0:
                return "Quay lui cơ bản: giữ nguyên miền đầy đủ {1..9}, không tiền xử lý."
            removed_cnt = sum(len(v) for v in step.pruned.values())
            return f"Thu hẹp miền ban đầu bằng tổ hợp tổng và lan truyền ràng buộc (loại {removed_cnt} ứng viên)."
        if kind == "SELECT_VAR":
            rem = len(step.domains.get(step.focus_pos, [])) if step.focus_pos else 0
            return f"Chọn {pos_str} đang còn {rem} ứng viên hợp lệ."
        if kind == "ASSIGN":
            return f"Thử gán chữ số {step.value} vào {pos_str}."
        if kind == "PRUNE":
            removed_cnt = sum(len(v) for v in step.pruned.values())
            return f"Lan truyền từ {pos_str} = {step.value}, loại bỏ {removed_cnt} ứng viên ở các ô cùng dãy."
        if kind == "REJECT":
            return f"Từ chối chữ số {step.value} tại {pos_str} do vi phạm tổng hoặc trùng chữ số."
        if kind == "FAILURE":
            return "Ngõ cụt: xuất hiện ô rỗng miền hoặc dãy không còn tổ hợp tổng hỗ trợ."
        if kind == "BACKTRACK":
            return f"Hoàn tác {step.value} tại {pos_str}, khôi phục miền ứng viên và thử nhánh khác."
        if kind == "SOLVED":
            return "Tất cả dãy ngang và dọc đều thỏa tổng chính xác và khác nhau đôi một."
        if kind == "UNSAT":
            return "Không tồn tại cách điền số nào thỏa mãn đồng thời mọi ràng buộc."
        return "Đã chạm giới hạn số nút duyệt tối đa."

    def _draw_solver_sidebar(self, step: Optional[SolverStep]) -> None:
        x0 = SIDEBAR_X + 24
        w = SIDEBAR_W - 48

        # 1. Cau hinh bang mau & che do giai
        self._draw_text("CẤU HÌNH", x0, 72, size=12, color=TEXT_SECONDARY, bold=True)
        gap = 6
        pill_w = (w - gap * (len(self.map_files) - 1)) // len(self.map_files)
        for i in range(len(self.map_files)):
            label = self.MAP_SHORT_LABELS[i] if i < len(self.MAP_SHORT_LABELS) else f"Mẫu {i + 1}"
            px = x0 + i * (pill_w + gap)
            pw = (x0 + w - px) if i == len(self.map_files) - 1 else pill_w
            self._draw_button(px, 94, pw, 30, label, f"MAP_{i}", active=(not self.custom and self.map_idx == i))

        for i, label in enumerate(self.MODE_LABELS):
            self._draw_button(
                x0,
                132 + i * 32,
                w,
                28,
                label,
                f"MODE_{i}",
                active=(self.mode_idx == i),
                font_size=12,
            )

        pygame.draw.line(self.screen, BORDER, (x0, 234), (x0 + w, 234), 1)

        # 2. Dieu khien phat tung buoc & toc do
        self._draw_text("ĐIỀU KHIỂN", x0, 246, size=12, color=TEXT_SECONDARY, bold=True)
        has_step = step is not None
        half_w = (w - 8) // 2
        self._draw_button(
            x0,
            268,
            half_w,
            36,
            "Tạm dừng" if self.auto_play else "Phát",
            "PLAY",
            enabled=has_step,
            primary=True,
        )
        self._draw_button(
            x0 + half_w + 8,
            268,
            w - half_w - 8,
            36,
            "Bước tiếp",
            "NEXT",
            enabled=has_step,
        )

        q_gap = 6
        q_w = (w - 3 * q_gap) // 4
        controls = (
            ("Trước", "PREV", has_step),
            ("Đặt lại", "RESET", has_step),
            ("Bước cuối", "END", has_step),
            ("Giải lại", "SOLVE", True),
        )
        for i, (label, act, en) in enumerate(controls):
            bx = x0 + i * (q_w + q_gap)
            bw = (x0 + w - bx) if i == 3 else q_w
            self._draw_button(bx, 312, bw, 30, label, act, enabled=en, font_size=12)

        # Thanh truot toc do phat
        self._draw_text("Tốc độ phát", x0, 354, size=12, color=TEXT_SECONDARY)
        self._draw_text(f"{self.step_delay_ms} ms/bước", x0 + w, 354, size=12, color=TEXT_PRIMARY, mono=True, align="right")
        ray_y = self.speed_slider.centery - 2
        pygame.draw.rect(self.screen, BORDER, (self.speed_slider.x, ray_y, self.speed_slider.w, 4), border_radius=2)
        frac = max(0.0, min(1.0, (1000 - self.step_delay_ms) / 975.0))
        fill_w = max(0, int(round(self.speed_slider.w * frac)))
        if fill_w > 0:
            pygame.draw.rect(self.screen, ACCENT_PRIMARY, (self.speed_slider.x, ray_y, fill_w, 4), border_radius=2)
        knob_x = self.speed_slider.x + fill_w
        pygame.draw.circle(self.screen, SURFACE, (knob_x, self.speed_slider.centery), 7)
        pygame.draw.circle(self.screen, ACCENT_PRIMARY, (knob_x, self.speed_slider.centery), 7, 2)

        pygame.draw.line(self.screen, BORDER, (x0, 400), (x0 + w, 400), 1)

        # 3. Tien trinh & thong so do luong
        self._draw_text("TIẾN TRÌNH & THÔNG SỐ", x0, 412, size=12, color=TEXT_SECONDARY, bold=True)
        if step is None or self.result is None:
            msg = "Đang tìm nghiệm trên luồng nền..." if self.busy else "Chưa có dữ liệu mô phỏng."
            self._draw_text(msg, x0, 444, size=13, color=TEXT_PRIMARY, bold=True)
            return

        total = len(self.result.steps_trace)
        self._draw_text(
            f"Bước {self.step_idx + 1:,}/{total:,}",
            x0 + w,
            412,
            size=12,
            color=TEXT_PRIMARY,
            bold=True,
            mono=True,
            align="right",
        )

        # Thanh tien do manh 4px
        prog_rect = pygame.Rect(x0, 435, w, 4)
        pygame.draw.rect(self.screen, BORDER, prog_rect, border_radius=2)
        prog_color = ACCENT_ALERT if step.step_type in ("UNSAT", "NODE_LIMIT", "FAILURE") else ACCENT_PRIMARY
        prog_w = max(2, int(round(w * (self.step_idx + 1) / max(1, total))))
        pygame.draw.rect(self.screen, prog_color, (x0, 435, prog_w, 4), border_radius=2)

        # Tieu de su kien va mo ta ngan
        kind = step.step_type
        if kind == "SOLVED":
            ev_color = ACCENT_PRIMARY
        elif kind in ("UNSAT", "FAILURE", "REJECT", "BACKTRACK", "NODE_LIMIT"):
            ev_color = ACCENT_ALERT
        else:
            ev_color = TEXT_PRIMARY
        self._draw_text(self.EVENT_TITLES.get(kind, kind), x0, 448, size=14, color=ev_color, bold=True)
        self._draw_wrapped(self._step_description(step), x0, 470, w, size=12, color=TEXT_SECONDARY, max_lines=2)

        pygame.draw.line(self.screen, BORDER, (x0, 514), (x0 + w, 514), 1)

        # Bang thong so 2 cot khong ke luoi theo UI.md
        pruned_now = self._pruned_prefix[self.step_idx] if self.step_idx < len(self._pruned_prefix) else 0
        if self.result.valid_verified and kind == "SOLVED":
            verify_text, verify_color = "Hợp lệ (100%)", ACCENT_PRIMARY
        elif self.result.status == "UNSAT":
            verify_text, verify_color = "Vô nghiệm", ACCENT_ALERT
        elif self.result.status == "NODE_LIMIT":
            verify_text, verify_color = "Chạm giới hạn", ACCENT_ALERT
        else:
            verify_text, verify_color = "Đang duyệt...", TEXT_SECONDARY

        rows_data: List[Tuple[str, str, Tuple[int, int, int]]] = [
            ("Ô đã gán", f"{len(step.assignment)} / {len(self.csp.variables)}", TEXT_PRIMARY),
            ("Số nút đã duyệt", f"{step.nodes_so_far:,}", TEXT_PRIMARY),
            ("Ứng viên cắt tỉa", f"{pruned_now:,} / {self.result.pruned_values:,}", TEXT_PRIMARY),
            ("Số lần quay lui", f"{step.backtracks_so_far:,}", ACCENT_ALERT if step.backtracks_so_far > 0 else TEXT_PRIMARY),
            ("Thời gian giải", f"{self.result.elapsed_ms:.2f} ms", TEXT_PRIMARY),
            ("Kiểm chứng nghiệm", verify_text, verify_color),
        ]
        for idx, (label, val, col) in enumerate(rows_data):
            ry = 524 + idx * 26
            self._draw_text(label, x0, ry, size=13, color=TEXT_SECONDARY)
            self._draw_text(val, x0 + w, ry, size=13, color=col, bold=True, mono=True, align="right")

        footer_hint = (
            "Lịch sử trung gian đã được rút gọn theo giới hạn bộ nhớ."
            if self.result.trace_truncated
            else "Phím tắt: Space phát · Trái/Phải bước · 0 đặt lại · Esc sửa"
        )
        self._draw_text(footer_hint, x0, 690, size=11, color=TEXT_SECONDARY, max_width=w)

    def _draw_editor_sidebar(self) -> None:
        x0 = SIDEBAR_X + 24
        w = SIDEBAR_W - 48
        half_w = (w - 8) // 2

        # 1. Mau & kich thuoc bang moi
        self._draw_text("SOẠN THẢO BẢNG", x0, 70, size=12, color=TEXT_SECONDARY, bold=True)
        gap = 6
        pill_w = (w - gap * (len(self.map_files) - 1)) // len(self.map_files)
        for i in range(len(self.map_files)):
            label = self.MAP_SHORT_LABELS[i] if i < len(self.MAP_SHORT_LABELS) else f"Mẫu {i + 1}"
            px = x0 + i * (pill_w + gap)
            pw = (x0 + w - px) if i == len(self.map_files) - 1 else pill_w
            self._draw_button(px, 90, pw, 28, label, f"MAP_{i}", active=(not self.custom and self.map_idx == i), font_size=12)

        self._draw_button(x0, 124, half_w, 30, f"Cỡ mới: {self.new_size}×{self.new_size}", "SIZE", font_size=12)
        self._draw_button(x0 + half_w + 8, 124, w - half_w - 8, 30, f"Tạo bảng {self.new_size}×{self.new_size}", "NEW", font_size=12)
        pygame.draw.line(self.screen, BORDER, (x0, 162), (x0 + w, 162), 1)

        # 2. Chinh sua o dang chon
        if self.selected is None:
            self._draw_text("Ô ĐANG CHỌN", x0, 172, size=12, color=TEXT_SECONDARY, bold=True)
            self._draw_wrapped(
                "Nhấp vào một ô trên lưới bên trái để chuyển loại ô trắng/đen, sửa tổng gợi ý hoặc nhập chữ số cho trước.",
                x0,
                196,
                w,
                size=12,
                color=TEXT_SECONDARY,
                max_lines=4,
            )
        else:
            r, c = self.selected
            cell = self.editor.grid[r][c]
            kind_str = "Ô trắng" if cell == "W" else "Ô đen / gợi ý"
            self._draw_text(f"Ô ({r + 1}, {c + 1}) — {kind_str}", x0, 172, size=12, color=TEXT_PRIMARY, bold=True)
            self._draw_button(
                x0,
                194,
                half_w,
                30,
                "Ô trắng",
                "WHITE",
                enabled=(r > 0 and c > 0),
                active=(cell == "W"),
                font_size=12,
            )
            self._draw_button(
                x0 + half_w + 8,
                194,
                w - half_w - 8,
                30,
                "Ô đen / gợi ý",
                "BLACK",
                enabled=True,
                active=(cell != "W"),
                font_size=12,
            )
            if cell == "W":
                self._draw_text("Số cho trước (1–9, nhập 0 để xóa)", x0, 234, size=12, color=TEXT_SECONDARY)
                self._draw_input_box(x0, 254, half_w, 32, "given", str(self.editor.givens.get(self.selected, "")))
                self._draw_button(
                    x0 + half_w + 8,
                    254,
                    w - half_w - 8,
                    32,
                    "Xóa số ô này",
                    "CLEAR_GIVEN",
                    enabled=(self.selected in self.editor.givens),
                    font_size=12,
                )
            else:
                for idx, (key, title) in enumerate((("across", "Tổng ngang"), ("down", "Tổng dọc"))):
                    fx = x0 + idx * (half_w + 8)
                    fw = half_w if idx == 0 else (w - half_w - 8)
                    self._draw_text(title, fx, 234, size=12, color=TEXT_SECONDARY)
                    if self.editor.run_cells(self.selected, key):
                        cur_val = str(cell.get(key, "")) if isinstance(cell, dict) else ""
                        self._draw_input_box(fx, 254, fw, 32, key, cur_val)
                    else:
                        self._draw_text("Không có dãy", fx, 262, size=12, color=TEXT_SECONDARY)

        pygame.draw.line(self.screen, BORDER, (x0, 300), (x0 + w, 300), 1)

        # 3. Cong cu bang
        self._draw_text("CÔNG CỤ BẢNG", x0, 310, size=12, color=TEXT_SECONDARY, bold=True)
        self._draw_button(x0, 330, half_w, 30, "Sửa nhanh (Bulk)", "BULK", font_size=12)
        self._draw_button(x0 + half_w + 8, 330, w - half_w - 8, 30, "Sinh gợi ý mới", "RANDOM", font_size=12)
        self._draw_button(x0, 366, half_w, 30, "Xóa mọi số cho trước", "CLEAR_ALL", font_size=12)
        self._draw_button(x0 + half_w + 8, 366, w - half_w - 8, 30, "Kiểm tra hợp lệ", "VALIDATE", font_size=12)

        pygame.draw.line(self.screen, BORDER, (x0, 406), (x0 + w, 406), 1)

        # 4. Luu / Mo JSON
        self._draw_text("TỆP JSON (mặc định: maps/custom/)", x0, 416, size=12, color=TEXT_SECONDARY, bold=True)
        self._draw_input_box(x0, 438, w, 32, "path", self.path_text)
        self._draw_button(x0, 476, half_w, 30, "Lưu JSON", "SAVE", font_size=12)
        self._draw_button(x0 + half_w + 8, 476, w - half_w - 8, 30, "Mở JSON", "LOAD", font_size=12)

        pygame.draw.line(self.screen, BORDER, (x0, 516), (x0 + w, 516), 1)

        # 5. Chon che do giai & nut chinh Teal
        self._draw_text("CHẾ ĐỘ GIẢI KHI CHẠY", x0, 526, size=12, color=TEXT_SECONDARY, bold=True)
        for i, label in enumerate(self.MODE_LABELS):
            self._draw_button(
                x0,
                548 + i * 31,
                w,
                27,
                label,
                f"MODE_{i}",
                active=(self.mode_idx == i),
                font_size=12,
            )
        self._draw_button(x0, 650, w, 38, "Giải bảng hiện tại", "SOLVE", primary=True, font_size=14)

    def _draw_bulk_sidebar(self) -> None:
        x0 = SIDEBAR_X + 24
        w = SIDEBAR_W - 48
        half_w = (w - 8) // 2

        self._draw_text("SỬA NHANH TOÀN BẢNG", x0, 72, size=12, color=TEXT_SECONDARY, bold=True)
        self._draw_wrapped(
            "Mỗi ô 1 ký hiệu cách nhau dấu cách: # ô đen, 0 ô trắng, 1–9 số cho trước, N/D tổng ngang/dọc (vd 17/0).",
            x0,
            92,
            w,
            size=12,
            color=TEXT_SECONDARY,
            max_lines=3,
        )

        rows_list = self.bulk or []
        for r, line in enumerate(rows_list):
            ry = 152 + r * 38
            self._draw_text(f"{r + 1:02}", x0, ry + 8, size=12, color=TEXT_SECONDARY, mono=True)
            self._draw_input_box(x0 + 26, ry, w - 26, 32, f"row:{r}", line, mono=True)

        self._draw_text(
            "Nhấn Enter để xác nhận dòng · Ctrl+A để xóa nhanh dòng đang nhập.",
            x0,
            510,
            size=11,
            color=TEXT_SECONDARY,
            max_width=w,
        )
        pygame.draw.line(self.screen, BORDER, (x0, 536), (x0 + w, 536), 1)
        self._draw_button(x0, 554, half_w, 32, "Xóa mọi chữ số", "BULK_CLEAR", font_size=12)
        self._draw_button(x0 + half_w + 8, 554, w - half_w - 8, 32, "Hủy thay đổi", "BULK_CANCEL", font_size=12)
        self._draw_button(x0, 598, w, 38, "Áp dụng toàn bộ", "BULK_APPLY", primary=True, font_size=14)

    # ------------------------------------------------------------------
    # Ket xuat khung hinh va xu ly tuong tac
    # ------------------------------------------------------------------

    def render_frame(self) -> None:
        """Ve toan bo giao dien toi gian 1160x720."""
        self.screen.fill(BG_CANVAS)
        self.buttons = []
        self.fields = {}

        step = (
            None
            if (self.editing or self.result is None or not self.result.steps_trace)
            else self.result.steps_trace[self.step_idx]
        )

        self._draw_header(step)
        self._draw_canvas_header()
        self._draw_grid(step)
        self._draw_canvas_footer()
        self._draw_sidebar_shell()

        if self.bulk is not None:
            self._draw_bulk_sidebar()
        elif self.editing:
            self._draw_editor_sidebar()
        else:
            self._draw_solver_sidebar(step)

        pygame.display.flip()

    def commit_field(self) -> None:
        """Xac nhan gia tri dang nhap trong o van ban hien tai."""
        if self.field is None:
            return
        field_key = self.field
        value = self.buffer.strip()
        self.field = None
        pygame.key.stop_text_input()

        if field_key.startswith("row:") and self.bulk is not None:
            self.bulk[int(field_key.split(":")[1])] = value
            return
        if field_key == "path":
            self.path_text = value or "custom_board.json"
            return
        if not value:
            return
        if not value.isascii() or not value.isdecimal():
            raise ValueError("Vui lòng nhập số nguyên rồi nhấn Enter.")
        if self.selected is None:
            return
        if field_key == "given":
            self.editor.set_given(self.selected, int(value))
        else:
            self.editor.set_clue(self.selected, field_key, int(value))
        self.custom = True
        self._notify("Đã cập nhật giá trị. Nhấn Giải bảng hiện tại để tìm nghiệm.")

    def _resolve_json_path(self) -> Path:
        path = Path(self.path_text).expanduser()
        if not path.is_absolute():
            path = self.maps_dir / "custom" / path
        if path.suffix.lower() != ".json":
            path = path.with_suffix(".json")
        return path

    def _dispatch_action(self, action_id: str) -> None:
        if self.busy and action_id != "EDIT":
            return
        self.commit_field()

        if action_id.startswith("MAP_"):
            idx = int(action_id.split("_")[1])
            self.select_map(idx, solve_sync=False)
        elif action_id.startswith("MODE_"):
            idx = int(action_id.split("_")[1])
            self.select_mode(idx, solve_sync=False)
        elif action_id == "EDIT":
            self.cancel_event.set()
            self.jobs = Queue()
            self.busy = False
            self.auto_play = False
            self.editing = True
            self.editor = BoardEditor(self.csp)
            self.selected = None
            self.bulk = None
            self._notify("Đã mở chế độ Soạn thảo. Chọn ô trên lưới hoặc nhấn Sửa nhanh (Bulk).")
        elif action_id == "CANCEL_EDIT":
            self.editing = False
            self.bulk = None
            self.selected = None
            if self.result is None:
                self.start_solve()
            else:
                self._notify("Đã quay lại chế độ Giải.")
        elif action_id == "BULK":
            self.bulk = self.editor.bulk_rows()
            self.selected = None
            self._notify("Chỉnh sửa từng dòng bên phải rồi nhấn Áp dụng toàn bộ.")
        elif action_id == "BULK_CANCEL":
            self.bulk = None
            self._notify("Đã hủy chế độ Sửa nhanh.")
        elif action_id == "BULK_CLEAR" and self.bulk is not None:
            self.bulk = [
                " ".join("0" if (tok in "123456789" and len(tok) == 1) else tok for tok in row.split())
                for row in self.bulk
            ]
            self._notify("Đã xóa mọi chữ số cho trước trong khung nhập nhanh.")
        elif action_id == "BULK_APPLY" and self.bulk is not None:
            self.editor.apply_bulk_rows(self.bulk)
            self.bulk = None
            self.custom = True
            self._notify("Đã áp dụng toàn bộ lưới mới. Nhấn Kiểm tra hợp lệ hoặc Giải bảng.")
        elif action_id == "RANDOM":
            self.editor.randomize_clues()
            self.custom = True
            self.selected = None
            self._notify("Đã sinh bộ tổng gợi ý mới đảm bảo có nghiệm.")
        elif action_id == "SIZE":
            self.new_size = 3 + (self.new_size - 3 + 1) % 7
        elif action_id == "NEW":
            self.editor = BoardEditor.new(self.new_size)
            self.selected = None
            self.custom = True
            self._notify(f"Đã tạo bảng trống {self.new_size}×{self.new_size}. Nhấp vào ô để tùy chỉnh.")
        elif action_id in ("WHITE", "BLACK") and self.selected is not None:
            self.editor.set_cell_type(self.selected, white=(action_id == "WHITE"))
            self.custom = True
            self._notify("Đã đổi loại ô và tự động đồng bộ lại hướng gợi ý.")
        elif action_id == "CLEAR_GIVEN" and self.selected is not None:
            self.editor.set_given(self.selected, 0)
            self.custom = True
            self._notify("Đã xóa chữ số cho trước tại ô đang chọn.")
        elif action_id == "CLEAR_ALL":
            self.editor.givens.clear()
            self.custom = True
            self._notify("Đã xóa toàn bộ các chữ số cho trước.")
        elif action_id == "VALIDATE":
            self.editor.validate()
            self._notify("Cấu trúc lưới và các cận tổng đều hợp lệ! Sẵn sàng giải.")
        elif action_id == "SAVE":
            out_path = self._resolve_json_path()
            self.editor.save(out_path)
            self._notify(f"Đã lưu tệp JSON tại: {out_path.name}")
        elif action_id == "LOAD":
            in_path = self._resolve_json_path()
            loaded = BoardEditor.load(in_path)
            if not (3 <= loaded.rows <= 9 and 3 <= loaded.cols <= 9):
                raise ValueError("Giao diện chỉ hỗ trợ bảng từ 3 đến 9 hàng và cột.")
            self.editor = loaded
            self.selected = None
            self.custom = True
            self._notify(f"Đã nạp tệp JSON: {in_path.name}")
        elif action_id == "SOLVE":
            self.start_solve()
        elif self.result is not None and self.result.steps_trace:
            end_idx = len(self.result.steps_trace) - 1
            if action_id == "PLAY":
                if self.step_idx >= end_idx:
                    self.step_idx = 0
                self.auto_play = not self.auto_play
                self.last_tick = pygame.time.get_ticks()
            else:
                self.auto_play = False
                if action_id == "PREV":
                    self.step_idx = max(0, self.step_idx - 1)
                elif action_id == "NEXT":
                    self.step_idx = min(end_idx, self.step_idx + 1)
                elif action_id == "RESET":
                    self.step_idx = 0
                elif action_id == "END":
                    self.step_idx = end_idx

    def _set_speed_from_x(self, mouse_x: int) -> None:
        frac = max(0.0, min(1.0, (mouse_x - self.speed_slider.x) / max(1, self.speed_slider.w)))
        self.step_delay_ms = int(round(1000 - 975 * frac))

    def _handle_click(self, pos: Tuple[int, int]) -> None:
        if self.busy:
            for btn in self.buttons:
                if btn.enabled and btn.action_id == "EDIT" and btn.rect.collidepoint(pos):
                    self._dispatch_action("EDIT")
                    return
            return

        for key, rect in self.fields.items():
            if rect.collidepoint(pos):
                if self.field == key:
                    return
                self.commit_field()
                self.field = key
                if key.startswith("row:") and self.bulk is not None:
                    self.buffer = self.bulk[int(key.split(":")[1])]
                elif key == "path":
                    self.buffer = self.path_text
                else:
                    self.buffer = ""
                pygame.key.start_text_input()
                return

        for btn in self.buttons:
            if btn.enabled and btn.rect.collidepoint(pos):
                self._dispatch_action(btn.action_id)
                return

        self.commit_field()
        if self.bulk is not None:
            return

        if self.editing:
            for r in range(self.editor.rows):
                for c in range(self.editor.cols):
                    if self._cell_rect(r, c).collidepoint(pos):
                        self.selected = (r, c)
                        return
        elif self.speed_slider.inflate(16, 16).collidepoint(pos):
            self.drag_speed = True
            self._set_speed_from_x(pos[0])

    def run(self) -> None:
        """Vong lap su kien chinh 60 FPS cua giao dien PyGame."""
        running = True
        while running:
            self._poll_worker()
            for ev in pygame.event.get():
                try:
                    if ev.type == pygame.QUIT:
                        self.cancel_event.set()
                        running = False
                    elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        self._handle_click(ev.pos)
                    elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                        self.drag_speed = False
                    elif ev.type == pygame.MOUSEMOTION and self.drag_speed:
                        self._set_speed_from_x(ev.pos[0])
                    elif ev.type == pygame.TEXTINPUT and self.field is not None:
                        if self.field.startswith("row:"):
                            filtered = "".join(ch for ch in ev.text if ch in "0123456789#/ ")
                            self.buffer = (self.buffer + filtered)[:240]
                        elif self.field == "path":
                            self.buffer = (self.buffer + ev.text)[:240]
                        elif ev.text.isascii() and ev.text.isdigit():
                            self.buffer = (self.buffer + ev.text)[:2]
                    elif ev.type == pygame.KEYDOWN:
                        if self.field is not None:
                            if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                                self.commit_field()
                            elif ev.key == pygame.K_ESCAPE:
                                self.field = None
                                pygame.key.stop_text_input()
                            elif ev.key == pygame.K_BACKSPACE:
                                self.buffer = self.buffer[:-1]
                            elif ev.key == pygame.K_a and (ev.mod & pygame.KMOD_CTRL):
                                self.buffer = ""
                        elif ev.key == pygame.K_ESCAPE and not self.editing:
                            self._dispatch_action("EDIT")
                        elif self.bulk is not None:
                            pass
                        elif (
                            self.editing
                            and self.selected is not None
                            and not self.busy
                            and self.editor.grid[self.selected[0]][self.selected[1]] == "W"
                        ):
                            if ev.unicode and ev.unicode in "0123456789":
                                self.editor.set_given(self.selected, int(ev.unicode))
                                self.custom = True
                            elif ev.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                                self.editor.set_given(self.selected, 0)
                                self.custom = True
                        elif not self.editing and not self.busy:
                            shortcut = {
                                pygame.K_SPACE: "PLAY",
                                pygame.K_LEFT: "PREV",
                                pygame.K_RIGHT: "NEXT",
                                pygame.K_0: "RESET",
                            }.get(ev.key)
                            if shortcut:
                                self._dispatch_action(shortcut)
                except (ValueError, OSError, KeyError, TypeError) as exc:
                    prefix = "Lỗi tệp: " if isinstance(exc, OSError) else "Lỗi: "
                    self._notify(prefix + self._localize_error(exc), error=True)

            if (
                self.auto_play
                and self.result is not None
                and self.result.steps_trace
                and pygame.time.get_ticks() - self.last_tick >= self.step_delay_ms
            ):
                end_idx = len(self.result.steps_trace) - 1
                self.step_idx = min(self.step_idx + 1, end_idx)
                self.last_tick = pygame.time.get_ticks()
                if self.step_idx >= end_idx:
                    self.auto_play = False

            self.render_frame()
            self.clock.tick(60)
        pygame.quit()

    def save_screenshot(self, path: Path | str) -> None:
        """Ket xuat khung hinh hien tai ra anh PNG phuc vu kiem thu va bao cao."""
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        self.render_frame()
        pygame.image.save(self.screen, str(out_path))
