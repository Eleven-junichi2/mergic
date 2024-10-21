from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum, auto
import random
from typing import Iterable, Optional, Sequence, Tuple, TypeAlias
from mergic import TextMenu
from mergic import wizard
from mergic.cli import PromptResult, ask_yes_no, inquire_typed_value
from mergic.components import (
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
)
from mergic.wizard import SpellRecord

UnitType: TypeAlias = (
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
)


class TurnActionType(StrEnum):
    CLOSE_COMBAT = auto()
    SPELL = auto()
    ESCAPE = auto()


@dataclass
class TurnAction:
    type_: TurnActionType
    actor: UnitType
    targets: tuple[UnitType]
    spell_name: Optional[str] = None


def sort_units_by_proper_order(units: list[UnitType]):
    units = sorted(
        list(units),
        key=lambda entity: entity.physical_ability,
        reverse=True,
    )
    for i, unit in enumerate(units):
        if i > 0:
            if ("enemy" in unit.friendly_factions) and (
                "player" in units[i - 1].hostile_factions
            ):
                if unit.physical_ability == units[i - 1]:
                    units[i], units[i - 1] = (
                        units[i - 1],
                        units[i],
                    )


def print_units_info(units: Iterable[UnitType]):
    print("-")
    for unit in units:
        print(
            f"{unit.name}: HP={unit.hp.current}/{unit.hp.max_} Mana={unit.mana.current}/{unit.mana.max_} PhysicalAbility={unit.physical_ability}"
        )
    print("-")


def target_menu_template(units: Iterable[UnitType]):
    """Returns a menu that can be used to select the target of `units`.
    The callback of each option is set to a function that returns the index of the unit in `units`."""
    target_menu = TextMenu()
    target_menu.add_option("Cancel", key="cancel")
    for i, target in enumerate(units):
        target_menu.add_option(
            target.name, tag="target", callback=lambda target_index=i: target_index
        )
    return target_menu


def inquire_turn_action() -> PromptResult[TurnActionType]:
    texts = {
        TurnActionType.CLOSE_COMBAT: "足掻く",
        TurnActionType.SPELL: "呪文",
        TurnActionType.ESCAPE: "逃げる",
    }
    actions_menu = TextMenu()
    for turn_action_type in TurnActionType:
        actions_menu.add_option(texts[turn_action_type], key=turn_action_type)
    for i, option in enumerate(actions_menu.options.values()):
        print(f"{i}:{option["text"]}")
    while True:
        if command := inquire_typed_value("番号を入力して選択", int, ask_cancel=False):
            try:
                actions_menu.selector_point_at(command.unwrap())
            except IndexError:
                continue
        return PromptResult.Ok(TurnActionType(actions_menu.current_selection()[0]))


def inquire_target(units_on_battlefield: Sequence[UnitType]) -> PromptResult[UnitType]:
    target_menu = target_menu_template(units_on_battlefield)
    for i, option in enumerate(target_menu.options.values()):
        print(f"{i}:{option["text"]}")
    if command := inquire_typed_value("番号を入力して選択", int):
        target_menu.selector_point_at(command.unwrap())
        if target_menu.current_selection()[0] == "cancel":
            return PromptResult.Cancel()
    else:
        return PromptResult.Cancel()
    return PromptResult.Ok(
        units_on_battlefield[target_menu.execute_current_selection()]
    )


def prompt_spell_generator(
    actor: UnitType, prompt_symbol: str = ">"
) -> PromptResult[Tuple[str, SpellRecord]]:
    """Returns auto name of the spell and Magic"""
    while True:
        try:
            integer_spell = int(input("詠唱整数" + prompt_symbol))
        except ValueError:
            if ask_yes_no("やめる？"):
                return PromptResult.Cancel()
            else:
                continue
        try:
            magic = wizard.spell_factory.generate(
                integer_spell, random.randint(0, actor.mana.max_)
            )
        except ValueError:
            print(
                f"その整数を扱うにはあまりにも大きすぎる。最大で{wizard.spell_factory.integer_spell_max}が限界だ"
            )
            continue
        break
    spell_name = wizard.auto_name(magic, language_code="ja")
    return PromptResult.Ok((spell_name, SpellRecord(magic)))


def inquire_spell(actor: UnitType) -> PromptResult[Tuple[str, SpellRecord]]:
    """Returns name of the spell and SpellRecord"""
    spell_menu = TextMenu()
    spell_menu.add_option("Cancel", key="cancel")
    spell_menu.add_option("Improvise spell", key="improvise_spell")
    for spell_name in actor.spell_database.keys():
        spell_menu.add_option(spell_name, tag="spell")
    for i, option in enumerate(spell_menu.options.values()):
        print(f"{i}:{option['text']}")
    while True:
        if command := inquire_typed_value("番号を入力して選択", int):
            try:
                spell_menu.selector_point_at(command.unwrap())
            except IndexError:
                continue
        else:
            continue
        if spell_menu.current_selection()[0] == "cancel":
            return PromptResult.Cancel()
        if spell_menu.current_selection()[0] == "improvise_spell":
            if result := prompt_spell_generator(actor=actor):
                spell_name, spell_record = result.unwrap()
            else:
                continue
            break
        else:
            spell_name, spell_record = (
                spell_menu.current_selection()[0],
                actor.spell_database[spell_menu.current_selection()[0]],
            )
            break
    return PromptResult.Ok((spell_name, spell_record))


def print_spell_info(spell_name: str, spell_record: SpellRecord):
    print(f"名前：{spell_name}")
    print("詠唱整数：", end="")
    if integer_spell := spell_record.magic.generator_integer:
        print(integer_spell)
    else:
        print("無し")
    print("属性：", end="")
    if elements := spell_record.magic.alchemical_elements:
        print(f"{' '.join(elements)}")
    else:
        print("無し")
    print("特性：", end="")
    if traits := spell_record.magic.traits:
        print(f"特性：{' '.join(traits)}")
    else:
        print("無し")
    if not (memo := spell_record.memo):
        memo = "…"
    print(memo)


def combat_loop_cli(
    units_on_battlefield: Iterable[UnitType],
    mob_types_controlled_manually: Iterable[str] = (
        "player_master",
        "player_apprentice",
    ),
):
    units_on_battlefield = list(units_on_battlefield)
    sort_units_by_proper_order(units_on_battlefield)
    turn_action_queue: deque[TurnAction] = deque()
    running = True
    deads = deque()
    while running:
        for dead in deads:
            units_on_battlefield.remove(dead)
        deads.clear()
        print_units_info(units_on_battlefield)
        for unit in units_on_battlefield:
            if unit.mob_type in mob_types_controlled_manually:
                if unit.hp.current <= 0:
                    continue
                print(f"({unit.name}の番だ)")
                manipulating_unit = True
                while manipulating_unit:
                    turn_action_type = inquire_turn_action().unwrap()
                    match turn_action_type:
                        case TurnActionType.ESCAPE:
                            running = False
                            break
                        case TurnActionType.CLOSE_COMBAT:
                            print("誰に？")
                            if not (
                                target := inquire_target(
                                    units_on_battlefield=units_on_battlefield,
                                )
                            ):
                                print("コンテ")
                                continue
                            turn_action_queue.append(
                                TurnAction(
                                    type_=turn_action_type,
                                    actor=unit,
                                    targets=(target.unwrap(),),
                                )
                            )
                            break
                        case TurnActionType.SPELL:
                            while True:
                                if result := inquire_spell(actor=unit):
                                    spell_name, spell_record = result.unwrap()
                                else:
                                    break
                                print_spell_info(spell_name, spell_record)
                                if ask_yes_no("使う？"):
                                    if strength := inquire_typed_value(
                                        "込めるマナ",
                                        int,
                                        default_value=spell_record.magic.strength,
                                    ):
                                        strength = strength.unwrap()
                                        if strength > unit.mana.current:
                                            print(
                                                f"マナが足りない（現在＝{unit.mana.current}）"
                                            )
                                            continue
                                        print("誰に？")
                                        if target := inquire_target(
                                            units_on_battlefield=units_on_battlefield,
                                        ):
                                            turn_action_queue.append(
                                                TurnAction(
                                                    type_=TurnActionType.SPELL,
                                                    actor=unit,
                                                    targets=(target.unwrap(),),
                                                    spell_name=spell_name,
                                                )
                                            )
                                            manipulating_unit = False
                                            break
                                        else:
                                            continue
            if not running:
                break
        if not running:
            break
        for turn_action in turn_action_queue:
            # print(turn_action)
            match turn_action.type_:
                case TurnActionType.SPELL:
                    print(f"{turn_action.actor.name}の{turn_action.spell_name}！")
                    print("未実装！")
                case TurnActionType.CLOSE_COMBAT:
                    print(f"{turn_action.actor.name}の攻撃！")
                    for target in turn_action.targets:
                        if target.hp.current <= 0:
                            continue
                        damage = random.randint(
                            0, turn_action.actor.physical_ability
                        ) - random.randint(0, target.physical_ability)
                        if damage < 0:
                            if turn_action.actor == target:
                                print(
                                    f"{turn_action.actor.name}は自身を傷つけようとしたが威力が足りなかった！"
                                )
                            elif (
                                target.physical_ability
                                > turn_action.actor.physical_ability
                            ):
                                print(f"{target.name}は攻撃を弾いた！")
                            elif (
                                target.physical_ability
                                < turn_action.actor.physical_ability
                            ):
                                print(f"{target.name}は攻撃を躱した！")
                            elif (
                                target.physical_ability
                                == turn_action.actor.physical_ability
                            ):
                                print(f"{target.name}は攻撃を受け止めた！")
                            damage = 0
                        else:
                            if turn_action.actor == target:
                                print(
                                    f"{turn_action.actor.name}は自身を傷つけ、{damage}ダメージを負った！"
                                )
                            else:
                                print(f"{target.name}は{damage}ダメージを受けた！")
                        target.hp.current -= damage
                        if target.hp.current <= 0:
                            print(f"{target.name}は倒れた！")
                            deads.append(target)
        turn_action_queue.clear()
