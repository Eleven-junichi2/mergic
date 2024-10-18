from mergic import entityclass
from mergic.components import (
    AbleToHaveMentor,
    AbleToHaveStudent,
    HasActions,
    HasCoordinate,
    HasHP,
    HasMana,
    HasSurface,
    HasVelocity,
    HasAffiliation,
    HasName,
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
    HasAffiliation,
):
    pass
