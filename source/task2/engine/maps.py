"""Validated predefined maps for endgame experiments and full arenas."""

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


@dataclass(frozen=True, slots=True)
class MapScenario:
    """Metadata and a fresh-state factory for a reproducible scenario."""

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
    """Parse ``. B # 1 2 M N`` as empty, brick, steel, tanks, and bases."""
    if not grid_lines or not grid_lines[0]:
        raise ValueError("Map must contain at least one non-empty row.")
    rows = len(grid_lines)
    cols = len(grid_lines[0])
    tanks: Dict[int, Tank] = {}
    bases: Dict[int, Base] = {}
    brick_walls: Dict[Tuple[int, int], BrickWall] = {}
    steel_walls: set[Tuple[int, int]] = set()
    markers: Dict[str, int] = {marker: 0 for marker in "12MN"}
    accepted = set(".B#12MN")

    for row, line in enumerate(grid_lines):
        if len(line) != cols:
            raise ValueError(f"Inconsistent map row length at row {row}.")
        for col, marker in enumerate(line):
            if marker not in accepted:
                raise ValueError(f"Unknown map marker {marker!r} at ({row}, {col}).")
            if marker in markers:
                markers[marker] += 1
            if marker == "B":
                brick_walls[(row, col)] = BrickWall(row, col, wall_hp)
            elif marker == "#":
                steel_walls.add((row, col))
            elif marker == "1":
                tanks[PLAYER_MAX] = Tank(PLAYER_MAX, row, col, max_facing, max_tank_hp)
            elif marker == "2":
                tanks[PLAYER_MIN] = Tank(PLAYER_MIN, row, col, min_facing, min_tank_hp)
            elif marker == "M":
                bases[PLAYER_MAX] = Base(PLAYER_MAX, row, col, max_base_hp)
            elif marker == "N":
                bases[PLAYER_MIN] = Base(PLAYER_MIN, row, col, min_base_hp)

    invalid_markers = {marker: count for marker, count in markers.items() if count != 1}
    if invalid_markers:
        raise ValueError(f"Map must contain exactly one of each tank/base marker: {invalid_markers}")

    return GameState(
        rows=rows,
        cols=cols,
        tanks=tanks,
        bases=bases,
        brick_walls=brick_walls,
        steel_walls=frozenset(steel_walls),
        current_player=PLAYER_MAX,
        ply=0,
        max_plies=max_plies,
    )


def build_endgame_duel_7x7() -> GameState:
    return _parse_ascii_map(
        [
            "...N...",
            "..B.B..",
            "...2...",
            ".#...#.",
            "...1...",
            "..B.B..",
            "...M...",
        ],
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
    return _parse_ascii_map(
        [
            "N....2.",
            ".B..B..",
            "...#...",
            ".1.....",
            "...#...",
            "..B..B.",
            ".....M.",
        ],
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
    return _parse_ascii_map(
        [
            "...N...",
            ".B...B.",
            "..2....",
            "...B...",
            "..1....",
            ".B...B.",
            "...M...",
        ],
        max_facing=DIR_RIGHT,
        min_facing=DIR_DOWN,
        max_tank_hp=1,
        min_tank_hp=1,
        max_base_hp=2,
        min_base_hp=1,
        wall_hp=1,
        max_plies=6,
    )


def build_classic_arena_9x9() -> GameState:
    return _parse_ascii_map(
        [
            "...BNB...",
            "...B.B...",
            ".B..2..B.",
            ".#..B..#.",
            "...B.B...",
            ".#..B..#.",
            ".B..1..B.",
            "...B.B...",
            "...BMB...",
        ],
        max_facing=DIR_UP,
        min_facing=DIR_DOWN,
        max_plies=140,
    )


def build_open_crossfire_9x9() -> GameState:
    return _parse_ascii_map(
        [
            "....N....",
            "..B...B..",
            "....2....",
            ".B..#..B.",
            ".........",
            ".B..#..B.",
            "....1....",
            "..B...B..",
            "....M....",
        ],
        max_facing=DIR_UP,
        min_facing=DIR_DOWN,
        max_plies=120,
    )


def build_fortress_11x11() -> GameState:
    return _parse_ascii_map(
        [
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
        ],
        max_facing=DIR_UP,
        min_facing=DIR_DOWN,
        max_plies=160,
    )


SCENARIOS: List[MapScenario] = [
    MapScenario(
        key="classic_9x9",
        title="Classic Battle City (9x9)",
        tier="tier2",
        description="Standard full-health 9x9 arena with brick base shields.",
        builder=build_classic_arena_9x9,
    ),
    MapScenario(
        key="crossfire_9x9",
        title="Open Crossfire (9x9)",
        tier="tier2",
        description="Open firing lanes favoring line-of-sight positioning and dodging.",
        builder=build_open_crossfire_9x9,
    ),
    MapScenario(
        key="fortress_11x11",
        title="Fortress Siege (11x11)",
        tier="tier2",
        description="Full-health 11x11 arena with layered brick walls and steel barriers.",
        builder=build_fortress_11x11,
    ),
    MapScenario(
        key="endgame_duel_7x7",
        title="Endgame Center Duel (7x7)",
        tier="tier1",
        description="Low-HP tactical endgame for exact search comparisons.",
        builder=build_endgame_duel_7x7,
    ),
    MapScenario(
        key="endgame_race_7x7",
        title="Endgame Base Race (7x7)",
        tier="tier1",
        description="Asymmetric base-sniping endgame with a six-ply horizon.",
        builder=build_endgame_base_race_7x7,
    ),
    MapScenario(
        key="endgame_ambush_7x7",
        title="Endgame Corner Ambush (7x7)",
        tier="tier1",
        description="Close-quarters evasion and counter-fire endgame.",
        builder=build_endgame_ambush_7x7,
    ),
]


def get_all_scenarios(tier: str | None = None) -> List[MapScenario]:
    if tier is None:
        return list(SCENARIOS)
    return [scenario for scenario in SCENARIOS if scenario.tier == tier]


def get_scenario(key: str) -> MapScenario:
    for scenario in SCENARIOS:
        if scenario.key == key:
            return scenario
    raise KeyError(f"Unknown scenario key: {key}")
