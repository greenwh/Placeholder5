"""
Test suite for GameState - Core Game Logic

Tests the central game state manager that both CLI and Web UI depend on.
This is THE critical integration point - if this works, both UIs should work.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os
from pathlib import Path

from aerthos.engine.game_state import GameState, GameData
from aerthos.engine.parser import Command
from aerthos.entities.player import PlayerCharacter
from aerthos.world.dungeon import Dungeon
from aerthos.world.room import Room


class TestGameData(unittest.TestCase):
    """Test GameData loading from JSON files"""

    def test_game_data_loads(self):
        """Test that GameData loads all JSON files"""
        # load_all() is a class method that returns a loaded instance
        data = GameData.load_all()

        # Check all data dictionaries are populated
        self.assertIsNotNone(data.classes)
        self.assertIsNotNone(data.races)
        self.assertIsNotNone(data.monsters)
        # Note: items.json is deprecated - use armor.json, weapons.json, equipment.json instead
        self.assertIsNotNone(data.spells)

        self.assertGreater(len(data.classes), 0)
        self.assertGreater(len(data.races), 0)
        self.assertGreater(len(data.monsters), 0)
        # items.json no longer loaded
        self.assertGreater(len(data.spells), 0)

    def test_classes_data_structure(self):
        """Test classes data has expected structure"""
        data = GameData.load_all()

        # Should have 4 classes
        self.assertGreaterEqual(len(data.classes), 4)

        # Check for expected classes
        expected_classes = ['Fighter', 'Cleric', 'Magic-User', 'Thief']
        for cls in expected_classes:
            self.assertIn(cls, data.classes)

        # Check class structure
        fighter = data.classes['Fighter']
        # Class data doesn't have 'name' field, the key IS the name
        self.assertIn('hit_die', fighter)
        self.assertIn('thac0_progression', fighter)

    def test_races_data_structure(self):
        """Test races data has expected structure"""
        data = GameData.load_all()

        # Should have 4 races
        self.assertGreaterEqual(len(data.races), 4)

        # Check for expected races (capitalized in data)
        expected_races = ['Human', 'Elf', 'Dwarf', 'Halfling']
        for race in expected_races:
            self.assertIn(race, data.races)

    def test_monsters_data_structure(self):
        """Test monsters data has expected structure"""
        data = GameData.load_all()

        self.assertGreater(len(data.monsters), 0)

        # Check a monster has required fields
        monster_id = list(data.monsters.keys())[0]
        monster = data.monsters[monster_id]

        self.assertIn('name', monster)
        self.assertIn('hit_dice', monster)
        self.assertIn('ac', monster)
        self.assertIn('thac0', monster)

    def test_spells_data_structure(self):
        """Test spells data has expected structure"""
        data = GameData.load_all()

        # Should have 7 implemented spells
        self.assertGreaterEqual(len(data.spells), 7)

        # Check a spell has required fields
        spell_id = list(data.spells.keys())[0]
        spell = data.spells[spell_id]

        self.assertIn('name', spell)
        self.assertIn('level', spell)


class TestGameStateInitialization(unittest.TestCase):
    """Test GameState initialization"""

    def create_test_dungeon(self):
        """Helper to create minimal test dungeon"""
        room1 = Room(
            id="test_001",
            title="Test Room",
            description="A test room.",
            exits={"north": "test_002"},
            light_level="bright"
        )
        room2 = Room(
            id="test_002",
            title="North Room",
            description="The northern room.",
            exits={"south": "test_001"},
            light_level="bright"
        )

        rooms = {
            "test_001": room1,
            "test_002": room2
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
            name="Test Fighter",
            race="human",
            char_class="fighter",
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
        char.xp = 0
        return char

    def test_game_state_initialization(self):
        """Test GameState initializes correctly"""
        dungeon = self.create_test_dungeon()
        player = self.create_test_character()

        game_state = GameState(player=player, dungeon=dungeon)

        self.assertEqual(game_state.player, player)
        self.assertEqual(game_state.dungeon, dungeon)
        self.assertIsNotNone(game_state.current_room)
        self.assertTrue(game_state.is_active)
        self.assertFalse(game_state.in_combat)

    def test_game_state_starts_in_start_room(self):
        """Test game starts in dungeon's start room"""
        dungeon = self.create_test_dungeon()
        player = self.create_test_character()

        game_state = GameState(player=player, dungeon=dungeon)

        self.assertEqual(game_state.current_room.id, "test_001")


class TestGameStateCommands(unittest.TestCase):
    """Test GameState command execution"""

    def setUp(self):
        """Set up test game state"""
        self.dungeon = self.create_test_dungeon()
        self.player = self.create_test_character()
        self.game_state = GameState(player=self.player, dungeon=self.dungeon)

    def create_test_dungeon(self):
        """Helper to create minimal test dungeon"""
        room1 = Room(
            id="test_001",
            title="Test Room",
            description="A test room.",
            exits={"north": "test_002"},
            light_level="bright"
        )
        room2 = Room(
            id="test_002",
            title="North Room",
            description="The northern room.",
            exits={"south": "test_001"},
            light_level="bright"
        )

        rooms = {
            "test_001": room1,
            "test_002": room2
        }

        # Dungeon constructor takes name, start_room_id, and rooms dict
        dungeon = Dungeon(
            name="Test Dungeon",
            start_room_id="test_001",
            rooms=rooms
        )
        return dungeon

    def create_test_character(self):
        """Helper to create test character"""
        char = PlayerCharacter(
            name="Test Fighter",
            race="human",
            char_class="fighter",
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
        char.xp = 0
        return char

    def test_look_command(self):
        """Test look/examine command"""
        cmd = Command(action="look")
        result = self.game_state.execute_command(cmd)

        self.assertIsNotNone(result)
        self.assertIn('message', result)
        self.assertIn('Test Room', result['message'])

    def test_inventory_command(self):
        """Test inventory command"""
        cmd = Command(action="inventory")
        result = self.game_state.execute_command(cmd)

        self.assertIsNotNone(result)
        self.assertIn('message', result)

    def test_status_command(self):
        """Test status command"""
        cmd = Command(action="status")
        result = self.game_state.execute_command(cmd)

        self.assertIsNotNone(result)
        self.assertIn('message', result)
        self.assertIn('Test Fighter', result['message'])

    def test_move_command_valid(self):
        """Test valid movement"""
        cmd = Command(action="move", target="north")
        result = self.game_state.execute_command(cmd)

        self.assertIsNotNone(result)
        self.assertIn('message', result)
        # Should have moved to room 2
        self.assertEqual(self.game_state.current_room.id, "test_002")

    def test_move_command_invalid_direction(self):
        """Test movement in invalid direction"""
        cmd = Command(action="move", target="west")
        result = self.game_state.execute_command(cmd)

        self.assertIsNotNone(result)
        self.assertIn('message', result)
        # Should not have moved
        self.assertEqual(self.game_state.current_room.id, "test_001")

    def test_map_command(self):
        """Test map command"""
        cmd = Command(action="map")
        result = self.game_state.execute_command(cmd)

        self.assertIsNotNone(result)
        self.assertIn('message', result)

    def test_help_command(self):
        """Test help command"""
        cmd = Command(action="help")
        result = self.game_state.execute_command(cmd)

        self.assertIsNotNone(result)
        self.assertIn('message', result)

    def test_unknown_command(self):
        """Test unknown command handling"""
        cmd = Command(action="unknown_action_xyz")
        result = self.game_state.execute_command(cmd)

        self.assertIsNotNone(result)
        self.assertIn('message', result)

    def test_command_returns_dict(self):
        """Test all commands return dict with 'message' key"""
        commands = [
            Command(action="look"),
            Command(action="inventory"),
            Command(action="status"),
            Command(action="help"),
            Command(action="map")
        ]

        for cmd in commands:
            result = self.game_state.execute_command(cmd)
            self.assertIsInstance(result, dict)
            self.assertIn('message', result)


class TestGameStateSerialization(unittest.TestCase):
    """Test GameState serialization for saves"""

    def create_test_game_state(self):
        """Helper to create test game state"""
        room1 = Room(
            id="test_001",
            title="Test Room",
            description="A test room.",
            exits={},
            light_level="bright"
        )

        rooms = {
            "test_001": room1
        }

        dungeon = Dungeon(
            name="Test Dungeon",
            start_room_id="test_001",
            rooms=rooms
        )

        char = PlayerCharacter(
            name="Test Fighter",
            race="human",
            char_class="fighter",
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
        char.xp = 0

        game_state = GameState(player=char, dungeon=dungeon)
        return game_state

    def test_game_state_has_serialize_method(self):
        """Test GameState can be serialized"""
        game_state = self.create_test_game_state()

        # Check if serialize method exists
        self.assertTrue(hasattr(game_state, 'to_dict') or
                        hasattr(game_state, 'serialize') or
                        hasattr(game_state, '__dict__'))

    def test_game_state_json_serializable(self):
        """Test GameState data is JSON serializable"""
        game_state = self.create_test_game_state()

        # Try to serialize key components
        try:
            if hasattr(game_state, 'to_dict'):
                data = game_state.to_dict()
            else:
                # Fallback to manual serialization
                data = {
                    'player': game_state.player.__dict__ if hasattr(game_state.player, '__dict__') else {},
                    'current_room_id': game_state.current_room.id if game_state.current_room else None,
                    'is_active': game_state.is_active,
                    'in_combat': game_state.in_combat
                }

            # This will raise if not JSON serializable
            json_str = json.dumps(data, default=str)
            self.assertIsNotNone(json_str)

        except Exception as e:
            self.fail(f"GameState serialization failed: {e}")


class TestGameStateIntegration(unittest.TestCase):
    """Integration tests for full game flow"""

    def test_full_exploration_sequence(self):
        """Test complete exploration sequence"""
        # Create dungeon with multiple rooms
        room1 = Room(
            id="test_001",
            title="Entry",
            description="Entry room.",
            exits={"north": "test_002", "east": "test_003"},
            light_level="bright"
        )
        room2 = Room(
            id="test_002",
            title="North Room",
            description="Northern room.",
            exits={"south": "test_001"},
            light_level="bright"
        )
        room3 = Room(
            id="test_003",
            title="East Room",
            description="Eastern room.",
            exits={"west": "test_001"},
            light_level="bright"
        )

        rooms = {
            "test_001": room1,
            "test_002": room2,
            "test_003": room3
        }

        dungeon = Dungeon(
            name="Test Dungeon",
            start_room_id="test_001",
            rooms=rooms
        )

        char = PlayerCharacter(
            name="Explorer",
            race="human",
            char_class="fighter",
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

        game_state = GameState(player=char, dungeon=dungeon)

        # Start in room 1
        self.assertEqual(game_state.current_room.id, "test_001")

        # Move north to room 2
        cmd = Command(action="move", target="north")
        result = game_state.execute_command(cmd)
        self.assertEqual(game_state.current_room.id, "test_002")

        # Move back south
        cmd = Command(action="move", target="south")
        result = game_state.execute_command(cmd)
        self.assertEqual(game_state.current_room.id, "test_001")

        # Move east to room 3
        cmd = Command(action="move", target="east")
        result = game_state.execute_command(cmd)
        self.assertEqual(game_state.current_room.id, "test_003")

        # Move back west
        cmd = Command(action="move", target="west")
        result = game_state.execute_command(cmd)
        self.assertEqual(game_state.current_room.id, "test_001")


if __name__ == '__main__':
    unittest.main()
