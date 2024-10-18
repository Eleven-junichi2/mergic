from dataclasses import dataclass
import unittest

from mergic import ECS, GameMap, TextMenu, entityclass, GameWorld


@dataclass
class DummyComponent:
    pass


@dataclass
class DummyComponent2:
    pass


@entityclass
class DummyEntity(DummyComponent):
    pass


@entityclass
class DummyEntity2(DummyComponent, DummyComponent2):
    pass

@entityclass
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
        self.assertEqual(len(list(world.entities_for_components(DummyComponent2, DummyComponent))), 1)
        world.add(DummyEntity2())
        for entity in world.entities_for_components(DummyComponent2, DummyComponent):
            self.assertEqual(entity.__class__, DummyEntity2)
        self.assertEqual(len(list(world.entities_for_components(DummyComponent2, DummyComponent))), 2)
        world.add(DummyEntity3())
        self.assertEqual(len(list(world.entities_for_components(DummyComponent2, DummyComponent))), 3)
        for entity in world.entities_for_components(DummyComponent):
            self.assertEqual(entity.__class__ in (DummyEntity, DummyEntity2, DummyEntity3), True)


class TestGameMap(unittest.TestCase):
    def test_painting_map(self):
        gamemap = GameMap(3, 3)
        gamemap.paint("example", 0, 0, 0)
        gamemap.paint("example", 2, 2, 1)
        self.assertEqual(gamemap.layer("example")["0,0"], 0)
        self.assertEqual(gamemap.layer("example")["2,2"], 1)

    def test_painting_map_with_invalid_xy(self):
        gamemap = GameMap(3, 3)
        with self.assertRaises(ValueError):
            gamemap.paint("example", 3, 0, 0)

    def test_gamemap_coords_for_elements(self):
        gamemap = GameMap(6, 6)
        gamemap.import_layer("ground", {"0,0": 1, "4,4": 1})
        for x, y in gamemap.coordinates_of_elements("ground"):
            pass

    def test_gamemap_example_usage(self):
        world = GameWorld()
        world.set_gamemap("departure", GameMap(5, 5))
        world.gamemap("departure").import_layer("ground", {"0,0": 1, "4,4": 1})
        list2d: list[list[int]] = []
        for y in range(0, world.gamemap("departure").height):
            list2d.append([])
            for x in range(0, world.gamemap("departure").width):
                list2d[y].append(
                    world.gamemap("departure").layer("ground").get(f"{x},{y}", 0)
                )

        self.assertEqual(
            list2d,
            [
                [1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1],
            ],
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


if __name__ == "__main__":
    unittest.main()
