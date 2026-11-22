"""Rules shared by the Tank Battle engine, agents, and user interface."""

from __future__ import annotations

from typing import Dict, Final, Tuple

PLAYER_MAX: Final[int] = 1
PLAYER_MIN: Final[int] = 2
PLAYER_IDS: Final[Tuple[int, int]] = (PLAYER_MAX, PLAYER_MIN)

MOVE_UP: Final[str] = "MOVE_UP"
MOVE_DOWN: Final[str] = "MOVE_DOWN"
MOVE_LEFT: Final[str] = "MOVE_LEFT"
MOVE_RIGHT: Final[str] = "MOVE_RIGHT"
FIRE: Final[str] = "FIRE"
STAY: Final[str] = "STAY"

ALL_ACTIONS: Final[Tuple[str, ...]] = (
    MOVE_UP,
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
    FIRE,
    STAY,
)

DIR_UP: Final[str] = "UP"
DIR_DOWN: Final[str] = "DOWN"
DIR_LEFT: Final[str] = "LEFT"
DIR_RIGHT: Final[str] = "RIGHT"
DIRECTIONS: Final[Tuple[str, ...]] = (DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT)

DIRECTION_DELTAS: Final[Dict[str, Tuple[int, int]]] = {
    DIR_UP: (-1, 0),
    DIR_DOWN: (1, 0),
    DIR_LEFT: (0, -1),
    DIR_RIGHT: (0, 1),
}

MOVE_ACTION_TO_DIR: Final[Dict[str, str]] = {
    MOVE_UP: DIR_UP,
    MOVE_DOWN: DIR_DOWN,
    MOVE_LEFT: DIR_LEFT,
    MOVE_RIGHT: DIR_RIGHT,
}

TANK_INITIAL_HP: Final[int] = 6
BASE_INITIAL_HP: Final[int] = 9
WALL_INITIAL_HP: Final[int] = 3
DAMAGE_PER_HIT: Final[int] = 1
BULLET_SPEED_PER_CYCLE: Final[int] = 3

WIN_UTILITY: Final[float] = 1000.0
LOSS_UTILITY: Final[float] = -1000.0
DRAW_UTILITY: Final[float] = 0.0
