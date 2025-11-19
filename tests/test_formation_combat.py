"""
Tests for formation-based combat targeting system
"""

import unittest
from aerthos.entities.character import Character
from aerthos.entities.player import PlayerCharacter
from aerthos.entities.monster import Monster
from aerthos.entities.party import Party
from aerthos.systems.monster_ai import MonsterTargetingAI
from aerthos.engine.combat import CombatResolver


class TestMonsterTargetingAI(unittest.TestCase):
    """Test monster targeting AI with formation awareness"""

    def setUp(self):
        """Set up test fixtures"""
        self.ai = MonsterTargetingAI()

        # Create a test party
        self.fighter = PlayerCharacter(
            name="Thorin",
            race="Dwarf",
            char_class="Fighter",
            strength=18,
            dexterity=14,
            constitution=16,
            intelligence=10,
            wisdom=10,
            charisma=12,
            strength_percentile=50
        )
        self.fighter.hp_current = 18
        self.fighter.hp_max = 18
        self.fighter.ac = 4

        self.cleric = PlayerCharacter(
            name="Gimli",
            race="Dwarf",
            char_class="Cleric",
            strength=16,
            dexterity=12,
            constitution=14,
            intelligence=10,
            wisdom=16,
            charisma=10
        )
        self.cleric.hp_current = 12
        self.cleric.hp_max = 12
        self.cleric.ac = 5

        self.mage = PlayerCharacter(
            name="Gandalf",
            race="Human",
            char_class="Magic-User",
            strength=10,
            dexterity=14,
            constitution=12,
            intelligence=18,
            wisdom=14,
            charisma=14
        )
        self.mage.hp_current = 6
        self.mage.hp_max = 6
        self.mage.ac = 8

        self.thief = PlayerCharacter(
            name="Bilbo",
            race="Halfling",
            char_class="Thief",
            strength=12,
            dexterity=18,
            constitution=14,
            intelligence=12,
            wisdom=10,
            charisma=14
        )
        self.thief.hp_current = 8
        self.thief.hp_max = 8
        self.thief.ac = 6

        # Create party with formation
        self.party = Party(max_size=6)
        self.party.add_member(self.fighter)
        self.party.add_member(self.cleric)
        self.party.add_member(self.mage)
        self.party.add_member(self.thief)

        # Set formation: fighters in front, spellcasters in back
        self.party.formation = ['front', 'front', 'back', 'back']

        # Create test monster
        self.orc = Monster(
            name="Orc",
            race="Orc",
            char_class="Warrior",
            level=1,
            strength=14,
            dexterity=12,
            constitution=14,
            intelligence=10,
            wisdom=10,
            charisma=8
        )
        self.orc.hp_current = 8
        self.orc.hp_max = 8

    def test_select_target_with_no_party(self):
        """Test target selection falls back to random without party"""
        targets = [self.fighter, self.mage, self.thief]
        target = self.ai.select_target(self.orc, None, targets)
        self.assertIn(target, targets)

    def test_front_line_preferential_targeting(self):
        """Test that front line gets targeted more often"""
        targets = [self.fighter, self.cleric, self.mage, self.thief]

        # Run 100 targeting attempts
        front_line_hits = 0
        back_line_hits = 0
        attempts = 100

        for _ in range(attempts):
            target = self.ai.select_target(self.orc, self.party, targets)

            if target in [self.fighter, self.cleric]:
                front_line_hits += 1
            else:
                back_line_hits += 1

        # Front line should get 60%+ of attacks (allowing for randomness)
        front_line_percentage = (front_line_hits / attempts) * 100
        self.assertGreater(front_line_percentage, 50,
                          f"Front line should be targeted >50% of time, got {front_line_percentage:.1f}%")

    def test_low_intelligence_targets_nearest(self):
        """Test that low intelligence monsters attack front line"""
        # Set orc to animal intelligence
        self.orc.intelligence = 3  # Below LOW_INT threshold

        targets = [self.fighter, self.cleric, self.mage, self.thief]

        # Run 50 targeting attempts
        front_line_hits = 0
        attempts = 50

        for _ in range(attempts):
            target = self.ai.select_target(self.orc, self.party, targets)
            if target in [self.fighter, self.cleric]:
                front_line_hits += 1

        # Low INT monsters should almost always target front line
        front_line_percentage = (front_line_hits / attempts) * 100
        self.assertGreater(front_line_percentage, 80,
                          f"Low INT monsters should target front line >80% of time, got {front_line_percentage:.1f}%")

    def test_weakest_target_selection(self):
        """Test selection of most wounded target"""
        # Wound the fighter
        self.fighter.hp_current = 5  # 28% HP

        targets = [self.fighter, self.cleric]

        weakest = self.ai._select_weakest_target(targets)
        self.assertEqual(weakest, self.fighter,
                        "Should select most wounded target")

    def test_back_line_exposed_when_front_line_dead(self):
        """Test that back line becomes vulnerable when front line falls"""
        # Kill front line
        self.fighter.take_damage(999)  # Kill fighter
        self.cleric.take_damage(999)   # Kill cleric

        targets = [self.mage, self.thief]  # Only back line alive

        # Now back line should be targetable
        target = self.ai.select_target(self.orc, self.party, targets)
        self.assertIn(target, [self.mage, self.thief],
                     "Should target back line when front line is dead")

    def test_formation_system_integration(self):
        """Test Party formation methods"""
        front = self.party.get_front_line()
        back = self.party.get_back_line()

        self.assertEqual(len(front), 2, "Should have 2 in front line")
        self.assertEqual(len(back), 2, "Should have 2 in back line")
        self.assertIn(self.fighter, front, "Fighter should be in front")
        self.assertIn(self.mage, back, "Mage should be in back")

    def test_is_front_line_standing(self):
        """Test detection of standing front line"""
        self.assertTrue(self.party.is_front_line_standing(),
                       "Front line should be standing")

        # Kill front line
        self.fighter.take_damage(999)  # Kill fighter
        self.cleric.take_damage(999)   # Kill cleric

        self.assertFalse(self.party.is_front_line_standing(),
                        "Front line should not be standing")


class TestCombatResolverFormation(unittest.TestCase):
    """Test combat resolver with formation support"""

    def setUp(self):
        """Set up test fixtures"""
        self.resolver = CombatResolver()

        # Create minimal test party
        self.fighter = PlayerCharacter(
            name="TestFighter",
            race="Human",
            char_class="Fighter",
            strength=16,
            dexterity=12,
            constitution=14,
            intelligence=10,
            wisdom=10,
            charisma=10
        )
        self.fighter.hp_current = 15
        self.fighter.hp_max = 15

        # Create test monster
        self.goblin = Monster(
            name="Goblin",
            race="Goblin",
            char_class="Warrior",
            level=1,
            strength=12,
            dexterity=14,
            constitution=12,
            intelligence=10,
            wisdom=10,
            charisma=8
        )
        self.goblin.hp_current = 5
        self.goblin.hp_max = 5

    def test_combat_resolver_accepts_party_obj(self):
        """Test that combat resolver accepts optional party_obj parameter"""
        party_members = [self.fighter]
        monsters = [self.goblin]

        # Should not raise error with party_obj=None
        try:
            result = self.resolver.resolve_combat_round(
                party_members,
                monsters,
                party_obj=None
            )
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.fail(f"Combat resolver raised exception with party_obj=None: {e}")


if __name__ == '__main__':
    unittest.main()
