import unittest

from witchfarm_autoclicker.clicker import WitchFarmClicker


class ClickerVectorTests(unittest.TestCase):
    def test_direction_vectors_cover_expected_grid(self):
        expected = {
            "center",
            "up-left",
            "up",
            "up-right",
            "left",
            "right",
            "down-left",
            "down",
            "down-right",
        }
        self.assertEqual(set(WitchFarmClicker.DIRECTION_VECTORS.keys()), expected)

    def test_direction_vector_signs(self):
        vectors = WitchFarmClicker.DIRECTION_VECTORS
        self.assertEqual(vectors["center"], (0, 0))
        self.assertEqual(vectors["right"], (1, 0))
        self.assertEqual(vectors["left"], (-1, 0))
        self.assertEqual(vectors["up"], (0, -1))
        self.assertEqual(vectors["down"], (0, 1))


if __name__ == "__main__":
    unittest.main()
