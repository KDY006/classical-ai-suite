"""Cac lop thuc the bat bien tren luoi trong tro choi Dau Tang."""

from __future__ import annotations

from dataclasses import dataclass

from ..config import (
    BASE_INITIAL_HP,
    DAMAGE_PER_HIT,
    DIRECTIONS,
    DIR_UP,
    PLAYER_IDS,
    TANK_INITIAL_HP,
    WALL_INITIAL_HP,
)


class Entity:
    """Hanh vi dung chung cho cac thuc the bat bien dat tren o luoi."""

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
        """Tra ve ban sao sau khi nhan sat thuong va co bi pha huy hay khong."""
        if amount < 0:
            raise ValueError("Luong sat thuong khong duoc am")
        if not self.destructible or amount == 0:
            return self, False

        updated_hp = max(0, self.hp - amount)
        if updated_hp == self.hp:
            return self, False
        return self._with_hp(updated_hp), self.hp > 0 and updated_hp == 0

    def _with_hp(self, hp: int) -> Entity:
        raise NotImplementedError(f"{type(self).__name__} chua cai dat cap nhat HP bat bien")


@dataclass(frozen=True, slots=True)
class Tank(Entity):
    """Thuc the xe tang cua mot phe gom toa do, huong quay nong va HP."""

    player_id: int
    row: int
    col: int
    facing: str = DIR_UP
    hp: int = TANK_INITIAL_HP

    def __post_init__(self) -> None:
        if self.player_id not in PLAYER_IDS:
            raise ValueError(f"Ma nguoi choi khong hop le: {self.player_id}")
        if self.facing not in DIRECTIONS:
            raise ValueError(f"Huong quay xe tang khong hop le: {self.facing}")
        _validate_position_and_hp(self.row, self.col, self.hp)

    def _with_hp(self, hp: int) -> Tank:
        return Tank(self.player_id, self.row, self.col, self.facing, hp)

    def clone(self) -> Tank:
        return self


@dataclass(frozen=True, slots=True)
class Base(Entity):
    """Thuc the can cu co the bi pha huy cua mot phe."""

    player_id: int
    row: int
    col: int
    hp: int = BASE_INITIAL_HP

    def __post_init__(self) -> None:
        if self.player_id not in PLAYER_IDS:
            raise ValueError(f"Ma nguoi choi khong hop le: {self.player_id}")
        _validate_position_and_hp(self.row, self.col, self.hp)

    def _with_hp(self, hp: int) -> Base:
        return Base(self.player_id, self.row, self.col, hp)

    def clone(self) -> Base:
        return self


@dataclass(frozen=True, slots=True)
class BrickWall(Entity):
    """Tuong gach co sinh luc 3 HP, giam 1 HP sau moi phat trung dan."""

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
    """Tuong thep bat tu chan di chuyen va chan dan."""

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
            raise ValueError("Toa do thuc the khong duoc am")

    def _with_hp(self, hp: int) -> SteelWall:
        return self

    def clone(self) -> SteelWall:
        return self


@dataclass(frozen=True, slots=True)
class Bullet:
    """Vien dan ton tai xuyen luot, bay toi da 3 o moi chu ky tung o mot."""

    owner_id: int
    row: int
    col: int
    direction: str
    active: bool = True

    def __post_init__(self) -> None:
        if self.owner_id not in PLAYER_IDS:
            raise ValueError(f"Chu so huu dan khong hop le: {self.owner_id}")
        if self.direction not in DIRECTIONS:
            raise ValueError(f"Huong dan bay khong hop le: {self.direction}")
        if self.row < 0 or self.col < 0:
            raise ValueError("Toa do vien dan khong duoc am")

    def clone(self) -> Bullet:
        return self


def _validate_position_and_hp(row: int, col: int, hp: int) -> None:
    if row < 0 or col < 0:
        raise ValueError("Toa do thuc the khong duoc am")
    if hp < 0:
        raise ValueError("Chi so sinh luc HP khong duoc am")
