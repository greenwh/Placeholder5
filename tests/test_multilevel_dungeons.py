"""
Tests for multi-level dungeon system
"""

import unittest
from aerthos.entities.player import PlayerCharacter
from aerthos.world.multilevel_dungeon import MultiLevelDungeon
from aerthos.world.dungeon import Dungeon
from aerthos.world.room import Room
from aerthos.generator.multilevel_generator import MultiLevelGenerator
from aerthos.engine.game_state import GameState, GameData
from aerthos.storage.scenario_library import ScenarioLibrary


class TestMultiLevelDungeon(unittest.TestCase):
    """Test multi-level dungeon functionality using generator"""

    def setUp(self):
        """Set up test fixtures"""
        self.player = PlayerCharacter(
            name="Test Hero",
            race="Human",
            char_class="Fighter",
            strength=16,
            dexterity=14,
            constitution=14,
            intelligence=10,
            wisdom=10,
            charisma=10
        )
        self.player.hp_max = 20
        self.player.hp_current = 20

    def test_multilevel_dungeon_num_levels_property(self):
        """Test num_levels property"""
        ml_dungeon = MultiLevelDungeon(name="Test Dungeon")

        # Should start with 0 levels
        self.assertEqual(ml_dungeon.num_levels, 0)

        # Generate a simple dungeon for each level
        generator = MultiLevelGenerator()
        test_dungeon = generator.generate(num_levels=2, rooms_per_level=5)

        self.assertEqual(test_dungeon.num_levels, 2)

    def test_game_state_with_multilevel_dungeon(self):
        """Test GameState recognizes multi-level dungeons"""
        # Generate multi-level dungeon
        generator = MultiLevelGenerator()
        ml_dungeon = generator.generate(num_levels=2, rooms_per_level=5)

        # Create game state
        game_data = GameData()
        game_state = GameState(self.player, ml_dungeon)

        self.assertTrue(game_state.is_multilevel)
        self.assertEqual(game_state.current_level, 1)

    def test_multilevel_serialization(self):
        """Test serializing and deserializing multi-level dungeons"""
        # Generate a multi-level dungeon
        generator = MultiLevelGenerator()
        ml_dungeon = generator.generate(num_levels=2, rooms_per_level=5)

        # Serialize
        serialized = ml_dungeon.serialize()

        self.assertIn('levels', serialized)
        self.assertIn('current_level', serialized)
        self.assertEqual(serialized['name'], ml_dungeon.name)

        # Deserialize (use deserialize() for serialize() format)
        restored = MultiLevelDungeon.deserialize(serialized)

        self.assertEqual(restored.name, ml_dungeon.name)
        self.assertEqual(restored.num_levels, ml_dungeon.num_levels)
        self.assertEqual(restored.current_level_number, ml_dungeon.current_level_number)

    def test_scenario_library_restore_multilevel(self):
        """Test restoring multi-level dungeon from saved state"""
        library = ScenarioLibrary()

        # Generate and serialize a multi-level dungeon
        generator = MultiLevelGenerator()
        ml_dungeon = generator.generate(num_levels=2, rooms_per_level=5)

        dungeon_state = ml_dungeon.serialize()

        # Restore it
        restored = library.restore_dungeon_from_state(dungeon_state)

        self.assertIsInstance(restored, MultiLevelDungeon)
        self.assertEqual(restored.name, ml_dungeon.name)
        self.assertEqual(restored.num_levels, 2)


class TestMultiLevelGenerator(unittest.TestCase):
    """Test multi-level dungeon generator"""

    def test_generator_creates_multilevel_dungeon(self):
        """Test that generator creates valid multi-level dungeons"""
        generator = MultiLevelGenerator()

        ml_dungeon = generator.generate(
            num_levels=2,
            rooms_per_level=5,
            dungeon_name="Test Depths"
        )

        self.assertIsInstance(ml_dungeon, MultiLevelDungeon)
        self.assertEqual(ml_dungeon.num_levels, 2)
        self.assertEqual(ml_dungeon.name, "Test Depths")

    def test_generator_difficulty_scaling(self):
        """Test that difficulty increases with depth"""
        generator = MultiLevelGenerator()

        ml_dungeon = generator.generate(
            num_levels=3,
            rooms_per_level=5
        )

        # Check that each level has appropriate difficulty tier
        for level_num in range(1, ml_dungeon.num_levels + 1):
            level = ml_dungeon.levels[level_num]
            # Difficulty tier should match level number (capped at 4)
            expected_tier = min(level_num, 4)
            self.assertEqual(level.difficulty_tier, expected_tier)

    def test_generator_connects_levels_with_stairs(self):
        """Test that levels are connected with stairs"""
        generator = MultiLevelGenerator()

        ml_dungeon = generator.generate(
            num_levels=2,
            rooms_per_level=10
        )

        # Check level 1 has at least one stairs_down exit
        level1 = ml_dungeon.get_current_dungeon()
        has_stairs_down = False

        for room in level1.rooms.values():
            if 'stairs_down' in room.exits or 'down' in room.exits:
                has_stairs_down = True
                break

        self.assertTrue(has_stairs_down, "Level 1 should have stairs going down")


if __name__ == '__main__':
    unittest.main()
