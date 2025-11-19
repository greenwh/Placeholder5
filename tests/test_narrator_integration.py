"""
Test suite for DMNarrator integration with dungeon generation
"""

import unittest
from aerthos.generator.dungeon_generator import DungeonGenerator
from aerthos.generator.config import DungeonConfig
from aerthos.systems.narrator import DMNarrator, NarrativeContext


class TestNarratorIntegration(unittest.TestCase):
    """Test DMNarrator integration with dungeon generator"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = DungeonConfig(
            num_rooms=5,
            layout_type='linear',
            dungeon_theme='mine',
            seed=12345  # Fixed seed for reproducibility
        )

    def test_narrator_enabled_by_default(self):
        """Test that DMNarrator is enabled by default"""
        generator = DungeonGenerator()
        self.assertTrue(generator.use_narrator)
        self.assertIsNotNone(generator.narrator)
        self.assertIsInstance(generator.narrator, DMNarrator)

    def test_narrator_can_be_disabled(self):
        """Test that DMNarrator can be disabled"""
        generator = DungeonGenerator(use_narrator=False)
        self.assertFalse(generator.use_narrator)
        self.assertIsNone(generator.narrator)

    def test_dungeon_generation_with_narrator(self):
        """Test that dungeon generation works with narrator enabled"""
        generator = DungeonGenerator(use_narrator=True)
        dungeon = generator.generate(self.config)

        self.assertIsNotNone(dungeon)
        self.assertIn('rooms', dungeon)
        self.assertGreaterEqual(len(dungeon['rooms']), 5)

        # Check that rooms have descriptions
        for room_id, room_data in dungeon['rooms'].items():
            self.assertIn('description', room_data)
            self.assertIsInstance(room_data['description'], str)
            self.assertGreater(len(room_data['description']), 10)

    def test_dungeon_generation_without_narrator(self):
        """Test that dungeon generation works without narrator (fallback)"""
        generator = DungeonGenerator(use_narrator=False)
        dungeon = generator.generate(self.config)

        self.assertIsNotNone(dungeon)
        self.assertIn('rooms', dungeon)

        # Should still have descriptions (using fallback templates)
        for room_id, room_data in dungeon['rooms'].items():
            self.assertIn('description', room_data)
            self.assertIsInstance(room_data['description'], str)
            self.assertGreater(len(room_data['description']), 10)

    def test_narrator_descriptions_are_different(self):
        """Test that narrator-enhanced descriptions differ from fallback"""
        # Generate with narrator
        gen_with_narrator = DungeonGenerator(use_narrator=True)
        dungeon_with = gen_with_narrator.generate(self.config)

        # Generate without narrator (same seed)
        gen_without_narrator = DungeonGenerator(use_narrator=False)
        dungeon_without = gen_without_narrator.generate(self.config)

        # Descriptions should be structurally different
        # (Narrator adds atmospheric language, sensory details, etc.)
        desc_with = dungeon_with['rooms']['room_001']['description']
        desc_without = dungeon_without['rooms']['room_001']['description']

        # They should both exist but be different
        self.assertNotEqual(desc_with, desc_without)

    def test_narrator_room_entrance_descriptions(self):
        """Test that narrator provides varied room entrance descriptions"""
        narrator = DMNarrator()
        context = NarrativeContext(
            location_type="dungeon",
            atmosphere=["dark", "ancient"],
            light_level="torch"
        )

        # Generate multiple descriptions for same parameters
        descriptions = []
        for _ in range(10):
            desc = narrator.describe_room_entrance(
                room_type="chamber",
                size="large",
                primary_features=["Stone pillars rise to the ceiling."],
                context=context
            )
            descriptions.append(desc)

        # All should be valid strings
        for desc in descriptions:
            self.assertIsInstance(desc, str)
            self.assertGreater(len(desc), 20)

        # Should have some variation (not all identical)
        unique_descriptions = set(descriptions)
        self.assertGreater(len(unique_descriptions), 1,
                          "Narrator should provide varied descriptions")

    def test_narrator_theme_integration(self):
        """Test that narrator integrates with different dungeon themes"""
        themes = ['mine', 'crypt', 'cave', 'ruins', 'sewer']

        for theme in themes:
            config = DungeonConfig(
                num_rooms=3,
                dungeon_theme=theme,
                seed=12345
            )
            generator = DungeonGenerator(use_narrator=True)
            dungeon = generator.generate(config)

            # Check entrance room has theme-appropriate description
            entrance_desc = dungeon['rooms']['room_001']['description']
            self.assertIsInstance(entrance_desc, str)
            self.assertGreater(len(entrance_desc), 20)

    def test_narrator_with_encounters(self):
        """Test that narrator works with rooms containing encounters"""
        config = DungeonConfig(
            num_rooms=8,
            layout_type='branching',
            combat_frequency=0.6,  # High encounter rate
            monster_pool=['kobold', 'goblin', 'orc'],
            seed=12345
        )

        generator = DungeonGenerator(use_narrator=True)
        dungeon = generator.generate(config)

        # Find room with encounter
        room_with_encounter = None
        for room_id, room_data in dungeon['rooms'].items():
            if room_data.get('encounters'):
                room_with_encounter = room_data
                break

        # Should have at least one encounter
        self.assertIsNotNone(room_with_encounter,
                            "Should have at least one room with encounter")

        # Room should have description with monster hint
        if room_with_encounter:
            self.assertIn('description', room_with_encounter)
            # Monster hints are appended, so description should mention danger
            # (This is handled by _add_monster_hint)


class TestNarrativeContext(unittest.TestCase):
    """Test NarrativeContext dataclass"""

    def test_context_creation(self):
        """Test creating narrative context"""
        context = NarrativeContext(
            location_type="dungeon",
            atmosphere=["dark", "damp"],
            time_of_day="night",
            light_level="torch"
        )

        self.assertEqual(context.location_type, "dungeon")
        self.assertEqual(context.atmosphere, ["dark", "damp"])
        self.assertEqual(context.time_of_day, "night")
        self.assertEqual(context.light_level, "torch")

    def test_context_defaults(self):
        """Test context default values"""
        context = NarrativeContext()

        self.assertEqual(context.location_type, "dungeon")
        self.assertEqual(context.atmosphere, [])
        self.assertEqual(context.time_of_day, "day")
        self.assertEqual(context.light_level, "torch")
        self.assertEqual(context.recent_events, [])
        self.assertEqual(context.party_condition, "healthy")


if __name__ == '__main__':
    unittest.main()
