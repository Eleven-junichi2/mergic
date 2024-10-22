from dataclasses import dataclass
from typing import Optional

import pygame

from mergic.wizard import AlchemicalElement, SpellRecord
from mergic.status import OwnedStatusEffects, Mana, HP
import mergic

MobTypeStr = str
FactionStr = str


@dataclass
class HasStatusEffects:
    status_effects: OwnedStatusEffects  # status_effect_variant: list_for_stack[int_for_remaining_turns]


@dataclass
class HasResistance:
    resistances: dict[AlchemicalElement, float]  # resistance_type: resistance_value


@dataclass
class HasMobType:
    mob_type: MobTypeStr


@dataclass
class HasHostileFactions:
    hostile_factions: set[FactionStr]


@dataclass
class HasFriendlyFactions:
    friendly_factions: set[FactionStr]


@dataclass
class HasHostileMobTypes:
    hostile_mob_types: set[MobTypeStr]


@dataclass
class HasFriendlyMobTypes:
    friendly_mob_types: set[MobTypeStr]


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
