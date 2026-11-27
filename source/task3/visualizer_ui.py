"""Giao diện PyGame trực quan hóa miền giá trị, lan truyền ràng buộc, quay lui và soạn thảo bảng Kakuro."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Thread
import pygame

from .board_editor import BoardEditor
from .csp_model import KakuroCSP
from .solver import KakuroSolver, SolverMode


@dataclass
class ControlButton:
    rect: pygame.Rect
    label: str
    action_id: str
    enabled: bool = True
    accent: bool = False


class KakuroVisualizerUI:
    WINDOW_W, WINDOW_H = 1160, 740
    BG = (15, 23, 42)
    PANEL = (30, 41, 59)
    TEXT = (241, 245, 249)
    MUTED = (164, 182, 204)
    BLUE = (37, 99, 235)
    GREEN = (52, 211, 153)
    RED = (248, 113, 113)
    ORANGE = (251, 191, 36)
    GRID = pygame.Rect(24, 110, 594, 574)
    MODES = [SolverMode.BT_MAC_HEURISTICS, SolverMode.BT_FC, SolverMode.PLAIN_BT]
    MODE_NAMES = [
        'Nâng cao: AC-3 mở rộng + MRV/Bậc/LCV',
        'Quay lui + Kiểm tra tiến + MRV',
        'Quay lui cơ bản',
    ]
    EVENTS = {
        'INITIAL': 'Khởi tạo miền giá trị',
        'PREPROCESS': 'Tiền xử lý thu hẹp miền',
        'SELECT_VAR': 'Chọn biến (MRV / Bậc)',
        'ASSIGN': 'Thử gán giá trị',
        'PRUNE': 'Lan truyền cắt tỉa miền',
        'REJECT': 'Từ chối ứng viên',
        'FAILURE': 'Phát hiện ngõ cụt',
        'BACKTRACK': 'Quay lui khôi phục',
        'SOLVED': 'Đã tìm thấy nghiệm!',
        'UNSAT': 'Bảng vô nghiệm',
        'NODE_LIMIT': 'Đạt giới hạn nút duyệt',
    }

    def __init__(self, maps_dir=None):
        pygame.init()
        pygame.display.set_caption('Trò chơi Kakuro | Nhiệm vụ 3 - Trực quan hóa CSP & Soạn thảo')
        self.window = pygame.display.set_mode((self.WINDOW_W, self.WINDOW_H), pygame.RESIZABLE)
        self.screen = pygame.Surface((self.WINDOW_W, self.WINDOW_H))
        self.clock = pygame.time.Clock()
        self.fonts = {}
        self.maps_dir = Path(maps_dir or Path(__file__).resolve().parent / 'maps')
        preferred = [
            'board_5x5_example.json',
            'board_9x9_complex.json',
            'board_6x6_medium.json',
            'board_8x8_hard.json',
        ]
        self.map_files = [self.maps_dir / n for n in preferred if (self.maps_dir / n).exists()]
        if not self.map_files:
            raise ValueError('Không tìm thấy bảng mẫu nào trong thư mục maps/.')
        self.map_idx, self.mode_idx = 0, 0
        self.csp = KakuroCSP.from_json(self.map_files[0])
        self.editor = BoardEditor(self.csp)
        self.editing = False
        self.result = self._compute_trace()
        self.step_idx = 0
        self.auto_play = False
        self.step_delay_ms = 220
        self.last_tick = 0
        self.selected = None
        self.field = None
        self.buffer = ''
        self.path_text = 'custom_board.json'
        self.size = 5
        self.notice = 'Chọn một bảng mẫu có sẵn hoặc nhấn Sửa bảng để tự tạo câu đố mới.'
        self.notice_error = False
        self.buttons = []
        self.fields = {}
        self.busy = False
        self.jobs = Queue()
        self.cancel_event = Event()
        self.bulk = None
        self.speed_slider = pygame.Rect(784, 320, 322, 8)
        self.drag_speed = False
        self.custom = False

    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self.fonts:
            path = next(
                (
                    p
                    for name in (
                        'Segoe UI',
                        'Arial',
                        'Tahoma',
                        'Helvetica Neue',
                        'Noto Sans',
                        'DejaVu Sans',
                        'Liberation Sans',
                    )
                    if (p := pygame.font.match_font(name, bold=bold))
                ),
                None,
            )
            self.fonts[key] = pygame.font.Font(path, size)
        return self.fonts[key]

    def text(self, value, x, y, size=16, color=None, bold=False, max_width=None):
        font = self.font(size, bold)
        value = str(value)
        if max_width is not None:
            while value and font.size(value)[0] > max_width:
                value = value[:-1]
        self.screen.blit(font.render(value, True, color or self.TEXT), (x, y))

    def centered(self, value, rect, size=16, color=None, bold=False):
        font = self.font(size, bold)
        while size > 9 and font.size(str(value))[0] > rect.width - 6:
            size -= 1
            font = self.font(size, bold)
        surf = font.render(str(value), True, color or self.TEXT)
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def wrap(self, value, x, y, width, size=15, color=None, max_lines=3):
        font = self.font(size)
        lines, line = [], ''
        for word in str(value).split():
            trial = (line + ' ' + word).strip()
            if line and font.size(trial)[0] > width:
                lines.append(line)
                line = word
            else:
                line = trial
        if line:
            lines.append(line)
        for i, line in enumerate(lines[:max_lines]):
            self.text(line, x, y + i * (size + 5), size, color, max_width=width)

    def button(self, x, y, w, h, label, action, enabled=True, accent=False):
        b = ControlButton(
            pygame.Rect(x, y, w, h),
            label,
            action,
            enabled and (not self.busy or action == "EDIT"),
            accent,
        )
        self.buttons.append(b)
        bg = self.BLUE if accent else (51, 65, 85)
        if not b.enabled:
            bg = (40, 48, 62)
        pygame.draw.rect(self.screen, bg, b.rect, border_radius=7)
        self.centered(label, b.rect, 15, self.TEXT if b.enabled else self.MUTED, True)

    def input_box(self, x, y, w, h, label, key, value):
        self.text(label, x, y - 21, 14, self.MUTED)
        rect = pygame.Rect(x, y, w, h)
        self.fields[key] = rect
        pygame.draw.rect(self.screen, (15, 23, 42), rect, border_radius=5)
        pygame.draw.rect(
            self.screen,
            (96, 165, 250) if self.field == key else (71, 85, 105),
            rect,
            2,
            border_radius=5,
        )
        self.text(self.buffer if self.field == key else value, x + 9, y + 7, 16, max_width=w - 18)

    def notify(self, msg, error=False):
        self.notice, self.notice_error = msg, error

    def _compute_trace(self):
        return KakuroSolver(self.MODES[self.mode_idx], record_steps=True, max_recorded_steps=30000).solve(self.csp)

    def _reload_problem(self):
        self.csp = KakuroCSP.from_json(self.map_files[self.map_idx])
        self.editor = BoardEditor(self.csp)
        self.custom = False
        self.editing = False
        self.result = self._compute_trace()
        self.step_idx = 0
        self.auto_play = False
        self.selected = None
        self.field = None

    def start_solve(self):
        if self.busy:
            return
        self.commit_field()
        self.csp = self.editor.to_csp() if self.editing else self.csp
        if not (3 <= self.csp.rows <= 9 and 3 <= self.csp.cols <= 9):
            raise ValueError('Giao diện hỗ trợ kích thước bảng từ 3 đến 9 hàng và cột.')
        self.editing = False
        self.auto_play = False
        self.busy = True
        self.step_idx = 0
        self.result = None
        self.notify('Đang giải... Nhấn Dừng & Sửa hoặc phím Esc để hủy.')
        csp, mode = self.csp, self.MODES[self.mode_idx]
        self.cancel_event = Event()
        self.jobs = Queue()
        jobs, cancel = self.jobs, self.cancel_event

        def worker():
            try:
                jobs.put(
                    (
                        KakuroSolver(
                            mode,
                            record_steps=True,
                            max_recorded_steps=30000,
                            cancel_event=cancel,
                        ).solve(csp),
                        None,
                    )
                )
            except Exception as exc:
                jobs.put((None, str(exc)))

        Thread(target=worker, daemon=True).start()

    def poll(self):
        if not self.busy:
            return
        try:
            result, error = self.jobs.get_nowait()
        except Empty:
            return
        self.busy = False
        self.result = result
        if result is not None and result.status == "CANCELLED":
            self.result = None
            self.editing = True
            self.notify("Đã hủy phiên tìm kiếm.")
            return
        if error:
            self.editing = True
            self.notify('Lỗi bộ giải: ' + error, True)
            return
        self.step_idx = 0
        self.notify('Đã giải xong! Nhấn Tự chạy hoặc Bước tiếp để theo dõi từng bước.')

    def cell_rect(self, r, c):
        rows, cols = (self.editor.rows, self.editor.cols) if self.editing else (self.csp.rows, self.csp.cols)
        n = min(self.GRID.width // cols, self.GRID.height // rows)
        left = self.GRID.x + (self.GRID.width - cols * n) // 2
        top = self.GRID.y + (self.GRID.height - rows * n) // 2
        return pygame.Rect(left + c * n, top + r * n, n, n)

    def draw_grid(self, step):
        grid = self.editor.grid if self.editing else self.csp.raw_grid
        givens = self.editor.givens if self.editing else self.csp.givens
        for r, row in enumerate(grid):
            for c, cell in enumerate(row):
                pos = (r, c)
                rect = self.cell_rect(r, c)
                n = rect.width
                if cell == 'W':
                    bg = (248, 250, 252)
                    if step and step.step_type == 'SOLVED':
                        bg = (209, 250, 229)
                    if step and pos in step.pruned:
                        bg = (254, 226, 226)
                    if step and pos == step.focus_pos:
                        bg = (
                            (219, 234, 254)
                            if step.step_type not in ('BACKTRACK', 'FAILURE', 'REJECT')
                            else (255, 237, 213)
                        )
                    pygame.draw.rect(self.screen, bg, rect)
                    value = givens.get(pos) if self.editing or not step else step.assignment.get(pos)
                    if value is not None:
                        self.centered(
                            value,
                            rect,
                            max(22, int(n * 0.43)),
                            (109, 40, 217) if pos in givens else (30, 64, 175),
                            True,
                        )
                        if pos in givens:
                            self.text('G', rect.x + 4, rect.y + 2, 12, (109, 40, 217), True)
                    elif step and not self.editing:
                        candidates = step.domains.get(pos, [])
                        removed = step.pruned.get(pos, [])
                        for d in range(1, 10):
                            if d not in candidates and d not in removed:
                                continue
                            mini = pygame.Rect(
                                rect.x + (d - 1) % 3 * n // 3,
                                rect.y + (d - 1) // 3 * n // 3,
                                n // 3,
                                n // 3,
                            )
                            color = (185, 28, 28) if d in removed else (51, 65, 85)
                            self.centered(d, mini, max(11, int(n * 0.19)), color)
                            if d in removed:
                                pygame.draw.line(
                                    self.screen,
                                    color,
                                    (mini.centerx - 5, mini.centery),
                                    (mini.centerx + 5, mini.centery),
                                    2,
                                )
                        if not candidates:
                            self.centered('x', rect, 28, (185, 28, 28), True)
                else:
                    pygame.draw.rect(self.screen, (42, 54, 73), rect)
                    if isinstance(cell, dict):
                        pygame.draw.line(self.screen, (112, 130, 156), rect.topleft, rect.bottomright, 1)
                        if 'across' in cell:
                            self.centered(
                                cell['across'],
                                pygame.Rect(rect.x + n // 2, rect.y, n // 2, n // 2),
                                max(13, n // 4),
                                self.TEXT,
                                True,
                            )
                        if 'down' in cell:
                            self.centered(
                                cell['down'],
                                pygame.Rect(rect.x, rect.y + n // 2, n // 2, n // 2),
                                max(13, n // 4),
                                self.TEXT,
                                True,
                            )
                pygame.draw.rect(self.screen, (100, 116, 139), rect, 1)
                if (self.editing and pos == self.selected) or (step and pos == step.focus_pos and not self.editing):
                    pygame.draw.rect(self.screen, (59, 130, 246), rect, 3)

    def draw_editor(self):
        x = 650
        self.text('SOẠN THẢO BẢNG KAKURO', x, 110, 20, bold=True)
        self.button(x, 146, 218, 34, 'Chọn bảng mẫu', 'NEXT_MAP')
        self.button(x + 228, 146, 234, 34, f'Tạo bảng {self.size}x{self.size}', 'NEW', accent=True)
        self.button(x, 187, 218, 32, f'Cỡ bảng: {self.size}x{self.size}', 'SIZE')
        self.button(x + 228, 187, 234, 32, 'Khôi phục mẫu', 'RESTORE')
        pygame.draw.line(self.screen, (71, 85, 105), (x, 232), (x + 462, 232))
        if self.selected is None:
            self.wrap(
                'Nhấp vào một ô để chỉnh sửa, hoặc nhấn Sửa nhanh toàn bảng để nhập nhiều hàng cùng lúc. Nút Sinh ngẫu nhiên gợi ý sẽ tạo bộ tổng mới có nghiệm.',
                x,
                246,
                462,
                15,
                self.MUTED,
                5,
            )
        else:
            r, c = self.selected
            cell = self.editor.grid[r][c]
            loai = 'Ô trắng điền số' if cell == 'W' else 'Ô đen / gợi ý'
            self.text(f'Ô ({r + 1}, {c + 1}) - {loai}', x, 244, 18, bold=True)
            self.button(x, 276, 218, 33, 'Đổi thành Ô trắng', 'WHITE', cell != 'W')
            self.button(x + 228, 276, 234, 33, 'Đổi thành Ô đen', 'BLACK', cell == 'W')
            if cell == 'W':
                self.input_box(
                    x,
                    339,
                    218,
                    34,
                    'Số cho trước (0 = xóa)',
                    'given',
                    str(self.editor.givens.get(self.selected, '')),
                )
                self.button(x + 228, 339, 234, 34, 'Xóa số cho trước', 'CLEAR_GIVEN')
            else:
                for i, (key, label) in enumerate([('across', 'Tổng ngang'), ('down', 'Tổng dọc')]):
                    if self.editor.run_cells(self.selected, key):
                        self.input_box(
                            x + i * 228,
                            339,
                            218,
                            34,
                            label,
                            key,
                            str(cell.get(key, '') if isinstance(cell, dict) else ''),
                        )
                    else:
                        self.text(label + ': không có dãy', x + i * 228, 347, 13, self.MUTED, max_width=218)
        self.button(x, 383, 218, 29, 'Sửa nhanh toàn bảng', 'BULK')
        self.button(x + 228, 383, 234, 29, 'Sinh ngẫu nhiên gợi ý', 'RANDOM')
        self.button(x, 418, 218, 34, 'Xóa mọi số cho trước', 'CLEAR_ALL')
        self.button(x + 228, 418, 234, 34, 'Kiểm tra hợp lệ', 'VALIDATE')
        self.input_box(x, 485, 462, 34, 'Tên hoặc đường dẫn file JSON (mặc định: maps/custom/)', 'path', self.path_text)
        self.button(x, 529, 218, 33, 'Lưu JSON', 'SAVE')
        self.button(x + 228, 529, 234, 33, 'Mở JSON', 'LOAD')
        self.button(x, 575, 462, 34, self.MODE_NAMES[self.mode_idx], 'NEXT_MODE')
        self.button(x, 619, 462, 41, 'GIẢI BẢNG HIỆN TẠI', 'SOLVE', accent=True)

    def draw_bulk(self):
        x = 650
        self.text('SỬA NHANH TOÀN BẢNG', x, 110, 20, bold=True)
        self.wrap(
            'Mỗi ô 1 ký hiệu cách nhau dấu cách: # ô đen, 0 ô trắng trống, 1-9 số cho trước, N/D tổng ngang/dọc (vd 17/0).',
            x,
            140,
            462,
            14,
            self.MUTED,
            3,
        )
        for r, line in enumerate(self.bulk):
            y = 212 + 39 * r
            self.text(f'{r + 1:02}', x, y + 7, 14, self.MUTED)
            rect = pygame.Rect(x + 28, y, 434, 32)
            key = f'row:{r}'
            self.fields[key] = rect
            pygame.draw.rect(self.screen, self.BG, rect, border_radius=4)
            pygame.draw.rect(
                self.screen,
                (96, 165, 250) if self.field == key else (71, 85, 105),
                rect,
                2,
                border_radius=4,
            )
            value = self.buffer if self.field == key else line
            self.centered(value, rect, 16)
        self.text('Nhấn Ctrl+A để xóa nhanh dòng đang chọn rồi nhập lại.', x, 568, 12, self.MUTED, max_width=462)
        self.button(x, 586, 218, 34, 'Xóa mọi chữ số', 'BULK_CLEAR')
        self.button(x + 228, 586, 234, 34, 'Hủy thay đổi', 'BULK_CANCEL')
        self.button(x, 625, 462, 35, 'ÁP DỤNG TOÀN BỘ', 'BULK_APPLY', accent=True)

    def step_message(self, step):
        pos = f'ô ({step.focus_pos[0] + 1}, {step.focus_pos[1] + 1})' if step.focus_pos else ''
        kind = step.step_type
        if kind == 'INITIAL':
            return 'Khởi tạo miền giá trị 1..9 và giữ nguyên các chữ số cho trước.'
        if kind == 'PREPROCESS':
            return (
                'Thu hẹp miền ứng viên bằng tổ hợp tổng và lan truyền ràng buộc theo chế độ đã chọn.'
                if self.mode_idx != 2
                else 'Quay lui cơ bản: giữ nguyên miền đầy đủ 1..9, không tiền xử lý.'
            )
        if kind == 'SELECT_VAR':
            return f'Chọn {pos} hiện còn {len(step.domains.get(step.focus_pos, []))} ứng viên hợp lệ.'
        if kind == 'ASSIGN':
            return f'Thử gán chữ số {step.value} vào {pos}.'
        if kind == 'PRUNE':
            return f'Loại bỏ {sum(map(len, step.pruned.values()))} ứng viên không thỏa tổng phần dư hoặc trùng số.'
        if kind == 'REJECT':
            return f'Từ chối chữ số {step.value} tại {pos} do vi phạm ràng buộc.'
        if kind == 'FAILURE':
            return 'Ngõ cụt: xuất hiện miền giá trị rỗng hoặc dãy không còn bộ số hỗ trợ.'
        if kind == 'BACKTRACK':
            return f'Hủy gán {step.value} tại {pos}, khôi phục miền giá trị và thử nhánh khác.'
        if kind == 'SOLVED':
            return 'Nghiệm hoàn chỉnh đã vượt qua kiểm tra 100% ràng buộc tổng và khác nhau đôi một.'
        if kind == 'UNSAT':
            return 'Không tồn tại cách điền số nào thỏa mãn đồng thời mọi ràng buộc của bảng.'
        return 'Đã chạm giới hạn số nút duyệt tối đa.'

    def draw_solver(self, step):
        x = 650
        self.text('ĐIỀU KHIỂN BỘ GIẢI CSP', x, 110, 20, bold=True)
        self.button(x, 146, 218, 34, 'Đổi bảng mẫu', 'NEXT_MAP')
        self.button(
            x + 228,
            146,
            234,
            34,
            'Dừng & Sửa' if self.busy or self.auto_play else 'Sửa bảng',
            'EDIT',
            accent=True,
        )
        self.button(x, 190, 462, 34, self.MODE_NAMES[self.mode_idx], 'NEXT_MODE')
        self.button(x, 236, 146, 35, 'Tạm dừng' if self.auto_play else 'Tự chạy', 'PLAY', step is not None, True)
        self.button(x + 156, 236, 146, 35, 'Bước trước', 'PREV', step is not None)
        self.button(x + 312, 236, 150, 35, 'Bước tiếp', 'NEXT', step is not None)
        self.button(x, 279, 146, 31, 'Đặt lại', 'RESET', step is not None)
        self.button(x + 156, 279, 146, 31, 'Bước cuối', 'END', step is not None)
        self.button(x + 312, 279, 150, 31, 'Giải lại', 'SOLVE')
        self.text('Tốc độ phát', x, 320, 14, self.MUTED)
        pygame.draw.rect(self.screen, (71, 85, 105), self.speed_slider, border_radius=4)
        frac = (1200 - self.step_delay_ms) / 1175
        pygame.draw.circle(
            self.screen,
            (96, 165, 250),
            (self.speed_slider.x + round(self.speed_slider.w * frac), self.speed_slider.centery),
            8,
        )
        self.text(f'{self.step_delay_ms} ms/bước', x, 342, 13, self.MUTED)
        if not step:
            self.text('Đang giải...' if self.busy else 'Chưa có kết quả.', x, 392, 20, bold=True)
            return
        total = len(self.result.steps_trace)
        self.text(f'Bước {self.step_idx + 1:,} / {total:,}', x, 376, 19, bold=True)
        pygame.draw.rect(self.screen, (71, 85, 105), (x, 406, 462, 6), border_radius=3)
        pygame.draw.rect(
            self.screen,
            (96, 165, 250),
            (x, 406, max(1, round(462 * (self.step_idx + 1) / total)), 6),
            border_radius=3,
        )
        kind = step.step_type
        color = (
            self.GREEN
            if kind == 'SOLVED'
            else self.RED
            if kind in ('UNSAT', 'FAILURE', 'REJECT')
            else self.ORANGE
            if kind in ('BACKTRACK', 'NODE_LIMIT', 'PRUNE')
            else self.TEXT
        )
        self.text(self.EVENTS.get(kind, kind), x, 426, 21, color, True)
        self.wrap(self.step_message(step), x, 456, 462, 16, max_lines=3)
        stats_cards = [
            ('Ô đã gán', f'{len(step.assignment)}/{len(self.csp.variables)}'),
            ('Số nút đã thử', step.nodes_so_far),
            ('Số lần quay lui', step.backtracks_so_far),
            ('Thời gian giải', f'{self.result.elapsed_ms:.2f} ms'),
        ]
        for i, (label, value) in enumerate(stats_cards):
            xx = x + (i % 2) * 234
            yy = 526 + (i // 2) * 62
            pygame.draw.rect(self.screen, (15, 23, 42), (xx, yy, 224, 53), border_radius=6)
            self.text(label, xx + 10, yy + 5, 13, self.MUTED)
            self.text(value, xx + 10, yy + 23, 19, bold=True)
        if self.result.trace_truncated:
            self.text('Đã lược bớt một số bước trung gian do giới hạn bộ nhớ lịch sử.', x, 657, 13, self.ORANGE, max_width=462)

    def render_frame(self):
        self.screen.fill(self.BG)
        self.buttons = []
        self.fields = {}
        self.text('TRÒ CHƠI KAKURO  |  TRÍ TUỆ NHÂN TẠO', 24, 15, 24, bold=True)
        self.text('Bài toán Thỏa mãn Ràng buộc (CSP) - Nhiệm vụ 3', 25, 47, 15, self.MUTED)
        rows, cols = (self.editor.rows, self.editor.cols) if self.editing else (self.csp.rows, self.csp.cols)
        board_label = f'Bảng tùy chỉnh {rows}x{cols}' if self.custom else self.csp.name
        mode_label = 'Chế độ Soạn thảo' if self.editing else 'Chế độ Giải'
        self.text(f'{board_label}  |  {mode_label}', 25, 79, 17, bold=True, max_width=860)
        top_btn_label = (
            'Quay lại Sửa'
            if self.bulk is not None
            else 'Giải bảng này'
            if self.editing
            else 'Dừng & Sửa'
            if self.busy or self.auto_play
            else 'Sửa bảng'
        )
        top_btn_act = 'BULK_CANCEL' if self.bulk is not None else 'SOLVE' if self.editing else 'EDIT'
        self.button(908, 25, 204, 35, top_btn_label, top_btn_act, accent=True)
        pygame.draw.rect(self.screen, self.PANEL, (634, 94, 500, 584), border_radius=12)
        step = None if self.editing or self.result is None else self.result.steps_trace[self.step_idx]
        self.draw_grid(step)
        if self.bulk is not None:
            self.draw_bulk()
        elif self.editing:
            self.draw_editor()
        else:
            self.draw_solver(step)
        self.text(
            'Tím (G): số cho trước  |  Xanh dương: ô đang xét  |  Đỏ gạch ngang: ứng viên bị loại  |  Cam: quay lui',
            24,
            687,
            13,
            self.MUTED,
            max_width=1100,
        )
        self.wrap(self.notice, 24, 709, 1112, 12, self.RED if self.notice_error else self.MUTED, max_lines=2)
        self.window.blit(pygame.transform.smoothscale(self.screen, self.window.get_size()), (0, 0))
        pygame.display.flip()

    def commit_field(self):
        if self.field is None:
            return
        field, value = self.field, self.buffer.strip()
        self.field = None
        pygame.key.stop_text_input()
        if field.startswith('row:'):
            self.bulk[int(field.split(':')[1])] = value
            return
        if field == 'path':
            self.path_text = value or 'custom_board.json'
            return
        if not value:
            return
        if not value.isdecimal():
            raise ValueError('Vui lòng nhập số nguyên rồi nhấn Enter.')
        if field == 'given':
            self.editor.set_given(self.selected, int(value))
        else:
            self.editor.set_clue(self.selected, field, int(value))
        self.custom = True
        self.notify('Đã cập nhật giá trị. Nhấn GIẢI BẢNG HIỆN TẠI để tính lại.')

    def get_path(self):
        path = Path(self.path_text).expanduser()
        if not path.is_absolute():
            path = self.maps_dir / 'custom' / path
        if path.suffix.lower() != '.json':
            path = path.with_suffix('.json')
        return path

    def action(self, a):
        if self.busy and a != "EDIT":
            return
        self.commit_field()
        if a in ('NEXT_MAP', 'RESTORE'):
            if a == 'NEXT_MAP':
                self.map_idx = (self.map_idx + 1) % len(self.map_files)
            if self.editing:
                self.editor = BoardEditor(KakuroCSP.from_json(self.map_files[self.map_idx]))
                self.selected = None
                self.custom = False
            else:
                self.csp = KakuroCSP.from_json(self.map_files[self.map_idx])
                self.editor = BoardEditor(self.csp)
                self.custom = False
                self.start_solve()
            self.notify('Đã nạp bảng mẫu.')
        elif a == 'EDIT':
            self.cancel_event.set()
            self.jobs = Queue()
            self.busy = False
            self.auto_play = False
            self.editing = True
            self.editor = BoardEditor(self.csp)
            self.selected = None
            self.result = None
            self.step_idx = 0
            self.bulk = None
            self.notify('Đã chuyển sang chế độ Soạn thảo. Chỉnh sửa tùy ý rồi nhấn Giải bảng hiện tại.')
        elif a == 'BULK':
            self.bulk = self.editor.bulk_rows()
            self.selected = None
            self.notify('Chỉnh sửa các dòng bên trên rồi nhấn ÁP DỤNG TOÀN BỘ.')
        elif a == 'BULK_CANCEL':
            self.bulk = None
            self.notify('Đã hủy thay đổi sửa nhanh.')
        elif a == 'BULK_CLEAR':
            self.bulk = [
                ' '.join('0' if t in '123456789' and len(t) == 1 else t for t in row.split())
                for row in self.bulk
            ]
        elif a == 'BULK_APPLY':
            self.editor.apply_bulk_rows(self.bulk)
            self.bulk = None
            self.custom = True
            self.notify('Đã áp dụng toàn bộ thay đổi. Nhấn Kiểm tra hợp lệ hoặc Giải bảng.')
        elif a == 'RANDOM':
            self.editor.randomize_clues()
            self.custom = True
            self.selected = None
            self.notify('Đã sinh bộ tổng gợi ý mới đảm bảo có nghiệm (đã xóa các số cho trước cũ).')
        elif a == 'NEXT_MODE':
            self.mode_idx = (self.mode_idx + 1) % len(self.MODES)
            if not self.editing:
                self.start_solve()
        elif a == 'SIZE':
            self.size = 3 + (self.size - 3 + 1) % 7
        elif a == 'NEW':
            self.editor = BoardEditor.new(self.size)
            self.selected = None
            self.custom = True
            self.notify('Đã tạo bảng mới. Bạn có thể sửa từng ô và các tổng gợi ý.')
        elif a in ('WHITE', 'BLACK'):
            self.editor.set_cell_type(self.selected, a == 'WHITE')
            self.custom = True
            self.notify('Đã đổi loại ô và tự động đồng bộ lại hướng gợi ý.')
        elif a == 'CLEAR_GIVEN':
            self.editor.set_given(self.selected, 0)
            self.custom = True
        elif a == 'CLEAR_ALL':
            self.editor.givens.clear()
            self.custom = True
            self.notify('Đã xóa toàn bộ các chữ số cho trước.')
        elif a == 'VALIDATE':
            self.editor.validate()
            self.notify('Cấu trúc lưới và cận tổng hợp lệ! Nhấn Giải bảng để tìm nghiệm.')
        elif a == 'SAVE':
            path = self.get_path()
            self.editor.save(path)
            self.notify('Đã lưu file: ' + str(path))
        elif a == 'LOAD':
            path = self.get_path()
            editor = BoardEditor.load(path)
            if not (3 <= editor.rows <= 9 and 3 <= editor.cols <= 9):
                raise ValueError('Giao diện chỉ hỗ trợ bảng từ 3 đến 9 hàng và cột.')
            self.editor = editor
            self.selected = None
            self.custom = True
            self.notify('Đã nạp file: ' + str(path))
        elif a == 'SOLVE':
            self.start_solve()
        elif self.result:
            end = len(self.result.steps_trace) - 1
            if a == 'PLAY':
                if self.step_idx == end:
                    self.step_idx = 0
                self.auto_play = not self.auto_play
                self.last_tick = pygame.time.get_ticks()
            else:
                self.auto_play = False
                if a == 'PREV':
                    self.step_idx = max(0, self.step_idx - 1)
                elif a == 'NEXT':
                    self.step_idx = min(end, self.step_idx + 1)
                elif a == 'RESET':
                    self.step_idx = 0
                elif a == 'END':
                    self.step_idx = end

    def click(self, pos):
        if self.busy:
            for b in self.buttons:
                if b.enabled and b.action_id == "EDIT" and b.rect.collidepoint(pos):
                    self.action("EDIT")
                    return
            return
        for key, rect in self.fields.items():
            if rect.collidepoint(pos):
                if self.field == key:
                    return
                self.commit_field()
                self.field = key
                self.buffer = (
                    self.bulk[int(key.split(':')[1])]
                    if key.startswith('row:')
                    else self.path_text
                    if key == 'path'
                    else ''
                )
                pygame.key.start_text_input()
                return
        for b in self.buttons:
            if b.rect.collidepoint(pos) and b.enabled:
                self.action(b.action_id)
                return
        self.commit_field()
        if self.bulk is not None:
            return
        if self.editing:
            for r in range(self.editor.rows):
                for c in range(self.editor.cols):
                    if self.cell_rect(r, c).collidepoint(pos):
                        self.selected = (r, c)
                        return
        elif self.speed_slider.inflate(20, 20).collidepoint(pos):
            self.drag_speed = True
            self.set_speed(pos[0])

    def set_speed(self, x):
        frac = max(0, min(1, (x - self.speed_slider.x) / self.speed_slider.w))
        self.step_delay_ms = round(1200 - 1175 * frac)

    def logical_pos(self, pos):
        w, h = self.window.get_size()
        return (int(pos[0] * self.WINDOW_W / max(w, 1)), int(pos[1] * self.WINDOW_H / max(h, 1)))

    def run(self):
        running = True
        while running:
            self.poll()
            for ev in pygame.event.get():
                try:
                    if ev.type == pygame.QUIT:
                        self.cancel_event.set()
                        running = False
                    elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        self.click(self.logical_pos(ev.pos))
                    elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                        self.drag_speed = False
                    elif ev.type == pygame.MOUSEMOTION and self.drag_speed:
                        self.set_speed(self.logical_pos(ev.pos)[0])
                    elif ev.type == pygame.TEXTINPUT and self.field:
                        if self.field.startswith('row:'):
                            self.buffer = (self.buffer + ''.join(ch for ch in ev.text if ch in '0123456789#/ '))[:240]
                        elif self.field == 'path':
                            self.buffer = (self.buffer + ev.text)[:240]
                        elif ev.text.isascii() and ev.text.isdigit():
                            self.buffer = (self.buffer + ev.text)[:2]
                    elif ev.type == pygame.KEYDOWN:
                        if self.field:
                            if ev.key == pygame.K_RETURN or ev.key == pygame.K_KP_ENTER:
                                self.commit_field()
                            elif ev.key == pygame.K_ESCAPE:
                                self.field = None
                                pygame.key.stop_text_input()
                            elif ev.key == pygame.K_BACKSPACE:
                                self.buffer = self.buffer[:-1]
                            elif ev.key == pygame.K_a and ev.mod & pygame.KMOD_CTRL:
                                self.buffer = ''
                        elif ev.key == pygame.K_ESCAPE and not self.editing:
                            self.action('EDIT')
                        elif self.bulk is not None:
                            pass
                        elif (
                            self.editing
                            and self.selected
                            and not self.busy
                            and self.editor.grid[self.selected[0]][self.selected[1]] == 'W'
                        ):
                            if ev.unicode in '1234567890' and ev.unicode:
                                self.editor.set_given(self.selected, int(ev.unicode))
                                self.custom = True
                            elif ev.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                                self.editor.set_given(self.selected, 0)
                                self.custom = True
                        elif not self.editing and not self.busy:
                            a = {
                                pygame.K_SPACE: 'PLAY',
                                pygame.K_LEFT: 'PREV',
                                pygame.K_RIGHT: 'NEXT',
                                pygame.K_0: 'RESET',
                            }.get(ev.key)
                            if a:
                                self.action(a)
                except (ValueError, OSError, KeyError, TypeError) as exc:
                    prefix = 'Lỗi đọc/ghi file: ' if isinstance(exc, OSError) else 'Lỗi: '
                    self.notify(prefix + str(exc), True)
            if self.auto_play and self.result and pygame.time.get_ticks() - self.last_tick >= self.step_delay_ms:
                self.step_idx = min(self.step_idx + 1, len(self.result.steps_trace) - 1)
                self.last_tick = pygame.time.get_ticks()
                if self.step_idx == len(self.result.steps_trace) - 1:
                    self.auto_play = False
            self.render_frame()
            self.clock.tick(60)
        pygame.quit()

    def save_screenshot(self, path):
        self.render_frame()
        pygame.image.save(self.screen, str(path))
