"""
Tests for Armor System

Tests armor database, class restrictions, AC calculations, and equipment management.
"""

import unittest
from aerthos.systems.armor_system import ArmorSystem
from aerthos.entities.player import Armor, Shield, Equipment


class TestArmorSystem(unittest.TestCase):
    """Test armor system functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.system = ArmorSystem()

    def test_armor_database_loaded(self):
        """Test armor database loads correctly"""
        self.assertIsNotNone(self.system.armor_data)
        self.assertIsNotNone(self.system.shield_data)
        self.assertIsNotNone(self.system.class_restrictions)

        # Check specific armor exists
        self.assertIn('leather', self.system.armor_data)
        self.assertIn('plate_mail', self.system.armor_data)
        self.assertIn('chain_mail', self.system.armor_data)

    def test_create_armor(self):
        """Test creating armor objects"""
        # Leather armor
        leather = self.system.create_armor('leather')
        self.assertIsNotNone(leather)
        self.assertEqual(leather.name, 'Leather Armor')
        self.assertEqual(leather.ac, 8)
        self.assertEqual(leather.armor_type, 'light')
        self.assertEqual(leather.movement_rate, 12)
        self.assertEqual(leather.magic_bonus, 0)

        # Plate mail
        plate = self.system.create_armor('plate_mail')
        self.assertIsNotNone(plate)
        self.assertEqual(plate.ac, 3)
        self.assertEqual(plate.armor_type, 'very_heavy')
        self.assertEqual(plate.movement_rate, 6)

        # Magic plate mail
        plate_plus_2 = self.system.create_armor('plate_mail', magic_bonus=2)
        self.assertEqual(plate_plus_2.name, 'Plate Mail +2')
        self.assertEqual(plate_plus_2.magic_bonus, 2)
        self.assertEqual(plate_plus_2.get_effective_ac(), 1)  # AC 3 - 2 = 1

    def test_create_shield(self):
        """Test creating shield objects"""
        # Small shield
        small = self.system.create_shield('shield_small')
        self.assertIsNotNone(small)
        self.assertEqual(small.ac_bonus, 1)
        self.assertEqual(small.max_attacks_blocked, 1)

        # Large shield
        large = self.system.create_shield('shield_large')
        self.assertEqual(large.max_attacks_blocked, 3)

        # Magic shield
        shield_plus_1 = self.system.create_shield('shield_small', magic_bonus=1)
        self.assertEqual(shield_plus_1.magic_bonus, 1)
        self.assertEqual(shield_plus_1.get_effective_bonus(), 2)  # 1 + 1 = 2

    def test_class_armor_restrictions_fighter(self):
        """Test Fighter can wear any armor"""
        self.assertTrue(self.system.can_wear_armor('Fighter', 'leather'))
        self.assertTrue(self.system.can_wear_armor('Fighter', 'chain_mail'))
        self.assertTrue(self.system.can_wear_armor('Fighter', 'plate_mail'))
        self.assertTrue(self.system.can_use_shield('Fighter', 'shield_small'))
        self.assertTrue(self.system.can_use_shield('Fighter', 'shield_large'))

    def test_class_armor_restrictions_magic_user(self):
        """Test Magic-User cannot wear armor or use shields"""
        self.assertFalse(self.system.can_wear_armor('Magic-User', 'leather'))
        self.assertFalse(self.system.can_wear_armor('Magic-User', 'plate_mail'))
        self.assertFalse(self.system.can_use_shield('Magic-User', 'shield_small'))

    def test_class_armor_restrictions_thief(self):
        """Test Thief can only wear leather, no shields"""
        self.assertTrue(self.system.can_wear_armor('Thief', 'leather'))
        self.assertTrue(self.system.can_wear_armor('Thief', 'padded'))
        self.assertFalse(self.system.can_wear_armor('Thief', 'chain_mail'))
        self.assertFalse(self.system.can_wear_armor('Thief', 'plate_mail'))
        self.assertFalse(self.system.can_use_shield('Thief', 'shield_small'))

    def test_class_armor_restrictions_druid(self):
        """Test Druid can only wear leather and use wooden shields"""
        self.assertTrue(self.system.can_wear_armor('Druid', 'leather'))
        self.assertFalse(self.system.can_wear_armor('Druid', 'chain_mail'))
        self.assertFalse(self.system.can_wear_armor('Druid', 'plate_mail'))

        # Druids can use wooden shields and light shields
        self.assertTrue(self.system.can_use_shield('Druid', 'shield_small_wood'))
        self.assertTrue(self.system.can_use_shield('Druid', 'shield_small'))
        # But not large shields (too heavy/metallic)
        self.assertFalse(self.system.can_use_shield('Druid', 'shield_large'))

    def test_class_armor_restrictions_cleric(self):
        """Test Cleric can wear any armor and use any shield"""
        self.assertTrue(self.system.can_wear_armor('Cleric', 'leather'))
        self.assertTrue(self.system.can_wear_armor('Cleric', 'chain_mail'))
        self.assertTrue(self.system.can_wear_armor('Cleric', 'plate_mail'))
        self.assertTrue(self.system.can_use_shield('Cleric', 'shield_small'))
        self.assertTrue(self.system.can_use_shield('Cleric', 'shield_large'))

    def test_ac_calculation_unarmored(self):
        """Test AC calculation for unarmored character"""
        ac = self.system.calculate_ac(armor=None, shield=None, dex_modifier=0)
        self.assertEqual(ac, 10)  # Base AC

    def test_ac_calculation_leather_only(self):
        """Test AC with leather armor, no shield"""
        leather = self.system.create_armor('leather')
        ac = self.system.calculate_ac(armor=leather, shield=None, dex_modifier=0)
        self.assertEqual(ac, 8)

    def test_ac_calculation_leather_and_shield(self):
        """Test AC with leather armor and shield"""
        leather = self.system.create_armor('leather')
        shield = self.system.create_shield('shield_small')
        ac = self.system.calculate_ac(armor=leather, shield=shield, dex_modifier=0)
        self.assertEqual(ac, 7)  # Leather (8) + Shield (1) = 7

    def test_ac_calculation_plate_and_shield(self):
        """Test AC with plate mail and shield"""
        plate = self.system.create_armor('plate_mail')
        shield = self.system.create_shield('shield_small')
        ac = self.system.calculate_ac(armor=plate, shield=shield, dex_modifier=0)
        self.assertEqual(ac, 2)  # Plate (3) + Shield (1) = 2

    def test_ac_calculation_with_dex(self):
        """Test AC calculation with DEX modifier"""
        leather = self.system.create_armor('leather')

        # High DEX (18) = -4 AC bonus
        ac_high_dex = self.system.calculate_ac(armor=leather, shield=None, dex_modifier=-4)
        self.assertEqual(ac_high_dex, 4)  # 8 + (-4) = 4

        # Low DEX (6) = +3 AC penalty
        ac_low_dex = self.system.calculate_ac(armor=leather, shield=None, dex_modifier=3)
        self.assertEqual(ac_low_dex, 11)  # 8 + 3 = 11

    def test_ac_calculation_magic_armor(self):
        """Test AC with magic armor"""
        # Plate Mail +3
        plate_plus_3 = self.system.create_armor('plate_mail', magic_bonus=3)
        ac = self.system.calculate_ac(armor=plate_plus_3, shield=None, dex_modifier=0)
        self.assertEqual(ac, 0)  # Plate (3) - magic (3) = 0

    def test_ac_calculation_magic_armor_and_shield(self):
        """Test AC with magic armor and shield"""
        # Plate Mail +2 and Shield +3
        plate_plus_2 = self.system.create_armor('plate_mail', magic_bonus=2)
        shield_plus_3 = self.system.create_shield('shield_small', magic_bonus=3)

        ac = self.system.calculate_ac(armor=plate_plus_2, shield=shield_plus_3, dex_modifier=0)
        # Plate (3) - magic (2) = 1, Shield (1) + magic (3) = 4, Total: 1 - 4 = -3
        self.assertEqual(ac, -3)

    def test_ac_calculation_complete_example(self):
        """Test complete AC calculation from PHB example"""
        # Example: Plate mail + shield + DEX 18 = AC -2
        plate = self.system.create_armor('plate_mail')
        shield = self.system.create_shield('shield_small')
        dex_18_modifier = -4  # DEX 18 gives -4 AC

        ac = self.system.calculate_ac(armor=plate, shield=shield, dex_modifier=dex_18_modifier)
        self.assertEqual(ac, -2)  # 3 - 1 - 4 = -2

    def test_get_armor_list(self):
        """Test getting list of armor"""
        all_armor = self.system.get_armor_list()
        self.assertGreater(len(all_armor), 0)

        # Check structure
        self.assertIn('id', all_armor[0])
        self.assertIn('name', all_armor[0])
        self.assertIn('ac', all_armor[0])
        self.assertIn('cost', all_armor[0])

    def test_get_armor_list_filtered_by_class(self):
        """Test getting armor list filtered by class"""
        # Thief can only wear leather/padded
        thief_armor = self.system.get_armor_list('Thief')
        armor_ids = [a['id'] for a in thief_armor]
        self.assertIn('leather', armor_ids)
        self.assertIn('padded', armor_ids)
        self.assertNotIn('plate_mail', armor_ids)
        self.assertNotIn('chain_mail', armor_ids)

        # Magic-User can't wear any armor
        mu_armor = self.system.get_armor_list('Magic-User')
        self.assertEqual(len(mu_armor), 0)

    def test_get_shield_list_filtered_by_class(self):
        """Test getting shield list filtered by class"""
        # Fighter can use all shields
        fighter_shields = self.system.get_shield_list('Fighter')
        self.assertGreater(len(fighter_shields), 0)

        # Thief can't use shields
        thief_shields = self.system.get_shield_list('Thief')
        self.assertEqual(len(thief_shields), 0)

    def test_get_best_armor_for_class(self):
        """Test getting best armor for a class"""
        # Fighter's best armor is plate mail (AC 3)
        best_fighter = self.system.get_best_armor_for_class('Fighter')
        self.assertEqual(best_fighter, 'plate_mail')

        # Thief's best armor is leather (AC 8)
        best_thief = self.system.get_best_armor_for_class('Thief')
        self.assertIn(best_thief, ['leather', 'padded'])  # Both are AC 8

        # Magic-User can't wear armor
        best_mu = self.system.get_best_armor_for_class('Magic-User')
        self.assertIsNone(best_mu)

    def test_magic_armor_negates_weight(self):
        """Test that magic armor negates weight penalty"""
        plate = self.system.create_armor('plate_mail')
        plate_magic = self.system.create_armor('plate_mail', magic_bonus=1)

        self.assertFalse(self.system.is_magic_armor_negates_weight(plate))
        self.assertTrue(self.system.is_magic_armor_negates_weight(plate_magic))

    def test_get_armor_by_ac(self):
        """Test getting armor by AC value"""
        # AC 8 armor (leather, padded)
        ac_8 = self.system.get_armor_by_ac(8)
        self.assertIn('leather', ac_8)
        self.assertIn('padded', ac_8)

        # AC 3 armor (plate mail)
        ac_3 = self.system.get_armor_by_ac(3)
        self.assertIn('plate_mail', ac_3)


class TestEquipmentClass(unittest.TestCase):
    """Test Equipment class functionality"""

    def test_equipment_initialization(self):
        """Test Equipment class initializes correctly"""
        equipment = Equipment()
        self.assertIsNone(equipment.weapon)
        self.assertIsNone(equipment.armor)
        self.assertIsNone(equipment.shield)
        self.assertIsNone(equipment.helmet)

    def test_equipment_ac_calculation(self):
        """Test Equipment get_total_ac method"""
        system = ArmorSystem()
        equipment = Equipment()

        # Unarmored
        ac = equipment.get_total_ac(base_ac=10, dex_modifier=0)
        self.assertEqual(ac, 10)

        # Equip leather armor
        equipment.armor = system.create_armor('leather')
        ac = equipment.get_total_ac(base_ac=10, dex_modifier=0)
        self.assertEqual(ac, 8)

        # Add shield
        equipment.shield = system.create_shield('shield_small')
        ac = equipment.get_total_ac(base_ac=10, dex_modifier=0)
        self.assertEqual(ac, 7)

        # Add high DEX
        ac = equipment.get_total_ac(base_ac=10, dex_modifier=-4)
        self.assertEqual(ac, 3)

    def test_equipment_movement_rate(self):
        """Test Equipment get_movement_rate method"""
        system = ArmorSystem()
        equipment = Equipment()

        # Unarmored = full movement
        movement = equipment.get_movement_rate(base_movement=12)
        self.assertEqual(movement, 12)

        # Light armor (leather) = 12"
        equipment.armor = system.create_armor('leather')
        movement = equipment.get_movement_rate(base_movement=12)
        self.assertEqual(movement, 12)

        # Heavy armor (chain mail) = 9"
        equipment.armor = system.create_armor('chain_mail')
        movement = equipment.get_movement_rate(base_movement=12)
        self.assertEqual(movement, 9)

        # Very heavy (plate mail) = 6"
        equipment.armor = system.create_armor('plate_mail')
        movement = equipment.get_movement_rate(base_movement=12)
        self.assertEqual(movement, 6)

        # Magic armor negates weight penalty
        equipment.armor = system.create_armor('plate_mail', magic_bonus=1)
        movement = equipment.get_movement_rate(base_movement=12, is_magic_armor=True)
        self.assertEqual(movement, 12)

    def test_equipment_total_weight(self):
        """Test Equipment get_total_weight method"""
        system = ArmorSystem()
        equipment = Equipment()

        # Start with 0
        self.assertEqual(equipment.get_total_weight(), 0.0)

        # Add armor
        equipment.armor = system.create_armor('plate_mail')
        self.assertEqual(equipment.get_total_weight(), 40.0)  # 400 GP weight = 40 lbs

        # Add shield
        equipment.shield = system.create_shield('shield_small')
        self.assertEqual(equipment.get_total_weight(), 41.0)  # 400 GP + 10 GP = 41 lbs


if __name__ == '__main__':
    unittest.main()
