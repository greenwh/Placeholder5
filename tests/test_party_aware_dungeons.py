"""
Tests for party-aware dungeon generation system
"""

import unittest
from aerthos.entities.player import PlayerCharacter
from aerthos.entities.party import Party
from aerthos.systems.party_analyzer import PartyAnalyzer
from aerthos.generator.config import DungeonConfig


class TestPartyAnalyzer(unittest.TestCase):
    """Test party analysis for dungeon scaling"""

    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = PartyAnalyzer()

        # Create test party
        self.fighter = PlayerCharacter(
            name="Fighter",
            race="Human",
            char_class="Fighter",
            strength=16,
            dexterity=12,
            constitution=14,
            intelligence=10,
            wisdom=10,
            charisma=10
        )
        self.fighter.hp_max = 18

        self.cleric = PlayerCharacter(
            name="Cleric",
            race="Human",
            char_class="Cleric",
            strength=14,
            dexterity=10,
            constitution=14,
            intelligence=10,
            wisdom=16,
            charisma=12
        )
        self.cleric.hp_max = 12

        self.mage = PlayerCharacter(
            name="Mage",
            race="Human",
            char_class="Magic-User",
            strength=10,
            dexterity=14,
            constitution=12,
            intelligence=18,
            wisdom=14,
            charisma=10
        )
        self.mage.hp_max = 6

        self.thief = PlayerCharacter(
            name="Thief",
            race="Halfling",
            char_class="Thief",
            strength=12,
            dexterity=18,
            constitution=14,
            intelligence=12,
            wisdom=10,
            charisma=14
        )
        self.thief.hp_max = 8

        self.party = Party(max_size=6)
        self.party.add_member(self.fighter)
        self.party.add_member(self.cleric)
        self.party.add_member(self.mage)
        self.party.add_member(self.thief)

    def test_analyze_party_basic_stats(self):
        """Test basic party analysis statistics"""
        analysis = self.analyzer.analyze_party(self.party)

        self.assertEqual(analysis['apl'], 1.0, "APL should be 1.0 for level 1 party")
        self.assertEqual(analysis['party_size'], 4, "Party size should be 4")
        self.assertEqual(analysis['fighters'], 1, "Should detect 1 fighter")
        self.assertEqual(analysis['healers'], 1, "Should detect 1 cleric")
        self.assertEqual(analysis['casters'], 1, "Should detect 1 magic-user")
        self.assertEqual(analysis['thieves'], 1, "Should detect 1 thief")

    def test_analyze_party_capabilities(self):
        """Test capability detection"""
        analysis = self.analyzer.analyze_party(self.party)

        self.assertTrue(analysis['has_thief_skills'], "Should detect thief skills")
        self.assertTrue(analysis['has_healing'], "Should detect healing capability")
        self.assertTrue(analysis['has_aoe_magic'], "Should detect AoE magic capability")

    def test_analyze_party_hp_pool(self):
        """Test HP pool calculation"""
        analysis = self.analyzer.analyze_party(self.party)

        expected_hp = 18 + 12 + 6 + 8  # Fighter + Cleric + Mage + Thief
        self.assertEqual(analysis['hp_pool'], expected_hp, f"HP pool should be {expected_hp}")

    def test_composition_detection_balanced(self):
        """Test composition detection for diverse party"""
        analysis = self.analyzer.analyze_party(self.party)

        # Party has 1 fighter, 1 cleric, 1 mage, 1 thief
        # Caster percentage = (casters + healers) / size = 2/4 = 50%
        # This triggers magic-heavy classification (>= 50%)
        self.assertEqual(analysis['composition'], 'magic-heavy',
                        "Party with 50% casters+healers classified as magic-heavy")

    def test_composition_detection_combat_heavy(self):
        """Test combat-heavy composition detection"""
        # Create combat-heavy party
        combat_party = Party(max_size=6)
        for i in range(3):
            fighter = PlayerCharacter(
                name=f"Fighter{i}",
                race="Human",
                char_class="Fighter",
                strength=16,
                dexterity=12,
                constitution=14,
                intelligence=10,
                wisdom=10,
                charisma=10
            )
            combat_party.add_member(fighter)

        analysis = self.analyzer.analyze_party(combat_party)
        self.assertEqual(analysis['composition'], 'combat-heavy',
                        "Should detect combat-heavy composition")

    def test_magic_level_none(self):
        """Test magic level detection when no magic items"""
        analysis = self.analyzer.analyze_party(self.party)

        self.assertEqual(analysis['magic_level'], 'none',
                        "Should detect no magic items")

    def test_effective_level_calculation(self):
        """Test effective level with magic boost"""
        analysis = self.analyzer.analyze_party(self.party)

        # With no magic items, effective level = APL + 0.0
        self.assertEqual(analysis['effective_level'], 1.0,
                        "Effective level should equal APL with no magic")

    def test_default_analysis_for_none_party(self):
        """Test default analysis when party is None"""
        analysis = self.analyzer.analyze_party(None)

        self.assertEqual(analysis['apl'], 1)
        self.assertEqual(analysis['party_size'], 1)
        self.assertEqual(analysis['magic_level'], 'none')
        self.assertEqual(analysis['composition'], 'balanced')


class TestDungeonConfigFromInterview(unittest.TestCase):
    """Test dungeon config generation from interview results"""

    def test_from_interview_basic(self):
        """Test creating config from interview results"""
        interview_results = {
            'apl': 2,
            'party_size': 4,
            'composition': 'balanced',
            'magic_level': 'low'
        }

        config = DungeonConfig.from_interview(interview_results)

        self.assertIsInstance(config, DungeonConfig)
        self.assertEqual(config.party_level, 2, "Party level should match APL")

    def test_from_interview_combat_heavy_adjustments(self):
        """Test combat-heavy composition adjustments"""
        interview_results = {
            'apl': 2,
            'party_size': 4,
            'composition': 'combat-heavy',
            'magic_level': 'low'
        }

        config = DungeonConfig.from_interview(interview_results)

        self.assertGreaterEqual(config.combat_frequency, 0.6,
                               "Combat-heavy should have high combat frequency")
        self.assertLessEqual(config.trap_frequency, 0.2,
                            "Combat-heavy should have low trap frequency")

    def test_from_interview_magic_heavy_adjustments(self):
        """Test magic-heavy composition adjustments"""
        interview_results = {
            'apl': 2,
            'party_size': 4,
            'composition': 'magic-heavy',
            'magic_level': 'medium'
        }

        config = DungeonConfig.from_interview(interview_results)

        self.assertLessEqual(config.combat_frequency, 0.6,
                            "Magic-heavy should have moderate combat frequency")

    def test_from_interview_lethality_adjustments(self):
        """Test lethality adjustments based on magic level"""
        # High magic = higher lethality
        high_magic = {
            'apl': 3,
            'party_size': 4,
            'composition': 'balanced',
            'magic_level': 'high'
        }

        config_high = DungeonConfig.from_interview(high_magic)
        self.assertGreaterEqual(config_high.lethality_factor, 1.0,
                               "High magic should increase lethality")

        # No magic = lower lethality
        no_magic = {
            'apl': 3,
            'party_size': 4,
            'composition': 'balanced',
            'magic_level': 'none'
        }

        config_low = DungeonConfig.from_interview(no_magic)
        self.assertLessEqual(config_low.lethality_factor, 1.0,
                            "No magic should decrease lethality")

    def test_from_interview_uses_for_party_internally(self):
        """Test that from_interview calls for_party internally"""
        interview_results = {
            'apl': 2,
            'party_size': 4,
            'composition': 'balanced',
            'magic_level': 'low'
        }

        config = DungeonConfig.from_interview(interview_results)

        # Config should have monster pool and boss (set by for_party)
        self.assertIsNotNone(config.monster_pool,
                            "Should have monster pool from for_party()")
        self.assertIsNotNone(config.boss_monster,
                            "Should have boss monster from for_party()")


if __name__ == '__main__':
    unittest.main()
