from collections import deque
from typing import Callable, Iterable, Sequence, Tuple
from mergic import TextMenu
from mergic import wizard
from mergic.status import (
    StatusEffect,
    StatusEffectContent,
    BuffVariants,
    DebuffVariants,
)
from mergic.ui import PromptResult
from mergic.cli import ask_yes_no, inquire_typed_value
from mergic.wizard import AlchemicalElement, SpellRecord, SpellTrait
from mergic.combat import (
    CombatUnit,
    TurnAction,
    TurnActionType,
    query_living_units,
    sorted_units_by_physical_ability,
    target_menu_template,
)
import random

BoolToToggleLoop = bool


def inquire_turn_action_type(
    turn_action_types: Sequence[TurnActionType],
) -> PromptResult[TurnActionType]:
    texts = {
        TurnActionType.CLOSE_COMBAT: "足掻く",
        TurnActionType.SPELL: "呪文",
        TurnActionType.ESCAPE: "逃げる",
    }
    actions_menu = TextMenu()
    for turn_action_type in turn_action_types:
        actions_menu.add_option(
            texts.get(turn_action_type, turn_action_type.value), key=turn_action_type
        )
    for i, option in enumerate(actions_menu.options.values()):
        print(f"{i}:{option["text"]}")
    while True:
        if command := inquire_typed_value("番号を入力して選択", int, ask_cancel=False):
            try:
                actions_menu.selector_point_at(command.unwrap())
            except IndexError:
                continue
        return PromptResult.Ok(TurnActionType(actions_menu.current_selection()[0]))


def inquire_target(
    units: Sequence[CombatUnit],
) -> PromptResult[CombatUnit]:
    target_menu = target_menu_template(units)
    for i, option in enumerate(target_menu.options.values()):
        print(f"{i}:{option["text"]}")
    if command := inquire_typed_value("番号を入力して選択", int):
        target_menu.selector_point_at(command.unwrap())
        if target_menu.current_selection()[0] == "cancel":
            return PromptResult.Cancel()
    else:
        return PromptResult.Cancel()
    return PromptResult.Ok(units[target_menu.execute_current_selection()])


def print_units_info(units: Iterable[CombatUnit]):
    print("-")
    for unit in units:
        print(
            f"{unit.name}: HP={unit.hp.current}/{unit.hp.max_} Mana={unit.mana.current}/{unit.mana.max_} PhysicalAbility={unit.physical_ability} StatusEffects={unit.status_effects.items()}"
        )
    print("-")


def prompt_spell_generator(
    actor: CombatUnit, prompt_symbol: str = ">"
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


def inquire_spell(actor: CombatUnit) -> PromptResult[Tuple[str, SpellRecord]]:
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


class CombatLoopCLI:
    @staticmethod
    def run(
        units_on_battlefield: Iterable[CombatUnit],
        manual_mob_types: Iterable[str],
        prompts_for_manual_mobs: dict[
            TurnActionType,
            Callable[[CombatUnit, Iterable[CombatUnit]], PromptResult[TurnAction]],
        ],
        turn_action_processors: dict[
            TurnActionType, Callable[[TurnAction], BoolToToggleLoop]
        ],
        instant_turn_action_types: set[TurnActionType],
    ):
        """戦闘をCLI上でシミュレートします。"""
        units = sorted_units_by_physical_ability(list(units_on_battlefield))
        turn_action_queue: deque[TurnAction] = deque()
        running = True
        while running:
            print_units_info(units)
            for unit in query_living_units(units):
                if unit.mob_type in manual_mob_types:
                    print(f"({unit.name}の番だ)")
                    while running:
                        turn_action_type = inquire_turn_action_type(
                            prompts_for_manual_mobs.keys()
                        ).unwrap()
                        if is_configured := prompts_for_manual_mobs[turn_action_type](
                            unit, units
                        ):
                            if turn_action := is_configured.unwrap():
                                if turn_action.type_ in instant_turn_action_types:
                                    running = turn_action_processors[turn_action.type_](
                                        turn_action
                                    )
                                    if not running:
                                        break
                                turn_action_queue.append(turn_action)
                            break
                        else:
                            continue
                if not running:
                    break
            for turn_action in turn_action_queue:
                print("-")
                running = turn_action_processors[turn_action.type_](turn_action)
                print("-")
            turn_action_queue.clear()


def prompt_close_combat(
    actor: CombatUnit, units=Iterable[CombatUnit]
) -> PromptResult[TurnAction]:
    print("誰に？")
    if not (
        target := inquire_target(
            units=list(query_living_units(units)),
        )
    ):
        return PromptResult.Cancel()
    return PromptResult.Ok(
        TurnAction(
            type_=TurnActionType.CLOSE_COMBAT,
            actor=actor,
            targets=(target.unwrap(),),
        )
    )


def prompt_escape(
    actor: CombatUnit, units=Iterable[CombatUnit]
) -> PromptResult[TurnAction]:
    return PromptResult.Ok(
        TurnAction(type_=TurnActionType.ESCAPE, actor=actor, targets=())
    )


def prompt_spell(actor: CombatUnit, units=Iterable[CombatUnit]):
    while True:
        if result := inquire_spell(actor=actor):
            spell_name, spell_record = result.unwrap()
        print_spell_info(spell_name, spell_record)
        if ask_yes_no("使う？"):
            if strength := inquire_typed_value(
                "込めるマナ",
                int,
                default_value=spell_record.magic.strength,
            ):
                strength = strength.unwrap()
                if strength > actor.mana.current:
                    print(f"マナが足りない（現在＝{actor.mana.current}）")
                    continue
                print("誰に？")
                if target := inquire_target(
                    units=units,
                ):
                    return PromptResult.Ok(
                        TurnAction(
                            type_=TurnActionType.SPELL,
                            actor=actor,
                            targets=(target.unwrap(),),
                            spell_name=spell_name,
                            spell_record=spell_record,
                        )
                    )
                else:
                    continue
        else:
            return PromptResult.Cancel()


def escape_processor(turn_action: TurnAction) -> BoolToToggleLoop:
    return False


def spell_processor(turn_action: TurnAction) -> BoolToToggleLoop:
    print(f"{turn_action.actor.name}の{turn_action.spell_name}！")
    actor = turn_action.actor
    actors_magic = turn_action.spell_record.magic
    for target in query_living_units(turn_action.targets):
        actor.mana.current -= actors_magic.strength
        target_hp_delta = 0
        if SpellTrait.HEAL in actors_magic.traits:
            target_hp_delta += actors_magic.strength
        if SpellTrait.DAMAGE in actors_magic.traits:
            target_hp_delta -= actors_magic.strength
        for element, resistance_value in target.resistances.items():
            if element in actors_magic.alchemical_elements:
                target_hp_delta *= 1 - resistance_value
        if AlchemicalElement.LIGHT in actors_magic.alchemical_elements:
            if random.random() < 0.22:
                print(f"{target.name}は強い光に目が眩んだ！")
                target.status_effects[StatusEffect.BLIND].append(
                    StatusEffectContent(
                        turns_remaining=random.randint(
                            1, 1 + actors_magic.strength // 3
                        ),
                        strength=0.5,
                    ),
                )
        if AlchemicalElement.DARK in actors_magic.alchemical_elements:
            if random.random() < 0.22:
                print(f"{target.name}は恐怖に怯え始めた！")
                target.status_effects[StatusEffect.TERRIFIED].append(
                    StatusEffectContent(
                        turns_remaining=random.randint(
                            1, 1 + actors_magic.strength // 3
                        )
                    ),
                )
        if AlchemicalElement.HEAT in actors_magic.alchemical_elements:
            if StatusEffect.BURNING in actor.status_effects:
                print(f"{actor.name}の背負う炎が威力を高めた！")
                target_hp_delta *= 2
            if random.random() < 0.22:
                print(f"{target.name}は炎上し始めた！")

                target.status_effects[StatusEffect.BURNING].append(
                    StatusEffectContent(
                        turns_remaining=random.randint(
                            1, 1 + actors_magic.strength // 3
                        ),
                        strength=actors_magic.strength // 2,
                    ),
                )
                if StatusEffect.FROZEN in target.status_effects:
                    target.status_effects[StatusEffect.FROZEN].clear()
                    print(f"{target.name}は解凍された！")
        if AlchemicalElement.COLD in actors_magic.alchemical_elements:
            if StatusEffect.FROSTBITED in actor.status_effects:
                actor.status_effects.setdefault(StatusEffect.FROZEN)
                actor.status_effects[StatusEffect.FROZEN].append(
                    StatusEffectContent(
                        turns_remaining=random.randint(
                            1, 1 + actors_magic.strength // 3
                        ),
                        strength=actors_magic.strength // 2,
                    ),
                )
                print(f"{actor.name}は凍結した！")
            if random.random() < 0.22:
                print(f"{target.name}は凍傷を負った！")
                target.status_effects[StatusEffect.FROSTBITED].append(
                    StatusEffectContent(
                        turns_remaining=random.randint(
                            1, 1 + actors_magic.strength // 3
                        ),
                        strength=actors_magic.strength // 2,
                    ),
                )
        if target_hp_delta < 0:
            print(f"{target.name}に{abs(target_hp_delta)}ダメージ！")
            if SpellTrait.VAMPIRE in actors_magic.traits:
                print(f"{target.name}のHPをダメージ分吸収した！")
        elif target_hp_delta > 0:
            if SpellTrait.VAMPIRE in actors_magic.traits:
                print(f"{actor.name}のHPが{target.name}に分け与えられた！")
            print(f"{target.name}のHPを{abs(target_hp_delta)}回復！")
        if SpellTrait.VAMPIRE in actors_magic.traits:
            actor.hp.current -= target_hp_delta
        target.hp.current += target_hp_delta
        if SpellTrait.CONFUSION in actors_magic.traits:
            print(f"{target.name}は混乱した！")

            target.status_effects[StatusEffect.CONFUSING].append(
                StatusEffectContent(
                    turns_remaining=random.randint(1, actors_magic.strength // 3)
                ),
            )
        if SpellTrait.STUN in actors_magic.traits:
            target.status_effects[StatusEffect.STUN].append(1)
        if SpellTrait.DISPEL in actors_magic.traits:
            print(f"{target.name}のバフが解除された！")
            for status_effect in target.status_effects.keys():
                if status_effect in BuffVariants:
                    target.status_effects[status_effect].clear()
        if SpellTrait.PURIFY in actors_magic.traits:
            print(f"{target.name}のデバフが解除された！")
            for status_effect in target.status_effects.keys():
                if status_effect in DebuffVariants:
                    target.status_effects[status_effect].clear()
        if SpellTrait.DROWSINESS in actors_magic.traits:
            print(f"{target.name}は眠気を感じ始めた…")

            target.status_effects[StatusEffect.DROWSY].append(
                StatusEffectContent(
                    turns_remaining=random.randint(1, actors_magic.strength // 3)
                ),
            )
        if SpellTrait.SLEEP in actors_magic.traits:
            print(f"{target.name}は眠り始めた！")

            target.status_effects[StatusEffect.SLEEPING].append(
                StatusEffectContent(
                    turns_remaining=random.randint(1, actors_magic.strength // 3)
                ),
            )
        if SpellTrait.POISON in actors_magic.traits:
            print(f"{target.name}は毒に侵された！")

            target.status_effects[StatusEffect.POISONED].append(
                StatusEffectContent(
                    turns_remaining=random.randint(1, actors_magic.strength // 3),
                    strength=0.1,
                ),
            )
        if SpellTrait.RANDOM_ELEMENTS in actors_magic.traits:
            print("RANDOM_ELEMENTSは未実装だ！")
    return True


def close_combat_processor(turn_action: TurnAction) -> BoolToToggleLoop:
    targets = list(query_living_units(turn_action.targets))
    if len(targets) > 0:
        print(f"{turn_action.actor.name}の攻撃！")
    for target in targets:
        damage = random.randint(0, turn_action.actor.physical_ability) - random.randint(
            0, target.physical_ability
        )
        if damage < 0:
            if turn_action.actor == target:
                print(
                    f"{turn_action.actor.name}は自身を傷つけようとしたが威力が足りなかった！"
                )
            elif target.physical_ability > turn_action.actor.physical_ability:
                print(f"{target.name}は攻撃を弾いた！")
            elif target.physical_ability < turn_action.actor.physical_ability:
                print(f"{target.name}は攻撃を躱した！")
            elif target.physical_ability == turn_action.actor.physical_ability:
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
    return True
