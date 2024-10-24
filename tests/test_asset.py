import unittest
import tempfile
import os

from mergic.asset import AssetFinder


class TestAssetFinder(unittest.TestCase):
    def test_load(self):
        def example_loader(filepath: str | os.PathLike):
            with open(filepath) as f:
                return f.read()
        asset_finder = AssetFinder()
        with tempfile.TemporaryFile(delete=False) as f:
            f.write(b"hello world!")
            f.seek(0)
            f.name
            asset_finder.register("example_text", f.name, "text")
            text = asset_finder.load("example_text", "text", example_loader)
            self.assertEqual(text, "hello world!")
