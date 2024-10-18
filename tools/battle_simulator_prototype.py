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
    HasAffiliation,
    HasHP,
    HasMana,
    HasName,
    HasPhysicalAbility,
    Mana,
)
from mergic.entities import Player, Mob


def main():
    menu = TextMenu()
    menu.add_option("足掻く", key="close_combat")
    menu.add_option("呪文", key="spell")
    menu.add_option("道具", key="item")
    menu.add_option("身を守る", key="guard")
    menu.add_option("逃げる", key="escape")
    # game_msg = "番号を入力して選択"
    PROMPT_SYMBOL = ">"

    player_master = Player(
        name="masterA",
        pos=Vector2(),
        surface=pygame.surface.Surface((32, 32)),
        vel=Vector2(),
        actions=ActionController(),
        hp=HP(max_=22),
        mana=Mana(max_=78),
        physical_ability=7,
        affiliation="playerside",
        mentor=None,
        student="apprenticeA",
    )
    player_apprentice = Player(
        name="apprenticeA",
        pos=Vector2(),
        surface=pygame.surface.Surface((32, 32)),
        vel=Vector2(),
        actions=ActionController(),
        hp=HP(max_=22),
        mana=Mana(max_=78),
        physical_ability=7,
        affiliation="playerside",
        mentor="masterA",
        student=None,
    )
    teams: dict[
        str,
        list[HasName | HasHP | HasMana | HasPhysicalAbility | HasAffiliation],
    ] = {}
    world = GameWorld()
    world.add(player_master)
    world.add(player_apprentice)
    for i in range(random.randint(2, 4)):
        world.add(
            Mob(
                name=f"enemy{i}",
                pos=Vector2(),
                surface=pygame.surface.Surface((32, 32)),
                vel=Vector2(),
                actions=ActionController(),
                hp=HP(max_=random.randint(44,88)),
                mana=Mana(max_=random.randint(156, 312)),
                physical_ability=random.randint(3, 9),
                affiliation="enemyside",
            )
        )
    for unit in world.entities_for_components(
        HasName, HasHP, HasMana, HasPhysicalAbility, HasAffiliation
    ):
        if not teams.get(unit.affiliation):
            teams.setdefault(unit.affiliation, list())
        teams[unit.affiliation].append(unit)
    print(teams.keys())

    timeline_queue = []
    battle_commands_queue: list[
        dict[str, HasName | HasHP | HasMana | HasPhysicalAbility | HasAffiliation | str]
    ] = []
    battle_state = "player_turn"
    while True:
        match battle_state:
            case "player_turn":
                for team, members in teams.items():
                    print(f"--{team}--")
                    for member in members:
                        print(
                            f"{member.name} HP={member.hp.current}/{member.hp.max_} Mana={member.mana.current}/{member.mana.max_} PhysicalAbility={member.physical_ability}"
                        )
                    print("----" + "-" * len(team))
                for i, option in enumerate(menu.options):
                    print(f"{i}:{option}")
                try:
                    command = int(input("番号を入力して選択" + PROMPT_SYMBOL))
                except ValueError:
                    continue
                else:
                    menu.selector_point_at(command)
                match menu.current_selection()[0]:
                    case "escape":
                        break
                    case "close_combat":
                        options = ["cancel"]
                        options += list(itertools.chain.from_iterable(teams.values()))
                        for i, option in enumerate(options):
                            if isinstance(option, (Player, Mob)):
                                target = option
                                print(f"{i}:{target.name}")
                            else:
                                print(f"{i}:{option}")
                        command = int(input("対象を選んでください" + PROMPT_SYMBOL))
                        if command > i or option == "cancel":
                            continue
                        else:
                            battle_commands_queue.append(
                                {
                                    "type": "close_combat",
                                    "target": option,
                                    "actor": player_master,
                                }
                            )
                            battle_state = "turn_progress"
                        if battle_state == "turn_progress":
                            for member in teams["playerside"]:
                                if member.name == player_master.name:
                                    continue
                                battle_commands_queue.append(
                                    {
                                        "type": "close_combat",
                                        "target": random.choice(teams["enemyside"]),
                                        "actor": member,
                                    }
                                )

            case "cpu_turn":
                for team, members in teams.items():
                    if team == "playerside":
                        continue
                    for member in members:
                        battle_commands_queue.append(
                            {
                                "type": "close_combat",
                                "target": random.choice(teams["playerside"]),
                                "actor": member,
                            }
                        )
                    else:
                        battle_state = "turn_progress"
            case "turn_progress":
                for battle_command in battle_commands_queue:
                    print(f"~~{battle_command["actor"].affiliation}~~")
                    match battle_command["type"]:
                        case "close_combat":
                            target = battle_command["target"]
                            actor = battle_command["actor"]
                            print(f"{actor.name}の攻撃！")
                            damage = random.randint(
                                0, actor.physical_ability
                            ) - random.randint(0, target.physical_ability)
                            if damage < 0:
                                if target.physical_ability > actor.physical_ability:
                                    print(f"{target.name}は攻撃を弾いた！")
                                elif target.physical_ability < actor.physical_ability:
                                    print(f"{target.name}は攻撃を躱した！")
                                elif target.physical_ability == actor.physical_ability:
                                    print(
                                        f"{target.name}と{actor.name}は互角の戦いを繰り広げる！"
                                    )
                                damage = 0
                            else:
                                print(f"{target.name}は{damage}ダメージを受けた！")
                            target.hp.current -= damage
                            if target.hp.current <= 0:
                                print(f"{target.name}は倒れた！")
                                teams[target.affiliation].remove(target)
                        case "cast_spell":
                            print("制作中")
                else:
                    battle_commands_queue.clear()
                    if len(teams["playerside"]) == 0:
                        print("<<<!>>>GAMEOVER<<<!>>>")
                        break
                    elif len(teams["enemyside"]) == 0:
                        print("<<<!>>>YOU WON<<<!>>>")
                        break
                    if actor.affiliation == "enemyside":
                        battle_state = "player_turn"
                    elif actor.affiliation == "playerside":
                        battle_state = "cpu_turn"
                print("~~~~")


if __name__ == "__main__":
    main()
