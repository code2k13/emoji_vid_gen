import unittest
from plugins.plugin_base import PluginBase

class TestPluginBase(unittest.TestCase):
    def test_valid_config(self):
        config = {
            "global": {
                "width": 1920,
                "height": 1080,
                "use_cuda": "true"
            }
        }
        try:
            plugin = PluginBase(config)
        except ValueError as e:
            self.fail(f"Unexpected ValueError: {e}")

    def test_invalid_width(self):
        config = {
            "global": {
                "width": 0,
                "height": 1080,
                "use_cuda": "true"
            }
        }
        with self.assertRaises(ValueError) as context:
            plugin = PluginBase(config)
        self.assertEqual(str(context.exception),
                         "Width and height must be positive numbers.")

    def test_invalid_use_cuda(self):
        config = {
            "global": {
                "width": 1920,
                "height": 1080,
                "use_cuda": "invalid_value"
            }
        }
        with self.assertRaises(ValueError) as context:
            plugin = PluginBase(config)
        self.assertEqual(str(context.exception),
                         "use_cuda must be 'true' or 'false' (case-sensitive).")


if __name__ == "__main__":
    unittest.main()
