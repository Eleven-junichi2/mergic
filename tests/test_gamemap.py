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
        tilemap.paint_tileid("ground", 0, 0, brush="dirt")
        self.assertEqual(tilemap.tileid_layers["ground"]["0,0"], "dirt")
        self.assertEqual(tilemap.tileid_layers["ground"][0, 0], "dirt")
        tilemap.paint_tileid("ground", 15, 15, brush="dirt")
        with self.assertRaises(ValueError):
            tilemap.paint_tileid("ground", 16, 16, brush="dirt")
        tilemap.paint_tiletype(13, 13, brush="wall")
        with self.assertRaises(ValueError):
            tilemap.paint_tiletype(16, 16, brush="water")

    def test_erase_cell(self):
        tilemap = TileMap(16, 16)
        tilemap.paint_tileid("ground", 1, 1, brush="dirt")
        tilemap.erase_tileid("ground", 1, 1)
        self.assertEqual(tilemap.tileid_layers["ground"].get((1, 1)), None)
        self.assertEqual(tilemap.tileid_layers["ground"].get("1,1"), None)

    def test_import_layer(self):
        tilemap = TileMap(16, 16)
        tilemap.import_layer("ground", {"0,0": "dirt", "1,1": "grass"})
        self.assertEqual(tilemap.tileid_layers["ground"]["0,0"], "dirt")
        self.assertEqual(tilemap.tileid_layers["ground"]["1,1"], "grass")
        tilemap.import_layer("water", {"2,2": "water"})
        self.assertEqual(tilemap.tileid_layers["water"]["2,2"], "water")
    
    def test_delete_layer(self):
        tilemap = TileMap(16, 16)
        tilemap.import_layer("ground", {"0,0": "dirt", "1,1": "grass"})
        tilemap.delete_layer("ground")
        self.assertNotIn("ground", tilemap.tileid_layers)
        with self.assertRaises(KeyError):
            tilemap.tileid_layers["ground"]["0,0"]


if __name__ == "__main__":
    unittest.main()
