from mergic import entityclass
from mergic.components import (
    HasActions,
    HasCoordinate,
    HasHP,
    HasMana,
    HasSurface,
    HasVelocity,
    HasAffiliation,
    HasName,
    HasPhysicalAbility,
    AbleToHaveMentor,
    AbleToHaveStudent,
)


@entityclass
class Player(
    HasName,
    HasCoordinate,
    HasSurface,
    HasVelocity,
    HasActions,
    HasHP,
    HasMana,
    HasPhysicalAbility,
    HasAffiliation,
    AbleToHaveStudent,
    AbleToHaveMentor,
):
    pass


@entityclass
class Mob(
    HasName,
    HasCoordinate,
    HasSurface,
    HasVelocity,
    HasActions,
    HasHP,
    HasMana,
    HasPhysicalAbility,
    HasAffiliation,
):
    pass
