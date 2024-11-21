from collections import deque
from dataclasses import dataclass, field
from enum import Enum, StrEnum, auto
from typing import Callable, Iterable, Optional, TypeAlias
from mergic import TextMenu
from examples.wizhalen_old.components import (
    HasFriendlyFactions,
    HasHP,
    HasHostileFactions,
    HasMana,
    HasName,
    HasMobType,
    HasPhysicalAbility,
    HasSpellDatabase,
    HasHostileMobTypes,
    HasFriendlyMobTypes,
    HasStatusEffects,
    HasResistance,
    MobTypeStr,
)
from examples.wizhalen_old.wizard import SpellRecord

CombatUnit: TypeAlias = (
    HasName
    | HasMobType
    | HasHP
    | HasMana
    | HasPhysicalAbility
    | HasFriendlyFactions
    | HasHostileFactions
    | HasSpellDatabase
    | HasFriendlyMobTypes
    | HasHostileMobTypes
    | HasStatusEffects
    | HasResistance
)


class TurnActionType(StrEnum):
    CLOSE_COMBAT = auto()
    SPELL = auto()
    ESCAPE = auto()


@dataclass
class TurnAction:
    type_: TurnActionType
    actor: CombatUnit
    targets: tuple[CombatUnit]
    spell_name: Optional[str] = None
    spell_record: Optional[SpellRecord] = None


def sorted_units_by_physical_ability(
    units: list[CombatUnit],
    priority_faction_a_against_b="player",
    delayed_faction_b_against_a="enemy",
):
    units = sorted(
        units,
        key=lambda entity: entity.physical_ability,
        reverse=True,
    )
    for i, unit in enumerate(units):
        if i > 0:
            if (delayed_faction_b_against_a in unit.friendly_factions) and (
                priority_faction_a_against_b in units[i - 1].hostile_factions
            ):
                if unit.physical_ability == units[i - 1]:
                    units[i], units[i - 1] = (
                        units[i - 1],
                        units[i],
                    )
    return units


def target_menu_template(units: Iterable[CombatUnit]):
    """Returns a menu that can be used to select the target of `units`.
    The callback of each option is set to a function that returns the index of the unit in `units`."""
    target_menu = TextMenu()
    target_menu.add_option("Cancel", key="cancel")
    for i, target in enumerate(units):
        target_menu.add_option(
            target.name, tag="target", callback=lambda target_index=i: target_index
        )
    return target_menu


def query_living_units(units: Iterable[CombatUnit]):
    yield from [unit for unit in units if unit.hp.current > 0]


def query_dead_units(units: Iterable[CombatUnit]):
    yield from [unit for unit in units if unit.hp.current <= 0]


class CombatPhase(Enum):
    ACTION_DECISION = auto()
    EXECUTE_ACTION = auto()


@dataclass
class CombatLoopConfig:
    units_on_battlefield: Iterable[CombatUnit]
    turn_action_deciders: dict[MobTypeStr, Callable[[CombatUnit], TurnAction]]
    turn_action_processors: dict[TurnActionType, Callable[[TurnAction], None]]
    manual_mob_types: Iterable[MobTypeStr] = field(default_factory=list)
    manual_turn_action_deciders: dict[
        MobTypeStr, Callable[[CombatUnit, Iterable[CombatUnit]], TurnAction]
    ] = field(default_factory=dict)
    instant_turn_action_types: set[TurnActionType] = field(default_factory=set)


class CombatLoop:
    def __init__(self, config: CombatLoopConfig):
        self.config: CombatLoopConfig = config
        self.phase: CombatPhase = CombatPhase.ACTION_DECISION
        self.units = sorted_units_by_physical_ability(list(self.config.units_on_battlefield))
        self.turn_action_queue: deque[TurnAction] = deque()

    def update(self, debug=False):
        print("!!!!!!!!!!")
        if debug:
            print("phase: ", self.phase)
        match self.phase:
            case CombatPhase.ACTION_DECISION:
                for unit in query_living_units(self.units):
                    if unit.mob_type in (self.config.manual_mob_types):
                        turn_action = self.config.manual_turn_action_deciders
                    else:
                        turn_action = self.config.turn_action_deciders[unit.mob_type](
                            unit
                        )
                    if turn_action.type_ in self.config.instant_turn_action_types:
                        self.phase = CombatPhase.EXECUTE_ACTION
                self.phase = CombatPhase.EXECUTE_ACTION
            case CombatPhase.EXECUTE_ACTION:
                for turn_action in self.turn_action_queue:
                    self.config.turn_action_processors[turn_action.type_](turn_action)
                self.turn_action_queue.clear()
        yield self.phase
