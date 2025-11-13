"""
Integration Tests - End-to-End Game Scenarios

Tests complete game flows that both CLI and Web UI depend on.
These tests verify that all systems work together correctly.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from aerthos.engine.game_state import GameState, GameData
from aerthos.engine.parser import CommandParser
from aerthos.entities.player import PlayerCharacter
from aerthos.entities.party import Party
from aerthos.world.dungeon import Dungeon
from aerthos.world.room import Room
from aerthos.generator.dungeon_generator import DungeonGenerator
from aerthos.generator.config import DungeonConfig
from aerthos.storage.character_roster import CharacterRoster
from aerthos.storage.party_manager import PartyManager
from aerthos.storage.scenario_library import ScenarioLibrary
from aerthos.storage.session_manager import SessionManager
from aerthos.ui.character_creation import CharacterCreator


class TestCompleteGameFlow(unittest.TestCase):
    """Test complete game flow from character creation to dungeon exploration"""

    def setUp(self):
        """Set up game data"""
        self.game_data = GameData()
        self.game_data.load_all()
        self.parser = CommandParser()

    def create_test_dungeon(self):
        """Helper to create test dungeon"""
        room1 = Room(
            id="test_001",
            title="Entry Hall",
            description="A large entry hall with stone walls.",
            exits={"north": "test_002", "east": "test_003"},
            light_level="bright",
            is_safe_for_rest=True
        )
        room2 = Room(
            id="test_002",
            title="Northern Passage",
            description="A narrow passage heading north.",
            exits={"south": "test_001", "north": "test_004"},
            light_level="dim"
        )
        room3 = Room(
            id="test_003",
            title="Eastern Chamber",
            description="A dusty chamber with old furniture.",
            exits={"west": "test_001"},
            light_level="dark"
        )
        room4 = Room(
            id="test_004",
            title="Treasure Room",
            description="A room filled with treasure!",
            exits={"south": "test_002"},
            light_level="bright",
            is_safe_for_rest=True
        )

        rooms = {
            "test_001": room1,
            "test_002": room2,
            "test_003": room3,
            "test_004": room4
        }

        dungeon = Dungeon(
            name="Test Dungeon",
            start_room_id="test_001",
            rooms=rooms
        )
        return dungeon

    def create_test_character(self):
        """Helper to create test character"""
        char = PlayerCharacter(
            name="Test Hero",
            race="human",
            char_class="Fighter",
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=10,
            wisdom=12,
            charisma=10
        )
        char.hp_current = 20
        char.hp_max = 20
        char.level = 1
        char.xp = 0
        return char

    def test_exploration_sequence(self):
        """Test complete exploration of dungeon"""
        dungeon = self.create_test_dungeon()
        player = self.create_test_character()
        game_state = GameState(player=player, dungeon=dungeon)

        # Start in entry hall
        self.assertEqual(game_state.current_room.id, "test_001")

        # Look around
        cmd = self.parser.parse("look")
        result = game_state.execute_command(cmd)
        self.assertIn('message', result)
        self.assertIn('Entry Hall', result['message'])

        # Check status
        cmd = self.parser.parse("status")
        result = game_state.execute_command(cmd)
        self.assertIn('Test Hero', result['message'])

        # Move north
        cmd = self.parser.parse("north")
        result = game_state.execute_command(cmd)
        self.assertEqual(game_state.current_room.id, "test_002")

        # Continue north
        cmd = self.parser.parse("north")
        result = game_state.execute_command(cmd)
        self.assertEqual(game_state.current_room.id, "test_004")

        # Check map shows explored rooms
        cmd = self.parser.parse("map")
        result = game_state.execute_command(cmd)
        self.assertIn('message', result)

        # Return to start
        cmd = self.parser.parse("south")
        game_state.execute_command(cmd)
        self.assertEqual(game_state.current_room.id, "test_002")

        cmd = self.parser.parse("south")
        game_state.execute_command(cmd)
        self.assertEqual(game_state.current_room.id, "test_001")

        # Explore east branch
        cmd = self.parser.parse("east")
        game_state.execute_command(cmd)
        self.assertEqual(game_state.current_room.id, "test_003")

    def test_command_parsing_to_execution(self):
        """Test complete flow from text input to game response"""
        dungeon = self.create_test_dungeon()
        player = self.create_test_character()
        game_state = GameState(player=player, dungeon=dungeon)

        # Test various command formats
        test_commands = [
            "look",
            "l",
            "status",
            "stats",
            "inventory",
            "i",
            "map",
            "m",
            "north",
            "n",
            "help"
        ]

        for cmd_text in test_commands:
            cmd = self.parser.parse(cmd_text)
            result = game_state.execute_command(cmd)

            self.assertIsInstance(result, dict, f"Failed for command: {cmd_text}")
            self.assertIn('message', result, f"No message for command: {cmd_text}")
            self.assertIsInstance(result['message'], str, f"Message not string for: {cmd_text}")

    def test_invalid_commands_handled(self):
        """Test invalid commands are handled gracefully"""
        dungeon = self.create_test_dungeon()
        player = self.create_test_character()
        game_state = GameState(player=player, dungeon=dungeon)

        invalid_commands = [
            "asdfghjkl",
            "west",  # No west exit
            "attack",  # No monster
            "take sword",  # No sword in room
            ""
        ]

        for cmd_text in invalid_commands:
            cmd = self.parser.parse(cmd_text)
            result = game_state.execute_command(cmd)

            # Should not crash
            self.assertIsInstance(result, dict)
            self.assertIn('message', result)


class TestPersistenceFlow(unittest.TestCase):
    """Test complete save/load flow across all storage systems"""

    def setUp(self):
        """Set up temporary storage"""
        self.test_dir = tempfile.mkdtemp()
        self.char_dir = Path(self.test_dir) / "characters"
        self.party_dir = Path(self.test_dir) / "parties"
        self.scenario_dir = Path(self.test_dir) / "scenarios"
        self.session_dir = Path(self.test_dir) / "sessions"

        for dir_path in [self.char_dir, self.party_dir, self.scenario_dir, self.session_dir]:
            dir_path.mkdir()

        self.roster = CharacterRoster(roster_dir=str(self.char_dir))
        self.party_manager = PartyManager(parties_dir=str(self.party_dir), character_roster=self.roster)
        self.scenario_library = ScenarioLibrary(scenarios_dir=str(self.scenario_dir))
        self.session_manager = SessionManager(
            sessions_dir=str(self.session_dir),
            character_roster_dir=str(self.char_dir),
            party_manager_dir=str(self.party_dir),
            scenario_library_dir=str(self.scenario_dir)
        )

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)

    def create_test_character(self, name="Fighter"):
        """Helper to create test character"""
        char = PlayerCharacter(
            name=name,
            race="human",
            char_class="Fighter",
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=10,
            wisdom=12,
            charisma=10
        )
        char.hp_current = 10
        char.hp_max = 10
        char.level = 1
        return char

    def create_test_dungeon(self):
        """Helper to create test dungeon"""
        room = Room(
            id="test_001",
            title="Test Room",
            description="A test room.",
            exits={},
            light_level="bright"
        )

        dungeon = Dungeon(
            name="Test Dungeon",
            start_room_id="test_001",
            rooms={"test_001": room}
        )
        return dungeon

    def test_complete_persistence_flow(self):
        """Test full flow: create characters → party → scenario → session"""

        # Step 1: Create and save characters
        char1 = self.create_test_character("Fighter")
        char2 = self.create_test_character("Cleric")
        char3 = self.create_test_character("Thief")
        char4 = self.create_test_character("Mage")

        char1_id = self.roster.save_character(char1)
        char2_id = self.roster.save_character(char2)
        char3_id = self.roster.save_character(char3)
        char4_id = self.roster.save_character(char4)

        # Verify characters saved
        self.assertIsNotNone(char1_id)
        self.assertEqual(len(self.roster.list_characters()), 4)

        # Step 2: Create and save party
        party = Party()
        party.add_member(char1)
        party.add_member(char2)
        party.add_member(char3)
        party.add_member(char4)

        party_id = self.party_manager.save_party(
            party_name="Test Party",
            character_ids=[char1_id, char2_id, char3_id, char4_id],
            formation=party.formation
        )

        # Verify party saved
        self.assertIsNotNone(party_id)
        loaded_party_data = self.party_manager.load_party(party_id)
        self.assertEqual(len(loaded_party_data['party'].members), 4)

        # Step 3: Create and save dungeon
        dungeon = self.create_test_dungeon()
        scenario_id = self.scenario_library.save_scenario(
            dungeon,
            scenario_name="Test Adventure",
            description="A test adventure"
        )

        # Verify scenario saved
        self.assertIsNotNone(scenario_id)
        scenario = self.scenario_library.load_scenario(scenario_id)
        self.assertEqual(scenario['name'], "Test Adventure")

        # Step 4: Create session
        session_id = self.session_manager.create_session(
            party_id=party_id,
            scenario_id=scenario_id,
            session_name="Epic Quest"
        )

        # Verify session created
        self.assertIsNotNone(session_id)
        sessions = self.session_manager.list_sessions()
        self.assertGreaterEqual(len(sessions), 1)

        # Step 5: Load everything back
        loaded_session = next(s for s in sessions if s['id'] == session_id)
        self.assertEqual(loaded_session['name'], "Epic Quest")

    def test_character_survives_roundtrip(self):
        """Test character data survives save/load"""
        char = self.create_test_character("Roundtrip Fighter")
        char.xp = 500
        char.hp_current = 5
        char.level = 2

        char_id = self.roster.save_character(char)
        loaded = self.roster.load_character(char_id)

        self.assertEqual(loaded.name, "Roundtrip Fighter")
        self.assertEqual(loaded.xp, 500)
        self.assertEqual(loaded.hp_current, 5)
        self.assertEqual(loaded.level, 2)

    def test_dungeon_survives_roundtrip(self):
        """Test dungeon data survives save/load"""
        dungeon = self.create_test_dungeon()

        scenario_id = self.scenario_library.save_scenario(
            dungeon,
            scenario_name="Roundtrip Dungeon"
        )

        recreated = self.scenario_library.create_dungeon_from_scenario(scenario_id)

        self.assertIsNotNone(recreated)
        self.assertEqual(recreated.name, "Test Dungeon")
        self.assertIsNotNone(recreated.get_room("test_001"))


class TestProceduralGeneration(unittest.TestCase):
    """Test procedural dungeon generation integration"""

    def setUp(self):
        """Set up game data and generator"""
        self.game_data = GameData()
        self.game_data.load_all()
        self.generator = DungeonGenerator(game_data=self.game_data)

    def test_generated_dungeon_playable(self):
        """Test generated dungeon can be played"""
        config = DungeonConfig(
            num_rooms=5,
            layout_type='linear',
            combat_frequency=0.0,  # No combat for this test
            trap_frequency=0.0,
            treasure_frequency=0.0
        )

        dungeon_data = self.generator.generate(config)
        dungeon = Dungeon.load_from_generator(dungeon_data)

        # Create character and game state
        player = PlayerCharacter(
            name="Explorer",
            race="human",
            char_class="Fighter",
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=10,
            wisdom=12,
            charisma=10
        )
        player.hp_current = 20
        player.hp_max = 20
        player.level = 1

        game_state = GameState(player=player, dungeon=dungeon)

        # Should be able to look around
        parser = CommandParser()
        cmd = parser.parse("look")
        result = game_state.execute_command(cmd)

        self.assertIn('message', result)

        # Should be able to check map
        cmd = parser.parse("map")
        result = game_state.execute_command(cmd)

        self.assertIn('message', result)

    def test_different_configs_generate_different_dungeons(self):
        """Test different configurations produce different results"""
        config_easy = DungeonConfig(
            num_rooms=5,
            combat_frequency=0.2
        )

        config_hard = DungeonConfig(
            num_rooms=15,
            combat_frequency=0.5,
            trap_frequency=0.2,
            treasure_frequency=0.2
        )

        dungeon_easy_data = self.generator.generate(config_easy)
        dungeon_hard_data = self.generator.generate(config_hard)

        dungeon_easy = Dungeon.load_from_generator(dungeon_easy_data)
        dungeon_hard = Dungeon.load_from_generator(dungeon_hard_data)

        # Different number of rooms (allow RNG variance)
        # EASY config requests 5 rooms, should get 4-6
        self.assertGreaterEqual(len(dungeon_easy.rooms), 4)
        self.assertLessEqual(len(dungeon_easy.rooms), 6)

        # HARD config requests 15 rooms, should get 12-18
        self.assertGreaterEqual(len(dungeon_hard.rooms), 12)
        self.assertLessEqual(len(dungeon_hard.rooms), 18)

        # Hard dungeon should have more rooms than easy
        self.assertGreater(len(dungeon_hard.rooms), len(dungeon_easy.rooms))


class TestCharacterCreation(unittest.TestCase):
    """Test character creation integration"""

    def setUp(self):
        """Set up game data"""
        self.game_data = GameData.load_all()
        self.creator = CharacterCreator(game_data=self.game_data)

    def test_quick_create_all_classes(self):
        """Test quick create for all classes"""
        classes = ['Fighter', 'Cleric', 'Magic-User', 'Thief']

        for char_class in classes:
            char = self.creator.quick_create(
                name=f"Test {char_class}",
                race='human',
                char_class=char_class
            )

            self.assertIsNotNone(char)
            self.assertEqual(char.char_class, char_class)
            self.assertGreater(char.hp_max, 0)
            self.assertEqual(char.hp_current, char.hp_max)

    def test_created_character_can_play(self):
        """Test created character can enter game"""
        char = self.creator.quick_create(
            name="Game Ready",
            race='human',
            char_class='Fighter'
        )

        # Create simple dungeon
        room = Room(
            id="test_001",
            title="Test",
            description="Test room",
            exits={},
            light_level="bright"
        )

        dungeon = Dungeon(
            name="Test",
            start_room_id="test_001",
            rooms={"test_001": room}
        )

        # Should be able to create game state
        game_state = GameState(player=char, dungeon=dungeon)

        self.assertIsNotNone(game_state)
        self.assertTrue(game_state.is_active)


if __name__ == '__main__':
    unittest.main()
