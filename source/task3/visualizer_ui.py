"""PyGame Visualizer UI for Task 3: Kakuro CSP Domains, Propagation, and Backtracking."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import pygame

from .csp_model import KakuroCSP
from .solver import KakuroSolveResult, KakuroSolver, SolverMode, SolverStep


@dataclass
class ControlButton:
    rect: pygame.Rect
    label: str
    action_id: str


class KakuroVisualizerUI:
    """Interactive PyGame interface visualizing candidate domains, pruning, and backtracking."""

    WINDOW_W: int = 1160
    WINDOW_H: int = 760
    GRID_AREA_SIZE: int = 660
    GRID_ORIGIN_X: int = 26
    GRID_ORIGIN_Y: int = 64

    BG_COLOR = (20, 24, 33)
    WHITE_CELL = (244, 247, 252)
    BLACK_CELL = (36, 42, 56)
    CLUE_LINE = (110, 124, 150)
    GRID_BORDER = (68, 78, 98)

    FOCUS_BG = (212, 236, 255)
    FOCUS_BORDER = (28, 136, 245)
    PRUNE_BG = (255, 232, 228)
    PRUNE_BORDER = (228, 76, 76)
    BACKTRACK_BG = (255, 236, 205)
    BACKTRACK_BORDER = (238, 138, 34)
    SOLVED_BG = (220, 248, 232)

    ASSIGNED_TEXT = (20, 92, 168)
    CAND_ACTIVE = (44, 58, 82)
    CAND_PRUNED_NOW = (220, 38, 38)
    PANEL_BG = (27, 33, 46)
    PANEL_BORDER = (64, 76, 102)
    TEXT_LIGHT = (236, 241, 250)
    TEXT_MUTED = (162, 174, 196)
    ACCENT_GREEN = (72, 208, 140)

    def __init__(self, maps_dir: Path | None = None) -> None:
        pygame.init()
        pygame.display.set_caption("Task 3 - Kakuro CSP Domain & Propagation Visualizer (TDTU AI)")
        self.screen = pygame.display.set_mode((self.WINDOW_W, self.WINDOW_H))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_ui = pygame.font.SysFont("Arial", 15, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 13)
        self.font_mono = pygame.font.SysFont("Consolas", 13)

        base_maps = maps_dir or (Path(__file__).resolve().parent / "maps")
        preferred_order = [
            "board_5x5_example.json",
            "board_9x9_complex.json",
            "board_6x6_medium.json",
            "board_8x8_hard.json",
        ]
        self.map_files: List[Path] = [
            base_maps / name for name in preferred_order if (base_maps / name).exists()
        ]
        for extra in sorted(base_maps.glob("*.json")):
            if extra not in self.map_files:
                self.map_files.append(extra)

        self.modes: List[SolverMode] = [
            SolverMode.BT_MAC_HEURISTICS,
            SolverMode.BT_FC,
            SolverMode.PLAIN_BT,
        ]
        self.map_idx: int = 0
        self.mode_idx: int = 0

        self.csp: KakuroCSP = KakuroCSP.from_json(self.map_files[self.map_idx])
        self.result: KakuroSolveResult = self._compute_trace()
        self.step_idx: int = 0

        self.auto_play: bool = False
        self.step_delay_ms: int = 260
        self.last_tick: int = 0

        self.buttons: List[ControlButton] = self._create_buttons()

    def _compute_trace(self) -> KakuroSolveResult:
        solver = KakuroSolver(
            mode=self.modes[self.mode_idx],
            record_steps=True,
            max_recorded_steps=3000,
        )
        res = solver.solve(self.csp)
        if not res.steps_trace:
            res.steps_trace.append(
                SolverStep(
                    step_type="PREPROCESS",
                    focus_pos=None,
                    value=None,
                    assignment={},
                    domains={p: list(range(1, 10)) for p in self.csp.ordered_positions},
                    message="Ready.",
                )
            )
        return res

    def _reload_problem(self) -> None:
        self.auto_play = False
        self.csp = KakuroCSP.from_json(self.map_files[self.map_idx])
        self.result = self._compute_trace()
        self.step_idx = 0

    def _create_buttons(self) -> List[ControlButton]:
        px = 716
        return [
            ControlButton(pygame.Rect(px, 68, 416, 32), "Switch Board", "NEXT_MAP"),
            ControlButton(pygame.Rect(px, 126, 416, 32), "Switch Mode", "NEXT_MODE"),
            ControlButton(pygame.Rect(px, 180, 132, 36), "Auto Play", "TOGGLE_PLAY"),
            ControlButton(pygame.Rect(px + 142, 180, 132, 36), "Step <", "STEP_PREV"),
            ControlButton(pygame.Rect(px + 284, 180, 132, 36), "Step >", "STEP_NEXT"),
            ControlButton(pygame.Rect(px, 226, 132, 32), "Reset (0)", "RESET"),
            ControlButton(pygame.Rect(px + 142, 226, 132, 32), "Speed -", "SLOWER"),
            ControlButton(pygame.Rect(px + 284, 226, 132, 32), "Speed +", "FASTER"),
            ControlButton(pygame.Rect(px, 266, 416, 30), "Jump to Solved State", "JUMP_END"),
        ]

    def _handle_action(self, action_id: str) -> None:
        max_idx = len(self.result.steps_trace) - 1
        if action_id == "NEXT_MAP":
            self.map_idx = (self.map_idx + 1) % len(self.map_files)
            self._reload_problem()
        elif action_id == "NEXT_MODE":
            self.mode_idx = (self.mode_idx + 1) % len(self.modes)
            self._reload_problem()
        elif action_id == "TOGGLE_PLAY":
            self.auto_play = not self.auto_play
            self.last_tick = pygame.time.get_ticks()
        elif action_id == "STEP_PREV":
            self.auto_play = False
            self.step_idx = max(0, self.step_idx - 1)
        elif action_id == "STEP_NEXT":
            self.auto_play = False
            self.step_idx = min(max_idx, self.step_idx + 1)
        elif action_id == "RESET":
            self.auto_play = False
            self.step_idx = 0
        elif action_id == "SLOWER":
            self.step_delay_ms = min(1200, self.step_delay_ms + 70)
        elif action_id == "FASTER":
            self.step_delay_ms = max(25, self.step_delay_ms - 70)
        elif action_id == "JUMP_END":
            self.auto_play = False
            self.step_idx = max_idx

    def render_frame(self) -> None:
        self.screen.fill(self.BG_COLOR)
        step = self.result.steps_trace[self.step_idx]

        header = self.font_title.render(
            f"KAKURO CSP VISUALIZER  |  {self.csp.name}  |  Step {self.step_idx + 1}/{len(self.result.steps_trace)}",
            True,
            self.TEXT_LIGHT,
        )
        self.screen.blit(header, (self.GRID_ORIGIN_X, 20))

        self._draw_kakuro_grid(step)
        self._draw_sidebar(step)
        pygame.display.flip()

    def _draw_kakuro_grid(self, step: SolverStep) -> None:
        rows, cols = self.csp.rows, self.csp.cols
        cell_px = min(self.GRID_AREA_SIZE // cols, self.GRID_AREA_SIZE // rows)
        gw, gh = cell_px * cols, cell_px * rows
        ox = self.GRID_ORIGIN_X + (self.GRID_AREA_SIZE - gw) // 2
        oy = self.GRID_ORIGIN_Y + (self.GRID_AREA_SIZE - gh) // 2

        font_val = pygame.font.SysFont("Arial", max(18, int(cell_px * 0.44)), bold=True)
        font_clue = pygame.font.SysFont("Arial", max(11, int(cell_px * 0.21)), bold=True)
        font_cand = pygame.font.SysFont("Consolas", max(9, int(cell_px * 0.19)), bold=True)

        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(ox + c * cell_px, oy + r * cell_px, cell_px, cell_px)
                spec = self.csp.raw_grid[r][c]
                pos = (r, c)

                if spec == "B":
                    pygame.draw.rect(self.screen, self.BLACK_CELL, rect)
                    pygame.draw.rect(self.screen, self.GRID_BORDER, rect, 1)
                elif isinstance(spec, dict):
                    pygame.draw.rect(self.screen, self.BLACK_CELL, rect)
                    pygame.draw.line(self.screen, self.CLUE_LINE, rect.topleft, rect.bottomright, 2)
                    pygame.draw.rect(self.screen, self.GRID_BORDER, rect, 1)

                    if "across" in spec:
                        ac_surf = font_clue.render(str(spec["across"]), True, (255, 226, 130))
                        ac_rect = ac_surf.get_rect(
                            center=(rect.left + int(cell_px * 0.70), rect.top + int(cell_px * 0.28))
                        )
                        self.screen.blit(ac_surf, ac_rect)

                    if "down" in spec:
                        dn_surf = font_clue.render(str(spec["down"]), True, (150, 222, 255))
                        dn_rect = dn_surf.get_rect(
                            center=(rect.left + int(cell_px * 0.30), rect.top + int(cell_px * 0.72))
                        )
                        self.screen.blit(dn_surf, dn_rect)
                else:
                    # Playable white cell: choose background & border based on current CSP event
                    bg = self.WHITE_CELL
                    border_col = self.GRID_BORDER
                    border_w = 1

                    if step.step_type == "SOLVED":
                        bg = self.SOLVED_BG
                    elif step.focus_pos == pos and step.step_type == "BACKTRACK":
                        bg = self.BACKTRACK_BG
                        border_col = self.BACKTRACK_BORDER
                        border_w = 3
                    elif pos in step.pruned:
                        bg = self.PRUNE_BG
                        border_col = self.PRUNE_BORDER
                        border_w = 3
                    elif step.focus_pos == pos:
                        bg = self.FOCUS_BG
                        border_col = self.FOCUS_BORDER
                        border_w = 3

                    pygame.draw.rect(self.screen, bg, rect)

                    if pos in step.assignment:
                        val_surf = font_val.render(str(step.assignment[pos]), True, self.ASSIGNED_TEXT)
                        self.screen.blit(val_surf, val_surf.get_rect(center=rect.center))
                    else:
                        # Render 3x3 candidate domain grid {1..9}
                        active_dom = set(step.domains.get(pos, []))
                        just_pruned = set(step.pruned.get(pos, []))
                        sub = cell_px / 3.0
                        for digit in range(1, 10):
                            dr_idx = (digit - 1) // 3
                            dc_idx = (digit - 1) % 3
                            cx = rect.left + int((dc_idx + 0.5) * sub)
                            cy = rect.top + int((dr_idx + 0.5) * sub)
                            if digit in just_pruned:
                                d_surf = font_cand.render(str(digit), True, self.CAND_PRUNED_NOW)
                                self.screen.blit(d_surf, d_surf.get_rect(center=(cx, cy)))
                            elif digit in active_dom:
                                d_surf = font_cand.render(str(digit), True, self.CAND_ACTIVE)
                                self.screen.blit(d_surf, d_surf.get_rect(center=(cx, cy)))

                    pygame.draw.rect(self.screen, border_col, rect, border_w)

    def _draw_sidebar(self, step: SolverStep) -> None:
        panel = pygame.Rect(702, 20, 442, 720)
        pygame.draw.rect(self.screen, self.PANEL_BG, panel, border_radius=8)
        pygame.draw.rect(self.screen, self.PANEL_BORDER, panel, width=1, border_radius=8)

        self.screen.blit(
            self.font_ui.render("CSP SOLVER CONTROLS & TELEMETRY", True, self.TEXT_LIGHT),
            (716, 34),
        )
        self.screen.blit(
            self.font_small.render("Puzzle Board (click to switch):", True, self.TEXT_MUTED),
            (716, 52),
        )
        self.screen.blit(
            self.font_small.render("Propagation & Heuristic Mode:", True, self.TEXT_MUTED),
            (716, 108),
        )

        dyn_text = {
            "NEXT_MAP": f"Board: {self.csp.name}",
            "NEXT_MODE": f"Mode: {self.modes[self.mode_idx].value}",
            "TOGGLE_PLAY": "Pause" if self.auto_play else "Auto Play",
        }
        for btn in self.buttons:
            bg = (46, 98, 156) if (btn.action_id == "TOGGLE_PLAY" and self.auto_play) else (42, 50, 68)
            pygame.draw.rect(self.screen, bg, btn.rect, border_radius=5)
            pygame.draw.rect(self.screen, self.PANEL_BORDER, btn.rect, width=1, border_radius=5)
            lbl = self.font_small.render(dyn_text.get(btn.action_id, btn.label), True, self.TEXT_LIGHT)
            self.screen.blit(lbl, lbl.get_rect(center=btn.rect.center))

        # Legend
        y = 312
        self.screen.blit(self.font_ui.render("VISUALIZATION COLOR LEGEND", True, self.ACCENT_GREEN), (716, y))
        y += 24
        legend_items = [
            (self.FOCUS_BORDER, "Blue Border   : Variable selected (MRV + Degree)"),
            (self.PRUNE_BORDER, "Red Highlight : Candidates pruned by Propagation"),
            (self.BACKTRACK_BORDER, "Orange Border : Dead-end & Backtrack undo"),
            (self.ACCENT_GREEN, "Green Tint    : Complete verified CSP solution"),
        ]
        for col, text in legend_items:
            pygame.draw.rect(self.screen, col, (716, y + 2, 14, 14), border_radius=3)
            self.screen.blit(self.font_small.render(text, True, self.TEXT_LIGHT), (738, y))
            y += 21

        # Solver Metrics
        y += 10
        self.screen.blit(self.font_ui.render("SOLVER PERFORMANCE METRICS", True, self.ACCENT_GREEN), (716, y))
        y += 24
        stats_lines = [
            f"Variables Assigned : {len(step.assignment)} / {len(self.csp.variables)}",
            f"Runs (Constraints) : {len(self.csp.runs)} (AllDiff + Exact Sum)",
            f"Current Event Type : {step.step_type}",
            f"Nodes (Step/Total) : {step.nodes_so_far} / {self.result.nodes_explored}",
            f"Backtracks         : {step.backtracks_so_far} / {self.result.backtracks}",
            f"Total Pruned Cands : {self.result.pruned_values}",
            f"Total Solve Time   : {self.result.elapsed_ms:.2f} ms (Verified={self.result.valid_verified})",
            f"Playback Delay     : {self.step_delay_ms} ms / step",
        ]
        for s_line in stats_lines:
            self.screen.blit(self.font_mono.render(s_line, True, self.TEXT_LIGHT), (716, y))
            y += 20

        # Current Step Explanation Box
        y += 10
        self.screen.blit(self.font_ui.render("LIVE STEP EXPLANATION", True, self.TEXT_LIGHT), (716, y))
        y += 22
        for wrapped in self._wrap_text(step.message, 48):
            self.screen.blit(self.font_mono.render(wrapped, True, (255, 226, 130)), (716, y))
            y += 18

    @staticmethod
    def _wrap_text(text: str, width: int) -> List[str]:
        words = text.split()
        lines: List[str] = []
        cur = ""
        for w in words:
            if len(cur) + len(w) + 1 <= width:
                cur = f"{cur} {w}".strip()
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

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
                            self._handle_action(btn.action_id)
                            break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_RIGHT:
                        self._handle_action("STEP_NEXT")
                    elif event.key == pygame.K_LEFT:
                        self._handle_action("STEP_PREV")
                    elif event.key == pygame.K_SPACE:
                        self._handle_action("TOGGLE_PLAY")

            if self.auto_play:
                if self.step_idx < len(self.result.steps_trace) - 1:
                    if now - self.last_tick >= self.step_delay_ms:
                        self.step_idx += 1
                        self.last_tick = now
                else:
                    self.auto_play = False

            self.render_frame()
            self.clock.tick(30)

        pygame.quit()
