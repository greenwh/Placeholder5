"""
Tests for the Saving Throw system
"""

import unittest
from unittest.mock import patch
from aerthos.entities.character import Character
from aerthos.entities.player import PlayerCharacter, Equipment, Armor, Shield
from aerthos.systems.saving_throws import SavingThrowResolver


class TestBasicSavingThrows(unittest.TestCase):
    """Test basic saving throw mechanics"""

    def setUp(self):
        """Create test character"""
        self.save_system = SavingThrowResolver()

        self.character = Character(
            name="Test Fighter",
            race="Human",
            char_class="Fighter",
            level=1,
            strength=15,
            dexterity=14,
            constitution=16,
            intelligence=10,
            wisdom=12,
            charisma=10,
            hp_max=10,
            hp_current=10,
            ac=5,
            thac0=20
        )

        # Set base saving throws for level 1 Fighter
        self.character.save_poison = 14
        self.character.save_rod_staff_wand = 16
        self.character.save_petrify_paralyze = 15
        self.character.save_breath = 17
        self.character.save_spell = 17

    def test_get_saves_for_level(self):
        """Test retrieving saves for a specific class and level"""
        saves = self.save_system.get_saves_for_level("Fighter", 1)

        self.assertEqual(saves['save_poison'], 14)
        self.assertEqual(saves['save_rod_staff_wand'], 16)
        self.assertEqual(saves['save_petrify_paralyze'], 15)
        self.assertEqual(saves['save_breath'], 17)
        self.assertEqual(saves['save_spell'], 17)

    def test_natural_1_always_succeeds(self):
        """Natural 1 should always succeed"""
        with patch('random.randint', return_value=1):
            result = self.save_system.make_save(self.character, 'poison')

            self.assertTrue(result['success'])
            self.assertEqual(result['roll'], 1)
            self.assertTrue(result['natural_20_or_1'])

    def test_natural_20_always_fails(self):
        """Natural 20 should always fail"""
        with patch('random.randint', return_value=20):
            result = self.save_system.make_save(self.character, 'poison')

            self.assertFalse(result['success'])
            self.assertEqual(result['roll'], 20)
            self.assertTrue(result['natural_20_or_1'])

    def test_successful_save(self):
        """Test a successful save"""
        # Roll 10, target 14 -> success (10 <= 14)
        with patch('random.randint', return_value=10):
            result = self.save_system.make_save(self.character, 'poison')

            self.assertTrue(result['success'])
            self.assertEqual(result['roll'], 10)
            self.assertFalse(result['natural_20_or_1'])

    def test_failed_save(self):
        """Test a failed save"""
        # Roll 18, target 14 -> failure (18 > 14)
        with patch('random.randint', return_value=18):
            result = self.save_system.make_save(self.character, 'poison')

            self.assertFalse(result['success'])
            self.assertEqual(result['roll'], 18)
            self.assertFalse(result['natural_20_or_1'])

    def test_category_aliases(self):
        """Test that category aliases work correctly"""
        # 'death' should map to 'save_poison'
        result1 = self.save_system.make_save(self.character, 'death')
        result2 = self.save_system.make_save(self.character, 'poison')

        self.assertEqual(result1['base_target'], result2['base_target'])

        # 'magic' should map to 'save_spell'
        result3 = self.save_system.make_save(self.character, 'magic')
        result4 = self.save_system.make_save(self.character, 'spell')

        self.assertEqual(result3['base_target'], result4['base_target'])


class TestRacialSavingThrowBonuses(unittest.TestCase):
    """Test racial bonuses to saving throws"""

    def setUp(self):
        """Create test characters of different races"""
        self.save_system = SavingThrowResolver()

    def test_dwarf_saving_throw_bonus(self):
        """Dwarves get +1 per 3.5 CON to saves"""
        # CON 14 = 4.0 -> bonus of 4
        dwarf = Character(
            name="Thorin",
            race="Dwarf",
            char_class="Fighter",
            level=1,
            strength=15, dexterity=12, constitution=14,
            intelligence=10, wisdom=12, charisma=10,
            hp_max=10, hp_current=10, ac=5, thac0=20
        )
        dwarf.save_poison = 14

        bonus = self.save_system.get_racial_save_bonus(dwarf)
        self.assertEqual(bonus, 4)  # 14 / 3.5 = 4.0

    def test_gnome_saving_throw_bonus(self):
        """Gnomes get +1 per 3.5 CON to saves"""
        # CON 18 = 5.14 -> bonus of 5 (max)
        gnome = Character(
            name="Gimble",
            race="Gnome",
            char_class="Fighter",
            level=1,
            strength=15, dexterity=12, constitution=18,
            intelligence=10, wisdom=12, charisma=10,
            hp_max=10, hp_current=10, ac=5, thac0=20
        )

        bonus = self.save_system.get_racial_save_bonus(gnome)
        self.assertEqual(bonus, 5)  # 18 / 3.5 = 5.14, capped at 5

    def test_halfling_saving_throw_bonus(self):
        """Halflings get +1 per 3.5 CON to saves"""
        # CON 16 = 4.57 -> bonus of 4
        halfling = Character(
            name="Bilbo",
            race="Halfling",
            char_class="Thief",
            level=1,
            strength=10, dexterity=16, constitution=16,
            intelligence=10, wisdom=12, charisma=10,
            hp_max=6, hp_current=6, ac=7, thac0=20
        )

        bonus = self.save_system.get_racial_save_bonus(halfling)
        self.assertEqual(bonus, 4)  # 16 / 3.5 = 4.57

    def test_human_no_racial_bonus(self):
        """Humans don't get racial saving throw bonuses"""
        human = Character(
            name="Aragorn",
            race="Human",
            char_class="Ranger",
            level=1,
            strength=16, dexterity=14, constitution=16,
            intelligence=12, wisdom=14, charisma=14,
            hp_max=10, hp_current=10, ac=5, thac0=20
        )

        bonus = self.save_system.get_racial_save_bonus(human)
        self.assertEqual(bonus, 0)

    def test_racial_bonus_applied_to_save(self):
        """Test that racial bonus is applied in actual save"""
        # Dwarf with CON 18 gets +5 bonus
        dwarf = Character(
            name="Thorin",
            race="Dwarf",
            char_class="Fighter",
            level=1,
            strength=15, dexterity=12, constitution=18,
            intelligence=10, wisdom=12, charisma=10,
            hp_max=10, hp_current=10, ac=5, thac0=20
        )
        dwarf.save_poison = 14

        result = self.save_system.make_save(dwarf, 'poison')

        # Base target 14, +5 racial = adjusted target 9
        self.assertEqual(result['base_target'], 14)
        self.assertEqual(result['adjusted_target'], 9)
        self.assertEqual(result['modifiers_applied'], 5)


class TestWisdomSavingThrowBonuses(unittest.TestCase):
    """Test WIS bonuses to mental saves"""

    def setUp(self):
        """Create test characters"""
        self.save_system = SavingThrowResolver()

    def test_wisdom_bonus_to_spell_save(self):
        """High WIS gives bonus to spell saves (mental)"""
        # WIS 18 gives +3 magic attack adjustment
        cleric = Character(
            name="Holy Warrior",
            race="Human",
            char_class="Cleric",
            level=1,
            strength=12, dexterity=10, constitution=14,
            intelligence=10, wisdom=18, charisma=14,
            hp_max=8, hp_current=8, ac=5, thac0=20
        )
        cleric.save_spell = 14

        bonus = self.save_system.get_wisdom_save_bonus(cleric, 'save_spell')
        self.assertEqual(bonus, 3)

    def test_wisdom_bonus_to_rod_staff_wand(self):
        """WIS bonus applies to rod/staff/wand saves (mental)"""
        # WIS 17 gives +2 magic attack adjustment
        druid = Character(
            name="Nature Priest",
            race="Human",
            char_class="Druid",
            level=1,
            strength=12, dexterity=12, constitution=14,
            intelligence=10, wisdom=17, charisma=12,
            hp_max=8, hp_current=8, ac=6, thac0=20
        )
        druid.save_rod_staff_wand = 14

        bonus = self.save_system.get_wisdom_save_bonus(druid, 'save_rod_staff_wand')
        self.assertEqual(bonus, 2)

    def test_wisdom_bonus_to_petrify_paralyze(self):
        """WIS bonus applies to petrify/paralyze saves (mental)"""
        # WIS 16 gives +1 magic attack adjustment
        char = Character(
            name="Wise Fighter",
            race="Human",
            char_class="Fighter",
            level=1,
            strength=16, dexterity=14, constitution=14,
            intelligence=10, wisdom=16, charisma=10,
            hp_max=10, hp_current=10, ac=5, thac0=20
        )
        char.save_petrify_paralyze = 15

        bonus = self.save_system.get_wisdom_save_bonus(char, 'save_petrify_paralyze')
        self.assertEqual(bonus, 1)

    def test_wisdom_no_bonus_to_poison(self):
        """WIS bonus does NOT apply to poison saves (not mental)"""
        # WIS 18 gives +3, but not to poison
        cleric = Character(
            name="Holy Warrior",
            race="Human",
            char_class="Cleric",
            level=1,
            strength=12, dexterity=10, constitution=14,
            intelligence=10, wisdom=18, charisma=14,
            hp_max=8, hp_current=8, ac=5, thac0=20
        )

        bonus = self.save_system.get_wisdom_save_bonus(cleric, 'save_poison')
        self.assertEqual(bonus, 0)  # No WIS bonus to poison

    def test_wisdom_no_bonus_to_breath(self):
        """WIS bonus does NOT apply to breath weapon saves (not mental)"""
        # WIS 18 gives +3, but not to breath
        cleric = Character(
            name="Holy Warrior",
            race="Human",
            char_class="Cleric",
            level=1,
            strength=12, dexterity=10, constitution=14,
            intelligence=10, wisdom=18, charisma=14,
            hp_max=8, hp_current=8, ac=5, thac0=20
        )

        bonus = self.save_system.get_wisdom_save_bonus(cleric, 'save_breath')
        self.assertEqual(bonus, 0)  # No WIS bonus to breath


class TestMagicItemBonuses(unittest.TestCase):
    """Test magic item bonuses to saving throws"""

    def setUp(self):
        """Create test character with equipment"""
        self.save_system = SavingThrowResolver()

    def test_magic_armor_bonus(self):
        """Magic armor gives bonus to saves"""
        # Create character with +2 plate mail
        char = PlayerCharacter(
            name="Paladin",
            race="Human",
            char_class="Paladin",
            level=1,
            strength=16, dexterity=12, constitution=16,
            intelligence=10, wisdom=14, charisma=16,
            hp_max=10, hp_current=10, ac=1, thac0=20
        )
        char.save_spell = 14

        # Add magic armor
        armor = Armor(
            name="Plate Mail +2",
            weight=400,
            ac=1,
            armor_type="very_heavy",
            magic_bonus=2
        )
        char.equipment = Equipment()
        char.equipment.armor = armor

        bonus = self.save_system.get_magic_item_bonus(char)
        self.assertEqual(bonus, 2)

    def test_magic_shield_bonus(self):
        """Magic shield gives bonus to saves"""
        char = PlayerCharacter(
            name="Fighter",
            race="Human",
            char_class="Fighter",
            level=1,
            strength=16, dexterity=12, constitution=14,
            intelligence=10, wisdom=12, charisma=10,
            hp_max=10, hp_current=10, ac=3, thac0=20
        )
        char.save_spell = 14

        # Add magic shield
        shield = Shield(
            name="Large Shield +1",
            weight=150,
            ac_bonus=1,
            max_attacks_blocked=3,
            magic_bonus=1
        )
        char.equipment = Equipment()
        char.equipment.shield = shield

        bonus = self.save_system.get_magic_item_bonus(char)
        self.assertEqual(bonus, 1)

    def test_magic_armor_and_shield_stack(self):
        """Magic armor and shield bonuses stack"""
        char = PlayerCharacter(
            name="Paladin",
            race="Human",
            char_class="Paladin",
            level=1,
            strength=16, dexterity=12, constitution=16,
            intelligence=10, wisdom=14, charisma=16,
            hp_max=10, hp_current=10, ac=0, thac0=20
        )

        armor = Armor(
            name="Plate Mail +1",
            weight=400,
            ac=2,
            armor_type="very_heavy",
            magic_bonus=1
        )
        shield = Shield(
            name="Large Shield +2",
            weight=150,
            ac_bonus=1,
            max_attacks_blocked=3,
            magic_bonus=2
        )
        char.equipment = Equipment()
        char.equipment.armor = armor
        char.equipment.shield = shield

        bonus = self.save_system.get_magic_item_bonus(char)
        self.assertEqual(bonus, 3)  # +1 armor + +2 shield

    def test_no_magic_items(self):
        """Character with no magic items gets 0 bonus"""
        char = Character(
            name="Fighter",
            race="Human",
            char_class="Fighter",
            level=1,
            strength=16, dexterity=14, constitution=14,
            intelligence=10, wisdom=12, charisma=10,
            hp_max=10, hp_current=10, ac=5, thac0=20
        )

        bonus = self.save_system.get_magic_item_bonus(char)
        self.assertEqual(bonus, 0)


class TestSituationalModifiers(unittest.TestCase):
    """Test situational modifiers to saving throws"""

    def setUp(self):
        """Create test character"""
        self.save_system = SavingThrowResolver()

        self.character = Character(
            name="Test Fighter",
            race="Human",
            char_class="Fighter",
            level=1,
            strength=15, dexterity=14, constitution=16,
            intelligence=10, wisdom=12, charisma=10,
            hp_max=10, hp_current=10, ac=5, thac0=20
        )
        self.character.save_breath = 17

    def test_cover_bonus(self):
        """Cover gives +2 to saves vs area effects"""
        result = self.save_system.make_save(
            self.character, 'breath', situational={'cover': True}
        )

        # Base target 17, +2 cover = adjusted target 15
        self.assertEqual(result['base_target'], 17)
        self.assertEqual(result['adjusted_target'], 15)
        self.assertEqual(result['modifiers_applied'], 2)

    def test_surprised_penalty(self):
        """Surprised gives -2 to saves"""
        result = self.save_system.make_save(
            self.character, 'spell', situational={'surprised': True}
        )

        # Base target depends on spell save, -2 surprised
        self.assertEqual(result['modifiers_applied'], -2)

    def test_blind_penalty(self):
        """Blind gives -4 to saves"""
        result = self.save_system.make_save(
            self.character, 'spell', situational={'blind': True}
        )

        # -4 blind penalty
        self.assertEqual(result['modifiers_applied'], -4)

    def test_multiple_situational_modifiers(self):
        """Multiple situational modifiers can apply"""
        result = self.save_system.make_save(
            self.character, 'breath',
            situational={'cover': True, 'surprised': True}
        )

        # +2 cover, -2 surprised = 0 net
        self.assertEqual(result['modifiers_applied'], 0)


class TestCombinedModifiers(unittest.TestCase):
    """Test all modifiers working together"""

    def setUp(self):
        """Create test character"""
        self.save_system = SavingThrowResolver()

    def test_all_modifiers_stacking(self):
        """Test racial + WIS + magic items + situational"""
        # Dwarf cleric with high CON and WIS, magic armor
        dwarf = PlayerCharacter(
            name="Thorin Cleric",
            race="Dwarf",
            char_class="Cleric",
            level=1,
            strength=14, dexterity=10, constitution=18,  # CON 18 = +5 racial
            intelligence=10, wisdom=18,  # WIS 18 = +3 to mental saves
            charisma=12,
            hp_max=10, hp_current=10, ac=2, thac0=20
        )
        dwarf.save_spell = 14

        # Add +2 magic armor
        armor = Armor(
            name="Chain Mail +2",
            weight=750,
            ac=3,
            armor_type="heavy",
            magic_bonus=2
        )
        dwarf.equipment = Equipment()
        dwarf.equipment.armor = armor

        result = self.save_system.make_save(
            dwarf, 'spell',
            modifier=1,  # +1 base modifier
            situational={'cover': True}  # +2 situational
        )

        # Expected modifiers:
        # +5 racial (Dwarf CON 18)
        # +3 WIS (18 WIS on mental save)
        # +2 magic armor
        # +1 base modifier
        # +2 cover
        # Total: +13
        self.assertEqual(result['modifiers_applied'], 13)
        self.assertEqual(result['base_target'], 14)
        self.assertEqual(result['adjusted_target'], 1)  # 14 - 13 = 1

    def test_modifiers_with_penalties(self):
        """Test modifiers with both bonuses and penalties"""
        human = Character(
            name="Fighter",
            race="Human",
            char_class="Fighter",
            level=1,
            strength=16, dexterity=14, constitution=12,
            intelligence=10, wisdom=10, charisma=10,
            hp_max=10, hp_current=10, ac=5, thac0=20
        )
        human.save_poison = 14

        result = self.save_system.make_save(
            human, 'poison',
            modifier=-2,  # -2 poison penalty
            situational={'surprised': True}  # -2 surprised
        )

        # Expected modifiers:
        # 0 racial (Human)
        # 0 WIS (10 WIS, and poison is not mental anyway)
        # 0 magic items
        # -2 base modifier
        # -2 surprised
        # Total: -4
        self.assertEqual(result['modifiers_applied'], -4)
        self.assertEqual(result['base_target'], 14)
        self.assertEqual(result['adjusted_target'], 18)  # 14 - (-4) = 18


class TestSaveOrDie(unittest.TestCase):
    """Test save-or-die mechanics"""

    def setUp(self):
        """Create test character"""
        self.save_system = SavingThrowResolver()

        self.character = Character(
            name="Victim",
            race="Human",
            char_class="Magic-User",
            level=1,
            strength=10, dexterity=12, constitution=10,
            intelligence=16, wisdom=12, charisma=10,
            hp_max=4, hp_current=4, ac=10, thac0=20
        )
        self.character.save_poison = 14

    def test_save_or_die_success(self):
        """Successful save means survival"""
        with patch('random.randint', return_value=10):
            result = self.save_system.save_or_die(self.character, 'poison')

            self.assertTrue(result['success'])
            self.assertFalse(result['died'])
            self.assertTrue(self.character.is_alive)

    def test_save_or_die_failure(self):
        """Failed save means death"""
        with patch('random.randint', return_value=19):
            result = self.save_system.save_or_die(self.character, 'poison')

            self.assertFalse(result['success'])
            self.assertTrue(result['died'])
            self.assertFalse(self.character.is_alive)
            self.assertEqual(self.character.hp_current, 0)


class TestSaveForHalfDamage(unittest.TestCase):
    """Test save-for-half-damage mechanics"""

    def setUp(self):
        """Create test character"""
        self.save_system = SavingThrowResolver()

        self.character = Character(
            name="Adventurer",
            race="Human",
            char_class="Fighter",
            level=1,
            strength=16, dexterity=14, constitution=14,
            intelligence=10, wisdom=12, charisma=10,
            hp_max=12, hp_current=12, ac=5, thac0=20
        )
        self.character.save_spell = 17

    def test_save_for_half_success(self):
        """Successful save reduces damage by half"""
        with patch('random.randint', return_value=10):
            result = self.save_system.save_for_half_damage(
                self.character, damage=20, save_type='spell'
            )

            self.assertTrue(result['success'])
            self.assertEqual(result['final_damage'], 10)  # 20 / 2
            self.assertEqual(self.character.hp_current, 2)  # 12 - 10

    def test_save_for_half_failure(self):
        """Failed save means full damage"""
        with patch('random.randint', return_value=19):
            result = self.save_system.save_for_half_damage(
                self.character, damage=20, save_type='spell'
            )

            self.assertFalse(result['success'])
            self.assertEqual(result['final_damage'], 20)  # Full damage
            self.assertEqual(self.character.hp_current, 0)  # 12 - 20 = 0 (dead)


if __name__ == '__main__':
    unittest.main()
