from collections import deque
from pathlib import Path
import random
import sys
import itertools

from pygame import Vector2
import pygame


sys.path.append(str(Path(__file__).parent.parent))

from mergic import GameWorld, wizard, TextMenu, ActionController
from mergic.components import (
    HP,
    HasFriendlyFactions,
    HasHP,
    HasHostileFactions,
    HasMana,
    HasMobType,
    HasName,
    HasPhysicalAbility,
    HasSpellDatabase,
)
from mergic.wizard import AlchemicalElement, Magic, Mana, SpellRecord, SpellTrait
from mergic.entities import Player, Mob


def main():
    menu = TextMenu()
    menu.add_option("足掻く", key="close_combat")
    menu.add_option("呪文", key="spell")
    menu.add_option("道具", key="item")
    menu.add_option("身を守る", key="guard")
    menu.add_option("逃げる", key="escape")
    PROMPT_SYMBOL = ">"

    world = GameWorld()
    player = Player(
        mob_type="player_master",
        name="masterA",
        pos=Vector2(),
        surface=pygame.surface.Surface((32, 32)),
        vel=Vector2(),
        actions=ActionController(),
        hp=HP(max_=22),
        mana=Mana(max_=78),
        physical_ability=7,
        friendly_factions={"player"},
        hostile_factions=set(),
        friendly_mob_types=set(),
        hostile_mob_types=set(),
        spell_database={},
        mentor=None,
        student="apprenticeA",
    )
    for element in AlchemicalElement:
        magic = Magic({element}, {}, random.randint(1, 22))
        player.spell_database[wizard.auto_name(magic, "ja")] = SpellRecord(magic=magic)
    world.add(player)
    world.add(
        Player(
            mob_type="player_apprentice",
            name="apprenticeA",
            pos=Vector2(),
            surface=pygame.surface.Surface((32, 32)),
            vel=Vector2(),
            actions=ActionController(),
            hp=HP(max_=22),
            mana=Mana(max_=78),
            physical_ability=7,
            friendly_factions={"player"},
            hostile_factions={"enemy"},
            friendly_mob_types=set(),
            hostile_mob_types=set(),
            spell_database={},
            mentor="masterA",
            student=None,
        )
    )
    for i in range(random.randint(2, 4)):
        world.add(
            Mob(
                mob_type="monster",
                name=f"enemy{i}",
                pos=Vector2(),
                surface=pygame.surface.Surface((32, 32)),
                vel=Vector2(),
                actions=ActionController(),
                hp=HP(max_=random.randint(11, 22)),
                mana=Mana(max_=random.randint(39, 78)),
                physical_ability=random.randint(5, 8),
                friendly_factions={"enemy"},
                hostile_factions={"player"},
                friendly_mob_types=set,
                hostile_mob_types=set(),
                spell_database={},
            )
        )
    units_on_battlefield = sorted(
        list(
            world.entities_for_components(
                HasName,
                HasMobType,
                HasHP,
                HasMana,
                HasPhysicalAbility,
                HasFriendlyFactions,
                HasHostileFactions,
                HasSpellDatabase,
            )
        ),
        key=lambda entity: entity.physical_ability,
        reverse=True,
    )
    for i, unit in enumerate(units_on_battlefield):
        if i > 0:
            if ("enemy" in unit.friendly_factions) and (
                "player" in units_on_battlefield[i - 1].hostile_factions
            ):
                if unit.physical_ability == units_on_battlefield[i - 1]:
                    units_on_battlefield[i], units_on_battlefield[i - 1] = (
                        units_on_battlefield[i - 1],
                        units_on_battlefield[i],
                    )
    battlecommand_queue: deque[
        dict[
            str,
            str
            | Magic
            | HasName
            | HasMobType
            | HasHP
            | HasMana
            | HasPhysicalAbility
            | HasFriendlyFactions
            | HasHostileFactions,
        ]
    ] = deque()
    running_battle = True
    while running_battle:
        for dead_entity in world.dead_entity_buffer:
            if isinstance(dead_entity, HasName):
                print(dead_entity.name, "（戦場から削除！）")
            units_on_battlefield.remove(dead_entity)
        world.do_reserved_deletions()
        if (
            len(
                [
                    unit
                    for unit in units_on_battlefield
                    if unit.mob_type in ("player_master", "player_apprentice")
                ]
            )
            == 0
        ):
            print("<<<GAMEOVER>>>")
            running_battle = False
            break
        elif (
            len(
                [
                    unit
                    for unit in units_on_battlefield
                    if unit.hostile_factions.issuperset(("player",))
                ]
            )
            == 0
        ):
            print("<<<YOU WON>>>")
            running_battle = False
            break
        for unit in units_on_battlefield:
            print("-")
            for unit_ in units_on_battlefield:
                print(
                    f"{unit_.name} HP={unit_.hp.current}/{unit_.hp.max_} Mana={unit_.mana.current}/{unit_.mana.max_} PhysicalAbility={unit_.physical_ability}"
                )
            print("-")
            if unit.mob_type in ("player_master", "player_apprentice"):
                print(f"({unit.name}の番だ)")
                while True:
                    for i, option in enumerate(menu.options):
                        print(f"{i}:{option}")
                    try:
                        command = int(input("番号を入力して選択" + PROMPT_SYMBOL))
                        if command > len(menu.options):
                            continue
                        menu.selector_point_at(command)
                    except ValueError:
                        continue
                    match menu.current_selection()[0]:
                        case "escape":
                            running_battle = False
                            break
                        case "spell":
                            spells_menu = TextMenu()
                            spells_menu.add_option("cancel", key="cancel", tag="menu")
                            spells_menu.add_option(
                                "improvise spell", key="improvise_spell"
                            )
                            for spell_name in unit.spell_database.keys():
                                spells_menu.add_option(
                                    spell_name,
                                    tag="spell",
                                )
                            for i, option in enumerate(spells_menu.options.values()):
                                print(f"{i}:{option["text"]}")
                            while True:
                                try:
                                    command = int(
                                        input("番号を入力して選択" + PROMPT_SYMBOL)
                                    )
                                    spells_menu.selector_point_at(command)
                                except ValueError:
                                    continue
                                except IndexError:
                                    continue
                                selection = spells_menu.current_selection()[0]
                                match selection:
                                    case "cancel":
                                        break
                                    case "improvise_spell":
                                        break
                                    case _:
                                        print("属性：", end="")
                                        if elements := unit.spell_database[
                                            selection
                                        ].magic.alchemical_elements:
                                            print(f"{' '.join(elements)}")
                                        else:
                                            print("無し")
                                        print("特性：", end="")
                                        if traits := unit.spell_database[
                                            selection
                                        ].magic.traits:
                                            print(f"特性：{' '.join(traits)}")
                                        else:
                                            print("無し")
                                        if not (
                                            memo := unit.spell_database[selection].memo
                                        ):
                                            memo = "メモに記述がない"
                                        print(memo)
                                        command = input("使う?(y/n)" + PROMPT_SYMBOL)
                                        match command:
                                            case "y":
                                                strength = input(
                                                    f"込めるマナ({unit.spell_database[selection].magic.strength})"
                                                    + PROMPT_SYMBOL
                                                )
                                                try:
                                                    if strength != "":
                                                        unit.spell_database[
                                                            selection
                                                        ].magic.strength = int(strength)
                                                except ValueError:
                                                    continue
                                                if (
                                                    unit.spell_database[
                                                        selection
                                                    ].magic.strength
                                                    > unit.mana.current
                                                ):
                                                    print("マナが足りない")
                                                    continue
                                                targets_menu = TextMenu()
                                                targets_menu.add_option(
                                                    "cancel", key="cancel", tag="menu"
                                                )
                                                for i, target_candidate in enumerate(
                                                    units_on_battlefield
                                                ):
                                                    targets_menu.add_option(
                                                        target_candidate.name,
                                                        callback=lambda target_id=i: target_id,
                                                    )
                                                for i, option in enumerate(
                                                    targets_menu.options
                                                ):
                                                    print(f"{i}:{option}")
                                                try:
                                                    command = int(
                                                        input(
                                                            "番号を入力して選択"
                                                            + PROMPT_SYMBOL
                                                        )
                                                    )
                                                    targets_menu.selector_point_at(
                                                        command
                                                    )
                                                except ValueError:
                                                    continue
                                                except IndexError:
                                                    continue
                                                match targets_menu.current_selection()[
                                                    0
                                                ]:
                                                    case "cancel":
                                                        break
                                                    case _:
                                                        target_id: int = targets_menu.execute_current_selection()
                                                        print("target_id", target_id)
                                                        target = units_on_battlefield[
                                                            target_id
                                                        ]
                                                        battlecommand_queue.append(
                                                            {
                                                                "type": "spell",
                                                                "spell_name": selection,
                                                                "spell": unit.spell_database[
                                                                    selection
                                                                ].magic,
                                                                "target": target,
                                                                "actor": unit,
                                                            }
                                                        )
                                                        break
                                            case _:
                                                continue
                            break

                        case "close_combat":
                            targets_menu = TextMenu()
                            targets_menu.add_option("cancel", key="cancel", tag="menu")
                            while True:
                                for i, target_candidate in enumerate(
                                    units_on_battlefield
                                ):
                                    targets_menu.add_option(
                                        target_candidate.name,
                                        callback=lambda target_id=i: target_id,
                                    )
                                for i, option in enumerate(targets_menu.options):
                                    print(f"{i}:{option}")
                                try:
                                    command = int(
                                        input("番号を入力して選択" + PROMPT_SYMBOL)
                                    )
                                    targets_menu.selector_point_at(command)
                                except ValueError:
                                    continue
                                except IndexError:
                                    continue
                                match targets_menu.current_selection()[0]:
                                    case "cancel":
                                        break
                                    case _:
                                        target_id: int = (
                                            targets_menu.execute_current_selection()
                                        )
                                        print("target_id", target_id)
                                        target = units_on_battlefield[target_id]
                                        battlecommand_queue.append(
                                            {
                                                "type": "close_combat",
                                                "target": target,
                                                "actor": unit,
                                            }
                                        )
                                        break
                            break
            else:
                input(f"({unit.name}の番だ)")
                command = random.choice(("close_combat",))
                match command:
                    case "close_combat":
                        target_candidates = [
                            enemy
                            for enemy in units_on_battlefield
                            if len(
                                enemy.friendly_factions.intersection(
                                    unit.hostile_factions
                                )
                            )
                            != 0
                        ]
                        target = random.choice(target_candidates)
                        battlecommand_queue.append(
                            {
                                "type": "close_combat",
                                "target": target,
                                "actor": unit,
                            }
                        )
            for battlecommand in battlecommand_queue:
                actor = battlecommand["actor"]
                target = battlecommand["target"]
                if actor.hp.current == 0:
                    continue
                if target.hp.current == 0:
                    continue
                match battlecommand["type"]:
                    case "spell":
                        print(f"{actor.name}の{battlecommand['spell_name']}！")
                        actor.mana.current -= battlecommand["spell"].strength
                        hp_delta = 0
                        if SpellTrait.SUBTRACTION in battlecommand["spell"].traits:
                            hp_delta -= battlecommand["spell"].strength
                        if SpellTrait.ADDITION in battlecommand["spell"].traits:
                            hp_delta += battlecommand["spell"].strength
                        if hp_delta < 0:
                            target.hp.current += hp_delta
                            print(f"{target.name}に{hp_delta}ダメージを与えた！")
                            if target.hp.current <= 0:
                                print(f"{target.name}は倒れた！")
                                world.reserve_to_delete(target)
                                break
                        elif hp_delta > 0:
                            target.hp.current += hp_delta
                            print(f"{target.name}のHPを{hp_delta}回復した！")
                            if target.hp.current > target.hp.max_:
                                target.hp.max_ = target.hp.current
                    case "guard":
                        print(f"{actor.name}は身を守っている！未実装")
                        # actor.status_effects.append({"heat_resistance": random.random()})
                        # actor.status_effects.append({"cold_resistance": random.random()})
                        # actor.status_effects.append({"light_resistance": random.random()})
                        # actor.status_effects.append({"dark_resistance": random.random()})
                    case "close_combat":
                        print(f"{actor.name}の攻撃！")
                        damage = random.randint(
                            0, actor.physical_ability
                        ) - random.randint(0, target.physical_ability)

                        if damage < 0:
                            if actor == target:
                                print(
                                    f"{actor.name}は自身を傷つけようとしたが威力が足りなかった！"
                                )
                            elif target.physical_ability > actor.physical_ability:
                                print(f"{target.name}は攻撃を弾いた！")
                            elif target.physical_ability < actor.physical_ability:
                                print(f"{target.name}は攻撃を躱した！")
                            elif target.physical_ability == actor.physical_ability:
                                print(f"{target.name}は攻撃を受け止めた！")
                            damage = 0
                        else:
                            if actor == target:
                                print(
                                    f"{actor.name}は自身を傷つけ、{damage}ダメージを負った！"
                                )
                            else:
                                print(f"{target.name}は{damage}ダメージを受けた！")
                        target.hp.current -= damage
                        if target.hp.current <= 0:
                            print(f"{target.name}は倒れた！")
                            world.reserve_to_delete(target)
            battlecommand_queue.clear()
            if not running_battle:
                break


if __name__ == "__main__":
    main()
