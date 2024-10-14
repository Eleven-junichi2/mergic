from dataclasses import dataclass

import pygame

@dataclass
class Hp:
    max_hp: int
    hp: int = 0

@dataclass
class PygameSurface:
    surface: pygame.Surface

@dataclass
class Coordinate:
    pos: pygame.math.Vector2

@dataclass
class Velocity:
    vel: pygame.math.Vector2