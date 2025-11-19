"""
Test suite for Magic Functionality

Converted from tests_manual/test_magic_functionality.py
Tests all functional magic items and monster special abilities to ensure they work mechanically.
"""

import unittest
from aerthos.systems.treasure import TreasureGenerator
from aerthos.systems.magic_item_factory import MagicItemFactory
from aerthos.entities.magic_items import Potion, Scroll, Ring, Wand, Staff, MiscMagic
from aerthos.entities.player import Weapon, Armor, PlayerCharacter, Equipment
from aerthos.entities.character import Character
from aerthos.entities.monster import Monster
from aerthos.engine.combat import CombatResolver
from aerthos.systems.monster_abilities import MonsterSpecialAbilities


class TestPotionFunctionality(unittest.TestCase):
    """Test that potions actually work"""

    def setUp(self):
        """Set up test character"""
        self.test_char = Character(
            name="Test Fighter",
            race="Human",
            char_class="Fighter",
            level=3,
            hp_current=10,
            hp_max=25,
            ac=5,
            thac0=18
        )

    def test_healing_potion(self):
        """Test healing potion restores HP"""
        healing_potion = Potion(
            name="Potion of Healing",
            effect_type="healing",
            effect_data={"heal_dice": "2d4+2"},
            xp_value=200,
            gp_value=400
        )

        hp_before = self.test_char.hp_current
        result = healing_potion.use(self.test_char)

        self.assertTrue(result['success'])
        self.assertIn('message', result)
        self.assertGreater(self.test_char.hp_current, hp_before,
                          "Healing potion should restore HP")

    def test_poison_potion(self):
        """Test poison potion deals damage"""
        poison_potion = Potion(
            name="Potion of Poison",
            effect_type="poison",
            effect_data={"damage": "3d6"},
            xp_value=0,
            gp_value=0
        )

        hp_before = self.test_char.hp_current
        result = poison_potion.use(self.test_char)

        self.assertTrue(result['success'])
        self.assertLess(self.test_char.hp_current, hp_before,
                       "Poison potion should deal damage")

    def test_buff_potion(self):
        """Test buff potion (invisibility)"""
        invis_potion = Potion(
            name="Potion of Invisibility",
            effect_type="invisibility",
            duration_turns=24,
            xp_value=250,
            gp_value=500
        )

        result = invis_potion.use(self.test_char)

        self.assertTrue(result['success'], "Potion should be usable")
        self.assertIn('effects', result)
        self.assertGreater(len(result['effects']), 0)
        self.assertIn('duration', result['effects'][0])


class TestScrollFunctionality(unittest.TestCase):
    """Test that scrolls actually work"""

    def setUp(self):
        """Set up test character"""
        self.test_char = Character(
            name="Test Cleric",
            race="Human",
            char_class="Cleric",
            level=3,
            hp_current=20,
            hp_max=20,
            ac=4,
            thac0=18
        )

    def test_protection_scroll(self):
        """Test protection from undead scroll"""
        protection_scroll = Scroll(
            name="Protection from Undead",
            scroll_type="protection",
            protection_type="undead",
            duration_turns=60,
            xp_value=1500,
            gp_value=1000
        )

        result = protection_scroll.use(self.test_char)

        self.assertTrue(result['success'], "Protection scroll should work")
        self.assertIn('effects', result)
        self.assertEqual(result['effects'][0]['type'], 'protection',
                        "Should grant protection")
        self.assertEqual(result['effects'][0]['protection_against'], 'undead')
        self.assertEqual(result['effects'][0]['duration'], 60)

    def test_spell_scroll(self):
        """Test spell scroll"""
        spell_scroll = Scroll(
            name="Scroll of Fireball",
            scroll_type="spell",
            spell_name="Fireball",
            spell_level=3,
            xp_value=300,
            gp_value=600
        )

        result = spell_scroll.use(self.test_char)

        self.assertTrue(result['success'])
        self.assertIn('effects', result)
        self.assertEqual(result['effects'][0]['type'], 'spell_cast',
                        "Should cast spell")


class TestRingFunctionality(unittest.TestCase):
    """Test that rings actually work"""

    def setUp(self):
        """Set up test character"""
        self.test_char = Character(
            name="Test Thief",
            race="Elf",
            char_class="Thief",
            level=4,
            hp_current=18,
            hp_max=18,
            ac=7,
            thac0=19
        )

    def test_ring_of_protection(self):
        """Test ring of protection provides AC bonus"""
        protection_ring = Ring(
            name="Ring of Protection +2",
            ring_type="protection",
            effect_data={"ac_bonus": 2},
            xp_value=4000,
            gp_value=20000
        )

        effect = protection_ring.get_continuous_effect()

        self.assertEqual(effect['type'], 'ac_bonus')
        self.assertEqual(effect['value'], 2, "Should provide +2 AC bonus")

    def test_ring_of_wishes(self):
        """Test ring of wishes consumes charges"""
        wish_ring = Ring(
            name="Ring of Wishes (3)",
            ring_type="wishes",
            effect_data={"wish_type": "limited"},
            charges=3,
            charges_remaining=3,
            xp_value=15000,
            gp_value=15000
        )

        charges_before = wish_ring.charges_remaining
        result = wish_ring.activate(self.test_char)

        self.assertTrue(result['success'])
        self.assertEqual(wish_ring.charges_remaining, charges_before - 1,
                        "Should consume 1 wish")

    def test_ring_of_regeneration(self):
        """Test ring of regeneration"""
        regen_ring = Ring(
            name="Ring of Regeneration",
            ring_type="regeneration",
            effect_data={"hp_per_turn": 1},
            xp_value=4000,
            gp_value=20000
        )

        effect = regen_ring.get_continuous_effect()

        self.assertEqual(effect['type'], 'regeneration')
        self.assertEqual(effect['rate'], 1, "Should regenerate 1 HP per turn")


class TestWandStaffFunctionality(unittest.TestCase):
    """Test that wands and staves actually work"""

    def setUp(self):
        """Set up test character"""
        self.test_char = Character(
            name="Test Magic-User",
            race="Human",
            char_class="Magic-User",
            level=5,
            hp_current=15,
            hp_max=15,
            ac=9,
            thac0=19
        )

    def test_wand_of_magic_missiles(self):
        """Test wand of magic missiles"""
        wand = Wand(
            name="Wand of Magic Missiles",
            wand_type="magic_missiles",
            charges=30,
            charges_remaining=30,
            spell_effect="magic_missile",
            effect_data={"missiles": 3, "damage_per_missile": "1d4+1"},
            xp_value=2000,
            gp_value=10000
        )

        charges_before = wand.charges_remaining
        result = wand.use(self.test_char)

        self.assertTrue(result['success'])
        self.assertEqual(wand.charges_remaining, charges_before - 1,
                        "Should consume 1 charge")
        self.assertEqual(result['effects'][0]['count'], 3,
                        "Should fire 3 missiles")

    def test_staff_of_striking(self):
        """Test staff of striking"""
        staff = Staff(
            name="Staff of Striking",
            staff_type="striking",
            charges=40,
            charges_remaining=40,
            powers=["striking"],
            effect_data={"damage_bonus": "3d6"},
            xp_value=3000,
            gp_value=15000
        )

        charges_before = staff.charges_remaining
        result = staff.use(self.test_char)

        self.assertTrue(result['success'])
        self.assertEqual(staff.charges_remaining, charges_before - 1,
                        "Should consume 1 charge")
        self.assertIn('damage_bonus', result['effects'][0])


class TestMagicWeaponProperties(unittest.TestCase):
    """Test that magic weapons' special properties actually work"""

    def setUp(self):
        """Set up factory and test characters"""
        self.factory = MagicItemFactory()

    def test_flame_tongue_properties(self):
        """Test Sword +1, Flame Tongue has correct properties"""
        flame_tongue_dict = {
            "type": "weapon",
            "name": "Sword +1, Flame Tongue",
            "xp_value": 900,
            "gp_value": 4500
        }

        flame_tongue = self.factory.create_from_treasure(flame_tongue_dict)

        self.assertIsInstance(flame_tongue, Weapon)
        self.assertGreater(flame_tongue.magic_bonus, 0)
        self.assertEqual(flame_tongue.properties['special'], 'flame_tongue',
                        "Should have flame tongue property")
        self.assertIn('fire_damage', flame_tongue.properties,
                     "Should deal fire damage")

    def test_dragon_slayer_properties(self):
        """Test Sword +2, Dragon Slayer has correct properties"""
        dragon_slayer_dict = {
            "type": "weapon",
            "name": "Sword +2, Dragon Slayer",
            "xp_value": 900,
            "gp_value": 4500
        }

        dragon_slayer = self.factory.create_from_treasure(dragon_slayer_dict)

        self.assertIsInstance(dragon_slayer, Weapon)
        self.assertGreater(dragon_slayer.magic_bonus, 0)
        self.assertEqual(dragon_slayer.properties['special'], 'dragon_slayer',
                        "Should have dragon slayer property")
        self.assertEqual(dragon_slayer.properties['bonus_vs_dragons'], 3,
                        "Should get +3 vs dragons")

    def test_special_weapon_in_combat(self):
        """Test special weapon works in combat"""
        flame_tongue_dict = {
            "type": "weapon",
            "name": "Sword +1, Flame Tongue",
            "xp_value": 900,
            "gp_value": 4500
        }
        flame_tongue = self.factory.create_from_treasure(flame_tongue_dict)

        fighter = Character(
            name="Fighter",
            race="Human",
            char_class="Fighter",
            level=5,
            hp_current=35,
            hp_max=35,
            ac=3,
            thac0=16,
            strength=16,  # Set STR during construction
            dexterity=12,
            constitution=14,
            intelligence=10,
            wisdom=10,
            charisma=10
        )

        dragon = Monster(
            name="Young Red Dragon",
            race="Dragon",
            char_class="Monster",
            level=7,
            hp_current=40,
            hp_max=40,
            ac=2,
            thac0=13
        )

        combat = CombatResolver()

        # Equip flame tongue
        fighter.equipment = Equipment()
        fighter.equipment.weapon = flame_tongue

        # Make an attack
        result = combat.attack_roll(fighter, dragon, fighter.equipment.weapon)

        # Verify result structure
        self.assertIn('hit', result)
        self.assertIn('roll', result)
        self.assertIn('damage', result)

        if result['hit']:
            self.assertGreater(result['damage'], 0, "Should deal damage")


class TestMonsterAbilities(unittest.TestCase):
    """Test that monster special abilities actually work"""

    def setUp(self):
        """Set up abilities system"""
        self.abilities = MonsterSpecialAbilities()

    def test_dragon_breath_weapon(self):
        """Test dragon breath weapon"""
        dragon = Monster(
            name="Red Dragon",
            race="Dragon",
            char_class="Monster",
            level=10,
            hp_current=80,
            hp_max=80,
            ac=-1,
            thac0=10,
            special_abilities=["breath_weapon_fire"]
        )

        result = self.abilities.use_ability(dragon, "breath_weapon_fire", [])

        self.assertTrue(result.success)
        self.assertGreater(result.damage, 0, "Breath weapon should deal damage")
        self.assertTrue(result.save_allowed, "Should allow save")
        self.assertEqual(result.save_type, "breath")
        self.assertEqual(result.effects[0]['type'], 'breath_weapon')

    def test_poison_attack(self):
        """Test poison attack"""
        spider = Monster(
            name="Giant Spider",
            race="Spider",
            char_class="Monster",
            level=2,
            hp_current=12,
            hp_max=12,
            ac=6,
            thac0=18,
            special_abilities=["poison_deadly"]
        )

        result = self.abilities.use_ability(spider, "poison_deadly", [])

        self.assertTrue(result.success)
        self.assertTrue(result.save_allowed, "Should allow save vs poison")
        self.assertIn('poison', result.save_type.lower())
        self.assertEqual(result.effects[0]['poison_type'], 'deadly')

    def test_regeneration(self):
        """Test regeneration"""
        troll = Monster(
            name="Troll",
            race="Troll",
            char_class="Monster",
            level=6,
            hp_current=25,
            hp_max=40,
            ac=4,
            thac0=13,
            special_abilities=["regeneration"]
        )

        hp_before = troll.hp_current
        result = self.abilities.use_ability(troll, "regeneration", [])

        self.assertTrue(result.success)
        self.assertGreater(troll.hp_current, hp_before,
                          "Troll should regenerate HP")

    def test_level_drain(self):
        """Test level drain"""
        vampire = Monster(
            name="Vampire",
            race="Undead",
            char_class="Monster",
            level=8,
            hp_current=50,
            hp_max=50,
            ac=1,
            thac0=12,
            special_abilities=["level_drain"]
        )

        result = self.abilities.use_ability(vampire, "level_drain", [])

        self.assertTrue(result.success)
        self.assertEqual(result.effects[0]['levels_lost'], 2,
                        "Vampire should drain 2 levels")
        self.assertFalse(result.save_allowed,
                        "No save allowed for level drain")


class TestTreasureIntegration(unittest.TestCase):
    """Test that treasure generation creates functional items"""

    def setUp(self):
        """Set up treasure generator"""
        self.generator = TreasureGenerator()

    def test_treasure_generates_functional_items(self):
        """Test that generated magic items are functional objects"""
        trials = 20
        functional_items_found = 0

        for _ in range(trials):
            hoard = self.generator.generate_lair_treasure("A")

            if hoard.magic_items:
                for item in hoard.magic_items:
                    # Verify it's a functional object
                    self.assertTrue(hasattr(item, 'name'),
                                   "Should have name attribute")
                    self.assertTrue(hasattr(item, 'xp_value'),
                                   "Should have XP value")
                    self.assertTrue(hasattr(item, 'gp_value'),
                                   "Should have GP value")

                    # Test if it's a recognized type
                    if isinstance(item, (Potion, Ring, Wand, Staff, Weapon, Armor, MiscMagic)):
                        functional_items_found += 1

        # Should find at least some functional items in 20 treasure hoards
        self.assertGreater(functional_items_found, 0,
                          "Should find at least some functional items")


if __name__ == '__main__':
    unittest.main()
