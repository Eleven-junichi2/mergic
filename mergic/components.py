from dataclasses import dataclass

import pygame

@dataclass
class Hp:
    max_hp: int
    hp: int = 0

@dataclass
class Surface:
    surface: pygame.Surface
