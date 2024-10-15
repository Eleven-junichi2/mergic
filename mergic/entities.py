from mergic import entityclass
from mergic.components import Actions, PygameSurface, TileCoordinate, TileVelocity, Coordinate, Velocity

@entityclass
class Player(Coordinate, PygameSurface, Velocity, Actions):
    pass

