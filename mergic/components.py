from dataclasses import dataclass, field
from typing import Optional

import pygame

from mergic.wizard import AlchemicalElement, Mana, SpellRecord, OwnedStatusEffects
import mergic


@dataclass
class HP:
    max_: int
    current: int = field(init=False)

    def __post_init__(self):
        self.current = self.max_

@dataclass
class HasStatusEffects:
    status_effects: OwnedStatusEffects # status_effect_variant: list_for_stack[int_for_remaining_turns]

@dataclass
class HasResistance:
    resistances: dict[AlchemicalElement, float] # resistance_type: resistance_value

@dataclass
class HasMobType:
    mob_type: str


@dataclass
class HasHostileFactions:
    hostile_factions: set[str]


@dataclass
class HasFriendlyFactions:
    friendly_factions: set[str]


@dataclass
class HasHostileMobTypes:
    hostile_mob_types: set[str]


@dataclass
class HasFriendlyMobTypes:
    friendly_mob_types: set[str]


@dataclass
class HasSpellDatabase:
    spell_database: dict[str, SpellRecord]


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
