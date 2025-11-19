"""
Test suite for thief skills with racial, DEX, and armor modifiers (Task 2.1)
"""

import unittest
from aerthos.entities.player import PlayerCharacter, Armor
from aerthos.systems.skills import SkillResolver


class TestThiefSkillsBase(unittest.TestCase):
    """Test base thief skill values from PH tables"""

    def setUp(self):
        """Create a human thief with DEX 12 (no modifiers) for testing"""
        self.skill_resolver = SkillResolver()

        # Create level 1 thief
        self.thief_l1 = PlayerCharacter(
            name="TestThief",
            char_class="Thief",
            race="Human",
            level=1,
            strength=10,
            dexterity=12,  # No DEX modifier
            constitution=10,
            intelligence=10,
            wisdom=10,
            charisma=10
        )
        self.thief_l1.thief_skills = {
            'pick_pockets': 30,
            'open_locks': 25,
            'find_remove_traps': 20,
            'move_silently': 15,
            'hide_in_shadows': 10,
            'hear_noise': 10,
            'climb_walls': 85,
            'read_languages': 0
        }

    def test_level_1_base_values(self):
        """Test that level 1 thief skills match PH table exactly"""
        expected = {
            'pick_pockets': 30,
            'open_locks': 25,
            'find_remove_traps': 20,
            'move_silently': 15,
            'hide_in_shadows': 10,
            'hear_noise': 10,
            'climb_walls': 85,  # Should be 85, not 80!
            'read_languages': 0
        }

        for skill, expected_value in expected.items():
            actual = self.skill_resolver.calculate_thief_skill(self.thief_l1, skill)
            self.assertEqual(actual, expected_value,
                           f"Level 1 {skill} should be {expected_value}%, got {actual}%")

    def test_level_5_base_values(self):
        """Test level 5 thief skills match PH"""
        thief = PlayerCharacter(
            name="LevelFiveThief",
            char_class="Thief",
            race="Human",
            level=5,
            dexterity=12
        )
        thief.thief_skills = {'pick_pockets': 1}  # Dummy

        expected_l5 = {
            'pick_pockets': 50,
            'open_locks': 42,
            'find_remove_traps': 40,
            'move_silently': 40,
            'hide_in_shadows': 31,
            'hear_noise': 20,
            'climb_walls': 90,
            'read_languages': 25
        }

        for skill, expected_value in expected_l5.items():
            actual = self.skill_resolver.calculate_thief_skill(thief, skill)
            self.assertEqual(actual, expected_value,
                           f"Level 5 {skill} should be {expected_value}%, got {actual}%")

    def test_level_10_base_values(self):
        """Test level 10 Master Thief skills"""
        thief = PlayerCharacter(
            name="MasterThief",
            char_class="Thief",
            race="Human",
            level=10,
            dexterity=12
        )
        thief.thief_skills = {'pick_pockets': 1}

        expected_l10 = {
            'pick_pockets': 90,
            'open_locks': 70,
            'find_remove_traps': 65,
            'move_silently': 80,
            'hide_in_shadows': 60,
            'hear_noise': 30,
            'climb_walls': 99,
            'read_languages': 50
        }

        for skill, expected_value in expected_l10.items():
            actual = self.skill_resolver.calculate_thief_skill(thief, skill)
            self.assertEqual(actual, expected_value,
                           f"Level 10 {skill} should be {expected_value}%, got {actual}%")


class TestThiefSkillsRacial(unittest.TestCase):
    """Test racial adjustments to thief skills"""

    def setUp(self):
        self.skill_resolver = SkillResolver()

    def test_halfling_bonuses(self):
        """Test Halfling thief gets proper racial bonuses"""
        halfling_thief = PlayerCharacter(
            name="HalflingThief",
            char_class="Thief",
            race="Halfling",
            level=1,
            dexterity=12
        )
        halfling_thief.thief_skills = {'pick_pockets': 1}

        # Halfling: +5 PP, +5 OL, +5 FRT, +10 MS, +15 HiS, +5 HN, -15 CW
        self.assertEqual(self.skill_resolver.calculate_thief_skill(halfling_thief, 'pick_pockets'), 35)  # 30+5
        self.assertEqual(self.skill_resolver.calculate_thief_skill(halfling_thief, 'open_locks'), 30)  # 25+5
        self.assertEqual(self.skill_resolver.calculate_thief_skill(halfling_thief, 'find_remove_traps'), 25)  # 20+5
        self.assertEqual(self.skill_resolver.calculate_thief_skill(halfling_thief, 'move_silently'), 25)  # 15+10
        self.assertEqual(self.skill_resolver.calculate_thief_skill(halfling_thief, 'hide_in_shadows'), 25)  # 10+15
        self.assertEqual(self.skill_resolver.calculate_thief_skill(halfling_thief, 'hear_noise'), 15)  # 10+5
        self.assertEqual(self.skill_resolver.calculate_thief_skill(halfling_thief, 'climb_walls'), 70)  # 85-15

    def test_elf_bonuses(self):
        """Test Elf thief gets proper racial bonuses"""
        elf_thief = PlayerCharacter(
            name="ElfThief",
            char_class="Thief",
            race="Elf",
            level=1,
            dexterity=12
        )
        elf_thief.thief_skills = {'pick_pockets': 1}

        # Elf: +5 PP, +5 HN, +10 HiS, +5 MS, -5 CW
        self.assertEqual(self.skill_resolver.calculate_thief_skill(elf_thief, 'pick_pockets'), 35)  # 30+5
        self.assertEqual(self.skill_resolver.calculate_thief_skill(elf_thief, 'hear_noise'), 15)  # 10+5
        self.assertEqual(self.skill_resolver.calculate_thief_skill(elf_thief, 'hide_in_shadows'), 20)  # 10+10
        self.assertEqual(self.skill_resolver.calculate_thief_skill(elf_thief, 'move_silently'), 20)  # 15+5
        self.assertEqual(self.skill_resolver.calculate_thief_skill(elf_thief, 'climb_walls'), 80)  # 85-5

    def test_dwarf_bonuses(self):
        """Test Dwarf thief gets proper racial bonuses"""
        dwarf_thief = PlayerCharacter(
            name="DwarfThief",
            char_class="Thief",
            race="Dwarf",
            level=1,
            dexterity=12
        )
        dwarf_thief.thief_skills = {'pick_pockets': 1}

        # Dwarf: +10 FRT, +5 OL, -10 CW, -5 RL
        self.assertEqual(self.skill_resolver.calculate_thief_skill(dwarf_thief, 'find_remove_traps'), 30)  # 20+10
        self.assertEqual(self.skill_resolver.calculate_thief_skill(dwarf_thief, 'open_locks'), 30)  # 25+5
        self.assertEqual(self.skill_resolver.calculate_thief_skill(dwarf_thief, 'climb_walls'), 75)  # 85-10
        self.assertEqual(self.skill_resolver.calculate_thief_skill(dwarf_thief, 'read_languages'), 0)  # 0-5 = -5, but base 0 stays 0


class TestThiefSkillsDexterity(unittest.TestCase):
    """Test DEX adjustments to thief skills"""

    def setUp(self):
        self.skill_resolver = SkillResolver()

    def test_low_dex_penalties(self):
        """Test low DEX (3) gives proper penalties"""
        clumsy_thief = PlayerCharacter(
            name="ClumsyThief",
            char_class="Thief",
            race="Human",
            level=1,
            dexterity=3  # Very clumsy!
        )
        clumsy_thief.thief_skills = {'pick_pockets': 1}

        # DEX 3: -15% PP, -10% OL, -10% FRT, -20% MS, -10% HiS, -10% HN, -10% CW, -10% RL
        self.assertEqual(self.skill_resolver.calculate_thief_skill(clumsy_thief, 'pick_pockets'), 15)  # 30-15
        self.assertEqual(self.skill_resolver.calculate_thief_skill(clumsy_thief, 'open_locks'), 15)  # 25-10
        self.assertEqual(self.skill_resolver.calculate_thief_skill(clumsy_thief, 'move_silently'), 1)  # 15-20 = -5, but min 1%
        self.assertEqual(self.skill_resolver.calculate_thief_skill(clumsy_thief, 'climb_walls'), 75)  # 85-10

    def test_high_dex_bonuses(self):
        """Test high DEX (18) gives proper bonuses"""
        nimble_thief = PlayerCharacter(
            name="NimbleThief",
            char_class="Thief",
            race="Human",
            level=1,
            dexterity=18  # Very nimble!
        )
        nimble_thief.thief_skills = {'pick_pockets': 1}

        # DEX 18: +10% PP, +15% OL, +5% FRT, +10% MS, +10% HiS, +10% HN, +10% CW, +10% RL
        self.assertEqual(self.skill_resolver.calculate_thief_skill(nimble_thief, 'pick_pockets'), 40)  # 30+10
        self.assertEqual(self.skill_resolver.calculate_thief_skill(nimble_thief, 'open_locks'), 40)  # 25+15
        self.assertEqual(self.skill_resolver.calculate_thief_skill(nimble_thief, 'find_remove_traps'), 25)  # 20+5
        self.assertEqual(self.skill_resolver.calculate_thief_skill(nimble_thief, 'move_silently'), 25)  # 15+10
        self.assertEqual(self.skill_resolver.calculate_thief_skill(nimble_thief, 'hide_in_shadows'), 20)  # 10+10
        self.assertEqual(self.skill_resolver.calculate_thief_skill(nimble_thief, 'climb_walls'), 95)  # 85+10

    def test_dex_17_bonuses(self):
        """Test DEX 17 gives proper bonuses"""
        agile_thief = PlayerCharacter(
            name="AgileThief",
            char_class="Thief",
            race="Human",
            level=1,
            dexterity=17
        )
        agile_thief.thief_skills = {'pick_pockets': 1}

        # DEX 17: +5% PP, +10% OL, +5% MS, +5% HiS, +5% HN, +5% CW, +5% RL
        self.assertEqual(self.skill_resolver.calculate_thief_skill(agile_thief, 'pick_pockets'), 35)  # 30+5
        self.assertEqual(self.skill_resolver.calculate_thief_skill(agile_thief, 'open_locks'), 35)  # 25+10


class TestThiefSkillsArmor(unittest.TestCase):
    """Test armor penalties to thief skills"""

    def setUp(self):
        self.skill_resolver = SkillResolver()

    def test_leather_armor_no_penalty(self):
        """Test that leather armor has no penalty"""
        thief = PlayerCharacter(
            name="LeatherThief",
            char_class="Thief",
            race="Human",
            level=1,
            dexterity=12
        )
        thief.thief_skills = {'pick_pockets': 1}
        thief.equipment.armor = Armor(name="Leather Armor", weight=15, ac=8)

        # Leather armor: no penalty
        self.assertEqual(self.skill_resolver.calculate_thief_skill(thief, 'pick_pockets'), 30)
        self.assertEqual(self.skill_resolver.calculate_thief_skill(thief, 'climb_walls'), 85)

    def test_studded_leather_penalty(self):
        """Test that studded leather gives -10% penalty"""
        thief = PlayerCharacter(
            name="StuddedThief",
            char_class="Thief",
            race="Human",
            level=1,
            dexterity=12
        )
        thief.thief_skills = {'pick_pockets': 1}
        thief.equipment.armor = Armor(name="Studded Leather", weight=20, ac=7)

        # Studded leather: -10% to all skills
        self.assertEqual(self.skill_resolver.calculate_thief_skill(thief, 'pick_pockets'), 20)  # 30-10
        self.assertEqual(self.skill_resolver.calculate_thief_skill(thief, 'open_locks'), 15)  # 25-10
        self.assertEqual(self.skill_resolver.calculate_thief_skill(thief, 'climb_walls'), 75)  # 85-10

    def test_chain_mail_forbidden(self):
        """Test that chain mail prevents thief skills (returns 0%)"""
        thief = PlayerCharacter(
            name="HeavyThief",
            char_class="Thief",
            race="Human",
            level=1,
            dexterity=12
        )
        thief.thief_skills = {'pick_pockets': 1}
        thief.equipment.armor = Armor(name="Chain Mail", weight=30, ac=5)

        # Chain mail: cannot use thief skills
        self.assertEqual(self.skill_resolver.calculate_thief_skill(thief, 'pick_pockets'), 0)
        self.assertEqual(self.skill_resolver.calculate_thief_skill(thief, 'climb_walls'), 0)


class TestThiefSkillsCombined(unittest.TestCase):
    """Test combined modifiers (racial + DEX + armor)"""

    def setUp(self):
        self.skill_resolver = SkillResolver()

    def test_halfling_dex18_leather(self):
        """Test Halfling with DEX 18 in leather armor"""
        super_thief = PlayerCharacter(
            name="SuperThief",
            char_class="Thief",
            race="Halfling",
            level=1,
            dexterity=18
        )
        super_thief.thief_skills = {'pick_pockets': 1}
        super_thief.equipment.armor = Armor(name="Leather Armor", weight=15, ac=8)

        # Pick Pockets: 30 (base) + 5 (Halfling) + 10 (DEX 18) = 45%
        self.assertEqual(self.skill_resolver.calculate_thief_skill(super_thief, 'pick_pockets'), 45)

        # Hide in Shadows: 10 (base) + 15 (Halfling) + 10 (DEX 18) = 35%
        self.assertEqual(self.skill_resolver.calculate_thief_skill(super_thief, 'hide_in_shadows'), 35)

    def test_elf_dex3_studded(self):
        """Test Elf with low DEX 3 in studded leather (worst case)"""
        weak_thief = PlayerCharacter(
            name="WeakThief",
            char_class="Thief",
            race="Elf",
            level=1,
            dexterity=3
        )
        weak_thief.thief_skills = {'pick_pockets': 1}
        weak_thief.equipment.armor = Armor(name="Studded Leather", weight=20, ac=7)

        # Pick Pockets: 30 (base) + 5 (Elf) - 15 (DEX 3) - 10 (studded) = 10%
        self.assertEqual(self.skill_resolver.calculate_thief_skill(weak_thief, 'pick_pockets'), 10)

        # Move Silently: 15 (base) + 5 (Elf) - 20 (DEX 3) - 10 (studded) = -10 -> minimum 1%
        self.assertEqual(self.skill_resolver.calculate_thief_skill(weak_thief, 'move_silently'), 1)

    def test_skill_caps(self):
        """Test that skills are capped at 1% minimum and 99% maximum"""
        # Test minimum cap for skills with positive base
        bad_thief = PlayerCharacter(
            name="BadThief",
            char_class="Thief",
            race="Human",
            level=1,
            dexterity=3
        )
        bad_thief.thief_skills = {'hide_in_shadows': 1}
        bad_thief.equipment.armor = Armor(name="Studded Leather", weight=20, ac=7)

        # Hide in Shadows: 10 (base) - 10 (DEX 3) - 10 (studded) = -10 -> minimum 1%
        self.assertEqual(self.skill_resolver.calculate_thief_skill(bad_thief, 'hide_in_shadows'), 1)

        # Test maximum cap (level 20 master thief)
        master_thief = PlayerCharacter(
            name="LegendaryThief",
            char_class="Thief",
            race="Human",
            level=20,
            dexterity=18
        )
        master_thief.thief_skills = {'pick_pockets': 1}

        # Most skills at level 20 are 99%, should cap at 99% even with bonuses
        skill_value = self.skill_resolver.calculate_thief_skill(master_thief, 'pick_pockets')
        self.assertLessEqual(skill_value, 99, "Skills should not exceed 99%")


if __name__ == '__main__':
    unittest.main()
