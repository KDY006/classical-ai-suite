"""Core constants, actions, directions, and entity specifications for Tank Battle."""

from __future__ import annotations

from typing import Dict, Tuple

# Players in the Zero-Sum Game
PLAYER_MAX: int = 1
PLAYER_MIN: int = 2

# Six discrete tank actions defined in the specification
MOVE_UP: str = "MOVE_UP"
MOVE_DOWN: str = "MOVE_DOWN"
MOVE_LEFT: str = "MOVE_LEFT"
MOVE_RIGHT: str = "MOVE_RIGHT"
FIRE: str = "FIRE"
STAY: str = "STAY"

ALL_ACTIONS: Tuple[str, ...] = (
    MOVE_UP,
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
    FIRE,
    STAY,
)

# Directional vectors (d_row, d_col)
DIR_UP: str = "UP"
DIR_DOWN: str = "DOWN"
DIR_LEFT: str = "LEFT"
DIR_RIGHT: str = "RIGHT"

DIRECTION_DELTAS: Dict[str, Tuple[int, int]] = {
    DIR_UP: (-1, 0),
    DIR_DOWN: (1, 0),
    DIR_LEFT: (0, -1),
    DIR_RIGHT: (0, 1),
}

MOVE_ACTION_TO_DIR: Dict[str, str] = {
    MOVE_UP: DIR_UP,
    MOVE_DOWN: DIR_DOWN,
    MOVE_LEFT: DIR_LEFT,
    MOVE_RIGHT: DIR_RIGHT,
}

# Predefined entity health and combat parameters from Task 2 specification table
TANK_INITIAL_HP: int = 6
BASE_INITIAL_HP: int = 9
WALL_INITIAL_HP: int = 3
DAMAGE_PER_HIT: int = 1
BULLET_SPEED_PER_CYCLE: int = 3

# Zero-Sum terminal utility values
WIN_UTILITY: float = 1000.0
LOSS_UTILITY: float = -1000.0
DRAW_UTILITY: float = 0.0
