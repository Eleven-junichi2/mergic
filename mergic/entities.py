from dataclasses import dataclass
from pygame.math import Vector2

from .components import Surface

@dataclass
class Player(Vector2, Surface):
    pass
