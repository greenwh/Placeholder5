"""
Tests for Ability Modifier System

Tests all six ability score tables and their modifiers:
- Strength (including exceptional strength)
- Intelligence (spell learning, languages)
- Wisdom (magic defense, bonus spells)
- Dexterity (to-hit, AC, thief skills)
- Constitution (HP, system shock, resurrection)
- Charisma (henchmen, loyalty, reactions)
"""

import unittest
from aerthos.systems.ability_modifiers import AbilityModifierSystem
from aerthos.entities.character import Character


class TestAbilityModifierSystem(unittest.TestCase):
    """Test ability modifier lookups"""

    def setUp(self):
        """Set up test fixtures"""
        self.system = AbilityModifierSystem()

    def test_strength_normal_range(self):
        """Test normal strength (3-18) modifiers"""
        # Minimum strength
        mods = self.system.get_strength_modifiers(3)
        self.assertEqual(mods['hit_prob'], -3)
        self.assertEqual(mods['damage'], -1)
        self.assertEqual(mods['weight_allowance'], -350)
        self.assertEqual(mods['bend_bars_lift_gates'], 1)

        # Average strength
        mods = self.system.get_strength_modifiers(10)
        self.assertEqual(mods['hit_prob'], 0)
        self.assertEqual(mods['damage'], 0)
        self.assertEqual(mods['weight_allowance'], 0)

        # High strength
        mods = self.system.get_strength_modifiers(18)
        self.assertEqual(mods['hit_prob'], 2)
        self.assertEqual(mods['damage'], 3)
        self.assertEqual(mods['weight_allowance'], 1000)
        self.assertEqual(mods['bend_bars_lift_gates'], 40)

    def test_exceptional_strength(self):
        """Test exceptional strength (18/01-18/00)"""
        # 18/50 (in 18/01-50 range)
        mods = self.system.get_strength_modifiers(18, 50)
        self.assertEqual(mods['hit_prob'], 1)
        self.assertEqual(mods['damage'], 3)
        self.assertEqual(mods['weight_allowance'], 1000)
        self.assertEqual(mods['open_doors'], '2(1)')

        # 18/75 (in 18/51-75 range)
        mods = self.system.get_strength_modifiers(18, 75)
        self.assertEqual(mods['hit_prob'], 2)
        self.assertEqual(mods['damage'], 3)
        self.assertEqual(mods['weight_allowance'], 1250)
        self.assertEqual(mods['bend_bars_lift_gates'], 45)

        # 18/90 (in 18/76-90 range)
        mods = self.system.get_strength_modifiers(18, 90)
        self.assertEqual(mods['hit_prob'], 2)
        self.assertEqual(mods['damage'], 4)
        self.assertEqual(mods['weight_allowance'], 1500)

        # 18/99 (in 18/91-99 range)
        mods = self.system.get_strength_modifiers(18, 99)
        self.assertEqual(mods['hit_prob'], 2)
        self.assertEqual(mods['damage'], 5)
        self.assertEqual(mods['weight_allowance'], 2000)

        # 18/00 (maximum)
        mods = self.system.get_strength_modifiers(18, 100)
        self.assertEqual(mods['hit_prob'], 3)
        self.assertEqual(mods['damage'], 6)
        self.assertEqual(mods['weight_allowance'], 2500)
        self.assertEqual(mods['bend_bars_lift_gates'], 70)

    def test_intelligence_modifiers(self):
        """Test intelligence modifiers"""
        # Low intelligence (no spellcasting)
        mods = self.system.get_intelligence_modifiers(8)
        self.assertEqual(mods['additional_languages'], 0)
        self.assertEqual(mods['spell_learn_chance'], 0)

        # Minimum magic-user
        mods = self.system.get_intelligence_modifiers(10)
        self.assertEqual(mods['additional_languages'], 1)
        self.assertEqual(mods['spell_learn_chance'], 45)
        self.assertEqual(mods['min_spells_per_level'], 5)
        self.assertEqual(mods['max_spells_per_level'], 7)
        self.assertEqual(mods['max_spell_level'], 5)

        # High intelligence
        mods = self.system.get_intelligence_modifiers(18)
        self.assertEqual(mods['additional_languages'], 7)
        self.assertEqual(mods['spell_learn_chance'], 95)
        self.assertEqual(mods['min_spells_per_level'], 10)
        self.assertEqual(mods['max_spells_per_level'], 999)  # All
        self.assertEqual(mods['max_spell_level'], 9)

    def test_wisdom_modifiers(self):
        """Test wisdom modifiers"""
        # Low wisdom
        mods = self.system.get_wisdom_modifiers(8)
        self.assertEqual(mods['magic_attack_adjustment'], -1)
        self.assertEqual(mods['spell_failure'], 10)
        self.assertEqual(mods['spell_bonus'], {})

        # Average wisdom
        mods = self.system.get_wisdom_modifiers(12)
        self.assertEqual(mods['magic_attack_adjustment'], 0)
        self.assertEqual(mods['spell_failure'], 0)

        # High wisdom (bonus spells)
        mods = self.system.get_wisdom_modifiers(16)
        self.assertEqual(mods['magic_attack_adjustment'], 1)
        self.assertEqual(mods['spell_bonus'], {'1': 2, '2': 1})

        mods = self.system.get_wisdom_modifiers(18)
        self.assertEqual(mods['magic_attack_adjustment'], 3)
        self.assertEqual(mods['spell_bonus'], {'1': 2, '2': 1, '3': 1, '4': 1})

    def test_dexterity_modifiers(self):
        """Test dexterity modifiers"""
        # Low dexterity
        mods = self.system.get_dexterity_modifiers(6)
        self.assertEqual(mods['reaction_attack_adj'], -2)
        self.assertEqual(mods['defensive_adj'], 3)  # Worse AC
        self.assertEqual(mods['pick_pockets'], -10)
        self.assertEqual(mods['open_locks'], -5)

        # Average dexterity
        mods = self.system.get_dexterity_modifiers(10)
        self.assertEqual(mods['reaction_attack_adj'], 0)
        self.assertEqual(mods['defensive_adj'], 0)
        self.assertEqual(mods['pick_pockets'], 0)

        # High dexterity
        mods = self.system.get_dexterity_modifiers(18)
        self.assertEqual(mods['reaction_attack_adj'], 3)
        self.assertEqual(mods['defensive_adj'], -4)  # Better AC
        self.assertEqual(mods['pick_pockets'], 10)
        self.assertEqual(mods['open_locks'], 15)
        self.assertEqual(mods['climb_walls'], 10)

    def test_constitution_modifiers(self):
        """Test constitution modifiers"""
        # Low constitution
        mods = self.system.get_constitution_modifiers(6, is_fighter=False)
        self.assertEqual(mods['hp_adjustment'], -1)
        self.assertEqual(mods['system_shock'], 45)
        self.assertEqual(mods['resurrection_survival'], 50)

        # Average constitution
        mods = self.system.get_constitution_modifiers(12, is_fighter=False)
        self.assertEqual(mods['hp_adjustment'], 0)
        self.assertEqual(mods['system_shock'], 75)
        self.assertEqual(mods['resurrection_survival'], 80)

        # High constitution (non-fighter)
        mods = self.system.get_constitution_modifiers(17, is_fighter=False)
        self.assertEqual(mods['hp_adjustment'], 2)
        self.assertEqual(mods['system_shock'], 95)

        # High constitution (fighter gets better bonus)
        mods = self.system.get_constitution_modifiers(17, is_fighter=True)
        self.assertEqual(mods['hp_adjustment'], 3)

        mods = self.system.get_constitution_modifiers(18, is_fighter=True)
        self.assertEqual(mods['hp_adjustment'], 4)

    def test_charisma_modifiers(self):
        """Test charisma modifiers"""
        # Low charisma
        mods = self.system.get_charisma_modifiers(3)
        self.assertEqual(mods['max_henchmen'], 1)
        self.assertEqual(mods['loyalty_base'], -30)
        self.assertEqual(mods['reaction_adjustment'], -25)

        # Average charisma
        mods = self.system.get_charisma_modifiers(10)
        self.assertEqual(mods['max_henchmen'], 4)
        self.assertEqual(mods['loyalty_base'], 0)
        self.assertEqual(mods['reaction_adjustment'], 0)

        # High charisma
        mods = self.system.get_charisma_modifiers(18)
        self.assertEqual(mods['max_henchmen'], 15)
        self.assertEqual(mods['loyalty_base'], 30)
        self.assertEqual(mods['reaction_adjustment'], 35)

    def test_spell_learning(self):
        """Test spell learning mechanics"""
        # Low INT can't learn
        success, chance = self.system.attempt_spell_learning(8)
        self.assertEqual(chance, 0)
        self.assertFalse(success)

        # Medium INT has 45% chance
        success, chance = self.system.attempt_spell_learning(10)
        self.assertEqual(chance, 45)
        # success is random, just verify it returns bool
        self.assertIsInstance(success, bool)

        # High INT has 95% chance
        success, chance = self.system.attempt_spell_learning(18)
        self.assertEqual(chance, 95)

    def test_system_shock(self):
        """Test system shock survival"""
        # Low CON has low survival
        survived, chance = self.system.check_system_shock(3)
        self.assertEqual(chance, 35)
        self.assertIsInstance(survived, bool)

        # High CON has high survival
        survived, chance = self.system.check_system_shock(18)
        self.assertEqual(chance, 99)

    def test_resurrection_survival(self):
        """Test resurrection survival"""
        # Low CON
        survived, chance = self.system.check_resurrection_survival(3)
        self.assertEqual(chance, 40)

        # High CON (perfect survival)
        survived, chance = self.system.check_resurrection_survival(18)
        self.assertEqual(chance, 100)

    def test_bend_bars(self):
        """Test bend bars/lift gates"""
        # Low STR has low chance
        success, chance = self.system.attempt_bend_bars(3)
        self.assertEqual(chance, 1)

        # High STR has good chance
        success, chance = self.system.attempt_bend_bars(18)
        self.assertEqual(chance, 40)

        # Exceptional STR has better chance
        success, chance = self.system.attempt_bend_bars(18, 100)  # 18/00
        self.assertEqual(chance, 70)

    def test_open_doors(self):
        """Test door forcing"""
        # Low STR
        success = self.system.attempt_open_doors(8)
        self.assertIsInstance(success, bool)

        # High STR
        success = self.system.attempt_open_doors(18)
        self.assertIsInstance(success, bool)

        # Locked door without exceptional STR should fail
        success = self.system.attempt_open_doors(16, locked=True, is_fighter=False)
        self.assertFalse(success)

        # Exceptional STR fighter can try locked doors
        # This is random but just verify it doesn't crash
        success = self.system.attempt_open_doors(18, 75, locked=True, is_fighter=True)
        self.assertIsInstance(success, bool)

    def test_bonus_spells(self):
        """Test cleric bonus spells from wisdom"""
        # Low WIS = no bonus
        bonus = self.system.get_bonus_spells(12, 1)
        self.assertEqual(bonus, 0)

        # WIS 13 = one 1st level bonus
        bonus = self.system.get_bonus_spells(13, 1)
        self.assertEqual(bonus, 1)

        # WIS 16 = two 1st level, one 2nd level
        bonus = self.system.get_bonus_spells(16, 1)
        self.assertEqual(bonus, 2)
        bonus = self.system.get_bonus_spells(16, 2)
        self.assertEqual(bonus, 1)

        # WIS 18 = bonus through 4th level
        bonus = self.system.get_bonus_spells(18, 4)
        self.assertEqual(bonus, 1)

    def test_spell_failure(self):
        """Test cleric spell failure from low wisdom"""
        # WIS 10+ = no failure
        failed, chance = self.system.check_spell_failure(10)
        self.assertEqual(chance, 0)
        self.assertFalse(failed)

        # WIS 9 = 5% failure
        failed, chance = self.system.check_spell_failure(9)
        self.assertEqual(chance, 5)

        # WIS 5 = 20% failure
        failed, chance = self.system.check_spell_failure(5)
        self.assertEqual(chance, 20)

    def test_max_spell_level(self):
        """Test max spell level from intelligence"""
        # INT 9 can only learn up to 4th level
        can_learn = self.system.can_learn_spell_level(9, 4)
        self.assertTrue(can_learn)
        can_learn = self.system.can_learn_spell_level(9, 5)
        self.assertFalse(can_learn)

        # INT 14 can learn up to 7th level
        can_learn = self.system.can_learn_spell_level(14, 7)
        self.assertTrue(can_learn)
        can_learn = self.system.can_learn_spell_level(14, 8)
        self.assertFalse(can_learn)

        # INT 18 can learn all levels
        can_learn = self.system.can_learn_spell_level(18, 9)
        self.assertTrue(can_learn)


class TestCharacterAbilityIntegration(unittest.TestCase):
    """Test Character class integration with ability modifiers"""

    def test_character_strength_bonus(self):
        """Test character gets correct STR bonuses"""
        char = Character(name="Test", race="Human", char_class="Fighter", strength=18, strength_percentile=100)

        # Should use ability system for bonuses
        self.assertEqual(char.get_to_hit_bonus(), 3)  # 18/00
        self.assertEqual(char.get_damage_bonus(), 6)  # 18/00

    def test_character_dexterity_bonus(self):
        """Test character gets correct DEX bonuses"""
        char = Character(name="Test", race="Human", char_class="Thief", dexterity=18)

        # DEX 18 = -4 AC bonus
        self.assertEqual(char.get_ac_bonus(), -4)

    def test_character_constitution_bonus(self):
        """Test character gets correct CON bonuses"""
        # Non-fighter
        char = Character(name="Test", race="Human", char_class="Cleric", constitution=17)
        self.assertEqual(char.get_hp_bonus_per_level(), 2)

        # Fighter gets better bonus
        fighter = Character(name="Test", race="Human", char_class="Fighter", constitution=17)
        self.assertEqual(fighter.get_hp_bonus_per_level(), 3)

        fighter18 = Character(name="Test", race="Human", char_class="Fighter", constitution=18)
        self.assertEqual(fighter18.get_hp_bonus_per_level(), 4)

    def test_character_ability_abbreviations(self):
        """Test character ability score abbreviation properties"""
        char = Character(
            name="Test",
            race="Human",
            char_class="Fighter",
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=12,
            wisdom=13,
            charisma=10
        )

        # Properties should return same as full attribute names
        self.assertEqual(char.str, 16)
        self.assertEqual(char.dex, 14)
        self.assertEqual(char.con, 15)
        self.assertEqual(char.int, 12)
        self.assertEqual(char.wis, 13)
        self.assertEqual(char.cha, 10)


if __name__ == '__main__':
    unittest.main()
