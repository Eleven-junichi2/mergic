from typing import get_args
import unittest
import random

from pygame import Vector2
import pygame

from mergic import ActionController, GameWorld
from mergic import wizard
from mergic.combat import CombatLoop, CombatLoopConfig, CombatUnit
from mergic.entities import Mob, Player
from mergic.status import HP, Mana, OwnedStatusEffects
from mergic.wizard import AlchemicalElement, Magic, SpellRecord


class TestCombat(unittest.TestCase):
    def test_combat_loop(self):
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
        world = GameWorld()
        world.add(player)
        combat_loop = CombatLoop(
            CombatLoopConfig(units_on_battlefield=world.entities_for_components(), turn_action_deciders={}, turn_action_processors={})
        )
        while True:
            combat_loop.update()
