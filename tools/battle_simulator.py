from pathlib import Path
import sys

from pygame import Vector2
import pygame


sys.path.append(str(Path(__file__).parent.parent))

from mergic import wizard, TextMenu, ActionController
from mergic.components import HP, Mana
from mergic.entities import Player, Mob


def main():
    menu = TextMenu()
    menu.add_option("足掻く", key="close_combat")
    menu.add_option("呪文", key="spell")
    menu.add_option("道具", key="item")
    menu.add_option("身を守る", key="guard")
    menu.add_option("逃げる", key="escape")
    game_msg = "番号を入力して選択"
    battle_state = "player_turn"
    PROMPT_SYMBOL = ">"

    player_master = Player(
        name="masterA",
        pos=Vector2(),
        surface=pygame.surface.Surface((32, 32)),
        vel=Vector2(),
        actions=ActionController(),
        hp=HP(max_=22),
        mana=Mana(max_=78),
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
        affiliation="playerside",
        mentor="masterA",
        student=None,
    )
    teams: dict[str, list[Player | Mob]] = {
        "player": [player_master, player_apprentice],
        "enemy": [
            Mob(
                name="enemyA",
                pos=Vector2(),
                surface=pygame.surface.Surface((32, 32)),
                vel=Vector2(),
                actions=ActionController(),
                hp=HP(max_=44),
                mana=Mana(max_=156),
                affiliation="enemyside",
            )
        ],
    }
    timeline_queue = []

    while True:
        for team, members in teams.items():
            print(f"--{team}--")
            for member in members:
                print(f"{member.name} HP={member.hp} Mana={member.mana}")
            print("----"+"-"*len(team))
        match battle_state:
            case "player_turn":
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


if __name__ == "__main__":
    main()
