from dataclasses import dataclass, field
from typing import Optional

import pygame

import mergic


@dataclass
class HasAffiliation:
    affiliation: str


@dataclass
class HP:
    max_: int
    current: int = field(init=False)

    def __post_init__(self):
        self.current = self.max_


@dataclass
class Mana:
    max_: int
    current: int = field(init=False)

    def __post_init__(self):
        self.current = self.max_

@dataclass
class HasPhysicalAbility:
    physical_ability: int


@dataclass
class HasHP:
    hp: HP


@dataclass
class HasMana:
    mana: Mana

@dataclass
class HasName:
    name: str

@dataclass
class AbleToHaveStudent:
    student: Optional[str]


@dataclass
class AbleToHaveMentor:
    mentor: Optional[str]


@dataclass
class HasSurface:
    surface: pygame.Surface


@dataclass
class HasCoordinate:
    pos: pygame.math.Vector2


@dataclass
class HasTileCoordinate:
    tile_pos: pygame.math.Vector2


@dataclass
class HasVelocity:
    vel: pygame.math.Vector2


@dataclass
class HasTileVelocity:
    tile_vel: pygame.math.Vector2


@dataclass
class HasActions:
    actions: mergic.ActionController
