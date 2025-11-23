"""
Test XP Calculation System

Tests for AD&D 1e XP awards from monster defeats.
These tests establish a baseline before implementing dynamic XP calculation.
"""

import unittest
import json
from pathlib import Path

from aerthos.entities.monster import Monster
from aerthos.entities.player import PlayerCharacter
from aerthos.entities.party import Party
from aerthos.engine.game_state import GameState


class TestXPCalculationBaseline(unittest.TestCase):
    """Test current XP award system before implementing AD&D 1e formula"""

    def setUp(self):
        """Load monster data for testing"""
        data_dir = Path(__file__).parent.parent / "aerthos" / "data"
        with open(data_dir / "monsters.json") as f:
            self.monsters_data = json.load(f)

    def test_monster_xp_values_exist(self):
        """Test that all monsters have xp_value field"""
        for monster_id, data in self.monsters_data.items():
            self.assertIn('xp_value', data,
                         f"Monster {monster_id} missing xp_value")
            self.assertIsInstance(data['xp_value'], int,
                                f"Monster {monster_id} xp_value not an integer")
            self.assertGreaterEqual(data['xp_value'], 0,
                                  f"Monster {monster_id} has negative XP")

    def test_xp_values_reasonable_by_hd(self):
        """Test that XP values increase with Hit Dice"""
        # Sample monsters of increasing power
        low_hd = self.monsters_data['kobold']  # 1d8
        mid_hd = self.monsters_data['ogre']    # 4+1
        high_hd = self.monsters_data['troll']  # 6+6

        self.assertLess(low_hd['xp_value'], mid_hd['xp_value'],
                       "Lower HD monster has more XP than higher HD")
        self.assertLess(mid_hd['xp_value'], high_hd['xp_value'],
                       "Mid HD monster has more XP than high HD")

    def test_monster_creation_preserves_xp(self):
        """Test that Monster objects correctly store XP value"""
        kobold_data = self.monsters_data['kobold']
        kobold = Monster(
            name=kobold_data['name'],
            race="Humanoid",  # Required by Character base class
            char_class="Monster",  # Required by Character base class
            hit_dice=kobold_data['hit_dice'],
            ac=kobold_data['ac'],
            thac0=kobold_data['thac0'],
            damage=kobold_data['damage'],
            xp_value=kobold_data['xp_value']
        )

        self.assertEqual(kobold.xp_value, kobold_data['xp_value'],
                        "Monster XP value not preserved in object")

    def test_xp_award_to_single_character(self):
        """Test XP is correctly awarded to a single character"""
        # Create a test character
        character = PlayerCharacter(
            name="Test Fighter",
            race="Human",
            char_class="Fighter",
            alignment="Lawful Good",
            level=1,
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=10,
            wisdom=10,
            charisma=12,
            hp_current=10,
            hp_max=10,
            ac=10,
            thac0=20,
            save_poison=14,
            save_rod_staff_wand=16,
            save_petrify_paralyze=15,
            save_breath=17,
            save_spell=17,
            xp=0,
            xp_to_next_level=2000
        )

        initial_xp = character.xp
        kobold_xp = self.monsters_data['kobold']['xp_value']

        # Award XP
        character.gain_xp(kobold_xp)

        self.assertEqual(character.xp, initial_xp + kobold_xp,
                        "Character did not receive correct XP")

    def test_xp_split_among_party(self):
        """Test XP is correctly split among party members"""
        # Create test party
        fighter = PlayerCharacter(
            name="Fighter", race="Human", char_class="Fighter",
            alignment="Lawful Good", level=1,
            strength=16, dexterity=14, constitution=15,
            intelligence=10, wisdom=10, charisma=12,
            hp_current=10, hp_max=10, ac=10, thac0=20,
            save_poison=14, save_rod_staff_wand=16,
            save_petrify_paralyze=15, save_breath=17, save_spell=17,
            xp=0, xp_to_next_level=2000
        )

        cleric = PlayerCharacter(
            name="Cleric", race="Human", char_class="Cleric",
            alignment="Lawful Good", level=1,
            strength=14, dexterity=10, constitution=14,
            intelligence=12, wisdom=16, charisma=13,
            hp_current=8, hp_max=8, ac=10, thac0=20,
            save_poison=10, save_rod_staff_wand=14,
            save_petrify_paralyze=13, save_breath=16, save_spell=15,
            xp=0, xp_to_next_level=1500
        )

        party = Party(max_size=6)
        party.add_member(fighter)
        party.add_member(cleric)

        # Award XP for killing an orc (10 XP)
        orc_xp = self.monsters_data['orc']['xp_value']
        xp_per_member = orc_xp // 2  # Split between 2 members

        fighter.gain_xp(xp_per_member)
        cleric.gain_xp(xp_per_member)

        self.assertEqual(fighter.xp, xp_per_member,
                        "Fighter did not receive correct XP share")
        self.assertEqual(cleric.xp, xp_per_member,
                        "Cleric did not receive correct XP share")


class TestXPCalculationEdgeCases(unittest.TestCase):
    """Test edge cases in XP calculation"""

    def setUp(self):
        """Create test character"""
        self.character = PlayerCharacter(
            name="Test", race="Human", char_class="Fighter",
            alignment="True Neutral", level=1,
            strength=16, dexterity=14, constitution=15,
            intelligence=10, wisdom=10, charisma=12,
            hp_current=10, hp_max=10, ac=10, thac0=20,
            save_poison=14, save_rod_staff_wand=16,
            save_petrify_paralyze=15, save_breath=17, save_spell=17,
            xp=0, xp_to_next_level=2000
        )

    def test_zero_xp_award(self):
        """Test that 0 XP can be awarded without error"""
        initial_xp = self.character.xp
        self.character.gain_xp(0)
        self.assertEqual(self.character.xp, initial_xp,
                        "Character XP changed with 0 XP award")

    def test_large_xp_award(self):
        """Test awarding large XP values (e.g., dragon)"""
        data_dir = Path(__file__).parent.parent / "aerthos" / "data"
        with open(data_dir / "monsters.json") as f:
            monsters_data = json.load(f)

        # Get a high-XP monster if available
        high_xp_monsters = [m for m in monsters_data.values()
                           if m.get('xp_value', 0) > 1000]

        if high_xp_monsters:
            dragon_xp = high_xp_monsters[0]['xp_value']
            initial_xp = self.character.xp
            self.character.gain_xp(dragon_xp)
            self.assertEqual(self.character.xp, initial_xp + dragon_xp,
                           "Large XP award not handled correctly")

    def test_xp_does_not_decrease(self):
        """Test that XP never decreases (documents current behavior)"""
        self.character.gain_xp(100)
        xp_after_gain = self.character.xp

        # NOTE: Current implementation DOES allow negative XP
        # This is a bug that should be fixed, but we document it here
        self.character.gain_xp(-50)

        # KNOWN ISSUE: gain_xp() allows negative values
        # After XP calculation refactor, this should be fixed
        # For now, we just document that XP can decrease (bug)
        self.assertEqual(self.character.xp, 50,
                        "XP behavior changed - update this test if gain_xp() was fixed")


class TestXPCalculationDocumentation(unittest.TestCase):
    """Document current XP values for regression testing"""

    def test_document_sample_monster_xp(self):
        """Document XP values for common monsters (baseline for future comparison)"""
        data_dir = Path(__file__).parent.parent / "aerthos" / "data"
        with open(data_dir / "monsters.json") as f:
            monsters_data = json.load(f)

        # Document key monsters and their current XP values
        expected_xp = {
            'kobold': 5,
            'orc': 10,
            'goblin': 10,  # Actual value in monsters.json
            'hobgoblin': 20,
            'ogre': 90,
            'troll': 525
        }

        for monster_id, expected in expected_xp.items():
            if monster_id in monsters_data:
                actual = monsters_data[monster_id]['xp_value']
                self.assertEqual(actual, expected,
                               f"{monster_id} XP changed: expected {expected}, got {actual}")


if __name__ == '__main__':
    unittest.main()
