import unittest

from mergic.gamemap import TileMap, StrAsCoordMapDict


class TestStrAsCoordMapDict(unittest.TestCase):
    def test_fetch_by_coordinate(self):
        tilemap = StrAsCoordMapDict()
        tilemap[0, 0] = "grass"
        self.assertEqual(tilemap[0, 0], "grass")
        tilemap["0,0"] = "grass"
        self.assertEqual(tilemap[0, 0], "grass")
        tilemap[0, 0] = "grass"
        self.assertEqual(tilemap["0,0"], "grass")
        tilemap[0, 0, 1] = "dirt"
        self.assertEqual(tilemap["0,0,1"], "dirt")


class TestGameMap(unittest.TestCase):
    def test_paint(self):
        tilemap = TileMap(16, 16)
        tilemap.paint_terrain("ground", 0, 0, brush="dirt")
        self.assertEqual(tilemap.terrain_layers["ground"][0, 0], "dirt")
        tilemap.paint_terrain("ground", 15, 15, brush="dirt")
        with self.assertRaises(ValueError):
            tilemap.paint_terrain("ground", 16, 16, brush="dirt")
        tilemap.paint_trait("ground", 13, 13, brush="wall")
        with self.assertRaises(ValueError):
            tilemap.paint_trait("ground", 16, 16, brush="water")

    def test_erase_cell(self):
        tilemap = TileMap(16, 16)
        tilemap.paint_terrain("ground", 1, 1, brush="dirt")
        tilemap.erase_terrain("ground", 1, 1)
        self.assertEqual(tilemap.terrain_layers["ground"].get((1, 1)), None)
        tilemap.paint_trait("collision", 1, 1, brush="wall")
        tilemap.erase_trait("collision", 1, 1)
        self.assertEqual(tilemap.trait_layers["collision"].get((1, 1)), None)

    def test_import_layer(self):
        tilemap = TileMap(16, 16)
        tilemap.import_terrain_map("ground", {"0,0": "dirt", "1,1": "grass"})
        self.assertEqual(tilemap.terrain_layers["ground"]["0,0"], "dirt")
        self.assertEqual(tilemap.terrain_layers["ground"]["1,1"], "grass")
        tilemap.import_trait_map("collision", {"2,2": "wall"})
        self.assertEqual(tilemap.trait_layers["collision"]["2,2"], "wall")

    def test_delete_layer(self):
        tilemap = TileMap(16, 16)
        tilemap.import_terrain_map("ground", {"0,0": "dirt", "1,1": "grass"})
        tilemap.delete_terrain_layer("ground")
        self.assertNotIn("ground", tilemap.terrain_layers)
        tilemap.import_trait_map("collision", {"2,2": "wall"})
        tilemap.delete_trait_layer("collision")
        self.assertNotIn("collision", tilemap.trait_layers)


if __name__ == "__main__":
    unittest.main()
