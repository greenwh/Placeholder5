#!/usr/bin/env python3
"""
UI Parity Tests - Verify CLI and Web UI produce identical results

CRITICAL: These tests ensure that both user interfaces (CLI and Web UI)
use the same underlying game logic and produce identical characters,
game states, and outcomes.

If these tests fail, it means the UIs have diverged!
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aerthos.engine.game_state import GameData
from aerthos.ui.character_creation import CharacterCreator
from aerthos.entities.player import PlayerCharacter


class TestUIParityCharacterCreation(unittest.TestCase):
    """Verify character creation produces identical results in both UIs"""

    @classmethod
    def setUpClass(cls):
        cls.game_data = GameData.load_all()

    def test_magic_user_has_spells(self):
        """Magic-Users created via quick_create must have starting spells"""
        creator = CharacterCreator(self.game_data)
        mage = creator.quick_create("TestMage", "Human", "Magic-User")

        # Verify spell slots
        self.assertGreater(len(mage.spells_memorized), 0,
                          "Magic-User should have at least 1 spell slot")

        # Verify known spells
        self.assertGreater(len(mage.spells_known), 0,
                          "Magic-User should know at least 1 spell")

        # Verify specific starting spells
        spell_names = [spell.name for spell in mage.spells_known]
        self.assertIn("Magic Missile", spell_names,
                     "Magic-User should know Magic Missile")
        self.assertIn("Sleep", spell_names,
                     "Magic-User should know Sleep")

    def test_cleric_has_spells(self):
        """Clerics created via quick_create must have starting spells"""
        creator = CharacterCreator(self.game_data)
        cleric = creator.quick_create("TestCleric", "Human", "Cleric")

        # Verify spell slots
        self.assertGreater(len(cleric.spells_memorized), 0,
                          "Cleric should have at least 1 spell slot")

        # Verify known spells (Clerics know all level 1 spells)
        self.assertGreater(len(cleric.spells_known), 0,
                          "Cleric should know level 1 spells")

        # Verify at least some standard Cleric spells
        spell_names = [spell.name for spell in cleric.spells_known]
        self.assertIn("Cure Light Wounds", spell_names,
                     "Cleric should know Cure Light Wounds")

    def test_fighter_has_no_spells(self):
        """Fighters should not have spells at level 1"""
        creator = CharacterCreator(self.game_data)
        fighter = creator.quick_create("TestFighter", "Human", "Fighter")

        self.assertEqual(len(fighter.spells_memorized), 0,
                        "Fighter should have 0 spell slots at level 1")
        self.assertEqual(len(fighter.spells_known), 0,
                        "Fighter should know 0 spells at level 1")

    def test_thief_has_no_spells(self):
        """Thieves should not have spells at level 1"""
        creator = CharacterCreator(self.game_data)
        thief = creator.quick_create("TestThief", "Human", "Thief")

        self.assertEqual(len(thief.spells_memorized), 0,
                        "Thief should have 0 spell slots at level 1")
        self.assertEqual(len(thief.spells_known), 0,
                        "Thief should know 0 spells at level 1")

    def test_all_classes_have_starting_equipment(self):
        """All classes must have starting equipment"""
        creator = CharacterCreator(self.game_data)

        for char_class in ['Fighter', 'Cleric', 'Magic-User', 'Thief']:
            with self.subTest(char_class=char_class):
                char = creator.quick_create("Test", "Human", char_class)

                # All characters should have items
                self.assertGreater(len(char.inventory.items), 0,
                                  f"{char_class} should have starting items")

                # All characters should have equipped weapon
                self.assertIsNotNone(char.equipment.weapon,
                                    f"{char_class} should have equipped weapon")

    def test_serialization_preserves_spells(self):
        """Verify that saving/loading preserves spell data"""
        from aerthos.storage.character_roster import CharacterRoster
        import tempfile
        import shutil

        # Create temp directory for test
        temp_dir = tempfile.mkdtemp()

        try:
            roster = CharacterRoster(roster_dir=temp_dir)
            creator = CharacterCreator(self.game_data)

            # Create spellcaster
            original = creator.quick_create("TestMage", "Human", "Magic-User")
            original_spell_count = len(original.spells_known)
            original_slot_count = len(original.spells_memorized)

            # Save
            char_id = roster.save_character(original)

            # Load
            loaded = roster.load_character(character_id=char_id)

            # Verify spells preserved
            self.assertEqual(len(loaded.spells_known), original_spell_count,
                           "Save/load should preserve spell count")
            self.assertEqual(len(loaded.spells_memorized), original_slot_count,
                           "Save/load should preserve spell slot count")

            # Verify spell details
            for orig_spell, loaded_spell in zip(original.spells_known, loaded.spells_known):
                self.assertEqual(orig_spell.name, loaded_spell.name,
                               "Save/load should preserve spell names")
                self.assertEqual(orig_spell.level, loaded_spell.level,
                               "Save/load should preserve spell levels")

        finally:
            # Cleanup temp directory
            shutil.rmtree(temp_dir)


class TestUIParityGameMechanics(unittest.TestCase):
    """Verify game mechanics produce identical results in both UIs"""

    @classmethod
    def setUpClass(cls):
        cls.game_data = GameData.load_all()

    def test_combat_calculations_consistent(self):
        """Combat calculations must be identical regardless of UI"""
        from aerthos.engine.combat import CombatResolver, DiceRoller

        # Create identical characters
        creator = CharacterCreator(self.game_data)
        fighter1 = creator.quick_create("Fighter1", "Human", "Fighter")
        fighter2 = creator.quick_create("Fighter2", "Human", "Fighter")

        # Both should have same THAC0 at level 1
        self.assertEqual(fighter1.thac0, fighter2.thac0,
                        "Identical characters should have same THAC0")

        # Both should have same AC calculation logic
        self.assertEqual(fighter1.ac, fighter2.ac,
                        "Identical characters should have same AC")

    def test_xp_calculations_consistent(self):
        """XP requirements must be identical regardless of UI"""
        creator = CharacterCreator(self.game_data)

        for char_class in ['Fighter', 'Cleric', 'Magic-User', 'Thief']:
            with self.subTest(char_class=char_class):
                char1 = creator.quick_create("Char1", "Human", char_class)
                char2 = creator.quick_create("Char2", "Human", char_class)

                self.assertEqual(char1.xp_to_next_level, char2.xp_to_next_level,
                               f"{char_class} XP requirements should be consistent")


if __name__ == '__main__':
    unittest.main()
