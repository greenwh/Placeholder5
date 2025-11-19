"""
Test suite for Spell Targeting

Tests spell targeting logic including:
- Targeting specific enemies with offensive spells
- Targeting party members with beneficial spells
- Abbreviated spell names
- Various targeting syntaxes (on/at/to)
"""

import unittest
from unittest.mock import Mock
from aerthos.engine.game_state import GameState
from aerthos.entities.player import PlayerCharacter, Spell, SpellSlot
from aerthos.entities.monster import Monster
from aerthos.entities.party import Party
from aerthos.world.dungeon import Dungeon
from aerthos.world.room import Room
from aerthos.engine.parser import Command


class TestSpellTargeting(unittest.TestCase):
    """Test spell targeting in combat"""

    def setUp(self):
        """Set up test fixtures"""
        # Create player
        self.player = PlayerCharacter(
            name="Test Wizard",
            char_class="Magic-User",
            race="Human",
            level=3,
            strength=10,
            dexterity=12,
            constitution=10,
            intelligence=16,
            wisdom=10,
            charisma=10
        )

        # Give player magic missile spell
        magic_missile_spell = Spell(
            name="Magic Missile",
            level=1,
            school="evocation",
            casting_time="1 segment",
            range="60 feet",
            duration="Instantaneous",
            area_of_effect="1 creature",
            saving_throw="None",
            components="standard",
            description="Automatically hits for 1d4+1 damage per missile"
        )

        self.player.spells_memorized = [
            SpellSlot(level=1, spell=magic_missile_spell, is_used=False)
        ]

        # Create dungeon
        test_room = Room(
            id='room_001',
            title='Test Room',
            description='A test room.',
            exits={},
            light_level='torch'
        )

        self.dungeon = Dungeon(
            name='Test Dungeon',
            start_room_id='room_001',
            rooms={'room_001': test_room}
        )

        # Create game state
        self.game_state = GameState(self.player, self.dungeon)

    def test_magic_missile_no_target_with_monsters(self):
        """Test casting magic missile with no specific target (should hit first monster)"""
        # Add monsters to combat
        goblin1 = Monster(
            name="Goblin",
            race="Goblin",
            char_class="Monster",
            level=1,
            hp_current=5,
            hp_max=5,
            ac=6,
            thac0=20
        )

        self.game_state.active_monsters = [goblin1]
        self.game_state.in_combat = True

        # Cast magic missile without target
        result = self.game_state.execute_command(Command('cast', 'magic missile'))

        self.assertTrue(result['success'], "Spell should cast successfully")
        self.assertIn('missile', result['message'].lower())

    def test_magic_missile_specific_target_syntax_on(self):
        """Test casting magic missile ON a specific monster"""
        goblin1 = Monster(name="Goblin", race="Goblin", char_class="Monster",
                         level=1, hp_current=5, hp_max=5, ac=6, thac0=20)
        goblin2 = Monster(name="Orc", race="Orc", char_class="Monster",
                         level=1, hp_current=8, hp_max=8, ac=6, thac0=20)

        self.game_state.active_monsters = [goblin1, goblin2]
        self.game_state.in_combat = True

        orc_hp_before = goblin2.hp_current
        goblin_hp_before = goblin1.hp_current

        # Cast magic missile ON orc specifically
        result = self.game_state.execute_command(Command('cast', 'magic missile on orc'))

        self.assertTrue(result['success'], "Spell should cast successfully")
        self.assertLess(goblin2.hp_current, orc_hp_before, "Orc should be damaged")
        self.assertEqual(goblin1.hp_current, goblin_hp_before, "Goblin should NOT be damaged")

    def test_magic_missile_specific_target_syntax_at(self):
        """Test casting magic missile AT a specific monster"""
        goblin1 = Monster(name="Goblin", race="Goblin", char_class="Monster",
                         level=1, hp_current=5, hp_max=5, ac=6, thac0=20)
        goblin2 = Monster(name="Orc", race="Orc", char_class="Monster",
                         level=1, hp_current=8, hp_max=8, ac=6, thac0=20)

        self.game_state.active_monsters = [goblin1, goblin2]
        self.game_state.in_combat = True

        orc_hp_before = goblin2.hp_current
        goblin_hp_before = goblin1.hp_current

        # Cast magic missile AT orc specifically
        result = self.game_state.execute_command(Command('cast', 'magic missile at orc'))

        self.assertTrue(result['success'], "Spell should cast successfully")
        self.assertLess(goblin2.hp_current, orc_hp_before, "Orc should be damaged")
        self.assertEqual(goblin1.hp_current, goblin_hp_before, "Goblin should NOT be damaged")

    def test_magic_missile_no_monsters(self):
        """Test casting magic missile with no monsters present"""
        self.game_state.active_monsters = []
        self.game_state.in_combat = False

        result = self.game_state.execute_command(Command('cast', 'magic missile'))

        self.assertFalse(result['success'])
        self.assertIn('no enemies', result['message'].lower())

    def test_cure_light_wounds_on_party_member(self):
        """Test casting cure light wounds on specific party member"""
        # Create party with multiple members
        thorin = PlayerCharacter(
            name="Thorin",
            char_class="Fighter",
            race="Dwarf",
            level=3,
            strength=16,
            dexterity=10,
            constitution=14,
            intelligence=8,
            wisdom=10,
            charisma=8
        )
        thorin.hp_current = 10
        thorin.hp_max = 20

        party = Party(members=[self.player, thorin])
        self.game_state.party = party

        # Give player cure light wounds
        cure_spell = Spell(
            name="Cure Light Wounds",
            level=1,
            school="necromancy",
            casting_time="5 segments",
            range="Touch",
            duration="Permanent",
            area_of_effect="1 creature",
            saving_throw="None",
            components="standard",
            description="Heals 1d8 HP"
        )

        self.player.spells_memorized = [
            SpellSlot(level=1, spell=cure_spell, is_used=False)
        ]

        # Cast cure on thorin
        result = self.game_state.execute_command(Command('cast', 'cure light wounds on thorin'))

        self.assertTrue(result['success'], "Spell should cast successfully")
        self.assertIn('thorin', result['message'].lower())

    def test_cure_light_wounds_abbreviated_on_party_member(self):
        """Test casting abbreviated 'c' for cure on party member"""
        thorin = PlayerCharacter(
            name="Thorin",
            char_class="Fighter",
            race="Dwarf",
            level=3,
            strength=16,
            dexterity=10,
            constitution=14,
            intelligence=8,
            wisdom=10,
            charisma=8
        )
        thorin.hp_current = 10
        thorin.hp_max = 20

        party = Party(members=[self.player, thorin])
        self.game_state.party = party

        # Give player cure light wounds
        cure_spell = Spell(
            name="Cure Light Wounds",
            level=1,
            school="necromancy",
            casting_time="5 segments",
            range="Touch",
            duration="Permanent",
            area_of_effect="1 creature",
            saving_throw="None",
            components="standard",
            description="Heals 1d8 HP"
        )

        self.player.spells_memorized = [
            SpellSlot(level=1, spell=cure_spell, is_used=False)
        ]

        # Cast abbreviated 'c' on thorin
        result = self.game_state.execute_command(Command('cast', 'c on thorin'))

        self.assertTrue(result['success'], "Abbreviated spell should cast successfully")
        self.assertIn('thorin', result['message'].lower())

    def test_beneficial_spell_cannot_target_monsters(self):
        """Test that beneficial spells cannot target monsters"""
        # Add monster
        goblin = Monster(name="Goblin", race="Goblin", char_class="Monster",
                        level=1, hp_current=3, hp_max=5, ac=6, thac0=20)

        self.game_state.active_monsters = [goblin]
        self.game_state.in_combat = True

        # Give player cure light wounds
        cure_spell = Spell(
            name="Cure Light Wounds",
            level=1,
            school="necromancy",
            casting_time="5 segments",
            range="Touch",
            duration="Permanent",
            area_of_effect="1 creature",
            saving_throw="None",
            components="standard",
            description="Heals 1d8 HP"
        )

        self.player.spells_memorized = [
            SpellSlot(level=1, spell=cure_spell, is_used=False)
        ]

        # Try to cast cure on goblin (should target self since no party and goblin isn't a party member)
        wizard_hp_before = self.player.hp_current
        result = self.game_state.execute_command(Command('cast', 'cure light wounds on goblin'))

        # Should succeed but target caster (self), not the goblin
        self.assertTrue(result['success'])
        # Wizard's name should be in message (healed self)
        self.assertIn('test wizard', result['message'].lower())
        # Goblin HP should be unchanged
        self.assertEqual(goblin.hp_current, 3)


class TestOtherSingleTargetSpells(unittest.TestCase):
    """Test targeting for other single-target spells"""

    def setUp(self):
        """Set up test fixtures"""
        self.player = PlayerCharacter(
            name="Test Wizard",
            char_class="Magic-User",
            race="Human",
            level=3,
            strength=10, dexterity=12, constitution=10,
            intelligence=16, wisdom=10, charisma=10
        )

        test_room = Room(
            id='room_001',
            title='Test Room',
            description='A test room.',
            exits={},
            light_level='torch'
        )

        self.dungeon = Dungeon(
            name='Test Dungeon',
            start_room_id='room_001',
            rooms={'room_001': test_room}
        )

        self.game_state = GameState(self.player, self.dungeon)

    def test_charm_person_specific_target(self):
        """Test charm person targeting specific enemy"""
        # Create spell
        charm_spell = Spell(
            name="Charm Person",
            level=1, school="enchantment",
            casting_time="1 segment", range="120 feet",
            duration="Special", area_of_effect="1 person",
            saving_throw="Negates", components="standard",
            description="Charms a single humanoid"
        )

        self.player.spells_memorized = [
            SpellSlot(level=1, spell=charm_spell, is_used=False)
        ]

        # Create two humanoid monsters
        bandit1 = Monster(name="Bandit", race="Human", char_class="Monster",
                         level=1, hp_current=5, hp_max=5, ac=7, thac0=20)
        bandit2 = Monster(name="Thug", race="Human", char_class="Monster",
                         level=1, hp_current=6, hp_max=6, ac=6, thac0=20)

        self.game_state.active_monsters = [bandit1, bandit2]
        self.game_state.in_combat = True

        # Cast charm on "thug" specifically
        result = self.game_state.execute_command(Command('cast', 'charm person on thug'))

        self.assertTrue(result['success'], "Charm person should cast successfully")
        # Should mention thug in message
        self.assertIn('thug', result['message'].lower())


class TestSpellTargetingEdgeCases(unittest.TestCase):
    """Test edge cases in spell targeting"""

    def setUp(self):
        """Set up test fixtures"""
        self.player = PlayerCharacter(
            name="Test Wizard",
            char_class="Magic-User",
            race="Human",
            level=3,
            strength=10, dexterity=12, constitution=10,
            intelligence=16, wisdom=10, charisma=10
        )

        magic_missile_spell = Spell(
            name="Magic Missile",
            level=1, school="evocation",
            casting_time="1 segment", range="60 feet",
            duration="Instantaneous", area_of_effect="1 creature",
            saving_throw="None", components="standard",
            description="Auto-hit missile"
        )

        self.player.spells_memorized = [
            SpellSlot(level=1, spell=magic_missile_spell, is_used=False)
        ]

        test_room = Room(
            id='room_001',
            title='Test Room',
            description='A test room.',
            exits={},
            light_level='torch'
        )

        self.dungeon = Dungeon(
            name='Test Dungeon',
            start_room_id='room_001',
            rooms={'room_001': test_room}
        )

        self.game_state = GameState(self.player, self.dungeon)

    def test_spell_name_with_target_in_name(self):
        """Test spell with word that looks like target (e.g., 'protection from evil')"""
        # This is a regression test to ensure spell parsing doesn't break on spell names
        # Protection from evil should parse correctly even with "from" and "evil" in name
        pass

    def test_multiple_monsters_same_name(self):
        """Test targeting when multiple monsters have same name"""
        goblin1 = Monster(name="Goblin", race="Goblin", char_class="Monster",
                         level=1, hp_current=5, hp_max=5, ac=6, thac0=20)
        goblin2 = Monster(name="Goblin", race="Goblin", char_class="Monster",
                         level=1, hp_current=5, hp_max=5, ac=6, thac0=20)

        self.game_state.active_monsters = [goblin1, goblin2]
        self.game_state.in_combat = True

        goblin1_hp_before = goblin1.hp_current
        goblin2_hp_before = goblin2.hp_current

        # Cast on "goblin" - should target first one
        result = self.game_state.execute_command(Command('cast', 'magic missile on goblin'))

        self.assertTrue(result['success'])
        # First goblin should be hit
        self.assertLess(goblin1.hp_current, goblin1_hp_before)

    def test_partial_name_match(self):
        """Test targeting with partial name match"""
        goblin = Monster(name="Goblin Shaman", race="Goblin", char_class="Monster",
                        level=2, hp_current=8, hp_max=8, ac=6, thac0=19)

        self.game_state.active_monsters = [goblin]
        self.game_state.in_combat = True

        hp_before = goblin.hp_current

        # Cast on "shaman" (partial match)
        result = self.game_state.execute_command(Command('cast', 'magic missile on shaman'))

        self.assertTrue(result['success'])
        self.assertLess(goblin.hp_current, hp_before, "Goblin Shaman should be hit by partial name")

    def test_no_target_found_error_message(self):
        """Test error message when target not found"""
        goblin = Monster(name="Goblin", race="Goblin", char_class="Monster",
                        level=1, hp_current=5, hp_max=5, ac=6, thac0=20)

        self.game_state.active_monsters = [goblin]
        self.game_state.in_combat = True

        # Try to target non-existent "orc"
        result = self.game_state.execute_command(Command('cast', 'magic missile on orc'))

        self.assertFalse(result['success'])
        self.assertIn('no enemy', result['message'].lower())
        self.assertIn('orc', result['message'].lower())


if __name__ == '__main__':
    unittest.main()
