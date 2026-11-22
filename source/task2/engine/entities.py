"""Immutable game entities used by the Tank Battle transition model."""

from __future__ import annotations

from dataclasses import dataclass

from ..config import (
    BASE_INITIAL_HP,
    DAMAGE_PER_HIT,
    DIRECTIONS,
    PLAYER_IDS,
    TANK_INITIAL_HP,
    WALL_INITIAL_HP,
    DIR_UP,
)


class Entity:
    """Common behavior for immutable, grid-positioned game entities."""

    row: int
    col: int
    hp: int

    @property
    def destructible(self) -> bool:
        return True

    @property
    def is_alive(self) -> bool:
        return not self.destructible or self.hp > 0

    def damaged(self, amount: int = DAMAGE_PER_HIT) -> tuple[Entity, bool]:
        """Return a damaged copy and whether this hit destroyed the entity."""
        if amount < 0:
            raise ValueError("Damage amount cannot be negative.")
        if not self.destructible or amount == 0:
            return self, False

        updated_hp = max(0, self.hp - amount)
        if updated_hp == self.hp:
            return self, False
        return self._with_hp(updated_hp), self.hp > 0 and updated_hp == 0

    def _with_hp(self, hp: int) -> Entity:
        raise NotImplementedError(f"{type(self).__name__} does not implement immutable damage.")


@dataclass(frozen=True, slots=True)
class Tank(Entity):
    """A player's tank, position, facing, and remaining hit points."""

    player_id: int
    row: int
    col: int
    facing: str = DIR_UP
    hp: int = TANK_INITIAL_HP

    def __post_init__(self) -> None:
        if self.player_id not in PLAYER_IDS:
            raise ValueError(f"Unknown player ID: {self.player_id}")
        if self.facing not in DIRECTIONS:
            raise ValueError(f"Unknown tank direction: {self.facing}")
        _validate_position_and_hp(self.row, self.col, self.hp)

    def _with_hp(self, hp: int) -> Tank:
        return Tank(self.player_id, self.row, self.col, self.facing, hp)

    def clone(self) -> Tank:
        return self


@dataclass(frozen=True, slots=True)
class Base(Entity):
    """A player's destructible headquarters."""

    player_id: int
    row: int
    col: int
    hp: int = BASE_INITIAL_HP

    def __post_init__(self) -> None:
        if self.player_id not in PLAYER_IDS:
            raise ValueError(f"Unknown player ID: {self.player_id}")
        _validate_position_and_hp(self.row, self.col, self.hp)

    def _with_hp(self, hp: int) -> Base:
        return Base(self.player_id, self.row, self.col, hp)

    def clone(self) -> Base:
        return self


@dataclass(frozen=True, slots=True)
class BrickWall(Entity):
    """A destructible wall segment."""

    row: int
    col: int
    hp: int = WALL_INITIAL_HP

    def __post_init__(self) -> None:
        _validate_position_and_hp(self.row, self.col, self.hp)

    def _with_hp(self, hp: int) -> BrickWall:
        return BrickWall(self.row, self.col, hp)

    def clone(self) -> BrickWall:
        return self


@dataclass(frozen=True, slots=True)
class SteelWall(Entity):
    """An indestructible wall segment."""

    row: int
    col: int

    @property
    def hp(self) -> int:
        return 999

    @property
    def destructible(self) -> bool:
        return False

    def __post_init__(self) -> None:
        if self.row < 0 or self.col < 0:
            raise ValueError("Entity coordinates cannot be negative.")

    def _with_hp(self, hp: int) -> SteelWall:
        return self

    def clone(self) -> SteelWall:
        return self


@dataclass(frozen=True, slots=True)
class Bullet:
    """A persistent projectile advanced cell-by-cell by the game engine."""

    owner_id: int
    row: int
    col: int
    direction: str
    active: bool = True

    def __post_init__(self) -> None:
        if self.owner_id not in PLAYER_IDS:
            raise ValueError(f"Unknown bullet owner: {self.owner_id}")
        if self.direction not in DIRECTIONS:
            raise ValueError(f"Unknown bullet direction: {self.direction}")
        if self.row < 0 or self.col < 0:
            raise ValueError("Bullet coordinates cannot be negative.")

    def clone(self) -> Bullet:
        return self


def _validate_position_and_hp(row: int, col: int, hp: int) -> None:
    if row < 0 or col < 0:
        raise ValueError("Entity coordinates cannot be negative.")
    if hp < 0:
        raise ValueError("Hit points cannot be negative.")
