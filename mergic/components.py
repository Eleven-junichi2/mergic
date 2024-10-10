from typing import Optional
from dataclasses import dataclass

import pygame

class Hp:
    def __init__(self, max: int, initial_hp: Optional[int] = None):
        self.max = max
        self.value = initial_hp if initial_hp else max

@dataclass
class Surface:
    surface: pygame.Surface
