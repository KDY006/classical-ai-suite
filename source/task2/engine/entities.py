"""Object-oriented game entities for Tank Battle."""

from __future__ import annotations

from dataclasses import dataclass

from ..config import (
    BASE_INITIAL_HP,
    DAMAGE_PER_HIT,
    TANK_INITIAL_HP,
    WALL_INITIAL_HP,
)


@dataclass
class Entity:
    """Base class for grid-positioned entities."""

    row: int
    col: int
    hp: int
    destructible: bool = True

    @property
    def is_alive(self) -> bool:
        return (not self.destructible) or (self.hp > 0)

    def take_damage(self, amount: int = DAMAGE_PER_HIT) -> bool:
        """Apply damage and return True if the entity was destroyed by this hit."""
        if not self.destructible:
            return False
        self.hp = max(0, self.hp - amount)
        return self.hp == 0


@dataclass
class Tank(Entity):
    """Controllable player tank with position, orientation, and HP."""

    player_id: int = 1
    facing: str = "UP"

    def __init__(
        self,
        player_id: int,
        row: int,
        col: int,
        facing: str = "UP",
        hp: int = TANK_INITIAL_HP,
    ) -> None:
        super().__init__(row=row, col=col, hp=hp, destructible=True)
        self.player_id = player_id
        self.facing = facing

    def clone(self) -> "Tank":
        return Tank(
            player_id=self.player_id,
            row=self.row,
            col=self.col,
            facing=self.facing,
            hp=self.hp,
        )


@dataclass
class Base(Entity):
    """Headquarters structure that must be defended by its owning player."""

    player_id: int = 1

    def __init__(self, player_id: int, row: int, col: int, hp: int = BASE_INITIAL_HP) -> None:
        super().__init__(row=row, col=col, hp=hp, destructible=True)
        self.player_id = player_id

    def clone(self) -> "Base":
        return Base(player_id=self.player_id, row=self.row, col=self.col, hp=self.hp)


@dataclass
class BrickWall(Entity):
    """Destructible brick wall segment with initial HP = 3."""

    def __init__(self, row: int, col: int, hp: int = WALL_INITIAL_HP) -> None:
        super().__init__(row=row, col=col, hp=hp, destructible=True)

    def clone(self) -> "BrickWall":
        return BrickWall(row=self.row, col=self.col, hp=self.hp)


@dataclass
class SteelWall(Entity):
    """Indestructible terrain barrier that blocks movement and stops bullets."""

    def __init__(self, row: int, col: int) -> None:
        super().__init__(row=row, col=col, hp=999, destructible=False)

    def clone(self) -> "SteelWall":
        return SteelWall(row=self.row, col=self.col)


@dataclass
class Bullet:
    """Projectile traveling 3 cells per game cycle in a fixed direction."""

    owner_id: int
    row: int
    col: int
    direction: str
    active: bool = True

    def clone(self) -> "Bullet":
        return Bullet(
            owner_id=self.owner_id,
            row=self.row,
            col=self.col,
            direction=self.direction,
            active=self.active,
        )
