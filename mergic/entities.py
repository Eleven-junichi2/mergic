from . import entityclass
from .components import PygameSurface, Coordinate, Velocity

@entityclass
class Player(Coordinate, PygameSurface, Velocity):
    pass

