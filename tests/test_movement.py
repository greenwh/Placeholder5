"""
Test suite for Movement & Encumbrance System (Task 2.2)
"""

import unittest
from aerthos.entities.player import PlayerCharacter, Armor, Item
from aerthos.systems.movement import MovementSystem


class TestBaseMovement(unittest.TestCase):
    """Test base movement rates by race"""

    def setUp(self):
        self.movement = MovementSystem()

    def test_human_base_movement(self):
        """Test Human base movement is 12 inches"""
        self.assertEqual(self.movement.get_base_movement('Human'), 12)

    def test_elf_base_movement(self):
        """Test Elf base movement is 12 inches"""
        self.assertEqual(self.movement.get_base_movement('Elf'), 12)

    def test_dwarf_base_movement(self):
        """Test Dwarf base movement is 6 inches"""
        self.assertEqual(self.movement.get_base_movement('Dwarf'), 6)

    def test_gnome_base_movement(self):
        """Test Gnome base movement is 6 inches"""
        self.assertEqual(self.movement.get_base_movement('Gnome'), 6)

    def test_halfling_base_movement(self):
        """Test Halfling base movement is 6 inches"""
        self.assertEqual(self.movement.get_base_movement('Halfling'), 6)

    def test_half_elf_base_movement(self):
        """Test Half-Elf base movement is 12 inches"""
        self.assertEqual(self.movement.get_base_movement('Half-Elf'), 12)

    def test_half_orc_base_movement(self):
        """Test Half-Orc base movement is 12 inches"""
        self.assertEqual(self.movement.get_base_movement('Half-Orc'), 12)


class TestArmorMovement(unittest.TestCase):
    """Test armor movement penalties"""

    def setUp(self):
        self.movement = MovementSystem()

    def test_no_armor(self):
        """Test no armor allows 12 inch movement"""
        rate = self.movement.get_armor_movement_rate(None)
        self.assertEqual(rate, 12)

    def test_leather_armor(self):
        """Test leather armor allows 12 inch movement (light armor)"""
        armor = Armor(name="Leather Armor", weight=15, ac=8)
        rate = self.movement.get_armor_movement_rate(armor)
        self.assertEqual(rate, 12)

    def test_padded_armor(self):
        """Test padded armor allows 12 inch movement (light armor)"""
        armor = Armor(name="Padded Armor", weight=10, ac=8)
        rate = self.movement.get_armor_movement_rate(armor)
        self.assertEqual(rate, 12)

    def test_studded_leather(self):
        """Test studded leather allows 12 inch movement (light armor)"""
        armor = Armor(name="Studded Leather", weight=20, ac=7)
        rate = self.movement.get_armor_movement_rate(armor)
        self.assertEqual(rate, 12)

    def test_chain_mail(self):
        """Test chain mail reduces to 9 inch movement (heavy armor)"""
        armor = Armor(name="Chain Mail", weight=30, ac=5)
        rate = self.movement.get_armor_movement_rate(armor)
        self.assertEqual(rate, 9)

    def test_scale_mail(self):
        """Test scale mail reduces to 9 inch movement (heavy armor)"""
        armor = Armor(name="Scale Mail", weight=40, ac=6)
        rate = self.movement.get_armor_movement_rate(armor)
        self.assertEqual(rate, 9)

    def test_plate_mail(self):
        """Test plate mail reduces to 6 inch movement (very heavy armor)"""
        armor = Armor(name="Plate Mail", weight=45, ac=3)
        rate = self.movement.get_armor_movement_rate(armor)
        self.assertEqual(rate, 6)

    def test_magic_armor_negates_penalty(self):
        """Test magic armor negates weight/movement penalty"""
        magic_chain = Armor(name="Chain Mail", weight=30, ac=5, magic_bonus=1)
        rate = self.movement.get_armor_movement_rate(magic_chain)
        self.assertEqual(rate, 12, "Magic armor should negate movement penalty")


class TestEncumbrance(unittest.TestCase):
    """Test encumbrance categories and modifiers"""

    def setUp(self):
        self.movement = MovementSystem()

    def test_unencumbered(self):
        """Test unencumbered (0-100% of max weight) = full movement"""
        category = self.movement.get_encumbrance_category(250, 500)  # 50%
        self.assertEqual(category, 'unencumbered')

        modifier = self.movement.get_encumbrance_modifier(250, 500)
        self.assertEqual(modifier, 1.0)

    def test_unencumbered_at_max(self):
        """Test exactly at max weight is still unencumbered"""
        category = self.movement.get_encumbrance_category(500, 500)  # 100%
        self.assertEqual(category, 'unencumbered')

        modifier = self.movement.get_encumbrance_modifier(500, 500)
        self.assertEqual(modifier, 1.0)

    def test_lightly_encumbered(self):
        """Test lightly encumbered (100-150% of max) = 3/4 movement"""
        category = self.movement.get_encumbrance_category(625, 500)  # 125%
        self.assertEqual(category, 'lightly')

        modifier = self.movement.get_encumbrance_modifier(625, 500)
        self.assertEqual(modifier, 0.75)

    def test_heavily_encumbered(self):
        """Test heavily encumbered (150-200% of max) = 1/2 movement"""
        category = self.movement.get_encumbrance_category(875, 500)  # 175%
        self.assertEqual(category, 'heavily')

        modifier = self.movement.get_encumbrance_modifier(875, 500)
        self.assertEqual(modifier, 0.5)

    def test_severely_encumbered(self):
        """Test severely encumbered (over 200% of max) = 1/4 movement"""
        category = self.movement.get_encumbrance_category(1100, 500)  # 220%
        self.assertEqual(category, 'severely')

        modifier = self.movement.get_encumbrance_modifier(1100, 500)
        self.assertEqual(modifier, 0.25)


class TestMovementCalculation(unittest.TestCase):
    """Test final movement rate calculations"""

    def setUp(self):
        self.movement = MovementSystem()

    def test_human_no_armor_unencumbered(self):
        """Test Human with no armor and unencumbered"""
        human = PlayerCharacter(
            name="TestHuman",
            char_class="Fighter",
            race="Human",
            level=1,
            strength=10,  # Normal STR
            dexterity=10,
            constitution=10,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        # No armor, low weight
        sword = Item(name="Sword", weight=40)  # 40 GP weight
        human.inventory.add_item(sword)

        rate = self.movement.calculate_movement_rate(human)
        self.assertEqual(rate, 12, "Unencumbered human should move 12 inches")

    def test_dwarf_no_armor_unencumbered(self):
        """Test Dwarf base movement is slower (6 inches)"""
        dwarf = PlayerCharacter(
            name="TestDwarf",
            char_class="Fighter",
            race="Dwarf",
            level=1,
            strength=10,
            dexterity=10,
            constitution=14,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        rate = self.movement.calculate_movement_rate(dwarf)
        self.assertEqual(rate, 6, "Dwarf should move 6 inches base")

    def test_human_chain_mail_unencumbered(self):
        """Test Human in chain mail has reduced movement"""
        human = PlayerCharacter(
            name="TestHuman",
            char_class="Fighter",
            race="Human",
            level=1,
            strength=10,
            dexterity=10,
            constitution=10,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        # Equip chain mail
        chain = Armor(name="Chain Mail", weight=30, ac=5)
        human.equipment.armor = chain

        rate = self.movement.calculate_movement_rate(human)
        self.assertEqual(rate, 9, "Human in chain mail should move 9 inches")

    def test_human_plate_mail_unencumbered(self):
        """Test Human in plate mail has greatly reduced movement"""
        human = PlayerCharacter(
            name="TestHuman",
            char_class="Fighter",
            race="Human",
            level=1,
            strength=10,
            dexterity=10,
            constitution=10,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        # Equip plate mail
        plate = Armor(name="Plate Mail", weight=45, ac=3)
        human.equipment.armor = plate

        rate = self.movement.calculate_movement_rate(human)
        self.assertEqual(rate, 6, "Human in plate mail should move 6 inches")

    def test_dwarf_plate_mail(self):
        """Test Dwarf in plate mail (doesn't slow further than 6)"""
        dwarf = PlayerCharacter(
            name="TestDwarf",
            char_class="Fighter",
            race="Dwarf",
            level=1,
            strength=10,
            dexterity=10,
            constitution=14,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        # Equip plate mail
        plate = Armor(name="Plate Mail", weight=45, ac=3)
        dwarf.equipment.armor = plate

        rate = self.movement.calculate_movement_rate(dwarf)
        self.assertEqual(rate, 6, "Dwarf in plate moves 6 (not slower)")

    def test_encumbrance_effect_on_movement(self):
        """Test that heavy encumbrance reduces movement"""
        human = PlayerCharacter(
            name="TestHuman",
            char_class="Fighter",
            race="Human",
            level=1,
            strength=10,  # STR 10 = 500 GP base capacity
            dexterity=10,
            constitution=10,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        # Add heavy weight (heavily encumbered: 150-200% = 750-1000 GP)
        heavy_pack = Item(name="Heavy Pack", weight=875)  # 875 GP
        human.inventory.add_item(heavy_pack)

        rate = self.movement.calculate_movement_rate(human)
        # Heavily encumbered = 1/2 movement, so 12 * 0.5 = 6
        self.assertEqual(rate, 6, "Heavily encumbered human should move 6 inches")

    def test_magic_armor_negates_weight_full_test(self):
        """Test magic armor negates movement penalty in full calculation"""
        human = PlayerCharacter(
            name="TestHuman",
            char_class="Fighter",
            race="Human",
            level=1,
            strength=10,
            dexterity=10,
            constitution=10,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        # Equip magic chain mail +1
        magic_chain = Armor(name="Chain Mail", weight=30, ac=5, magic_bonus=1)
        human.equipment.armor = magic_chain

        rate = self.movement.calculate_movement_rate(human)
        self.assertEqual(rate, 12, "Magic chain mail should allow 12 inch movement")


class TestRunningAndCharging(unittest.TestCase):
    """Test running and charging mechanics"""

    def setUp(self):
        self.movement = MovementSystem()

    def test_can_run_normal(self):
        """Test that lightly armored character can run"""
        human = PlayerCharacter(
            name="TestHuman",
            char_class="Fighter",
            race="Human",
            level=1,
            strength=10,
            dexterity=10,
            constitution=12,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        # Leather armor
        leather = Armor(name="Leather Armor", weight=15, ac=8)
        human.equipment.armor = leather

        self.assertTrue(self.movement.can_run(human))

    def test_cannot_run_plate(self):
        """Test that character in plate mail cannot run"""
        human = PlayerCharacter(
            name="TestHuman",
            char_class="Fighter",
            race="Human",
            level=1,
            strength=10,
            dexterity=10,
            constitution=12,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        # Plate mail
        plate = Armor(name="Plate Mail", weight=45, ac=3)
        human.equipment.armor = plate

        self.assertFalse(self.movement.can_run(human), "Cannot run in plate mail")

    def test_run_movement_tripled(self):
        """Test that running movement is 3x normal"""
        human = PlayerCharacter(
            name="TestHuman",
            char_class="Fighter",
            race="Human",
            level=1,
            strength=10,
            dexterity=10,
            constitution=12,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        normal_rate = self.movement.calculate_movement_rate(human)
        run_rate = self.movement.calculate_run_movement(human)

        self.assertEqual(run_rate, normal_rate * 3, "Running should be 3x normal movement")

    def test_run_duration_equals_con(self):
        """Test that run duration equals CON score"""
        human = PlayerCharacter(
            name="TestHuman",
            char_class="Fighter",
            race="Human",
            level=1,
            strength=10,
            dexterity=10,
            constitution=14,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        duration = self.movement.calculate_run_duration(human)
        self.assertEqual(duration, 14, "Run duration should equal CON score")

    def test_charge_movement_doubled(self):
        """Test that charging movement is 2x normal"""
        human = PlayerCharacter(
            name="TestHuman",
            char_class="Fighter",
            race="Human",
            level=1,
            strength=10,
            dexterity=10,
            constitution=12,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        normal_rate = self.movement.calculate_movement_rate(human)
        charge_rate = self.movement.calculate_charge_movement(human)

        self.assertEqual(charge_rate, normal_rate * 2, "Charging should be 2x normal movement")

    def test_cannot_run_severely_encumbered(self):
        """Test that severely encumbered character cannot run"""
        human = PlayerCharacter(
            name="TestHuman",
            char_class="Fighter",
            race="Human",
            level=1,
            strength=10,  # 500 GP capacity
            dexterity=10,
            constitution=12,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        # Severely encumbered (over 200% = 1000+ GP)
        very_heavy_pack = Item(name="Very Heavy Pack", weight=1100)  # 1100 GP
        human.inventory.add_item(very_heavy_pack)

        self.assertFalse(self.movement.can_run(human), "Cannot run when severely encumbered")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def setUp(self):
        self.movement = MovementSystem()

    def test_minimum_movement_never_zero(self):
        """Test that movement never drops below 1 inch"""
        human = PlayerCharacter(
            name="TestHuman",
            char_class="Fighter",
            race="Human",
            level=1,
            strength=3,  # Very low STR
            dexterity=10,
            constitution=10,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        # Plate mail + severe encumbrance
        plate = Armor(name="Plate Mail", weight=45, ac=3)
        human.equipment.armor = plate
        overload = Item(name="Overloaded", weight=500)  # 500 GP
        human.inventory.add_item(overload)

        rate = self.movement.calculate_movement_rate(human)
        self.assertGreaterEqual(rate, 1, "Movement should never be less than 1 inch")

    def test_high_strength_increases_capacity(self):
        """Test that high STR increases weight capacity"""
        strong_human = PlayerCharacter(
            name="StrongHuman",
            char_class="Fighter",
            race="Human",
            level=1,
            strength=18,  # High STR
            dexterity=10,
            constitution=10,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        # Add same weight that would heavily encumber STR 10
        heavy_pack = Item(name="Heavy Pack", weight=875)  # 875 GP
        strong_human.inventory.add_item(heavy_pack)

        # With STR 18 (+500 GP), capacity is 1000 GP, so 875 is 87.5% = unencumbered
        rate = self.movement.calculate_movement_rate(strong_human)
        self.assertEqual(rate, 12, "High STR should allow more weight without penalty")


if __name__ == '__main__':
    unittest.main()
