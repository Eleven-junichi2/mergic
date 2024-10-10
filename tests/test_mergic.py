from dataclasses import dataclass
import unittest

from mergic import ECS, GameMap, entityclass


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

    def test_entities_for_components(self):
        world = ECS()
        world.add(DummyEntity())
        world.add(DummyEntity2())
        for entity in world.entities_for_components(DummyComponent):
            self.assertEqual(entity.__class__ in (DummyEntity, DummyEntity2), True)
        for entity in world.entities_for_components(DummyComponent2):
            self.assertEqual(entity.__class__, DummyEntity2)

class TestGameMap(unittest.TestCase):
    def test_painting_map(self):
        gamemap = GameMap(3, 3)
        gamemap.paint("example", 0, 0, 0)
        gamemap.paint("example", 2, 2, 1)
        self.assertEqual(gamemap.get_layer("example")[0, 0], 0)
        self.assertEqual(gamemap.get_layer("example")[2, 2], 1)
    
    def test_painting_map_with_invalid_xy(self):
        gamemap = GameMap(3, 3)
        with self.assertRaises(ValueError):
            gamemap.paint("example", 3, 0, 0)


if __name__ == "__main__":
    unittest.main()
