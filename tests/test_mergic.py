from dataclasses import dataclass
from typing import get_args
import unittest

from mergic import ECS, TextMenu, GameWorld


@dataclass
class DummyComponent:
    pass


@dataclass
class DummyComponent2:
    pass


@dataclass(slots=True)
class DummyEntity(DummyComponent):
    pass


@dataclass(slots=True)
class DummyEntity2(DummyComponent, DummyComponent2):
    pass


@dataclass(slots=True)
class DummyEntity3(DummyComponent, DummyComponent2):
    pass


class TestECS(unittest.TestCase):
    def test_add_entity(self):
        world = ECS()
        entity = DummyEntity()
        world.add(entity)
        self.assertEqual(len(world.entities), 1)
        self.assertTrue(DummyEntity in world.entities.keys())
        self.assertEqual(world.entities[DummyEntity][0], entity)

    def test_delete_entity(self):
        world = ECS()
        entity = DummyEntity()
        world.add(entity)
        world.delete_now(entity)
        self.assertEqual(len(world.entities[DummyEntity]), 0)

    def test_reserve_to_delete_entity(self):
        world = ECS()
        entity = DummyEntity()
        world.add(entity)
        world.reserve_to_delete(entity)
        self.assertTrue(entity in world.entities[DummyEntity])
        world.do_reserved_deletions()
        self.assertFalse(entity in world.entities[DummyEntity])

    def test_entities_for_type(self):
        world = ECS()
        entity = DummyEntity()
        world.add(entity)
        for entity in world.entities_for_type(DummyEntity):
            self.assertEqual(isinstance(entity, DummyEntity), True)

    def test_entities_for_component(self):
        world = ECS()
        world.add(DummyEntity())
        world.add(DummyEntity2())
        for entity in world.entities_for_components(DummyComponent):
            self.assertEqual(entity.__class__ in (DummyEntity, DummyEntity2), True)
        self.assertEqual(len(list(world.entities_for_components(DummyComponent))), 2)
        for entity in world.entities_for_components(DummyComponent2):
            self.assertEqual(entity.__class__, DummyEntity2)
        self.assertEqual(len(list(world.entities_for_components(DummyComponent2))), 1)
        for entity in world.entities_for_components(DummyComponent2, DummyComponent):
            self.assertEqual(entity.__class__, DummyEntity2)
        self.assertEqual(
            len(list(world.entities_for_components(DummyComponent2, DummyComponent))), 1
        )
        world.add(DummyEntity2())
        for entity in world.entities_for_components(DummyComponent2, DummyComponent):
            self.assertEqual(entity.__class__, DummyEntity2)
        self.assertEqual(
            len(list(world.entities_for_components(DummyComponent2, DummyComponent))), 2
        )
        world.add(DummyEntity3())
        self.assertEqual(
            len(list(world.entities_for_components(DummyComponent2, DummyComponent))), 3
        )
        for entity in world.entities_for_components(DummyComponent):
            self.assertEqual(
                entity.__class__ in (DummyEntity, DummyEntity2, DummyEntity3), True
            )

    def test_get_entities_from_components_type_alias(self):
        ExampleTypeAlias = DummyComponent | DummyComponent2
        world = ECS()
        world.add(DummyEntity())
        world.add(DummyEntity2())
        world.add(DummyEntity3())
        result = [
            entity.__class__
            for entity in world.entities_for_components(*get_args(ExampleTypeAlias))
        ]
        self.assertCountEqual(
            [DummyEntity3, DummyEntity2], result, msg=f"result={result}"
        )


class TestTextMenu(unittest.TestCase):
    def test_game_menu_selector(self):
        gamemenu = TextMenu()
        gamemenu.add_option("New Game")
        gamemenu.add_option(text="Save Game", key="save")
        gamemenu.add_option("Load Game")
        self.assertEqual(gamemenu.current_selection()[1]["text"], "New Game")
        gamemenu.selector_up()
        self.assertEqual(gamemenu.current_selection()[1]["text"], "Load Game")
        gamemenu.selector_down()
        self.assertEqual(gamemenu.current_selection()[1]["text"], "New Game")
        gamemenu.selector_down()
        self.assertEqual(gamemenu.current_selection()[1]["text"], "Save Game")
        gamemenu.selector_down()
        self.assertEqual(gamemenu.current_selection()[1]["text"], "Load Game")
        gamemenu.selector_down()
        self.assertEqual(gamemenu.current_selection()[1]["text"], "New Game")

    def test_game_menu_storing_longest_text_length(self):
        gamemenu = TextMenu()
        gamemenu.add_option("abc")
        gamemenu.add_option(text="happy", key="save")
        gamemenu.add_option("うおお")
        self.assertEqual(gamemenu.longest_text_length, 5)

    def test_game_menu_select_at_index(self):
        gamemenu = TextMenu()
        gamemenu.add_option("abc")
        with self.assertRaises(IndexError):
            gamemenu.selector_point_at(-1)
            gamemenu.selector_point_at(2)


if __name__ == "__main__":
    unittest.main()
