"""
Test suite for Storage Systems

Tests character roster, party manager, scenario library, and session manager.
These are used by BOTH CLI and Web UI for persistence.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json

from aerthos.storage.character_roster import CharacterRoster
from aerthos.storage.party_manager import PartyManager
from aerthos.storage.scenario_library import ScenarioLibrary
from aerthos.storage.session_manager import SessionManager
from aerthos.entities.player import PlayerCharacter
from aerthos.entities.party import Party
from aerthos.world.dungeon import Dungeon
from aerthos.world.room import Room


class TestCharacterRoster(unittest.TestCase):
    """Test character persistence"""

    def setUp(self):
        """Set up temporary test directory"""
        self.test_dir = tempfile.mkdtemp()
        self.roster = CharacterRoster(roster_dir=self.test_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)

    def create_test_character(self, name="Test Fighter"):
        """Helper to create test character"""
        char = PlayerCharacter(
            name=name,
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

    def test_save_character(self):
        """Test saving a character"""
        char = self.create_test_character()
        char_id = self.roster.save_character(char)

        self.assertIsNotNone(char_id)
        self.assertTrue(len(char_id) > 0)

        # Check file was created (filename format: {name}_{id}.json)
        char_file = Path(self.test_dir) / f"{char.name.lower().replace(' ', '_')}_{char_id}.json"
        self.assertTrue(char_file.exists())

    def test_load_character(self):
        """Test loading a saved character"""
        char = self.create_test_character(name="Loadable Fighter")
        char_id = self.roster.save_character(char)

        # Load it back
        loaded_char = self.roster.load_character(char_id)

        self.assertIsNotNone(loaded_char)
        self.assertEqual(loaded_char.name, "Loadable Fighter")
        self.assertEqual(loaded_char.char_class, "fighter")
        self.assertEqual(loaded_char.level, 1)

    def test_save_load_preserves_stats(self):
        """Test save/load preserves all stats"""
        char = self.create_test_character()
        char.strength = 18
        char.dexterity = 16
        char.hp_current = 15
        char.hp_max = 20
        char.xp = 1000

        char_id = self.roster.save_character(char)
        loaded_char = self.roster.load_character(char_id)

        self.assertEqual(loaded_char.strength, 18)
        self.assertEqual(loaded_char.dexterity, 16)
        self.assertEqual(loaded_char.hp_current, 15)
        self.assertEqual(loaded_char.hp_max, 20)
        self.assertEqual(loaded_char.xp, 1000)

    def test_list_characters(self):
        """Test listing all characters"""
        char1 = self.create_test_character(name="Fighter1")
        char2 = self.create_test_character(name="Fighter2")

        self.roster.save_character(char1)
        self.roster.save_character(char2)

        characters = self.roster.list_characters()

        self.assertGreaterEqual(len(characters), 2)
        names = [c['name'] for c in characters]
        self.assertIn("Fighter1", names)
        self.assertIn("Fighter2", names)

    def test_delete_character(self):
        """Test deleting a character"""
        char = self.create_test_character()
        char_id = self.roster.save_character(char)

        # Verify it exists (filename format: {name}_{id}.json)
        char_file = Path(self.test_dir) / f"{char.name.lower().replace(' ', '_')}_{char_id}.json"
        self.assertTrue(char_file.exists())

        # Delete it
        result = self.roster.delete_character(char_id)
        self.assertTrue(result)

        # Verify it's gone
        self.assertFalse(char_file.exists())

    def test_load_nonexistent_character(self):
        """Test loading non-existent character returns None"""
        char = self.roster.load_character("nonexistent_id_12345")
        self.assertIsNone(char)

    def test_multiple_characters_independent(self):
        """Test multiple characters don't interfere"""
        char1 = self.create_test_character(name="Char1")
        char1.hp_current = 5

        char2 = self.create_test_character(name="Char2")
        char2.hp_current = 15

        id1 = self.roster.save_character(char1)
        id2 = self.roster.save_character(char2)

        loaded1 = self.roster.load_character(id1)
        loaded2 = self.roster.load_character(id2)

        self.assertEqual(loaded1.name, "Char1")
        self.assertEqual(loaded1.hp_current, 5)

        self.assertEqual(loaded2.name, "Char2")
        self.assertEqual(loaded2.hp_current, 15)


class TestPartyManager(unittest.TestCase):
    """Test party persistence"""

    def setUp(self):
        """Set up temporary test directories"""
        self.test_dir = tempfile.mkdtemp()
        self.char_dir = Path(self.test_dir) / "characters"
        self.party_dir = Path(self.test_dir) / "parties"
        self.char_dir.mkdir()
        self.party_dir.mkdir()

        self.roster = CharacterRoster(roster_dir=str(self.char_dir))
        self.party_manager = PartyManager(parties_dir=str(self.party_dir), character_roster=self.roster)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)

    def create_test_character(self, name="Fighter"):
        """Helper to create test character"""
        char = PlayerCharacter(
            name=name,
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

    def test_save_party(self):
        """Test saving a party"""
        # Create and save characters
        char1 = self.create_test_character(name="Fighter")
        char2 = self.create_test_character(name="Cleric")
        char1_id = self.roster.save_character(char1)
        char2_id = self.roster.save_character(char2)

        # Create party
        party = Party()
        party.add_member(char1)
        party.add_member(char2)

        # Save party
        party_name = "Test Party"
        party_id = self.party_manager.save_party(party_name=party_name, character_ids=[char1_id, char2_id], formation=party.formation)

        self.assertIsNotNone(party_id)

        # Check file was created (filename format: {name}_{id}.json)
        party_file = Path(self.party_dir) / f"{party_name.lower().replace(' ', '_')}_{party_id}.json"
        self.assertTrue(party_file.exists())

    def test_load_party(self):
        """Test loading a saved party"""
        # Create and save characters
        char1 = self.create_test_character(name="Fighter")
        char2 = self.create_test_character(name="Cleric")
        char1_id = self.roster.save_character(char1)
        char2_id = self.roster.save_character(char2)

        # Create and save party
        party = Party()
        party.add_member(char1)
        party.add_member(char2)
        party_id = self.party_manager.save_party(party_name="Test Party", character_ids=[char1_id, char2_id], formation=party.formation)

        # Load it back
        loaded_party_data = self.party_manager.load_party(party_id)

        self.assertIsNotNone(loaded_party_data)
        # load_party returns {'party': Party, 'name': str, 'id': str, ...}
        self.assertEqual(loaded_party_data['name'], "Test Party")
        self.assertIn('party', loaded_party_data)
        self.assertEqual(len(loaded_party_data['party'].members), 2)

    def test_list_parties(self):
        """Test listing all parties"""
        # Create characters
        char1 = self.create_test_character(name="F1")
        char1_id = self.roster.save_character(char1)

        # Create parties
        party1 = Party()
        party1.add_member(char1)

        party2 = Party()
        party2.add_member(char1)

        self.party_manager.save_party(party_name="Party1", character_ids=[char1_id], formation=party1.formation)
        self.party_manager.save_party(party_name="Party2", character_ids=[char1_id], formation=party2.formation)

        parties = self.party_manager.list_parties()

        self.assertGreaterEqual(len(parties), 2)
        names = [p['name'] for p in parties]
        self.assertIn("Party1", names)
        self.assertIn("Party2", names)

    def test_delete_party(self):
        """Test deleting a party"""
        char = self.create_test_character()
        char_id = self.roster.save_character(char)

        party = Party()
        party.add_member(char)
        party_name = "Test Party"
        party_id = self.party_manager.save_party(party_name=party_name, character_ids=[char_id], formation=party.formation)

        # Verify exists (filename format: {name}_{id}.json)
        party_file = Path(self.party_dir) / f"{party_name.lower().replace(' ', '_')}_{party_id}.json"
        self.assertTrue(party_file.exists())

        # Delete
        result = self.party_manager.delete_party(party_id)
        self.assertTrue(result)

        # Verify gone
        self.assertFalse(party_file.exists())


class TestScenarioLibrary(unittest.TestCase):
    """Test dungeon/scenario persistence"""

    def setUp(self):
        """Set up temporary test directory"""
        self.test_dir = tempfile.mkdtemp()
        self.library = ScenarioLibrary(scenarios_dir=self.test_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)

    def create_test_dungeon(self):
        """Helper to create test dungeon"""
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
            description="Northern room.",
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

    def test_save_scenario(self):
        """Test saving a scenario"""
        dungeon = self.create_test_dungeon()

        scenario_id = self.library.save_scenario(
            dungeon,
            scenario_name="Test Scenario",
            description="Test description"
        )

        self.assertIsNotNone(scenario_id)

        # Check file was created (filename format: {name}_{id}.json)
        scenario_file = Path(self.test_dir) / f"test_scenario_{scenario_id}.json"
        self.assertTrue(scenario_file.exists())

    def test_load_scenario(self):
        """Test loading a saved scenario"""
        dungeon = self.create_test_dungeon()

        scenario_id = self.library.save_scenario(
            dungeon,
            scenario_name="Loadable Scenario"
        )

        # Load it back
        scenario_data = self.library.load_scenario(scenario_id)

        self.assertIsNotNone(scenario_data)
        self.assertEqual(scenario_data['name'], "Loadable Scenario")
        self.assertIn('dungeon_data', scenario_data)

    def test_create_dungeon_from_scenario(self):
        """Test creating dungeon from saved scenario"""
        dungeon = self.create_test_dungeon()

        scenario_id = self.library.save_scenario(
            dungeon,
            scenario_name="Dungeon Scenario"
        )

        # Load and recreate dungeon
        recreated_dungeon = self.library.create_dungeon_from_scenario(scenario_id)

        self.assertIsNotNone(recreated_dungeon)
        self.assertEqual(recreated_dungeon.name, "Test Dungeon")
        self.assertIsNotNone(recreated_dungeon.get_room("test_001"))
        self.assertIsNotNone(recreated_dungeon.get_room("test_002"))

    def test_list_scenarios(self):
        """Test listing all scenarios"""
        dungeon1 = self.create_test_dungeon()
        dungeon2 = self.create_test_dungeon()

        self.library.save_scenario(dungeon1, scenario_name="Scenario1")
        self.library.save_scenario(dungeon2, scenario_name="Scenario2")

        scenarios = self.library.list_scenarios()

        self.assertGreaterEqual(len(scenarios), 2)
        names = [s['name'] for s in scenarios]
        self.assertIn("Scenario1", names)
        self.assertIn("Scenario2", names)

    def test_delete_scenario(self):
        """Test deleting a scenario"""
        dungeon = self.create_test_dungeon()
        scenario_name = "Delete Me"
        scenario_id = self.library.save_scenario(dungeon, scenario_name=scenario_name)

        # Verify exists (filename format: {name}_{id}.json)
        scenario_file = Path(self.test_dir) / f"{scenario_name.lower().replace(' ', '_')}_{scenario_id}.json"
        self.assertTrue(scenario_file.exists())

        # Delete
        result = self.library.delete_scenario(scenario_id)
        self.assertTrue(result)

        # Verify gone
        self.assertFalse(scenario_file.exists())


class TestSessionManager(unittest.TestCase):
    """Test game session persistence"""

    def setUp(self):
        """Set up temporary test directories"""
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
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)

    def create_test_character(self, name="Fighter"):
        """Helper to create test character"""
        char = PlayerCharacter(
            name=name,
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

        rooms = {
            "test_001": room
        }

        dungeon = Dungeon(
            name="Test Dungeon",
            start_room_id="test_001",
            rooms=rooms
        )
        return dungeon

    def test_create_session(self):
        """Test creating a game session"""
        # Create character and party
        char = self.create_test_character()
        char_id = self.roster.save_character(char)

        party = Party()
        party.add_member(char)
        party_id = self.party_manager.save_party(party_name="Test Party", character_ids=[char_id], formation=party.formation)

        # Create scenario
        dungeon = self.create_test_dungeon()
        scenario_id = self.scenario_library.save_scenario(dungeon, scenario_name="Test Scenario")

        # Create session
        session_id = self.session_manager.create_session(
            session_name="Test Session",
            party_id=party_id,
            scenario_id=scenario_id
        )

        self.assertIsNotNone(session_id)

        # Check file was created (filename format: session_{id}.json)
        session_file = Path(self.session_dir) / f"session_{session_id}.json"
        self.assertTrue(session_file.exists())

    def test_list_sessions(self):
        """Test listing all sessions"""
        # Create minimal session
        char = self.create_test_character()
        char_id = self.roster.save_character(char)

        party = Party()
        party.add_member(char)
        party_id = self.party_manager.save_party(party_name="Test Party", character_ids=[char_id], formation=party.formation)

        dungeon = self.create_test_dungeon()
        scenario_id = self.scenario_library.save_scenario(dungeon, scenario_name="Scenario")

        session_id = self.session_manager.create_session(
            party_id=party_id,
            scenario_id=scenario_id,
            session_name="Session1"
        )

        sessions = self.session_manager.list_sessions()

        self.assertGreaterEqual(len(sessions), 1)
        names = [s['name'] for s in sessions]
        self.assertIn("Session1", names)

    def test_delete_session(self):
        """Test deleting a session"""
        # Create minimal session
        char = self.create_test_character()
        char_id = self.roster.save_character(char)

        party = Party()
        party.add_member(char)
        party_id = self.party_manager.save_party(party_name="Test Party", character_ids=[char_id], formation=party.formation)

        dungeon = self.create_test_dungeon()
        scenario_id = self.scenario_library.save_scenario(dungeon, scenario_name="Scenario")

        session_id = self.session_manager.create_session(
            party_id=party_id,
            scenario_id=scenario_id,
            session_name="Delete Me"
        )

        # Verify exists (filename format: session_{id}.json)
        session_file = Path(self.session_dir) / f"session_{session_id}.json"
        self.assertTrue(session_file.exists())

        # Delete
        result = self.session_manager.delete_session(session_id)
        self.assertTrue(result)

        # Verify gone
        self.assertFalse(session_file.exists())


if __name__ == '__main__':
    unittest.main()
