import random
import typing
from pygame import Vector2
import pygame
from mergic import ActionController, GameWorld
from mergic import wizard
from mergic.components import HP
from mergic.entities import Mob, Player
from mergic.wizard import AlchemicalElement, Magic, SpellRecord
from mergic.status import Mana, OwnedStatusEffects
from mergic import combat, combat_cli


def main():
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
        status_effects=OwnedStatusEffects(),
        resistances={},
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
            status_effects=OwnedStatusEffects(),
            resistances={},
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
                status_effects=OwnedStatusEffects(),
                resistances={},
            )
        )
    combat_cli.CombatLoopCLI().run(
        units_on_battlefield=world.entities_for_components(
            *typing.get_args(combat.CombatUnit)
        ),
        manual_control_mob_types=("player_master", "player_apprentice"),
        prompts_for_manual_control_mobs={
            combat.TurnActionType.CLOSE_COMBAT: combat_cli.prompt_close_combat,
            combat.TurnActionType.SPELL: combat_cli.prompt_spell,
            combat.TurnActionType.ESCAPE: combat_cli.prompt_escape,
        },
        turn_action_processors={
            combat.TurnActionType.CLOSE_COMBAT: combat_cli.close_combat_processor,
            combat.TurnActionType.SPELL: combat_cli.spell_processor,
            combat.TurnActionType.ESCAPE: combat_cli.escape_processor,
        },
        instant_turn_action_types={combat.TurnActionType.ESCAPE}
    )


if __name__ == "__main__":
    main()
