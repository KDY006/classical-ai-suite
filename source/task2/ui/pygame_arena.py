"""PyGame GUI Arena for Task 2: Tank Battle with live telemetry and external bot selector."""

from __future__ import annotations

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
    WALL_INITIAL_HP,
)
from ..engine import GameState, MapScenario, StepEvent, TankBattleEngine, get_all_scenarios


@dataclass
class UIButton:
    rect: pygame.Rect
    label: str
    action_id: str


class HumanController:
    """Placeholder sentinel representing keyboard control inside PyGame."""

    def __init__(self) -> None:
        self.name = "Human (WASD + Space)"
        self.last_metrics = SearchMetrics()


class TankBattleArenaUI:
    """Interactive PyGame Arena supporting AI vs AI, Human vs AI, and External Bot Plugins."""

    WINDOW_W: int = 1120
    WINDOW_H: int = 740
    BOARD_AREA_SIZE: int = 640
    BOARD_MARGIN_X: int = 28
    BOARD_MARGIN_Y: int = 64

    BG_COLOR = (18, 22, 30)
    GRID_BG = (28, 34, 46)
    GRID_LINE = (46, 54, 72)
    PANEL_BG = (25, 30, 42)
    PANEL_BORDER = (62, 74, 98)
    TEXT_MAIN = (235, 240, 248)
    TEXT_MUTED = (158, 170, 192)
    MAX_COLOR = (64, 156, 255)
    MIN_COLOR = (242, 88, 88)
    BRICK_COLOR = (186, 98, 56)
    STEEL_COLOR = (142, 154, 172)
    BULLET_COLOR = (255, 224, 92)
    ACCENT_GREEN = (68, 204, 136)

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Task 2 - Tank Battle Adversarial Search Arena (TDTU AI)")
        self.screen = pygame.display.set_mode((self.WINDOW_W, self.WINDOW_H))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_ui = pygame.font.SysFont("Arial", 15, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 13)
        self.font_mono = pygame.font.SysFont("Consolas", 13)

        self.scenarios: List[MapScenario] = get_all_scenarios()
        self.scenario_idx: int = 0

        self.controllers: List[object] = self._build_controllers()
        self.max_ctrl_idx: int = 0  # Heuristic Alpha-Beta default
        self.min_ctrl_idx: int = 1  # Heuristic Minimax default

        self.state: GameState = self.scenarios[self.scenario_idx].builder()
        self.auto_play: bool = False
        self.step_delay_ms: int = 280
        self.last_step_tick: int = 0
        self.action_log: List[str] = []
        self.last_impacts: List[Tuple[int, int, str]] = []
        self.anim_frames: List[List[Tuple[int, int, int, str]]] = []
        self.anim_tick: int = 0

        self.buttons: List[UIButton] = self._create_buttons()

    def _build_controllers(self) -> List[object]:
        ctrls: List[object] = [
            HeuristicAlphaBetaAgent(max_depth=4, name="Heuristic Alpha-Beta (d=4)"),
            HeuristicMinimaxAgent(max_depth=3, name="Heuristic Minimax (d=3)"),
            AlphaBetaAgent(max_ply_cap=6, name="Pure Alpha-Beta (cap=6)"),
            MinimaxAgent(max_ply_cap=5, name="Pure Minimax (cap=5)"),
            HumanController(),
        ]
        external = discover_external_agents()
        ctrls.extend(external)
        return ctrls

    def _create_buttons(self) -> List[UIButton]:
        px = 700
        return [
            UIButton(pygame.Rect(px, 68, 390, 32), "Map", "CYCLE_MAP"),
            UIButton(pygame.Rect(px, 126, 390, 32), "MAX Bot", "CYCLE_MAX"),
            UIButton(pygame.Rect(px, 184, 390, 32), "MIN Bot", "CYCLE_MIN"),
            UIButton(pygame.Rect(px, 236, 122, 36), "Play / Pause", "TOGGLE_PLAY"),
            UIButton(pygame.Rect(px + 134, 236, 122, 36), "Step 1 Turn", "STEP_ONCE"),
            UIButton(pygame.Rect(px + 268, 236, 122, 36), "Reset Match", "RESET"),
            UIButton(pygame.Rect(px, 282, 190, 30), "Speed -", "SLOWER"),
            UIButton(pygame.Rect(px + 200, 282, 190, 30), "Speed +", "FASTER"),
            UIButton(pygame.Rect(px, 320, 390, 28), "Reload external_agents/*.py", "RELOAD_EXT"),
        ]

    def reset_match(self) -> None:
        self.state = self.scenarios[self.scenario_idx].builder()
        self.action_log.clear()
        self.last_impacts.clear()
        self.anim_frames.clear()
        self.auto_play = False

    def _active_controller(self, player_id: int) -> object:
        idx = self.max_ctrl_idx if player_id == PLAYER_MAX else self.min_ctrl_idx
        return self.controllers[idx % len(self.controllers)]

    def execute_turn(self, forced_action: Optional[str] = None) -> None:
        if self.state.is_terminal():
            self.auto_play = False
            return

        pid = self.state.current_player
        ctrl = self._active_controller(pid)

        if isinstance(ctrl, HumanController):
            if forced_action is None:
                return
            action = forced_action
        else:
            assert isinstance(ctrl, BaseTankAgent)
            action = ctrl.safe_choose_action(self.state)

        next_state, step_ev = TankBattleEngine.step_with_events(self.state, action)
        self.state = next_state
        self.last_impacts = step_ev.impacts
        self.anim_frames = list(step_ev.bullet_frames)
        self.anim_tick = pygame.time.get_ticks()

        who = "MAX(P1)" if pid == PLAYER_MAX else "MIN(P2)"
        ms = getattr(ctrl, "last_metrics", SearchMetrics()).elapsed_ms
        nodes = getattr(ctrl, "last_metrics", SearchMetrics()).explored_states
        self.action_log.append(f"#{self.state.ply:03d} {who}: {action:<10} ({nodes} st, {ms:.1f}ms)")
        if len(self.action_log) > 10:
            self.action_log = self.action_log[-10:]

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
            self.controllers = self._build_controllers()
            self.max_ctrl_idx %= len(self.controllers)
            self.min_ctrl_idx %= len(self.controllers)

    def _handle_human_key(self, key: int) -> None:
        ctrl = self._active_controller(self.state.current_player)
        if not isinstance(ctrl, HumanController):
            return
        key_map: Dict[int, str] = {
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
        if key in key_map:
            self.execute_turn(forced_action=key_map[key])

    def render_frame(self) -> None:
        self.screen.fill(self.BG_COLOR)

        # Header
        scen = self.scenarios[self.scenario_idx]
        header = self.font_title.render(
            f"TANK BATTLE ARENA  |  {scen.title}  |  Turn {self.state.ply}/{self.state.max_plies}",
            True,
            self.TEXT_MAIN,
        )
        self.screen.blit(header, (self.BOARD_MARGIN_X, 20))

        self._draw_board()
        self._draw_sidebar()
        pygame.display.flip()

    def _draw_board(self) -> None:
        rows, cols = self.state.rows, self.state.cols
        cell_px = min(self.BOARD_AREA_SIZE // cols, self.BOARD_AREA_SIZE // rows)
        bw = cell_px * cols
        bh = cell_px * rows
        ox = self.BOARD_MARGIN_X + (self.BOARD_AREA_SIZE - bw) // 2
        oy = self.BOARD_MARGIN_Y + (self.BOARD_AREA_SIZE - bh) // 2

        board_rect = pygame.Rect(ox, oy, bw, bh)
        pygame.draw.rect(self.screen, self.GRID_BG, board_rect, border_radius=4)

        # Grid lines
        for r in range(rows + 1):
            y = oy + r * cell_px
            pygame.draw.line(self.screen, self.GRID_LINE, (ox, y), (ox + bw, y), 1)
        for c in range(cols + 1):
            x = ox + c * cell_px
            pygame.draw.line(self.screen, self.GRID_LINE, (x, oy), (x, oy + bh), 1)

        # Steel walls
        for r, c in self.state.steel_walls:
            rect = pygame.Rect(ox + c * cell_px + 3, oy + r * cell_px + 3, cell_px - 6, cell_px - 6)
            pygame.draw.rect(self.screen, self.STEEL_COLOR, rect, border_radius=3)
            pygame.draw.rect(self.screen, (205, 215, 228), rect, width=2, border_radius=3)

        # Brick walls with HP indicator
        for (r, c), wall in self.state.brick_walls.items():
            if wall.hp <= 0:
                continue
            ratio = wall.hp / WALL_INITIAL_HP
            shade = (
                int(self.BRICK_COLOR[0] * (0.55 + 0.45 * ratio)),
                int(self.BRICK_COLOR[1] * (0.55 + 0.45 * ratio)),
                int(self.BRICK_COLOR[2] * (0.55 + 0.45 * ratio)),
            )
            rect = pygame.Rect(ox + c * cell_px + 3, oy + r * cell_px + 3, cell_px - 6, cell_px - 6)
            pygame.draw.rect(self.screen, shade, rect, border_radius=3)
            hp_txt = self.font_small.render(str(wall.hp), True, (255, 238, 220))
            self.screen.blit(hp_txt, hp_txt.get_rect(center=rect.center))

        # Bases
        for pid, base in self.state.bases.items():
            color = self.MAX_COLOR if pid == PLAYER_MAX else self.MIN_COLOR
            rect = pygame.Rect(ox + base.col * cell_px + 5, oy + base.row * cell_px + 5, cell_px - 10, cell_px - 10)
            if base.hp > 0:
                pygame.draw.rect(self.screen, color, rect, width=3, border_radius=6)
                lbl = self.font_ui.render(f"B{pid}:{base.hp}", True, color)
                self.screen.blit(lbl, lbl.get_rect(center=rect.center))
            else:
                pygame.draw.line(self.screen, self.MIN_COLOR, rect.topleft, rect.bottomright, 3)
                pygame.draw.line(self.screen, self.MIN_COLOR, rect.topright, rect.bottomleft, 3)

        # Tanks
        for pid, tank in self.state.tanks.items():
            if tank.hp <= 0:
                continue
            color = self.MAX_COLOR if pid == PLAYER_MAX else self.MIN_COLOR
            cx = ox + tank.col * cell_px + cell_px // 2
            cy = oy + tank.row * cell_px + cell_px // 2
            body_r = max(10, cell_px // 3)
            pygame.draw.circle(self.screen, color, (cx, cy), body_r)
            pygame.draw.circle(self.screen, (245, 248, 255), (cx, cy), body_r, 2)

            # Gun barrel showing facing direction
            barrel_len = int(cell_px * 0.44)
            end_pos = {
                DIR_UP: (cx, cy - barrel_len),
                DIR_DOWN: (cx, cy + barrel_len),
                DIR_LEFT: (cx - barrel_len, cy),
                DIR_RIGHT: (cx + barrel_len, cy),
            }[tank.facing]
            pygame.draw.line(self.screen, (250, 250, 250), (cx, cy), end_pos, 4)

            # Mini HP bar above tank
            bar_w = cell_px - 10
            bx = ox + tank.col * cell_px + 5
            by = oy + tank.row * cell_px + 3
            pygame.draw.rect(self.screen, (50, 55, 65), (bx, by, bar_w, 5))
            fill_w = int(bar_w * max(0.0, tank.hp / TANK_INITIAL_HP))
            pygame.draw.rect(self.screen, self.ACCENT_GREEN, (bx, by, fill_w, 5))

        # Active bullets (or animated sub-step frame)
        bullets_to_draw = [
            (b.owner_id, b.row, b.col, b.direction) for b in self.state.bullets if b.active
        ]
        if self.anim_frames:
            elapsed = pygame.time.get_ticks() - self.anim_tick
            frame_idx = elapsed // 60
            if frame_idx < len(self.anim_frames):
                bullets_to_draw = self.anim_frames[frame_idx]
            else:
                self.anim_frames.clear()

        for owner_id, br, bc, _ in bullets_to_draw:
            bx = ox + bc * cell_px + cell_px // 2
            by = oy + br * cell_px + cell_px // 2
            pygame.draw.circle(self.screen, self.BULLET_COLOR, (bx, by), max(5, cell_px // 7))
            ring_col = self.MAX_COLOR if owner_id == PLAYER_MAX else self.MIN_COLOR
            pygame.draw.circle(self.screen, ring_col, (bx, by), max(7, cell_px // 5), 2)

        # Impact flash markers
        for ir, ic, _ in self.last_impacts:
            ix = ox + ic * cell_px + cell_px // 2
            iy = oy + ir * cell_px + cell_px // 2
            pygame.draw.circle(self.screen, (255, 140, 50), (ix, iy), max(8, cell_px // 4), 2)

        # Winner banner overlay
        winner = self.state.winner()
        if winner is not None:
            banner = pygame.Rect(ox + 40, oy + bh // 2 - 34, bw - 80, 68)
            pygame.draw.rect(self.screen, (15, 20, 28), banner, border_radius=8)
            pygame.draw.rect(self.screen, self.BULLET_COLOR, banner, width=2, border_radius=8)
            msg = (
                "MATCH RESULT: DRAW"
                if winner == 0
                else f"WINNER: {'PLAYER 1 (MAX - BLUE)' if winner == PLAYER_MAX else 'PLAYER 2 (MIN - RED)'}!"
            )
            txt = self.font_title.render(msg, True, self.BULLET_COLOR)
            self.screen.blit(txt, txt.get_rect(center=banner.center))

    def _draw_sidebar(self) -> None:
        panel = pygame.Rect(686, 20, 416, 700)
        pygame.draw.rect(self.screen, self.PANEL_BG, panel, border_radius=8)
        pygame.draw.rect(self.screen, self.PANEL_BORDER, panel, width=1, border_radius=8)

        title = self.font_ui.render("MATCH CONFIGURATION & CONTROLS", True, self.TEXT_MAIN)
        self.screen.blit(title, (700, 34))

        scen = self.scenarios[self.scenario_idx]
        max_ctrl = self._active_controller(PLAYER_MAX)
        min_ctrl = self._active_controller(PLAYER_MIN)

        # Selector labels
        self.screen.blit(self.font_small.render("Scenario (click button to switch):", True, self.TEXT_MUTED), (700, 52))
        self.screen.blit(self.font_small.render("Player 1 - MAX (Blue Tank):", True, self.MAX_COLOR), (700, 108))
        self.screen.blit(self.font_small.render("Player 2 - MIN (Red Tank):", True, self.MIN_COLOR), (700, 166))

        dynamic_labels = {
            "CYCLE_MAP": f"Map: {scen.title}",
            "CYCLE_MAX": f"MAX: {getattr(max_ctrl, 'name', 'Bot')}",
            "CYCLE_MIN": f"MIN: {getattr(min_ctrl, 'name', 'Bot')}",
            "TOGGLE_PLAY": "Pause" if self.auto_play else "Auto Play",
        }

        for btn in self.buttons:
            bg = (48, 92, 148) if (btn.action_id == "TOGGLE_PLAY" and self.auto_play) else (40, 48, 66)
            pygame.draw.rect(self.screen, bg, btn.rect, border_radius=5)
            pygame.draw.rect(self.screen, self.PANEL_BORDER, btn.rect, width=1, border_radius=5)
            text = dynamic_labels.get(btn.action_id, btn.label)
            surf = self.font_small.render(text, True, self.TEXT_MAIN)
            self.screen.blit(surf, surf.get_rect(center=btn.rect.center))

        # Status & HP Telemetry
        y = 360
        t1, t2 = self.state.tanks[PLAYER_MAX], self.state.tanks[PLAYER_MIN]
        b1, b2 = self.state.bases[PLAYER_MAX], self.state.bases[PLAYER_MIN]
        turn_lbl = "MAX (Blue)" if self.state.current_player == PLAYER_MAX else "MIN (Red)"
        info_lines = [
            f"Active Turn : {turn_lbl}   |   Delay: {self.step_delay_ms} ms",
            f"MAX Status  : Tank HP {t1.hp}/{TANK_INITIAL_HP} ({t1.facing}) | Base HP {b1.hp}/{BASE_INITIAL_HP}",
            f"MIN Status  : Tank HP {t2.hp}/{TANK_INITIAL_HP} ({t2.facing}) | Base HP {b2.hp}/{BASE_INITIAL_HP}",
        ]
        for line in info_lines:
            self.screen.blit(self.font_mono.render(line, True, self.TEXT_MAIN), (700, y))
            y += 20

        # Search Telemetry for both agents
        y += 8
        self.screen.blit(self.font_ui.render("SEARCH TELEMETRY (LAST DECISION)", True, self.ACCENT_GREEN), (700, y))
        y += 22
        for tag, ctrl, col in (("MAX", max_ctrl, self.MAX_COLOR), ("MIN", min_ctrl, self.MIN_COLOR)):
            m: SearchMetrics = getattr(ctrl, "last_metrics", SearchMetrics())
            line = (
                f"{tag}: act={m.chosen_action:<10} d={m.depth_reached} "
                f"nodes={m.explored_states:<5} t={m.elapsed_ms:.1f}ms"
            )
            self.screen.blit(self.font_mono.render(line, True, col), (700, y))
            y += 19

        # Recent Action Log
        y += 10
        self.screen.blit(self.font_ui.render("ACTION & COLLISION LOG", True, self.TEXT_MAIN), (700, y))
        y += 22
        for entry in self.action_log:
            self.screen.blit(self.font_mono.render(entry, True, self.TEXT_MUTED), (700, y))
            y += 17

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
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for btn in self.buttons:
                        if btn.rect.collidepoint(event.pos):
                            self._handle_button(btn.action_id)
                            break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self._handle_human_key(event.key)

            if self.auto_play and not self.state.is_terminal():
                active = self._active_controller(self.state.current_player)
                if not isinstance(active, HumanController) and (now - self.last_step_tick >= self.step_delay_ms):
                    self.execute_turn()
                    self.last_step_tick = pygame.time.get_ticks()

            self.render_frame()
            self.clock.tick(30)

        pygame.quit()
