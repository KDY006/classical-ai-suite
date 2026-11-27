"""Giao dien PyGame toi gian (1160x720) cho Tro choi Dau Tang tuan thu UI.md."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import pygame

from ..agents import (
    AlphaBetaAgent,
    BaseTankAgent,
    HeuristicAlphaBetaAgent,
    HeuristicMinimaxAgent,
    MinimaxAgent,
    SearchMetrics,
    discover_external_agents,
)
from ..config import (
    ACTION_LABELS_VI,
    BASE_INITIAL_HP,
    DIR_DOWN,
    DIR_LEFT,
    DIR_RIGHT,
    DIR_UP,
    FIRE,
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
    MOVE_UP,
    PLAYER_MAX,
    PLAYER_MIN,
    STAY,
    TANK_INITIAL_HP,
    WALL_INITIAL_HP,
)
from ..engine import BulletTrail, Impact, MapScenario, TankBattleEngine, get_all_scenarios


# Bang mau gioi han 3 tong chu dao theo quy uoc UI.md
BG_CANVAS = (250, 250, 250)
SURFACE = (255, 255, 255)
SURFACE_SUBTLE = (243, 244, 246)
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
class ArenaButton:
    """Mo ta hinh hoc va trang thai hien thi cua mot nut bam toi gian."""

    action_id: str
    label: str
    rect: pygame.Rect
    primary: bool = False
    active: bool = False
    dot_color: Optional[Tuple[int, int, int]] = None
    align_left: bool = False


class HumanController:
    """Bo dieu khien danh dau phe choi bang ban phim."""

    def __init__(self) -> None:
        self.name = "Người chơi (Bàn phím)"
        self.cli_name = "Nguoi choi (Ban phim)"
        self.last_metrics = SearchMetrics()


class TankBattleArenaUI:
    """Giao dien PyGame vector toi gian 2 cot cho Tro choi Dau Tang doi khang."""

    def __init__(self, initial_scenario_key: Optional[str] = None) -> None:
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("Đấu Tăng Đối Kháng | Nhiệm Vụ 2")
        self.clock = pygame.time.Clock()

        self.font_h1 = self._load_font(SANS_FONTS, 20, bold=True)
        self.font_h2 = self._load_font(SANS_FONTS, 12, bold=True)
        self.font_body = self._load_font(SANS_FONTS, 13, bold=False)
        self.font_body_bold = self._load_font(SANS_FONTS, 13, bold=True)
        self.font_caption = self._load_font(SANS_FONTS, 12, bold=False)
        self.font_mono = self._load_font(MONO_FONTS, 12, bold=False)
        self.font_mono_bold = self._load_font(MONO_FONTS, 12, bold=True)
        self.font_coord = self._load_font(MONO_FONTS, 11, bold=False)

        self.scenarios: List[MapScenario] = get_all_scenarios()
        self.scenario_idx: int = 0
        if initial_scenario_key is not None:
            for idx, sc in enumerate(self.scenarios):
                if sc.key == initial_scenario_key:
                    self.scenario_idx = idx
                    break

        self.external_count: int = 0
        self.controllers: List[object] = self._build_controllers()
        self.max_ctrl_idx: int = 0
        self.min_ctrl_idx: int = 1 if len(self.controllers) > 1 else 0
        self.state = self.scenarios[self.scenario_idx].builder()

        self.auto_play: bool = False
        self.step_delay_ms: int = 260
        self.last_step_tick: int = 0
        self._dragging_slider: bool = False

        self.anim_frames: List[List[Tuple[int, int, int, str]]] = []
        self.anim_tick: int = 0
        self.last_trails: List[BulletTrail] = []
        self.last_impacts: List[Impact] = []
        self.last_event_text: str = "Nhấn Tự chạy hoặc Từng bước để quan sát trận đấu đối kháng."

        self.slider_rect = pygame.Rect(SIDEBAR_X + 24, 340, SIDEBAR_W - 48, 16)
        self._board_rect = pygame.Rect(0, 0, 0, 0)
        self._cell_px: int = 48
        self.buttons: List[ArenaButton] = []
        self._rebuild_buttons()

    @staticmethod
    def _load_font(candidates: Tuple[str, ...], size: int, bold: bool = False) -> pygame.font.Font:
        """Tim font he thong co san ho tro day du tieng Viet co dau."""
        for family in candidates:
            path = pygame.font.match_font(family, bold=bold)
            if path:
                return pygame.font.Font(path, size)
        return pygame.font.SysFont(",".join(candidates), size, bold=bold)

    def _build_controllers(self) -> List[object]:
        controllers: List[object] = [
            HeuristicAlphaBetaAgent(max_depth=4, name="Heuristic Alpha-Beta (sâu 4)"),
            HeuristicMinimaxAgent(max_depth=3, name="Heuristic Minimax (sâu 3)"),
            AlphaBetaAgent(max_ply_cap=6, name="Alpha-Beta thuần (cắt 6)"),
            MinimaxAgent(max_ply_cap=5, name="Minimax thuần (cắt 5)"),
            HumanController(),
        ]
        externals = discover_external_agents()
        self.external_count = len(externals)
        controllers.extend(externals)
        return controllers

    def _active_controller(self, player_id: int) -> object:
        idx = self.max_ctrl_idx if player_id == PLAYER_MAX else self.min_ctrl_idx
        return self.controllers[idx % len(self.controllers)]

    def _rebuild_buttons(self) -> None:
        x0 = SIDEBAR_X + 24
        w = SIDEBAR_W - 48
        scen = self.scenarios[self.scenario_idx]
        max_name = getattr(self._active_controller(PLAYER_MAX), "name", "MAX")
        min_name = getattr(self._active_controller(PLAYER_MIN), "name", "MIN")

        play_label = "Tạm dừng" if self.auto_play else "Tự chạy"
        b1_w = 132
        b2_w = 104
        b3_w = w - b1_w - b2_w - 16

        self.buttons = [
            ArenaButton("CYCLE_MAP", f"Bản đồ: {scen.title}", pygame.Rect(x0, 90, w, 32), align_left=True),
            ArenaButton(
                "CYCLE_MAX",
                f"MAX: {max_name}",
                pygame.Rect(x0, 128, w, 32),
                dot_color=ACCENT_PRIMARY,
                align_left=True,
            ),
            ArenaButton(
                "CYCLE_MIN",
                f"MIN: {min_name}",
                pygame.Rect(x0, 166, w, 32),
                dot_color=ACCENT_ALERT,
                align_left=True,
            ),
            ArenaButton(
                "RELOAD_EXT",
                f"Nạp lại Bot nhóm ngoài ({self.external_count} bot)",
                pygame.Rect(x0, 204, w, 28),
            ),
            ArenaButton(
                "TOGGLE_PLAY",
                play_label,
                pygame.Rect(x0, 272, b1_w, 34),
                primary=True,
            ),
            ArenaButton(
                "STEP_ONCE",
                "Từng bước",
                pygame.Rect(x0 + b1_w + 8, 272, b2_w, 34),
            ),
            ArenaButton(
                "RESET",
                "Đặt lại",
                pygame.Rect(x0 + b1_w + b2_w + 16, 272, b3_w, 34),
            ),
        ]

    def reset_match(self) -> None:
        """Khoi dong lai van dau tren kich ban ban do dang chon."""
        self.state = self.scenarios[self.scenario_idx].builder()
        self.auto_play = False
        self.anim_frames.clear()
        self.last_trails.clear()
        self.last_impacts.clear()
        for ctrl in self.controllers:
            if hasattr(ctrl, "last_metrics"):
                ctrl.last_metrics = SearchMetrics()
        self.last_event_text = f"Đã đặt lại bản đồ {self.scenarios[self.scenario_idx].title}."
        self._rebuild_buttons()

    def execute_turn(self, forced_action: Optional[str] = None) -> None:
        """Thuc thi dung 1 luot cho nguoi choi hien tai va cap nhat su kien dan."""
        if self.state.is_terminal():
            self.auto_play = False
            self._rebuild_buttons()
            return

        player_id = self.state.current_player
        controller = self._active_controller(player_id)
        if isinstance(controller, HumanController):
            if forced_action is None:
                return
            action = forced_action
            controller.last_metrics = SearchMetrics(chosen_action=action, depth_reached=1, explored_states=1)
        else:
            if not isinstance(controller, BaseTankAgent):
                raise TypeError(f"Bo dieu khien khong ho tro: {type(controller).__name__}")
            action = controller.safe_choose_action(self.state)

        next_state, event = TankBattleEngine.step_with_events(self.state, action)
        self.state = next_state
        self.last_trails = list(event.bullet_trails)
        self.last_impacts = list(event.impacts)
        self.anim_frames = list(event.bullet_frames)
        self.anim_tick = pygame.time.get_ticks()

        metrics = getattr(controller, "last_metrics", SearchMetrics())
        side = "MAX" if player_id == PLAYER_MAX else "MIN"
        act_vi = ACTION_LABELS_VI.get(action, action)
        hit_note = ""
        if event.impacts:
            impact_map = {
                "TANK": "trúng xe tăng",
                "BASE": "trúng căn cứ",
                "WALL": "trúng tường gạch",
                "STEEL": "chạm tường thép",
                "BULLET": "triệt tiêu đạn",
            }
            hit_note = f" — {impact_map.get(event.impacts[-1][2], 'va chạm')}"
        self.last_event_text = (
            f"Lượt {self.state.ply}: Phe {side} chọn {act_vi} "
            f"({metrics.explored_states:,} nút, {metrics.elapsed_ms:.1f} ms){hit_note}."
        )
        if self.state.is_terminal():
            self.auto_play = False
            self._rebuild_buttons()

    def _find_controller_index(self, previous: object) -> int:
        prev_name = getattr(previous, "name", None)
        for idx, ctrl in enumerate(self.controllers):
            if ctrl is previous or (prev_name is not None and getattr(ctrl, "name", None) == prev_name):
                return idx
        return 0

    def _handle_button(self, action_id: str) -> None:
        if action_id == "CYCLE_MAP":
            self.scenario_idx = (self.scenario_idx + 1) % len(self.scenarios)
            self.reset_match()
        elif action_id == "CYCLE_MAX":
            self.max_ctrl_idx = (self.max_ctrl_idx + 1) % len(self.controllers)
            self._rebuild_buttons()
        elif action_id == "CYCLE_MIN":
            self.min_ctrl_idx = (self.min_ctrl_idx + 1) % len(self.controllers)
            self._rebuild_buttons()
        elif action_id == "TOGGLE_PLAY":
            if self.state.is_terminal():
                self.reset_match()
            self.auto_play = not self.auto_play
            self.last_step_tick = pygame.time.get_ticks()
            self._rebuild_buttons()
        elif action_id == "STEP_ONCE":
            self.auto_play = False
            self.execute_turn()
            self._rebuild_buttons()
        elif action_id == "RESET":
            self.reset_match()
        elif action_id == "RELOAD_EXT":
            prev_max = self._active_controller(PLAYER_MAX)
            prev_min = self._active_controller(PLAYER_MIN)
            self.controllers = self._build_controllers()
            self.max_ctrl_idx = self._find_controller_index(prev_max)
            self.min_ctrl_idx = self._find_controller_index(prev_min)
            self.last_event_text = f"Đã quét lại thư mục external_agents/: phát hiện {self.external_count} bot."
            self._rebuild_buttons()

    def _update_slider_from_x(self, mouse_x: int) -> None:
        ratio = (mouse_x - self.slider_rect.left) / max(1, self.slider_rect.width)
        ratio = max(0.0, min(1.0, ratio))
        # Keo sang phai nhanh hon (tu 800ms giam xuong 60ms)
        self.step_delay_ms = int(round(800 - ratio * 740))

    def _handle_human_key(self, key: int) -> None:
        if not isinstance(self._active_controller(self.state.current_player), HumanController):
            return
        key_map = {
            pygame.K_w: MOVE_UP,
            pygame.K_UP: MOVE_UP,
            pygame.K_s: MOVE_DOWN,
            pygame.K_DOWN: MOVE_DOWN,
            pygame.K_a: MOVE_LEFT,
            pygame.K_LEFT: MOVE_LEFT,
            pygame.K_d: MOVE_RIGHT,
            pygame.K_RIGHT: MOVE_RIGHT,
            pygame.K_SPACE: FIRE,
            pygame.K_RETURN: STAY,
        }
        action = key_map.get(key)
        if action is not None:
            self.execute_turn(forced_action=action)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Xu ly su kien chuot va ban phim; tra ve False khi dong cua so."""
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if isinstance(self._active_controller(self.state.current_player), HumanController):
                self._handle_human_key(event.key)
            else:
                if event.key == pygame.K_SPACE:
                    self._handle_button("TOGGLE_PLAY")
                elif event.key == pygame.K_RIGHT:
                    self._handle_button("STEP_ONCE")
                elif event.key == pygame.K_r:
                    self._handle_button("RESET")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.slider_rect.inflate(8, 12).collidepoint(event.pos):
                self._dragging_slider = True
                self._update_slider_from_x(event.pos[0])
            else:
                for btn in self.buttons:
                    if btn.rect.collidepoint(event.pos):
                        self._handle_button(btn.action_id)
                        break
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging_slider = False
        elif event.type == pygame.MOUSEMOTION and self._dragging_slider:
            self._update_slider_from_x(event.pos[0])
        return True

    def _cell_rect(self, row: int, col: int) -> pygame.Rect:
        return pygame.Rect(
            self._board_rect.x + col * self._cell_px,
            self._board_rect.y + row * self._cell_px,
            self._cell_px,
            self._cell_px,
        )

    def _draw_dashed_line(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        color: Tuple[int, int, int],
        width: int = 2,
        dash_len: float = 6.0,
        gap_len: float = 5.0,
    ) -> None:
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist = (dx * dx + dy * dy) ** 0.5
        if dist < 1e-6:
            return
        ux, uy = dx / dist, dy / dist
        pos = 0.0
        while pos < dist:
            seg = min(pos + dash_len, dist)
            p1 = (int(round(start[0] + ux * pos)), int(round(start[1] + uy * pos)))
            p2 = (int(round(start[0] + ux * seg)), int(round(start[1] + uy * seg)))
            pygame.draw.line(self.screen, color, p1, p2, width)
            pos += dash_len + gap_len

    def _draw_clipped_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: Tuple[int, int, int],
        pos: Tuple[int, int],
        max_width: int,
    ) -> None:
        shown = text
        while shown and font.size(shown)[0] > max_width:
            if shown.endswith("..."):
                shown = shown[:-4] + "..."
            else:
                shown = shown[:-1] + "..."
        self.screen.blit(font.render(shown, True, color), pos)

    def _draw_header(self) -> None:
        pygame.draw.rect(self.screen, SURFACE, (0, 0, WINDOW_W, HEADER_H))
        pygame.draw.line(self.screen, BORDER, (0, HEADER_H - 1), (WINDOW_W, HEADER_H - 1), 1)

        title_surf = self.font_h1.render("Đấu Tăng Đối Kháng", True, TEXT_PRIMARY)
        self.screen.blit(title_surf, (28, (HEADER_H - title_surf.get_height()) // 2))

        scen = self.scenarios[self.scenario_idx]
        sub_text = f"Nhiệm vụ 2  |  {scen.title}  |  Lượt {self.state.ply}/{self.state.max_plies}"
        sub_surf = self.font_caption.render(sub_text, True, TEXT_SECONDARY)
        self.screen.blit(
            sub_surf,
            (28 + title_surf.get_width() + 18, (HEADER_H - sub_surf.get_height()) // 2 + 2),
        )

        winner = self.state.winner()
        if winner == PLAYER_MAX:
            pill_text, bg, fg, bd = "Phe MAX chiến thắng", ACCENT_PRIMARY, SURFACE, ACCENT_PRIMARY
        elif winner == PLAYER_MIN:
            pill_text, bg, fg, bd = "Phe MIN chiến thắng", ACCENT_ALERT, SURFACE, ACCENT_ALERT
        elif winner == 0:
            pill_text, bg, fg, bd = "Kết quả: Hòa trận", SURFACE_SUBTLE, TEXT_PRIMARY, BORDER_STRONG
        elif self.state.current_player == PLAYER_MAX:
            pill_text, bg, fg, bd = "Lượt phe MAX", ACCENT_PRIMARY_SOFT, ACCENT_PRIMARY, ACCENT_PRIMARY
        else:
            pill_text, bg, fg, bd = "Lượt phe MIN", ACCENT_ALERT_SOFT, ACCENT_ALERT, ACCENT_ALERT

        st_surf = self.font_caption.render(pill_text, True, fg)
        pill_w = st_surf.get_width() + 24
        pill_rect = pygame.Rect(WINDOW_W - 28 - pill_w, (HEADER_H - 26) // 2, pill_w, 26)
        pygame.draw.rect(self.screen, bg, pill_rect, border_radius=13)
        pygame.draw.rect(self.screen, bd, pill_rect, width=1, border_radius=13)
        self.screen.blit(
            st_surf,
            (pill_rect.centerx - st_surf.get_width() // 2, pill_rect.centery - st_surf.get_height() // 2),
        )

    def _draw_arena(self) -> None:
        pygame.draw.rect(self.screen, BG_CANVAS, (0, HEADER_H, SIDEBAR_X, WINDOW_H - HEADER_H))

        rows, cols = self.state.rows, self.state.cols
        max_side = 540
        self._cell_px = max(24, min(max_side // cols, max_side // rows))
        board_w = self._cell_px * cols
        board_h = self._cell_px * rows

        origin_x = (SIDEBAR_X - board_w) // 2 + 10
        origin_y = HEADER_H + (WINDOW_H - HEADER_H - board_h - 30) // 2 + 8
        self._board_rect = pygame.Rect(origin_x, origin_y, board_w, board_h)

        # Nen sang sach va luoi chia o manh 1px
        pygame.draw.rect(self.screen, SURFACE, self._board_rect)
        for r in range(rows):
            for c in range(cols):
                rect = self._cell_rect(r, c)
                pygame.draw.rect(self.screen, BORDER, rect, width=1)

        # Toa do hang va cot manh
        for c in range(cols):
            lbl = self.font_coord.render(str(c), True, TEXT_SECONDARY)
            cx = origin_x + c * self._cell_px + self._cell_px // 2 - lbl.get_width() // 2
            self.screen.blit(lbl, (cx, origin_y - 18))
        for r in range(rows):
            lbl = self.font_coord.render(str(r), True, TEXT_SECONDARY)
            cy = origin_y + r * self._cell_px + self._cell_px // 2 - lbl.get_height() // 2
            self.screen.blit(lbl, (origin_x - lbl.get_width() - 8, cy))

        self._draw_walls()
        self._draw_bases()
        self._draw_bullet_trails_and_projectiles()
        self._draw_tanks()
        self._draw_impacts()

        pygame.draw.rect(self.screen, BORDER_STRONG, self._board_rect, width=1)

        # Dong ghi chu 1 dong ben duoi dau truong
        is_human = isinstance(self._active_controller(self.state.current_player), HumanController)
        caption = (
            "Lượt Người chơi: WASD / Mũi tên để đi  |  Space để bắn  |  Enter để chờ"
            if (is_human and not self.state.is_terminal())
            else self.last_event_text
        )
        cap_surf = self.font_caption.render(caption, True, TEXT_SECONDARY)
        self.screen.blit(
            cap_surf,
            (SIDEBAR_X // 2 - cap_surf.get_width() // 2, self._board_rect.bottom + 18),
        )

    def _draw_walls(self) -> None:
        cell = self._cell_px
        pad = max(4, cell // 10)

        # Tuong thep bat tu: khoi muc toi gian co net cheo manh ben trong
        for r, c in self.state.steel_walls:
            rect = self._cell_rect(r, c).inflate(-pad * 2, -pad * 2)
            pygame.draw.rect(self.screen, TEXT_PRIMARY, rect, border_radius=4)
            inner = rect.inflate(-8, -8)
            if inner.width > 4 and inner.height > 4:
                pygame.draw.line(self.screen, TEXT_SECONDARY, inner.topleft, inner.bottomright, 1)
                pygame.draw.line(self.screen, TEXT_SECONDARY, inner.topright, inner.bottomleft, 1)

        # Tuong gach (3 HP): o xam nhe kem 3 thanh nac HP (3 -> 2 -> 1)
        for (r, c), wall in self.state.brick_walls.items():
            if wall.hp <= 0:
                continue
            rect = self._cell_rect(r, c).inflate(-pad * 2, -pad * 2)
            pygame.draw.rect(self.screen, SURFACE_SUBTLE, rect, border_radius=4)
            pygame.draw.rect(self.screen, BORDER_STRONG, rect, width=1, border_radius=4)

            # Net gach ngang nhe the hien ket cau tuong gach
            mid_y = rect.y + int(rect.height * 0.44)
            pygame.draw.line(self.screen, BORDER, (rect.left + 4, mid_y), (rect.right - 4, mid_y), 1)

            # 3 nac HP ro rang o phia duoi o tuong
            seg_gap = 3
            seg_total = rect.width - 10
            seg_w = max(4, (seg_total - seg_gap * (WALL_INITIAL_HP - 1)) // WALL_INITIAL_HP)
            seg_y = rect.bottom - 7
            for idx in range(WALL_INITIAL_HP):
                sx = rect.left + 5 + idx * (seg_w + seg_gap)
                seg_color = TEXT_PRIMARY if idx < wall.hp else BORDER
                pygame.draw.rect(self.screen, seg_color, (sx, seg_y, seg_w, 3), border_radius=1)

            hp_lbl = self.font_coord.render(str(wall.hp), True, TEXT_SECONDARY)
            self.screen.blit(hp_lbl, (rect.right - hp_lbl.get_width() - 4, rect.top + 2))

    def _draw_bases(self) -> None:
        cell = self._cell_px
        for pid, base in self.state.bases.items():
            rect = self._cell_rect(base.row, base.col)
            color = ACCENT_PRIMARY if pid == PLAYER_MAX else ACCENT_ALERT
            soft = ACCENT_PRIMARY_SOFT if pid == PLAYER_MAX else ACCENT_ALERT_SOFT
            pygame.draw.rect(self.screen, soft, rect.inflate(-2, -2))

            if base.hp <= 0:
                inner = rect.inflate(-cell // 4, -cell // 4)
                pygame.draw.line(self.screen, ACCENT_ALERT, inner.topleft, inner.bottomright, 3)
                pygame.draw.line(self.screen, ACCENT_ALERT, inner.topright, inner.bottomleft, 3)
                continue

            # Bieu tuong phao dai toi gian: khung vuong + 4 goc thap + hinh thoi trung tam
            fort = rect.inflate(-max(10, cell // 4), -max(12, cell // 4))
            fort.y -= 2
            pygame.draw.rect(self.screen, SURFACE, fort, border_radius=4)
            pygame.draw.rect(self.screen, color, fort, width=2, border_radius=4)
            cx, cy = fort.center
            d = max(5, min(fort.width, fort.height) // 4)
            diamond = [(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)]
            pygame.draw.polygon(self.screen, color, diamond)

            # Thanh HP manh cua can cu
            bar = pygame.Rect(rect.left + 6, rect.bottom - 7, max(8, cell - 12), 3)
            self._draw_hp_bar(bar, base.hp, BASE_INITIAL_HP, color)

    def _draw_tanks(self) -> None:
        cell = self._cell_px
        for pid, tank in self.state.tanks.items():
            if tank.hp <= 0:
                continue
            rect = self._cell_rect(tank.row, tank.col)
            color = ACCENT_PRIMARY if pid == PLAYER_MAX else ACCENT_ALERT

            # Vien 2px danh dau xe dang toi luot di
            if not self.state.is_terminal() and self.state.current_player == pid:
                pygame.draw.rect(self.screen, TEXT_PRIMARY, rect.inflate(-2, -2), width=2)

            cx, cy = rect.center
            cy -= 2
            body_s = max(14, int(cell * 0.48))
            body = pygame.Rect(cx - body_s // 2, cy - body_s // 2, body_s, body_s)

            # Hai dai xich ben hong toi gian
            tread_t = max(3, body_s // 5)
            if tank.facing in (DIR_UP, DIR_DOWN):
                pygame.draw.rect(self.screen, TEXT_PRIMARY, (body.left - tread_t + 1, body.top + 2, tread_t, body.height - 4), border_radius=2)
                pygame.draw.rect(self.screen, TEXT_PRIMARY, (body.right - 1, body.top + 2, tread_t, body.height - 4), border_radius=2)
            else:
                pygame.draw.rect(self.screen, TEXT_PRIMARY, (body.left + 2, body.top - tread_t + 1, body.width - 4, tread_t), border_radius=2)
                pygame.draw.rect(self.screen, TEXT_PRIMARY, (body.left + 2, body.bottom - 1, body.width - 4, tread_t), border_radius=2)

            # Than xe tang va thap phao
            pygame.draw.rect(self.screen, color, body, border_radius=5)
            turret_r = max(4, body_s // 4)
            pygame.draw.circle(self.screen, SURFACE, (cx, cy), turret_r)
            pygame.draw.circle(self.screen, color, (cx, cy), turret_r, 2)

            # Nong phao xoay theo 4 huong ro net
            barrel_len = max(10, int(cell * 0.38))
            barrel_w = max(3, cell // 14)
            end_map = {
                DIR_UP: (cx, cy - barrel_len),
                DIR_DOWN: (cx, cy + barrel_len),
                DIR_LEFT: (cx - barrel_len, cy),
                DIR_RIGHT: (cx + barrel_len, cy),
            }
            pygame.draw.line(self.screen, TEXT_PRIMARY, (cx, cy), end_map[tank.facing], barrel_w)

            # Thanh HP manh duoi o xe tang
            bar = pygame.Rect(rect.left + 6, rect.bottom - 7, max(8, cell - 12), 3)
            self._draw_hp_bar(bar, tank.hp, TANK_INITIAL_HP, color)

    def _draw_bullet_trails_and_projectiles(self) -> None:
        # Vet duong dan net dut cho luot vua dien ra
        for owner_id, pts in self.last_trails:
            color = ACCENT_PRIMARY if owner_id == PLAYER_MAX else ACCENT_ALERT
            if len(pts) >= 2:
                p_start = self._cell_rect(*pts[0]).center
                p_end = self._cell_rect(*pts[-1]).center
                self._draw_dashed_line(p_start, p_end, color, width=2)

        # Hoat anh dan bay tung o mot (55 ms / khung)
        bullets = [(b.owner_id, b.row, b.col, b.direction) for b in self.state.bullets]
        if self.anim_frames:
            frame_idx = (pygame.time.get_ticks() - self.anim_tick) // 55
            if frame_idx < len(self.anim_frames):
                bullets = self.anim_frames[frame_idx]
            else:
                self.anim_frames.clear()

        for owner_id, row, col, direction in bullets:
            color = ACCENT_PRIMARY if owner_id == PLAYER_MAX else ACCENT_ALERT
            cx, cy = self._cell_rect(row, col).center
            r = max(4, self._cell_px // 11)
            pygame.draw.circle(self.screen, color, (cx, cy), r)
            pygame.draw.circle(self.screen, SURFACE, (cx, cy), max(1, r // 2))

    def _draw_impacts(self) -> None:
        for row, col, impact_type in self.last_impacts:
            center = self._cell_rect(row, col).center
            color = ACCENT_ALERT if impact_type in ("TANK", "BASE", "WALL") else TEXT_PRIMARY
            r1 = max(7, self._cell_px // 5)
            r2 = max(11, self._cell_px // 3)
            pygame.draw.circle(self.screen, color, center, r1, width=2)
            pygame.draw.circle(self.screen, color, center, r2, width=1)

    def _draw_hp_bar(
        self,
        rect: pygame.Rect,
        current: int,
        maximum: int,
        color: Tuple[int, int, int],
    ) -> None:
        pygame.draw.rect(self.screen, BORDER, rect, border_radius=2)
        ratio = max(0.0, min(1.0, current / maximum)) if maximum else 0.0
        fill_w = int(round(rect.width * ratio))
        if fill_w > 0:
            pygame.draw.rect(self.screen, color, (rect.x, rect.y, fill_w, rect.height), border_radius=2)

    def _draw_button(self, btn: ArenaButton, mouse_pos: Tuple[int, int]) -> None:
        hovered = btn.rect.collidepoint(mouse_pos)
        if btn.primary:
            bg = ACCENT_PRIMARY_HOVER if hovered else ACCENT_PRIMARY
            fg = SURFACE
            border = None
        else:
            bg = SURFACE_SUBTLE if hovered else SURFACE
            fg = TEXT_PRIMARY
            border = BORDER_STRONG if hovered else BORDER

        pygame.draw.rect(self.screen, bg, btn.rect, border_radius=6)
        if border is not None:
            pygame.draw.rect(self.screen, border, btn.rect, width=1, border_radius=6)

        font = self.font_body_bold if btn.primary else self.font_body
        if btn.align_left:
            tx = btn.rect.left + 12
            if btn.dot_color is not None:
                pygame.draw.circle(self.screen, btn.dot_color, (tx + 4, btn.rect.centery), 4)
                tx += 14
            self._draw_clipped_text(
                btn.label,
                font,
                fg,
                (tx, btn.rect.centery - font.get_height() // 2),
                btn.rect.right - tx - 10,
            )
        else:
            surf = font.render(btn.label, True, fg)
            self.screen.blit(
                surf,
                (btn.rect.centerx - surf.get_width() // 2, btn.rect.centery - surf.get_height() // 2),
            )

    def _draw_sidebar(self, mouse_pos: Tuple[int, int]) -> None:
        pygame.draw.rect(self.screen, SURFACE, (SIDEBAR_X, HEADER_H, SIDEBAR_W, WINDOW_H - HEADER_H))
        pygame.draw.line(self.screen, BORDER, (SIDEBAR_X, HEADER_H), (SIDEBAR_X, WINDOW_H), 1)

        x0 = SIDEBAR_X + 24
        x1 = WINDOW_W - 24
        w = x1 - x0

        # Nhom 1: Cau hinh
        self.screen.blit(self.font_h2.render("CẤU HÌNH", True, TEXT_SECONDARY), (x0, 70))
        pygame.draw.line(self.screen, BORDER, (x0, 244), (x1, 244), 1)

        # Nhom 2: Dieu khien
        self.screen.blit(self.font_h2.render("ĐIỀU KHIỂN", True, TEXT_SECONDARY), (x0, 254))
        for btn in self.buttons:
            self._draw_button(btn, mouse_pos)

        # Thanh truot toc do
        self.screen.blit(self.font_caption.render("Tốc độ trận đấu", True, TEXT_SECONDARY), (x0, 318))
        spd_surf = self.font_mono.render(f"{self.step_delay_ms} ms/lượt", True, TEXT_PRIMARY)
        self.screen.blit(spd_surf, (x1 - spd_surf.get_width(), 318))

        ty = self.slider_rect.centery
        pygame.draw.line(self.screen, BORDER, (self.slider_rect.left, ty), (self.slider_rect.right, ty), 4)
        ratio = max(0.0, min(1.0, (800 - self.step_delay_ms) / 740.0))
        knob_x = int(round(self.slider_rect.left + ratio * self.slider_rect.width))
        pygame.draw.line(self.screen, ACCENT_PRIMARY, (self.slider_rect.left, ty), (knob_x, ty), 4)
        pygame.draw.circle(self.screen, SURFACE, (knob_x, ty), 7)
        pygame.draw.circle(self.screen, ACCENT_PRIMARY, (knob_x, ty), 7, 2)

        pygame.draw.line(self.screen, BORDER, (x0, 366), (x1, 366), 1)

        # Nhom 3: Sinh luc 2 phe (2 cot song song gon gang)
        self.screen.blit(self.font_h2.render("SINH LỰC ĐƠN VỊ", True, TEXT_SECONDARY), (x0, 376))
        col_w = (w - 16) // 2
        for idx, (pid, side, color) in enumerate(((PLAYER_MAX, "MAX", ACCENT_PRIMARY), (PLAYER_MIN, "MIN", ACCENT_ALERT))):
            cx = x0 + idx * (col_w + 16)
            tank = self.state.tanks[pid]
            base = self.state.bases[pid]

            self.screen.blit(self.font_caption.render(f"Xe {side}", True, TEXT_SECONDARY), (cx, 398))
            t_lbl = self.font_mono_bold.render(f"{tank.hp}/{TANK_INITIAL_HP}", True, TEXT_PRIMARY)
            self.screen.blit(t_lbl, (cx + col_w - t_lbl.get_width(), 398))
            self._draw_hp_bar(pygame.Rect(cx, 417, col_w, 5), tank.hp, TANK_INITIAL_HP, color)

            self.screen.blit(self.font_caption.render(f"Căn cứ {side}", True, TEXT_SECONDARY), (cx, 428))
            b_lbl = self.font_mono_bold.render(f"{base.hp}/{BASE_INITIAL_HP}", True, TEXT_PRIMARY)
            self.screen.blit(b_lbl, (cx + col_w - b_lbl.get_width(), 428))
            self._draw_hp_bar(pygame.Rect(cx, 447, col_w, 5), base.hp, BASE_INITIAL_HP, color)

        pygame.draw.line(self.screen, BORDER, (x0, 464), (x1, 464), 1)

        # Thong so tim kiem cho ca 2 phe
        self.screen.blit(self.font_h2.render("THÔNG SỐ TÌM KIẾM", True, TEXT_SECONDARY), (x0, 474))
        y_cursor = 496
        for pid, side, color in ((PLAYER_MAX, "MAX", ACCENT_PRIMARY), (PLAYER_MIN, "MIN", ACCENT_ALERT)):
            ctrl = self._active_controller(pid)
            m: SearchMetrics = getattr(ctrl, "last_metrics", SearchMetrics())
            ctrl_name = getattr(ctrl, "name", side)

            # Thanh doc nhan mau 3px gon kieu Notion
            pygame.draw.rect(self.screen, color, (x0, y_cursor + 2, 3, 72), border_radius=2)
            tx = x0 + 12
            self._draw_clipped_text(f"{side} — {ctrl_name}", self.font_body_bold, TEXT_PRIMARY, (tx, y_cursor), w - 14)

            act_vi = ACTION_LABELS_VI.get(m.chosen_action, m.chosen_action)
            rows = (
                ("Nước đi / Độ sâu", f"{act_vi}  |  sâu {m.depth_reached}"),
                ("Trạng thái / Cắt tỉa", f"{m.explored_states:,} nút  |  cắt {m.pruned_branches}  |  TT {m.tt_hits}"),
                ("Thời gian quyết định", f"{m.elapsed_ms:.2f} ms"),
            )
            for r_idx, (lbl, val) in enumerate(rows):
                ry = y_cursor + 21 + r_idx * 18
                self.screen.blit(self.font_caption.render(lbl, True, TEXT_SECONDARY), (tx, ry))
                vs = self.font_mono.render(val, True, TEXT_PRIMARY)
                self.screen.blit(vs, (x1 - vs.get_width(), ry))

            y_cursor += 86

        # Chu giai mau toi gian o day sidebar
        legend_y = 684
        lx = x0
        for color, shape, text in (
            (ACCENT_PRIMARY, "dot", "Phe MAX"),
            (ACCENT_ALERT, "dot", "Phe MIN"),
            (TEXT_PRIMARY, "sq", "Thép"),
            (BORDER_STRONG, "sq", "Gạch (3 HP)"),
        ):
            if shape == "dot":
                pygame.draw.circle(self.screen, color, (lx + 5, legend_y + 7), 5)
            else:
                pygame.draw.rect(self.screen, color, (lx, legend_y + 2, 10, 10), border_radius=2)
            s = self.font_caption.render(text, True, TEXT_SECONDARY)
            self.screen.blit(s, (lx + 15, legend_y))
            lx += s.get_width() + 28

    def render(self) -> None:
        """Ve toan bo khung hinh hien tai."""
        mouse_pos = pygame.mouse.get_pos()
        self._draw_header()
        self._draw_arena()
        self._draw_sidebar(mouse_pos)
        pygame.display.flip()

    def save_screenshot(self, output_path: Path) -> None:
        """Xuat anh chup giao dien PNG phuc vu kiem thu va minh hoa."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.render()
        pygame.image.save(self.screen, str(output_path))

    def run(self) -> None:
        """Vong lap su kien chinh cua dau truong PyGame."""
        running = True
        while running:
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False
                    break

            if self.auto_play and not self.state.is_terminal():
                current_ctrl = self._active_controller(self.state.current_player)
                if not isinstance(current_ctrl, HumanController):
                    now = pygame.time.get_ticks()
                    if now - self.last_step_tick >= self.step_delay_ms:
                        self.execute_turn()
                        self.last_step_tick = now

            self.render()
            self.clock.tick(60)
        pygame.quit()
