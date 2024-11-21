from collections import UserDict
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Optional


@dataclass
class Mana:
    max_: int
    current: int = field(init=False)

    def __post_init__(self):
        self.current = self.max_


@dataclass
class HP:
    max_: int
    current: int = field(init=False)

    def __post_init__(self):
        self.current = self.max_


class StatusEffect(StrEnum):
    DOT = auto()
    POISONED = auto()
    CONFUSING = auto()
    TEMPTED = auto()
    BURNING = auto()
    FROSTBITED = auto()
    FROZEN = auto()
    BLIND = auto()
    DROWSY = auto()
    SLEEPING = auto()
    STUN = auto()
    TERRIFIED = auto()


@dataclass
class StatusEffectContent:
    turns_remaining: int
    strength: Optional[float] = None


@dataclass
class OwnedStatusEffects(UserDict[StatusEffect, list[StatusEffectContent]]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key: StatusEffect) -> list[StatusEffectContent]:
        while True:
            try:
                item = super().__getitem__(key)
                return item
            except KeyError:
                self[key] = []


BuffVariants = (StatusEffect.BURNING, StatusEffect.FROSTBITED, StatusEffect.FROZEN)
DebuffVariants = (
    StatusEffect.DOT,
    StatusEffect.POISONED,
    StatusEffect.TEMPTED,
    StatusEffect.BURNING,
    StatusEffect.FROSTBITED,
    StatusEffect.FROZEN,
    StatusEffect.BLIND,
    StatusEffect.DROWSY,
    StatusEffect.SLEEPING,
    StatusEffect.STUN,
)
