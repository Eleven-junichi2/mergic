from pygame.math import Vector2

from . import entityclass
from .components import Surface

@entityclass
class Player(Vector2, Surface):
    pass

