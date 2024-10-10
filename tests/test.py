from dataclasses import dataclass
import unittest

from mergic import ECS

@dataclass
class DummyComponent:
    pass


@dataclass
class DummyEntity(DummyComponent):
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
        entity = DummyEntity()
        world.add(entity)
        for entity in world.entities_for_components(DummyComponent):
            self.assertEqual(isinstance(entity, DummyEntity), True)


if __name__ == "__main__":
    unittest.main()
