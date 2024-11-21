from dataclasses import dataclass
from examples.wizhalen_old.components import (
    HasActions,
    HasCoordinate,
    HasHP,
    HasMana,
    HasSurface,
    HasVelocity,
    HasName,
    HasPhysicalAbility,
    AbleToHaveMentor,
    AbleToHaveStudent,
    HasMobType,
    HasHostileFactions,
    HasFriendlyFactions,
    HasHostileMobTypes,
    HasFriendlyMobTypes,
    HasSpellDatabase,
    HasStatusEffects,
    HasResistance,
)


@dataclass(slots=True)
class Player(
    HasMobType,
    HasName,
    HasCoordinate,
    HasSurface,
    HasVelocity,
    HasActions,
    HasHP,
    HasMana,
    HasPhysicalAbility,
    HasHostileFactions,
    HasFriendlyFactions,
    HasHostileMobTypes,
    HasFriendlyMobTypes,
    HasSpellDatabase,
    HasStatusEffects,
    HasResistance,
    AbleToHaveStudent,
    AbleToHaveMentor,
):
    pass


@dataclass(slots=True)
class Mob(
    HasMobType,
    HasName,
    HasCoordinate,
    HasSurface,
    HasVelocity,
    HasActions,
    HasHP,
    HasMana,
    HasPhysicalAbility,
    HasHostileFactions,
    HasFriendlyFactions,
    HasSpellDatabase,
    HasStatusEffects,
    HasResistance,
    HasHostileMobTypes,
    HasFriendlyMobTypes,
):
    pass
