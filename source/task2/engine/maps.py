"""Predefined Tier-1 (Endgame Micro-Scenarios) and Tier-2 (Full Battle Arenas) maps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

from ..config import (
    BASE_INITIAL_HP,
    DIR_DOWN,
    DIR_LEFT,
    DIR_RIGHT,
    DIR_UP,
    PLAYER_MAX,
    PLAYER_MIN,
    TANK_INITIAL_HP,
    WALL_INITIAL_HP,
)
from .entities import Base, BrickWall, Tank
from .game_state import GameState


@dataclass(frozen=True)
class MapScenario:
    """Metadata and factory function for a reproducible Tank Battle scenario."""

    key: str
    title: str
    tier: str
    description: str
    builder: Callable[[], GameState]


def _parse_ascii_map(
    grid_lines: List[str],
    max_facing: str = DIR_UP,
    min_facing: str = DIR_DOWN,
    max_tank_hp: int = TANK_INITIAL_HP,
    min_tank_hp: int = TANK_INITIAL_HP,
    max_base_hp: int = BASE_INITIAL_HP,
    min_base_hp: int = BASE_INITIAL_HP,
    wall_hp: int = WALL_INITIAL_HP,
    max_plies: int = 120,
) -> GameState:
    """Build a GameState from an ASCII legend:
    '.' = empty, 'B' = brick wall, '#' = steel wall,
    '1' = MAX tank, '2' = MIN tank, 'M' = MAX base, 'N' = MIN base.
    """
    rows = len(grid_lines)
    cols = len(grid_lines[0])
    tanks: Dict[int, Tank] = {}
    bases: Dict[int, Base] = {}
    brick_walls: Dict[Tuple[int, int], BrickWall] = {}
    steel_set = set()

    for r, line in enumerate(grid_lines):
        if len(line) != cols:
            raise ValueError(f"Inconsistent map row length at row {r}.")
        for c, ch in enumerate(line):
            if ch == "B":
                brick_walls[(r, c)] = BrickWall(r, c, hp=wall_hp)
            elif ch == "#":
                steel_set.add((r, c))
            elif ch == "1":
                tanks[PLAYER_MAX] = Tank(PLAYER_MAX, r, c, facing=max_facing, hp=max_tank_hp)
            elif ch == "2":
                tanks[PLAYER_MIN] = Tank(PLAYER_MIN, r, c, facing=min_facing, hp=min_tank_hp)
            elif ch == "M":
                bases[PLAYER_MAX] = Base(PLAYER_MAX, r, c, hp=max_base_hp)
            elif ch == "N":
                bases[PLAYER_MIN] = Base(PLAYER_MIN, r, c, hp=min_base_hp)

    if PLAYER_MAX not in tanks or PLAYER_MIN not in tanks:
        raise ValueError("Map must specify both '1' (MAX tank) and '2' (MIN tank).")
    if PLAYER_MAX not in bases or PLAYER_MIN not in bases:
        raise ValueError("Map must specify both 'M' (MAX base) and 'N' (MIN base).")

    return GameState(
        rows=rows,
        cols=cols,
        tanks=tanks,
        bases=bases,
        brick_walls=brick_walls,
        steel_walls=frozenset(steel_set),
        current_player=PLAYER_MAX,
        ply=0,
        max_plies=max_plies,
    )


# ---------------------------------------------------------------------------
# Tier 1: Tactical Endgame Micro-Scenarios (Allows exact terminal comparison
#         across ALL 4 algorithms including pure Minimax and pure Alpha-Beta)
# ---------------------------------------------------------------------------

def build_endgame_duel_7x7() -> GameState:
    lines = [
        "...N...",
        "..B.B..",
        "...2...",
        ".#...#.",
        "...1...",
        "..B.B..",
        "...M...",
    ]
    return _parse_ascii_map(
        lines,
        max_facing=DIR_UP,
        min_facing=DIR_DOWN,
        max_tank_hp=1,
        min_tank_hp=1,
        max_base_hp=2,
        min_base_hp=2,
        wall_hp=1,
        max_plies=6,
    )


def build_endgame_base_race_7x7() -> GameState:
    lines = [
        "N....2.",
        ".B..B..",
        "...#...",
        ".1.....",
        "...#...",
        "..B..B.",
        ".....M.",
    ]
    return _parse_ascii_map(
        lines,
        max_facing=DIR_UP,
        min_facing=DIR_LEFT,
        max_tank_hp=2,
        min_tank_hp=2,
        max_base_hp=1,
        min_base_hp=1,
        wall_hp=1,
        max_plies=6,
    )


def build_endgame_ambush_7x7() -> GameState:
    lines = [
        "...N...",
        ".B...B.",
        "..2....",
        "...B...",
        "..1....",
        ".B...B.",
        "...M...",
    ]
    return _parse_ascii_map(
        lines,
        max_facing=DIR_RIGHT,
        min_facing=DIR_DOWN,
        max_tank_hp=1,
        min_tank_hp=1,
        max_base_hp=2,
        min_base_hp=1,
        wall_hp=1,
        max_plies=6,
    )


# ---------------------------------------------------------------------------
# Tier 2: Full-Scale Battle City Arenas (Tank=6 HP, Base=9 HP, Wall=3 HP)
# ---------------------------------------------------------------------------

def build_classic_arena_9x9() -> GameState:
    lines = [
        "...BNB...",
        "...B.B...",
        ".B..2..B.",
        ".#..B..#.",
        "...B.B...",
        ".#..B..#.",
        ".B..1..B.",
        "...B.B...",
        "...BMB...",
    ]
    return _parse_ascii_map(lines, max_facing=DIR_UP, min_facing=DIR_DOWN, max_plies=140)


def build_open_crossfire_9x9() -> GameState:
    lines = [
        "....N....",
        "..B...B..",
        "....2....",
        ".B..#..B.",
        ".........",
        ".B..#..B.",
        "....1....",
        "..B...B..",
        "....M....",
    ]
    return _parse_ascii_map(lines, max_facing=DIR_UP, min_facing=DIR_DOWN, max_plies=120)


def build_fortress_11x11() -> GameState:
    lines = [
        "....BNB....",
        "....BBB....",
        ".B...2...B.",
        ".#B.....B#.",
        "...B...B...",
        "..#..B..#..",
        "...B...B...",
        ".#B.....B#.",
        ".B...1...B.",
        "....BBB....",
        "....BMB....",
    ]
    return _parse_ascii_map(lines, max_facing=DIR_UP, min_facing=DIR_DOWN, max_plies=160)


SCENARIOS: List[MapScenario] = [
    MapScenario(
        key="classic_9x9",
        title="Classic Battle City (9x9)",
        tier="tier2",
        description="Standard 9x9 symmetrical arena with brick base shields (Tank=6, Base=9, Wall=3).",
        builder=build_classic_arena_9x9,
    ),
    MapScenario(
        key="crossfire_9x9",
        title="Open Crossfire (9x9)",
        tier="tier2",
        description="Open firing lanes favoring aggressive line-of-sight positioning and dodging.",
        builder=build_open_crossfire_9x9,
    ),
    MapScenario(
        key="fortress_11x11",
        title="Fortress Siege (11x11)",
        tier="tier2",
        description="Full 11x11 Battle City fortress with multi-layer brick walls and steel pillars.",
        builder=build_fortress_11x11,
    ),
    MapScenario(
        key="endgame_duel_7x7",
        title="Endgame Center Duel (7x7)",
        tier="tier1",
        description="Low-HP tactical endgame allowing exact comparison with pure Minimax/Alpha-Beta.",
        builder=build_endgame_duel_7x7,
    ),
    MapScenario(
        key="endgame_race_7x7",
        title="Endgame Base Race (7x7)",
        tier="tier1",
        description="Asymmetric base-sniping endgame race (horizon=6 plies).",
        builder=build_endgame_base_race_7x7,
    ),
    MapScenario(
        key="endgame_ambush_7x7",
        title="Endgame Corner Ambush (7x7)",
        tier="tier1",
        description="Close-quarters evasion and counter-fire tactical scenario (horizon=6 plies).",
        builder=build_endgame_ambush_7x7,
    ),
]


def get_all_scenarios(tier: str | None = None) -> List[MapScenario]:
    if tier is None:
        return list(SCENARIOS)
    return [s for s in SCENARIOS if s.tier == tier]


def get_scenario(key: str) -> MapScenario:
    for s in SCENARIOS:
        if s.key == key:
            return s
    raise KeyError(f"Unknown scenario key: {key}")
