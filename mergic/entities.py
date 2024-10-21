from mergic import entityclass
from mergic.components import (
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


@entityclass
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


@entityclass
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
