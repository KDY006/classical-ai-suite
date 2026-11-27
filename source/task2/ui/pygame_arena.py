"""Minimal two-column PyGame arena for Tank Battle."""

from __future__ import annotations

import ctypes
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
)
from ..engine import MapScenario, TankBattleEngine, get_all_scenarios


@dataclass
class UIButton:
    rect: pygame.Rect
    label: str
    action_id: str


class HumanController:
    """Sentinel controller for a player operated from the keyboard."""

    def __init__(self) -> None:
        self.name = "Người chơi (Bàn phím)"
        self.last_metrics = SearchMetrics()


ACTION_LABELS_VI = {
    MOVE_UP: "LÊN",
    MOVE_DOWN: "XUỐNG",
    MOVE_LEFT: "TRÁI",
    MOVE_RIGHT: "PHẢI",
    FIRE: "BẮN",
    STAY: "CHỜ",
}


class TankBattleArenaUI:
    """Responsive two-column game board and match-control panel."""

    WINDOW_W = 920
    WINDOW_H = 600

    BG = (15, 19, 27)
    PANEL = (24, 30, 41)
    PANEL_ALT = (30, 37, 50)
    BORDER = (47, 57, 74)
    TEXT = (235, 240, 248)
    MUTED = (145, 158, 178)
    BLUE = (77, 165, 255)
    RED = (255, 104, 104)
    GREEN = (82, 211, 151)
    GOLD = (255, 204, 92)
    BRICK = (168, 103, 70)
    STEEL = (131, 147, 168)

    ASSET_FILES = {
        "tank_max": "tank_blue.png",
        "tank_min": "tank_red.png",
        "bullet_max": "bulletBlue1_outline.png",
        "bullet_min": "bulletRed1_outline.png",
        "base": "crateMetal.png",
        "brick": "crateWood.png",
        "steel": "barricadeMetal.png",
        "grass_a": "tileGrass1.png",
        "grass_b": "tileGrass2.png",
    }

    DIRECTION_ANGLE = {
        DIR_UP: 0,
        DIR_RIGHT: -90,
        DIR_DOWN: 180,
        DIR_LEFT: 90,
    }

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Đấu Tăng Đối Kháng | Nhiệm vụ 2 - Tìm kiếm Đối kháng")
        window_size = self._initial_window_size()
        self.screen = pygame.display.set_mode(
            window_size,
            pygame.RESIZABLE,
        )
        self.clock = pygame.time.Clock()

        font_path = next(
            (
                p
                for name in ("Segoe UI", "Arial", "Tahoma", "Helvetica Neue", "Noto Sans", "DejaVu Sans")
                if (p := pygame.font.match_font(name))
            ),
            None,
        )
        bold_path = next(
            (
                p
                for name in ("Segoe UI", "Arial", "Tahoma", "Helvetica Neue", "Noto Sans", "DejaVu Sans")
                if (p := pygame.font.match_font(name, bold=True))
            ),
            font_path,
        )
        self.font_title = pygame.font.Font(bold_path, 21)
        self.font_heading = pygame.font.Font(bold_path, 15)
        self.font_ui = pygame.font.Font(font_path, 14)
        self.font_small = pygame.font.Font(font_path, 12)
        self.font_mono = pygame.font.Font(font_path, 12)

        self.asset_dir = Path(__file__).resolve().parent / "assets"
        self.sprites: Dict[str, Optional[pygame.Surface]] = {}
        self._sprite_cache: Dict[tuple[str, int, int, int], pygame.Surface] = {}
        self._load_sprites()

        self.scenarios: List[MapScenario] = get_all_scenarios()
        self.scenario_idx = 0
        self.controllers: List[object] = self._build_controllers()
        self.max_ctrl_idx = 0
        self.min_ctrl_idx = 1 if len(self.controllers) > 1 else 0
        self.state = self.scenarios[self.scenario_idx].builder()

        self.auto_play = False
        self.step_delay_ms = 300
        self.last_step_tick = 0
        self.action_log: List[str] = []
        self.last_impacts: List[Tuple[int, int, str]] = []
        self.anim_frames: List[List[Tuple[int, int, int, str]]] = []
        self.anim_tick = 0
        self.buttons: List[UIButton] = []
        self._board_rect = pygame.Rect(0, 0, 0, 0)
        self._cell_px = 0

    @classmethod
    def _initial_window_size(cls) -> Tuple[int, int]:
        desktop_sizes = pygame.display.get_desktop_sizes()
        desktop_width, desktop_height = desktop_sizes[0] if desktop_sizes else (
            cls.WINDOW_W,
            cls.WINDOW_H,
        )
        work_width, work_height = desktop_width, desktop_height

        if sys.platform == "win32":
            class Rect(ctypes.Structure):
                _fields_ = [
                    ("left", ctypes.c_long),
                    ("top", ctypes.c_long),
                    ("right", ctypes.c_long),
                    ("bottom", ctypes.c_long),
                ]

            work_area = Rect()
            try:
                user32 = ctypes.windll.user32
                if user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(work_area), 0):
                    work_width = work_area.right - work_area.left
                    work_height = work_area.bottom - work_area.top
                else:
                    work_height = max(1, desktop_height - 48)
            except (AttributeError, OSError):
                work_height = max(1, desktop_height - 48)

        width = min(cls.WINDOW_W, max(1, int(work_width * 0.92)))
        height = min(cls.WINDOW_H, max(1, int(work_height * 0.85)))
        return width, height

    def _load_sprites(self) -> None:
        for key, filename in self.ASSET_FILES.items():
            path = self.asset_dir / filename
            if not path.is_file():
                self.sprites[key] = None
                continue
            try:
                self.sprites[key] = pygame.image.load(str(path)).convert_alpha()
            except (OSError, pygame.error):
                self.sprites[key] = None

    def _build_controllers(self) -> List[object]:
        controllers: List[object] = [
            HeuristicAlphaBetaAgent(max_depth=4, name="Heuristic Alpha-Beta (sâu 4)"),
            HeuristicMinimaxAgent(max_depth=3, name="Heuristic Minimax (sâu 3)"),
            AlphaBetaAgent(max_ply_cap=6, name="Alpha-Beta thuần (cắt 6)"),
            MinimaxAgent(max_ply_cap=5, name="Minimax thuần (cắt 5)"),
            HumanController(),
        ]
        controllers.extend(discover_external_agents())
        return controllers

    def reset_match(self) -> None:
        self.state = self.scenarios[self.scenario_idx].builder()
        self.action_log.clear()
        self.last_impacts.clear()
        self.anim_frames.clear()
        self.auto_play = False

    def _active_controller(self, player_id: int) -> object:
        index = self.max_ctrl_idx if player_id == PLAYER_MAX else self.min_ctrl_idx
        return self.controllers[index % len(self.controllers)]

    def execute_turn(self, forced_action: Optional[str] = None) -> None:
        if self.state.is_terminal():
            self.auto_play = False
            return

        player_id = self.state.current_player
        controller = self._active_controller(player_id)
        if isinstance(controller, HumanController):
            if forced_action is None:
                return
            action = forced_action
            controller.last_metrics = SearchMetrics(chosen_action=action)
        else:
            if not isinstance(controller, BaseTankAgent):
                raise TypeError(f"Unsupported controller type: {type(controller).__name__}")
            action = controller.safe_choose_action(self.state)

        next_state, event = TankBattleEngine.step_with_events(self.state, action)
        self.state = next_state
        self.last_impacts = event.impacts
        self.anim_frames = list(event.bullet_frames)
        self.anim_tick = pygame.time.get_ticks()

        metrics = getattr(controller, "last_metrics", SearchMetrics())
        side = "MAX" if player_id == PLAYER_MAX else "MIN"
        act_vi = ACTION_LABELS_VI.get(action, action)
        self.action_log.append(
            f"{side}  {act_vi}   {metrics.explored_states:,} nút   {metrics.elapsed_ms:.1f} ms"
        )
        self.action_log = self.action_log[-4:]

    def _handle_button(self, action_id: str) -> None:
        if action_id == "CYCLE_MAP":
            self.scenario_idx = (self.scenario_idx + 1) % len(self.scenarios)
            self.reset_match()
        elif action_id == "CYCLE_MAX":
            self.max_ctrl_idx = (self.max_ctrl_idx + 1) % len(self.controllers)
        elif action_id == "CYCLE_MIN":
            self.min_ctrl_idx = (self.min_ctrl_idx + 1) % len(self.controllers)
        elif action_id == "TOGGLE_PLAY":
            self.auto_play = not self.auto_play
            self.last_step_tick = pygame.time.get_ticks()
        elif action_id == "STEP_ONCE":
            self.auto_play = False
            self.execute_turn()
        elif action_id == "RESET":
            self.reset_match()
        elif action_id == "SLOWER":
            self.step_delay_ms = min(1200, self.step_delay_ms + 80)
        elif action_id == "FASTER":
            self.step_delay_ms = max(40, self.step_delay_ms - 80)
        elif action_id == "RELOAD_EXT":
            previous_max = self._active_controller(PLAYER_MAX)
            previous_min = self._active_controller(PLAYER_MIN)
            self.controllers = self._build_controllers()
            self.max_ctrl_idx = self._find_controller_index(previous_max)
            self.min_ctrl_idx = self._find_controller_index(previous_min)

    def _find_controller_index(self, previous: object) -> int:
        previous_name = getattr(previous, "name", None)
        for index, controller in enumerate(self.controllers):
            if controller is previous or (
                previous_name is not None
                and getattr(controller, "name", None) == previous_name
            ):
                return index
        return 0

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

    def render_frame(self) -> None:
        self.buttons.clear()
        self.screen.fill(self.BG)
        width, height = self.screen.get_size()
        right_width = min(440, max(320, int(width * 0.32)))
        gap = 22
        margin = 22
        left_rect = pygame.Rect(
            margin,
            margin,
            max(1, width - right_width - gap - margin * 2),
            max(1, height - margin * 2),
        )
        self._draw_board(left_rect)
        self._draw_sidebar(
            pygame.Rect(
                left_rect.right + gap,
                margin,
                right_width,
                max(1, height - margin * 2),
            )
        )
        pygame.display.flip()

    def _draw_board(self, area: Optional[pygame.Rect] = None) -> None:
        if area is None:
            width, height = self.screen.get_size()
            panel_width = min(440, max(320, int(width * 0.32)))
            area = pygame.Rect(22, 22, width - panel_width - 66, height - 44)

        pygame.draw.rect(self.screen, self.PANEL, area, border_radius=18)
        pygame.draw.rect(self.screen, self.BORDER, area, width=1, border_radius=18)

        title_y = area.y + 16
        self._draw_text("ĐẤU TĂNG ĐỐI KHÁNG", self.font_title, self.TEXT, (area.x + 22, title_y))
        scenario = self.scenarios[self.scenario_idx]
        self._draw_text(
            f"{scenario.title}  |  Lượt {self.state.ply}/{self.state.max_plies}",
            self.font_ui,
            self.MUTED,
            (area.x + 24, title_y + 32),
        )

        available = pygame.Rect(
            area.x + 26,
            area.y + 72,
            max(1, area.width - 52),
            max(1, area.height - 98),
        )
        self._cell_px = max(
            1,
            min(available.width // self.state.cols, available.height // self.state.rows),
        )
        board_width = self._cell_px * self.state.cols
        board_height = self._cell_px * self.state.rows
        self._board_rect = pygame.Rect(
            available.centerx - board_width // 2,
            available.centery - board_height // 2,
            board_width,
            board_height,
        )
        self._draw_board_cells()
        self._draw_board_entities()
        self._draw_projectiles()
        self._draw_impacts()
        self._draw_winner_banner()

    def _draw_board_cells(self) -> None:
        cell = self._cell_px
        for row in range(self.state.rows):
            for col in range(self.state.cols):
                rect = pygame.Rect(
                    self._board_rect.x + col * cell,
                    self._board_rect.y + row * cell,
                    cell,
                    cell,
                )
                sprite_key = "grass_a" if (row + col) % 2 == 0 else "grass_b"
                sprite = self._get_sprite(sprite_key, (cell, cell))
                if sprite is None:
                    shade = (50, 75, 67) if (row + col) % 2 == 0 else (45, 68, 61)
                    pygame.draw.rect(self.screen, shade, rect)
                else:
                    self.screen.blit(sprite, rect)
                pygame.draw.rect(self.screen, (16, 25, 30), rect, width=1)

    def _draw_board_entities(self) -> None:
        cell = self._cell_px
        for row, col in self.state.steel_walls:
            rect = self._cell_rect(row, col)
            sprite_rect = rect.inflate(-max(2, cell // 10), -max(2, cell // 10))
            sprite = self._get_sprite("steel", sprite_rect.size)
            if sprite is None:
                pygame.draw.rect(self.screen, self.STEEL, sprite_rect, border_radius=5)
                pygame.draw.line(self.screen, (225, 233, 241), sprite_rect.topleft, sprite_rect.bottomright, 3)
                pygame.draw.line(self.screen, (225, 233, 241), sprite_rect.topright, sprite_rect.bottomleft, 3)
            else:
                self.screen.blit(sprite, sprite_rect)

        for (row, col), wall in self.state.brick_walls.items():
            if wall.hp <= 0:
                continue
            rect = self._cell_rect(row, col)
            sprite_rect = rect.inflate(-max(2, cell // 10), -max(2, cell // 10))
            sprite = self._get_sprite("brick", sprite_rect.size)
            if sprite is None:
                pygame.draw.rect(self.screen, self.BRICK, sprite_rect, border_radius=5)
                pygame.draw.rect(self.screen, (226, 176, 128), sprite_rect, width=2, border_radius=5)
            else:
                self.screen.blit(sprite, sprite_rect)
            self._draw_badge(str(wall.hp), rect.right - 5, rect.top + 5, self.BRICK)

        for player_id, base in self.state.bases.items():
            rect = self._cell_rect(base.row, base.col)
            color = self.BLUE if player_id == PLAYER_MAX else self.RED
            if base.hp > 0:
                sprite_rect = rect.inflate(-max(4, cell // 5), -max(4, cell // 5))
                sprite = self._get_sprite("base", sprite_rect.size)
                if sprite is None:
                    pygame.draw.rect(self.screen, (54, 63, 76), sprite_rect, border_radius=7)
                    pygame.draw.rect(self.screen, color, sprite_rect, width=3, border_radius=7)
                else:
                    self.screen.blit(sprite, sprite_rect)
                    pygame.draw.rect(self.screen, color, sprite_rect, width=2, border_radius=5)
                self._draw_badge(f"CC{player_id}", rect.centerx, rect.bottom - 4, color)
            else:
                pygame.draw.line(self.screen, self.RED, rect.topleft, rect.bottomright, 4)
                pygame.draw.line(self.screen, self.RED, rect.topright, rect.bottomleft, 4)

        for player_id, tank in self.state.tanks.items():
            if tank.hp <= 0:
                continue
            rect = self._cell_rect(tank.row, tank.col)
            color = self.BLUE if player_id == PLAYER_MAX else self.RED
            size = max(8, int(cell * 0.82))
            sprite = self._get_sprite(
                "tank_max" if player_id == PLAYER_MAX else "tank_min",
                (size, size),
                self.DIRECTION_ANGLE[tank.facing],
            )
            tank_rect = pygame.Rect(0, 0, size, size)
            tank_rect.center = rect.center
            if sprite is None:
                self._draw_fallback_tank(tank_rect, color, tank.facing)
            else:
                self.screen.blit(sprite, tank_rect)
            self._draw_hp_bar(
                pygame.Rect(rect.x + 4, rect.bottom - 8, max(1, cell - 8), 4),
                tank.hp,
                TANK_INITIAL_HP,
                color,
            )

    def _draw_projectiles(self) -> None:
        bullets = [
            (bullet.owner_id, bullet.row, bullet.col, bullet.direction)
            for bullet in self.state.bullets
        ]
        if self.anim_frames:
            frame_index = (pygame.time.get_ticks() - self.anim_tick) // 55
            if frame_index < len(self.anim_frames):
                bullets = self.anim_frames[frame_index]
            else:
                self.anim_frames.clear()

        for owner_id, row, col, direction in bullets:
            cell_rect = self._cell_rect(row, col)
            width = max(5, int(self._cell_px * 0.22))
            height = max(9, int(self._cell_px * 0.48))
            key = "bullet_max" if owner_id == PLAYER_MAX else "bullet_min"
            sprite = self._get_sprite(
                key,
                (width, height),
                self.DIRECTION_ANGLE[direction],
            )
            if sprite is None:
                self._draw_fallback_bullet(cell_rect.center, direction, owner_id)
            else:
                destination = sprite.get_rect(center=cell_rect.center)
                self.screen.blit(sprite, destination)

    def _draw_impacts(self) -> None:
        for row, col, _ in self.last_impacts:
            center = self._cell_rect(row, col).center
            radius = max(6, self._cell_px // 4)
            pygame.draw.circle(self.screen, self.GOLD, center, radius, width=2)

    def _draw_winner_banner(self) -> None:
        winner = self.state.winner()
        if winner is None:
            return
        banner = pygame.Rect(0, 0, min(self._board_rect.width - 24, 390), 68)
        banner.center = self._board_rect.center
        pygame.draw.rect(self.screen, (18, 23, 31), banner, border_radius=12)
        pygame.draw.rect(self.screen, self.GOLD, banner, width=2, border_radius=12)
        if winner == 0:
            message = "KẾT QUẢ: HÒA TRẬN"
        else:
            message = f"{'PHE MAX' if winner == PLAYER_MAX else 'PHE MIN'} CHIẾN THẮNG!"
        self._draw_text(
            message,
            self.font_title,
            self.GOLD,
            (banner.centerx, banner.centery),
            center=True,
        )

    def _draw_sidebar(self, panel: Optional[pygame.Rect] = None) -> None:
        if panel is None:
            width, height = self.screen.get_size()
            panel_width = min(440, max(320, int(width * 0.32)))
            panel = pygame.Rect(width - panel_width - 22, 22, panel_width, height - 44)
        pygame.draw.rect(self.screen, self.PANEL, panel, border_radius=18)
        pygame.draw.rect(self.screen, self.BORDER, panel, width=1, border_radius=18)

        scale = min(1.0, max(0.72, panel.height / 680))
        x = panel.x + 18
        width = panel.width - 36
        y = panel.y + 16
        self._draw_text("ĐIỀU KHIỂN TRẬN ĐẤU", self.font_heading, self.TEXT, (x, y))
        self._draw_text(
            "Chọn bản đồ và bộ điều khiển cho mỗi phe",
            self.font_small,
            self.MUTED,
            (x, y + 22),
        )

        y += int(52 * scale)
        self._draw_text("BẢN ĐỒ KỊCH BẢN", self.font_small, self.MUTED, (x, y))
        self._add_button(
            pygame.Rect(x, y + 16, width, max(29, int(34 * scale))),
            self.scenarios[self.scenario_idx].title,
            "CYCLE_MAP",
        )

        y += int(57 * scale)
        half = (width - 10) // 2
        for player_id, action_id, color in (
            (PLAYER_MAX, "CYCLE_MAX", self.BLUE),
            (PLAYER_MIN, "CYCLE_MIN", self.RED),
        ):
            button_x = x if player_id == PLAYER_MAX else x + half + 10
            controller = self._active_controller(player_id)
            self._add_button(
                pygame.Rect(button_x, y, half, max(32, int(38 * scale))),
                f"{'MAX' if player_id == PLAYER_MAX else 'MIN'}: {self._display_controller_name(controller)}",
                action_id,
                highlighted=isinstance(controller, HumanController),
            )

        y += int(46 * scale)
        button_gap = 8
        button_width = (width - button_gap * 2) // 3
        self._add_button(
            pygame.Rect(x, y, button_width, max(29, int(32 * scale))),
            "Tạm dừng" if self.auto_play else "Tự chạy",
            "TOGGLE_PLAY",
            highlighted=self.auto_play,
        )
        self._add_button(
            pygame.Rect(x + button_width + button_gap, y, button_width, max(29, int(32 * scale))),
            "Từng bước",
            "STEP_ONCE",
        )
        self._add_button(
            pygame.Rect(x + (button_width + button_gap) * 2, y, button_width, max(29, int(32 * scale))),
            "Đặt lại",
            "RESET",
        )

        y += int(39 * scale)
        self._draw_text(f"{self.step_delay_ms} ms / lượt", self.font_small, self.MUTED, (x, y + 3))
        reload_width = 96
        speed_x = panel.right - 18 - reload_width - 8 - 86
        self._add_button(pygame.Rect(speed_x, y, 39, 25), "-", "SLOWER")
        self._add_button(
            pygame.Rect(speed_x + 45, y, 39, 25),
            "+",
            "FASTER",
        )
        self._add_button(
            pygame.Rect(panel.right - 18 - reload_width, y, reload_width, 25),
            "Nạp lại Bot",
            "RELOAD_EXT",
        )

        y += int(33 * scale)
        self._draw_text("TRẠNG THÁI ĐƠN VỊ", self.font_small, self.MUTED, (x, y))
        y += 16
        for player_id, color, label in (
            (PLAYER_MAX, self.BLUE, "MAX"),
            (PLAYER_MIN, self.RED, "MIN"),
        ):
            tank = self.state.tanks[player_id]
            base = self.state.bases[player_id]
            self._draw_text(f"Xe {label}", self.font_small, color, (x, y))
            self._draw_hp_bar(pygame.Rect(x + 56, y + 2, max(24, int(width * 0.48)), 8), tank.hp, TANK_INITIAL_HP, color)
            self._draw_text(f"{tank.hp}/{TANK_INITIAL_HP}", self.font_small, self.TEXT, (x + int(width * 0.72), y - 1))
            self._draw_text("Căn cứ", self.font_small, self.MUTED, (x, y + 17))
            self._draw_hp_bar(pygame.Rect(x + 56, y + 19, max(24, int(width * 0.48)), 8), base.hp, BASE_INITIAL_HP, color)
            self._draw_text(f"{base.hp}/{BASE_INITIAL_HP}", self.font_small, self.TEXT, (x + int(width * 0.72), y + 16))
            y += int(39 * scale)

        y += 1
        self._draw_text("THÔNG SỐ TÌM KIẾM", self.font_small, self.MUTED, (x, y))
        y += 16
        for player_id, color, label in (
            (PLAYER_MAX, self.BLUE, "MAX"),
            (PLAYER_MIN, self.RED, "MIN"),
        ):
            controller = self._active_controller(player_id)
            metrics = getattr(controller, "last_metrics", SearchMetrics())
            card_height = max(53, int(53 * scale))
            card = pygame.Rect(x, y, width, card_height)
            pygame.draw.rect(self.screen, self.PANEL_ALT, card, border_radius=10)
            pygame.draw.rect(self.screen, self.BORDER, card, width=1, border_radius=10)
            self._draw_text(
                f"{label}  {self._controller_name(controller)}",
                self.font_small,
                color,
                (card.x + 9, card.y + 5),
                max_width=card.width - 20,
            )
            act_vi = ACTION_LABELS_VI.get(metrics.chosen_action, metrics.chosen_action)
            self._draw_text(
                f"{act_vi} | sâu {metrics.depth_reached} | {metrics.elapsed_ms:.1f} ms",
                self.font_mono,
                self.TEXT,
                (card.x + 9, card.y + 22),
                max_width=card.width - 20,
            )
            self._draw_text(
                f"{metrics.explored_states:,} nút | cắt {metrics.pruned_branches} | TT {metrics.tt_hits}",
                self.font_mono,
                self.MUTED,
                (card.x + 9, card.y + 37),
                max_width=card.width - 20,
            )
            y += max(card_height + 4, int(59 * scale))

        if panel.height >= 700 and y + 68 < panel.bottom - 8:
            self._draw_text("NHẬT KÝ LƯỢT ĐI", self.font_small, self.MUTED, (x, y))
            y += 18
            for message in self.action_log[-3:]:
                self._draw_text(
                    message,
                    self.font_small,
                    self.TEXT,
                    (x, y),
                    max_width=width,
                )
                y += 17

        hint_y = panel.bottom - 20
        is_human_turn = isinstance(
            self._active_controller(self.state.current_player),
            HumanController,
        )
        self._draw_text(
            "WASD/Mũi tên: Đi | Space: Bắn | Enter: Chờ" if is_human_turn else "Nhấn ESC để thoát",
            self.font_small,
            self.GOLD if is_human_turn else self.MUTED,
            (x, hint_y),
            max_width=width,
        )

    def _draw_hp_bar(
        self,
        rect: pygame.Rect,
        current: int,
        maximum: int,
        color: Tuple[int, int, int],
    ) -> None:
        pygame.draw.rect(self.screen, (52, 61, 75), rect, border_radius=max(2, rect.height // 2))
        ratio = max(0.0, min(1.0, current / maximum)) if maximum else 0.0
        fill = rect.copy()
        fill.width = int(rect.width * ratio)
        if fill.width > 0:
            pygame.draw.rect(self.screen, color, fill, border_radius=max(2, rect.height // 2))

    def _draw_badge(
        self,
        label: str,
        x: int,
        y: int,
        color: Tuple[int, int, int],
    ) -> None:
        text = self.font_small.render(label, True, self.TEXT)
        badge = pygame.Rect(0, 0, text.get_width() + 10, text.get_height() + 5)
        badge.center = (x, y)
        pygame.draw.rect(self.screen, color, badge, border_radius=5)
        self.screen.blit(text, text.get_rect(center=badge.center))

    def _draw_fallback_tank(
        self,
        rect: pygame.Rect,
        color: Tuple[int, int, int],
        direction: str,
    ) -> None:
        pygame.draw.rect(self.screen, color, rect.inflate(-rect.width // 5, -rect.height // 5), border_radius=8)
        center = rect.center
        length = max(6, min(rect.width, rect.height) // 2)
        endpoint = {
            DIR_UP: (center[0], center[1] - length),
            DIR_DOWN: (center[0], center[1] + length),
            DIR_LEFT: (center[0] - length, center[1]),
            DIR_RIGHT: (center[0] + length, center[1]),
        }[direction]
        pygame.draw.line(self.screen, self.TEXT, center, endpoint, max(2, rect.width // 7))

    def _draw_fallback_bullet(
        self,
        center: Tuple[int, int],
        direction: str,
        owner_id: int,
    ) -> None:
        color = self.BLUE if owner_id == PLAYER_MAX else self.RED
        delta = {
            DIR_UP: (0, -1),
            DIR_DOWN: (0, 1),
            DIR_LEFT: (-1, 0),
            DIR_RIGHT: (1, 0),
        }[direction]
        end = (
            center[0] + delta[0] * max(5, self._cell_px // 4),
            center[1] + delta[1] * max(5, self._cell_px // 4),
        )
        pygame.draw.line(self.screen, color, center, end, max(3, self._cell_px // 8))
        pygame.draw.circle(self.screen, self.GOLD, end, max(2, self._cell_px // 12))

    def _get_sprite(
        self,
        key: str,
        size: Tuple[int, int],
        angle: int = 0,
    ) -> Optional[pygame.Surface]:
        source = self.sprites.get(key)
        if source is None or size[0] <= 0 or size[1] <= 0:
            return None
        cache_key = (key, size[0], size[1], angle)
        cached = self._sprite_cache.get(cache_key)
        if cached is not None:
            return cached
        scaled = pygame.transform.smoothscale(source, size)
        rotated = pygame.transform.rotate(scaled, angle) if angle else scaled
        self._sprite_cache[cache_key] = rotated
        return rotated

    def _cell_rect(self, row: int, col: int) -> pygame.Rect:
        return pygame.Rect(
            self._board_rect.x + col * self._cell_px,
            self._board_rect.y + row * self._cell_px,
            self._cell_px,
            self._cell_px,
        )

    def _add_button(
        self,
        rect: pygame.Rect,
        label: str,
        action_id: str,
        highlighted: bool = False,
    ) -> None:
        self.buttons.append(UIButton(rect, label, action_id))
        background = (45, 91, 137) if highlighted else self.PANEL_ALT
        pygame.draw.rect(self.screen, background, rect, border_radius=8)
        pygame.draw.rect(self.screen, self.BORDER, rect, width=1, border_radius=8)
        self._draw_text(
            label,
            self.font_ui,
            self.TEXT,
            rect.center,
            center=True,
            max_width=rect.width - 14,
        )

    def _draw_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: Tuple[int, int, int],
        position: Tuple[int, int],
        center: bool = False,
        max_width: Optional[int] = None,
    ) -> None:
        display_text = text
        if max_width is not None:
            while display_text and font.size(display_text)[0] > max_width:
                if display_text.endswith("..."):
                    display_text = display_text[:-4].rstrip() + "..."
                else:
                    display_text = display_text[:-1].rstrip() + "..."
        surface = font.render(display_text, True, color)
        destination = surface.get_rect()
        if center:
            destination.center = position
        else:
            destination.topleft = position
        self.screen.blit(surface, destination)

    @staticmethod
    def _controller_name(controller: object) -> str:
        name = getattr(controller, "name", type(controller).__name__)
        return str(name)

    @classmethod
    def _display_controller_name(cls, controller: object) -> str:
        name = cls._controller_name(controller)
        aliases = {
            "Heuristic Alpha-Beta (sâu 4)": "Heuristic AB (s4)",
            "Heuristic Minimax (sâu 3)": "Heuristic MM (s3)",
            "Alpha-Beta thuần (cắt 6)": "Alpha-Beta (c6)",
            "Minimax thuần (cắt 5)": "Minimax (c5)",
            "Người chơi (Bàn phím)": "Người chơi",
        }
        return aliases.get(name, name)

    def save_screenshot(self, path: Path) -> None:
        self.render_frame()
        path.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(self.screen, str(path))

    def run(self) -> None:
        running = True
        while running:
            now = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in self.buttons:
                        if button.rect.collidepoint(event.pos):
                            self._handle_button(button.action_id)
                            break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self._handle_human_key(event.key)

            if self.auto_play and not self.state.is_terminal():
                active = self._active_controller(self.state.current_player)
                if isinstance(active, HumanController):
                    self.auto_play = False
                elif now - self.last_step_tick >= self.step_delay_ms:
                    self.execute_turn()
                    self.last_step_tick = pygame.time.get_ticks()

            self.render_frame()
            self.clock.tick(30)
        pygame.quit()
