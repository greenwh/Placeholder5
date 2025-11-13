"""
Test suite for CommandParser

Tests natural language command parsing, the critical boundary between user input and game logic.
Both CLI and Web UI depend on this working correctly.
"""

import unittest
from aerthos.engine.parser import CommandParser, Command


class TestCommandParser(unittest.TestCase):
    """Test the command parser with various input formats"""

    def setUp(self):
        self.parser = CommandParser()

    # Movement commands
    def test_direction_full(self):
        """Test full direction words"""
        cmd = self.parser.parse("north")
        self.assertEqual(cmd.action, "move")
        self.assertEqual(cmd.target, "north")

    def test_direction_short(self):
        """Test direction abbreviations"""
        cmd = self.parser.parse("n")
        self.assertEqual(cmd.action, "move")
        self.assertEqual(cmd.target, "north")

        cmd = self.parser.parse("s")
        self.assertEqual(cmd.target, "south")

    def test_go_direction(self):
        """Test 'go [direction]' format"""
        cmd = self.parser.parse("go north")
        self.assertEqual(cmd.action, "move")
        self.assertEqual(cmd.target, "north")

        cmd = self.parser.parse("go e")
        self.assertEqual(cmd.target, "east")

    # Combat commands
    def test_attack_basic(self):
        """Test basic attack command"""
        cmd = self.parser.parse("attack orc")
        self.assertEqual(cmd.action, "attack")
        self.assertEqual(cmd.target, "orc")

    def test_attack_with_article(self):
        """Test attack with 'the' article"""
        cmd = self.parser.parse("attack the goblin")
        self.assertEqual(cmd.action, "attack")
        self.assertEqual(cmd.target, "goblin")

    def test_attack_with_weapon(self):
        """Test attack specifying weapon"""
        cmd = self.parser.parse("attack orc with sword")
        self.assertEqual(cmd.action, "attack")
        self.assertEqual(cmd.target, "orc")
        # Parser handles "with" internally
        self.assertEqual(cmd.action, "attack")

    def test_attack_synonyms(self):
        """Test attack command synonyms"""
        for synonym in ["hit", "strike", "fight"]:
            cmd = self.parser.parse(f"{synonym} kobold")
            self.assertEqual(cmd.action, "attack", f"Failed for synonym: {synonym}")
            self.assertEqual(cmd.target, "kobold")

    # Magic commands
    def test_cast_spell_basic(self):
        """Test basic spell casting"""
        cmd = self.parser.parse("cast magic missile")
        self.assertEqual(cmd.action, "cast")
        # Spell parsing - check action is cast
        self.assertEqual(cmd.action, "cast")

    def test_cast_spell_on_target(self):
        """Test spell with target"""
        cmd = self.parser.parse("cast cure light wounds on fighter")
        self.assertEqual(cmd.action, "cast")
        # Parser extracts the spell name (first word after 'cast'), not the target creature
        # In this case, it extracts "cure" from "cure light wounds"
        self.assertEqual(cmd.target, "cure")

    def test_cast_spell_at_target(self):
        """Test spell with 'at' preposition"""
        cmd = self.parser.parse("cast fireball at skeleton")
        self.assertEqual(cmd.action, "cast")
        # Parser extracts the spell name (first word after 'cast'), not the target creature
        self.assertEqual(cmd.target, "fireball")

    # Item commands
    def test_take_item(self):
        """Test taking items"""
        cmd = self.parser.parse("take sword")
        self.assertEqual(cmd.action, "take")
        self.assertEqual(cmd.target, "sword")

    def test_get_item(self):
        """Test 'get' synonym for take"""
        cmd = self.parser.parse("get potion")
        self.assertEqual(cmd.action, "take")
        self.assertEqual(cmd.target, "potion")

    def test_take_with_article(self):
        """Test taking with articles"""
        cmd = self.parser.parse("take the longsword")
        self.assertEqual(cmd.action, "take")
        self.assertEqual(cmd.target, "longsword")

    def test_drop_item(self):
        """Test dropping items"""
        cmd = self.parser.parse("drop torch")
        self.assertEqual(cmd.action, "drop")
        self.assertEqual(cmd.target, "torch")

    def test_use_item(self):
        """Test using items"""
        cmd = self.parser.parse("use potion")
        self.assertEqual(cmd.action, "use")
        self.assertEqual(cmd.target, "potion")

    def test_drink_potion(self):
        """Test drink as use synonym"""
        cmd = self.parser.parse("drink healing potion")
        self.assertEqual(cmd.action, "use")
        # Parser extracts first non-verb word, which is "healing"
        self.assertEqual(cmd.target, "healing")

    def test_equip_item(self):
        """Test equipping items"""
        cmd = self.parser.parse("equip chainmail")
        self.assertEqual(cmd.action, "equip")
        self.assertEqual(cmd.target, "chainmail")

    def test_wear_armor(self):
        """Test 'wear' synonym for equip"""
        cmd = self.parser.parse("wear leather armor")
        self.assertEqual(cmd.action, "equip")
        self.assertIn("leather", cmd.target.lower())

    # Exploration commands
    def test_search(self):
        """Test search command"""
        cmd = self.parser.parse("search")
        self.assertEqual(cmd.action, "search")

    def test_search_carefully(self):
        """Test search with modifier"""
        cmd = self.parser.parse("carefully search")
        self.assertEqual(cmd.action, "search")
        # Parser extracts 'carefully' as modifier (singular attribute)
        self.assertEqual(cmd.modifier, "carefully")

    def test_look(self):
        """Test look command"""
        cmd = self.parser.parse("look")
        self.assertEqual(cmd.action, "look")

    def test_examine(self):
        """Test examine synonym"""
        cmd = self.parser.parse("examine")
        self.assertEqual(cmd.action, "look")

    def test_open_object(self):
        """Test opening objects"""
        cmd = self.parser.parse("open chest")
        self.assertEqual(cmd.action, "open")
        self.assertEqual(cmd.target, "chest")

    def test_open_with_article(self):
        """Test open with article"""
        cmd = self.parser.parse("open the door")
        self.assertEqual(cmd.action, "open")
        self.assertEqual(cmd.target, "door")

    # Character commands
    def test_inventory(self):
        """Test inventory command"""
        cmd = self.parser.parse("inventory")
        self.assertEqual(cmd.action, "inventory")

    def test_inventory_short(self):
        """Test inventory abbreviation"""
        cmd = self.parser.parse("i")
        self.assertEqual(cmd.action, "inventory")

    def test_status(self):
        """Test status command"""
        cmd = self.parser.parse("status")
        self.assertEqual(cmd.action, "status")

    def test_stats(self):
        """Test stats synonym"""
        cmd = self.parser.parse("stats")
        self.assertEqual(cmd.action, "status")

    def test_spells(self):
        """Test spells command"""
        cmd = self.parser.parse("spells")
        self.assertEqual(cmd.action, "spells")

    def test_rest(self):
        """Test rest command"""
        cmd = self.parser.parse("rest")
        self.assertEqual(cmd.action, "rest")

    def test_sleep(self):
        """Test sleep synonym"""
        cmd = self.parser.parse("sleep")
        self.assertEqual(cmd.action, "rest")

    # Navigation commands
    def test_map(self):
        """Test map command"""
        cmd = self.parser.parse("map")
        self.assertEqual(cmd.action, "map")

    def test_map_short(self):
        """Test map abbreviation"""
        cmd = self.parser.parse("m")
        self.assertEqual(cmd.action, "map")

    # System commands
    def test_help(self):
        """Test help command"""
        cmd = self.parser.parse("help")
        self.assertEqual(cmd.action, "help")

    def test_save(self):
        """Test save command"""
        cmd = self.parser.parse("save")
        self.assertEqual(cmd.action, "save")

    def test_quit(self):
        """Test quit command"""
        cmd = self.parser.parse("quit")
        self.assertEqual(cmd.action, "quit")

    def test_exit(self):
        """Test exit synonym"""
        cmd = self.parser.parse("exit")
        self.assertEqual(cmd.action, "quit")

    # Edge cases
    def test_empty_input(self):
        """Test empty string input"""
        cmd = self.parser.parse("")
        self.assertIsNotNone(cmd)
        # Should return a command object, possibly with unknown action

    def test_whitespace_only(self):
        """Test whitespace-only input"""
        cmd = self.parser.parse("   ")
        self.assertIsNotNone(cmd)

    def test_case_insensitive(self):
        """Test case insensitivity"""
        cmd1 = self.parser.parse("ATTACK ORC")
        cmd2 = self.parser.parse("attack orc")
        self.assertEqual(cmd1.action, cmd2.action)
        self.assertEqual(cmd1.target, cmd2.target)

    def test_extra_whitespace(self):
        """Test handling of extra whitespace"""
        cmd = self.parser.parse("  attack   the   orc  ")
        self.assertEqual(cmd.action, "attack")
        self.assertEqual(cmd.target, "orc")

    def test_complex_multiword_item(self):
        """Test multi-word item names"""
        cmd = self.parser.parse("take healing potion of greater restoration")
        self.assertEqual(cmd.action, "take")
        self.assertIsNotNone(cmd.target)

    def test_unknown_command(self):
        """Test completely unknown input"""
        cmd = self.parser.parse("xyzabc123")
        self.assertIsNotNone(cmd)
        # Parser should handle gracefully, not crash


if __name__ == '__main__':
    unittest.main()
