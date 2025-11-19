"""
Test suite for Treasure Generation System

Converted from tests_manual/test_magic_items.py
Tests treasure generation with magic items, statistical validation, and treasure types.
"""

import unittest
from aerthos.systems.treasure import TreasureGenerator


class TestTreasureGeneration(unittest.TestCase):
    """Test treasure generation with magic items"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = TreasureGenerator()

    def test_treasure_generator_initialized(self):
        """Test that TreasureGenerator loads treasure tables"""
        self.assertIsNotNone(self.generator)
        self.assertIsNotNone(self.generator.treasure_types)
        self.assertIn('A', self.generator.treasure_types)
        self.assertIn('G', self.generator.treasure_types)

    def test_treasure_type_a_generation(self):
        """Test Treasure Type A generation (30% chance of magic items)"""
        # Generate several hoards
        for _ in range(10):
            hoard = self.generator.generate_lair_treasure("A")

            # Should have treasure structure
            self.assertIsNotNone(hoard)
            self.assertHasAttr(hoard, 'magic_items')
            self.assertHasAttr(hoard, 'copper')
            self.assertHasAttr(hoard, 'silver')
            self.assertHasAttr(hoard, 'gold')
            self.assertHasAttr(hoard, 'platinum')

            # Magic items should be list (may be empty)
            self.assertIsInstance(hoard.magic_items, list)

    def test_treasure_type_g_generation(self):
        """Test Treasure Type G generation (35% chance of magic + scroll)"""
        # Generate several hoards
        for _ in range(10):
            hoard = self.generator.generate_lair_treasure("G")

            self.assertIsNotNone(hoard)
            self.assertIsInstance(hoard.magic_items, list)

    def test_treasure_type_f_generation(self):
        """Test Treasure Type F generation (complex magic items)"""
        # Generate several hoards
        for _ in range(10):
            hoard = self.generator.generate_lair_treasure("F")

            self.assertIsNotNone(hoard)
            self.assertIsInstance(hoard.magic_items, list)

    def test_direct_magic_item_generation(self):
        """Test direct magic item generation by category"""
        categories = ["potions", "scrolls", "weapons", "armor", "rings", "misc_magic"]

        for category in categories:
            item = self.generator._generate_magic_item(category)

            # _generate_magic_item returns dict (converted to object when added to hoard)
            self.assertIsInstance(item, dict)
            self.assertIn('name', item)
            self.assertIn('xp_value', item)
            self.assertIn('gp_value', item)

            # Values should be non-negative
            self.assertGreaterEqual(item['xp_value'], 0)
            self.assertGreaterEqual(item['gp_value'], 0)

            # Name should not be empty
            self.assertGreater(len(item['name']), 0)

    def test_statistical_magic_item_rate_type_a(self):
        """Test that Type A has approximately 30% magic item rate"""
        magic_count = 0
        total_items = 0
        trials = 100

        for _ in range(trials):
            hoard = self.generator.generate_lair_treasure("A")
            if hoard.magic_items:
                magic_count += 1
                total_items += len(hoard.magic_items)

        # Should have approximately 30% magic rate (allow 10-50% range due to RNG)
        magic_percentage = (magic_count / trials) * 100
        self.assertGreaterEqual(magic_percentage, 10,
                               f"Magic item rate too low: {magic_percentage}%")
        self.assertLessEqual(magic_percentage, 50,
                            f"Magic item rate too high: {magic_percentage}%")

        # When magic items present, should average around 3
        if magic_count > 0:
            avg_items = total_items / magic_count
            self.assertGreaterEqual(avg_items, 1)
            self.assertLessEqual(avg_items, 6)

    def test_treasure_hoard_structure(self):
        """Test that treasure hoards have expected structure"""
        hoard = self.generator.generate_lair_treasure("A")

        # Check hoard has required attributes
        self.assertTrue(hasattr(hoard, 'copper'))
        self.assertTrue(hasattr(hoard, 'silver'))
        self.assertTrue(hasattr(hoard, 'gold'))
        self.assertTrue(hasattr(hoard, 'platinum'))
        self.assertTrue(hasattr(hoard, 'gems'))
        self.assertTrue(hasattr(hoard, 'jewelry'))
        self.assertTrue(hasattr(hoard, 'magic_items'))

        # Coin values should be integers
        self.assertIsInstance(hoard.copper, int)
        self.assertIsInstance(hoard.silver, int)
        self.assertIsInstance(hoard.gold, int)
        self.assertIsInstance(hoard.platinum, int)

        # Gems and jewelry should be lists
        self.assertIsInstance(hoard.gems, list)
        self.assertIsInstance(hoard.jewelry, list)

        # Magic items should be list
        self.assertIsInstance(hoard.magic_items, list)

    def test_magic_items_have_proper_structure(self):
        """Test that generated magic items are proper objects"""
        # Generate enough hoards to ensure we get some magic items
        found_magic = False
        for _ in range(50):
            hoard = self.generator.generate_lair_treasure("A")
            if hoard.magic_items:
                found_magic = True
                for item in hoard.magic_items:
                    # Each item should be an object with name attribute
                    self.assertTrue(hasattr(item, 'name'))
                    self.assertIsInstance(item.name, str)
                    self.assertGreater(len(item.name), 0)

                    # Should have xp_value and gp_value
                    self.assertTrue(hasattr(item, 'xp_value'))
                    self.assertTrue(hasattr(item, 'gp_value'))

                    # Values should be numeric and non-negative
                    self.assertIsInstance(item.xp_value, (int, float))
                    self.assertIsInstance(item.gp_value, (int, float))
                    self.assertGreaterEqual(item.xp_value, 0)
                    self.assertGreaterEqual(item.gp_value, 0)

                break

        # We should have found at least one magic item in 50 tries
        self.assertTrue(found_magic, "Failed to generate any magic items in 50 treasure hoards")

    def test_different_treasure_types_exist(self):
        """Test that multiple treasure types can be generated"""
        treasure_types_to_test = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        for treasure_type in treasure_types_to_test:
            hoard = self.generator.generate_lair_treasure(treasure_type)

            # Should generate valid hoard
            self.assertIsNotNone(hoard)
            self.assertIsInstance(hoard.magic_items, list)

    def test_coins_generated_with_treasure(self):
        """Test that treasure includes coins (statistically)"""
        # Should have individual coin attributes
        hoard = self.generator.generate_lair_treasure("A")
        self.assertTrue(hasattr(hoard, 'copper'))
        self.assertTrue(hasattr(hoard, 'silver'))
        self.assertTrue(hasattr(hoard, 'gold'))
        self.assertTrue(hasattr(hoard, 'platinum'))

        # Type A has probability of coins, not guaranteed
        # Test that at least SOME hoards have coins
        coin_count = 0
        for _ in range(20):
            hoard = self.generator.generate_lair_treasure("A")
            total_coins = hoard.copper + hoard.silver + hoard.gold + hoard.platinum
            if total_coins > 0:
                coin_count += 1

        self.assertGreater(coin_count, 0, "Should generate some hoards with coins")

    def assertHasAttr(self, obj, attr):
        """Helper assertion to check if object has attribute"""
        self.assertTrue(hasattr(obj, attr),
                       f"Object {obj} missing attribute '{attr}'")


if __name__ == '__main__':
    unittest.main()
