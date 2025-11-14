"""
Central game state manager - coordinates all game systems
"""

import json
import random
from typing import Dict, List, Optional
from pathlib import Path

from ..entities.player import PlayerCharacter, Item, Weapon, Armor, LightSource, Spell
from ..entities.monster import Monster
from ..world.dungeon import Dungeon
from ..world.room import Room
from ..world.encounter import EncounterManager, CombatEncounter, TrapEncounter, PuzzleEncounter
from ..engine.combat import CombatResolver, DiceRoller
from ..engine.time_tracker import TimeTracker, RestSystem
from ..systems.magic import MagicSystem
from ..systems.skills import SkillResolver
from ..systems.saving_throws import SavingThrowResolver
from ..engine.parser import Command


class GameData:
    """Holds all loaded game data"""

    def __init__(self):
        self.classes = {}
        self.races = {}
        self.monsters = {}
        self.items = {}
        self.spells = {}

    @classmethod
    def load_all(cls, data_dir: str = "aerthos/data") -> 'GameData':
        """Load all JSON game data"""

        data = cls()

        # Load JSON files
        with open(f"{data_dir}/classes.json") as f:
            data.classes = json.load(f)

        with open(f"{data_dir}/races.json") as f:
            data.races = json.load(f)

        with open(f"{data_dir}/monsters.json") as f:
            data.monsters = json.load(f)

        with open(f"{data_dir}/items.json") as f:
            data.items = json.load(f)

        with open(f"{data_dir}/spells.json") as f:
            data.spells = json.load(f)

        return data


class GameState:
    """Central game state manager"""

    def __init__(self, player: PlayerCharacter, dungeon: Dungeon):
        self.player = player
        self.dungeon = dungeon
        self.current_room = dungeon.get_start_room()
        self.is_active = True

        # Game systems
        self.combat_resolver = CombatResolver()
        self.time_tracker = TimeTracker()
        self.rest_system = RestSystem()
        self.magic_system = MagicSystem()
        self.skill_resolver = SkillResolver()
        self.save_resolver = SavingThrowResolver()
        self.encounter_manager = EncounterManager()

        # Combat state
        self.active_monsters: List[Monster] = []
        self.in_combat = False
        self.current_encounter: Optional[CombatEncounter] = None

        # Game data
        self.game_data: Optional[GameData] = None

    def load_game_data(self, data_dir: str = "aerthos/data"):
        """Load all game data"""
        self.game_data = GameData.load_all(data_dir)

    def execute_command(self, command: Command) -> Dict:
        """
        Execute a parsed command

        Args:
            command: Parsed command

        Returns:
            Dict with results and narrative
        """

        # Route to appropriate handler
        handlers = {
            'move': self._handle_move,
            'attack': self._handle_attack,
            'take': self._handle_take,
            'drop': self._handle_drop,
            'use': self._handle_use,
            'equip': self._handle_equip,
            'cast': self._handle_cast,
            'look': self._handle_look,
            'search': self._handle_search,
            'open': self._handle_open,
            'rest': self._handle_rest,
            'inventory': self._handle_inventory,
            'status': self._handle_status,
            'spells': self._handle_spells,
            'memorize': self._handle_memorize,
            'map': self._handle_map,
            'directions': self._handle_directions,
            'help': self._handle_help,
            'save': self._handle_save,
            'load': self._handle_load,
            'quit': self._handle_quit
        }

        handler = handlers.get(command.action)
        if handler:
            return handler(command)
        else:
            return {'success': False, 'message': "I don't understand that command. Type 'help' for options."}

    def _handle_move(self, command: Command) -> Dict:
        """Handle movement"""

        if self.in_combat:
            return {'success': False, 'message': "You can't flee while in combat!"}

        direction = command.target
        if not direction:
            return {'success': False, 'message': "Move where? (north, south, east, west, up, down)"}

        new_room = self.dungeon.move(self.current_room.id, direction)

        if not new_room:
            return {'success': False, 'message': f"You can't go {direction} from here."}

        # Move successful
        self.current_room = new_room

        # Advance time
        time_messages = self.time_tracker.advance_turn(self.player)

        # Get room description
        room_desc = self.current_room.on_enter(self.player.has_light(), self.player)

        # Check for encounters
        encounter_msg = self._check_encounters('on_enter')

        messages = [room_desc]
        if encounter_msg:
            messages.append(encounter_msg)
        messages.extend(time_messages)

        return {'success': True, 'message': '\n\n'.join(messages)}

    def _handle_attack(self, command: Command) -> Dict:
        """Handle combat"""

        if not self.active_monsters:
            return {'success': False, 'message': "There's nothing to attack here."}

        # Find target
        target_name = command.target if command.target else None

        target = None
        if target_name:
            for monster in self.active_monsters:
                if target_name.lower() in monster.name.lower():
                    target = monster
                    break
        else:
            # Attack first living monster
            target = next((m for m in self.active_monsters if m.is_alive), None)

        if not target or not target.is_alive:
            return {'success': False, 'message': f"There's no {target_name} to attack!"}

        # Player attacks
        weapon = self.player.equipment.weapon

        # Check for weapon restrictions
        weapon_penalty = 0
        if weapon:
            can_use, restriction_msg = self.player.can_use_weapon(weapon)
            if not can_use:
                weapon_penalty = -4  # Severe penalty for using improper weapon
                messages = [f"⚠️  {restriction_msg}"]
                messages.append(f"You struggle with the unfamiliar weapon! (-4 to hit)")
            else:
                messages = []
        else:
            messages = []

        # Temporarily modify THAC0 for weapon restriction penalty
        original_thac0 = self.player.thac0
        if weapon_penalty:
            self.player.thac0 -= weapon_penalty  # Lower THAC0 = worse to-hit

        result = self.combat_resolver.attack_roll(self.player, target, weapon)

        # Restore original THAC0
        if weapon_penalty:
            self.player.thac0 = original_thac0

        messages.append(result['narrative'])

        # Check if target died
        if result['defender_died']:
            self.active_monsters.remove(target)

            # Award XP to party or player
            if hasattr(self, 'party') and self.party:
                living_members = self.party.get_living_members()
                if living_members:
                    xp_per_member = target.xp_value // len(living_members)
                    for member in living_members:
                        level_up_msg = member.gain_xp(xp_per_member)
                        if level_up_msg:
                            messages.append(f"{member.name}: {level_up_msg}")
                    messages.append(f"Party gains {target.xp_value} XP! ({xp_per_member} each)")
                else:
                    # Party wiped out - no XP awarded
                    messages.append(f"The party has fallen! No XP awarded.")
            else:
                level_up_msg = self.player.gain_xp(target.xp_value)
                messages.append(f"You gain {target.xp_value} XP!")
                if level_up_msg:
                    messages.append(level_up_msg)

            # Check if combat over
            if not any(m.is_alive for m in self.active_monsters):
                self.in_combat = False
                messages.append("\n═══ VICTORY ═══")

                # Award boss treasure if this was a boss encounter
                if self.current_encounter and self.current_encounter.is_boss:
                    treasure_msg = self._award_boss_treasure()
                    if treasure_msg:
                        messages.append(treasure_msg)

                self.current_encounter = None  # Clear current encounter
                return {'success': True, 'message': '\n'.join(messages)}

        # Monsters counter-attack
        for monster in self.active_monsters:
            if monster.is_alive:
                monster_result = self.combat_resolver.attack_roll(monster, self.player)
                messages.append(monster_result['narrative'])

                if monster_result['defender_died']:
                    messages.append("\n═══ YOU HAVE DIED ═══")
                    self.is_active = False
                    return {'success': False, 'message': '\n'.join(messages)}

        # Show monster status after combat round
        if self.in_combat and self.active_monsters:
            messages.append(self._format_monster_status())

        # Advance time (combat takes time)
        time_messages = self.time_tracker.advance_turn(self.player)
        messages.extend(time_messages)

        return {'success': True, 'message': '\n'.join(messages)}

    def _handle_take(self, command: Command) -> Dict:
        """Handle taking items"""

        if not command.target:
            return {'success': False, 'message': "Take what?"}

        search_term = command.target

        # Handle "take all" - pick up everything in the room
        if search_term.lower() == 'all':
            if not self.current_room.items:
                return {'success': False, 'message': "There's nothing here to take."}

            taken_items = []
            failed_items = []

            # Try to take each item
            for item_name in list(self.current_room.items):  # Copy list since we'll modify it
                item = self._create_item_from_name(item_name)

                if item:
                    # Check encumbrance
                    if self.player.inventory.current_weight + item.weight <= self.player.inventory.max_weight:
                        self.player.inventory.add_item(item)
                        self.current_room.remove_item(item_name)
                        taken_items.append(item.name)
                    else:
                        failed_items.append(f"{item.name} (too heavy)")
                else:
                    failed_items.append(f"{item_name} (not found in database)")

            messages = []
            if taken_items:
                messages.append(f"You take: {', '.join(taken_items)}")
            if failed_items:
                messages.append(f"Could not take: {', '.join(failed_items)}")

            if not messages:
                return {'success': False, 'message': "Failed to take any items."}

            return {'success': True, 'message': '\n'.join(messages)}

        # Handle single item
        # Find item in room using flexible matching
        item_name = self.current_room.find_item(search_term)

        if not item_name:
            return {'success': False, 'message': f"There's no {search_term} here."}

        # Create item from game data
        item = self._create_item_from_name(item_name)

        if not item:
            return {'success': False, 'message': f"Can't find {item_name} in item database."}

        # Check encumbrance
        if self.player.inventory.current_weight + item.weight > self.player.inventory.max_weight:
            return {'success': False, 'message': f"The {item.name} is too heavy! You're carrying {self.player.inventory.current_weight}/{self.player.inventory.max_weight} lbs."}

        # Add to inventory
        self.player.inventory.add_item(item)
        self.current_room.remove_item(item_name)

        return {'success': True, 'message': f"You take the {item.name}."}

    def _handle_drop(self, command: Command) -> Dict:
        """Handle dropping items"""

        if not command.target:
            return {'success': False, 'message': "Drop what?"}

        item = self.player.inventory.remove_item(command.target)

        if not item:
            return {'success': False, 'message': f"You don't have {command.target}."}

        self.current_room.add_item(item.name)
        return {'success': True, 'message': f"You drop the {item.name}."}

    def _handle_use(self, command: Command) -> Dict:
        """Handle using items"""

        if not command.target:
            return {'success': False, 'message': "Use what?"}

        item = self.player.inventory.get_item(command.target)

        if not item:
            return {'success': False, 'message': f"You don't have {command.target}."}

        # Handle consumables
        if item.item_type == 'consumable':
            if 'healing' in item.properties:
                healing = DiceRoller.roll(item.properties['healing'])
                self.player.heal(healing)
                self.player.inventory.remove_item(item.name)
                return {'success': True, 'message': f"You drink the potion and heal {healing} HP!"}
            elif item.name.lower().find('ration') != -1:
                # Rations should be eaten during rest, not used directly
                return {'success': False, 'message': "Rations are food for resting. Use the 'rest' command to eat and recover."}
            else:
                return {'success': False, 'message': f"You can't use the {item.name} like that."}

        return {'success': False, 'message': f"You can't use the {item.name} like that."}

    def _handle_equip(self, command: Command) -> Dict:
        """Handle equipping items"""

        if not command.target:
            return {'success': False, 'message': "Equip what?"}

        item = self.player.inventory.get_item(command.target)

        if not item:
            return {'success': False, 'message': f"You don't have {command.target}."}

        if isinstance(item, Weapon):
            # Check class weapon restrictions
            can_use, restriction_msg = self.player.can_use_weapon(item)
            if not can_use:
                return {'success': False, 'message': restriction_msg}

            self.player.equip_weapon(item)
            return {'success': True, 'message': f"You equip the {item.name}."}
        elif isinstance(item, Armor):
            self.player.equip_armor(item)
            return {'success': True, 'message': f"You equip the {item.name}."}
        elif isinstance(item, LightSource):
            self.player.equip_light(item)
            return {'success': True, 'message': f"You light the {item.name}."}
        elif item.item_type == 'light_source':
            # Fallback for generic Item objects that are light sources
            # Convert to proper LightSource object
            light = LightSource(name=item.name, weight=item.weight, burn_time_turns=6, light_radius=30)
            self.player.inventory.remove_item(item.name)
            self.player.inventory.add_item(light)
            self.player.equip_light(light)
            return {'success': True, 'message': f"You light the {item.name}."}
        else:
            return {'success': False, 'message': f"You can't equip the {item.name}."}

    def _handle_cast(self, command: Command) -> Dict:
        """Handle casting spells"""

        if not command.target:
            return {'success': False, 'message': "Cast what spell?"}

        # Parse spell name and optional target from command
        # Examples: "cast cure" or "cast cure thorin" or "cast cure light wounds" or "cast magic missile goblin"
        full_command = command.target
        spell_name = full_command
        target_name = None

        # Check if last word is a party member name (for beneficial spells)
        parts = full_command.split()
        if len(parts) > 1 and hasattr(self, 'party') and self.party:
            potential_target = parts[-1]
            # Check if it matches a party member
            for member in self.party.members:
                if potential_target.lower() in member.name.lower():
                    target_name = potential_target
                    spell_name = ' '.join(parts[:-1])
                    break

        # Determine if this is a beneficial spell (healing/buff) or harmful spell
        spell_name_lower = spell_name.lower()
        beneficial_spells = ['cure', 'heal', 'bless', 'protection', 'shield', 'aid']
        is_beneficial = any(keyword in spell_name_lower for keyword in beneficial_spells)

        # Build targets list
        if is_beneficial:
            # Check if a specific party member was targeted
            if target_name and hasattr(self, 'party') and self.party:
                # Find party member by name
                target_char = None
                for member in self.party.members:
                    if target_name.lower() in member.name.lower():
                        target_char = member
                        break
                if target_char:
                    targets = [target_char]
                else:
                    return {'success': False, 'message': f"No party member named '{target_name}' found."}
            else:
                # No specific target, use caster
                targets = [self.player]
        else:
            # Harmful spells target monsters, or caster if no monsters (for non-combat spells)
            if self.active_monsters:
                targets = self.active_monsters
            else:
                targets = [self.player]

        result = self.magic_system.cast_spell(self.player, spell_name, targets)

        messages = [result['narrative']]

        # Check if any monsters died from the spell
        if not is_beneficial and self.active_monsters:
            dead_monsters = [m for m in self.active_monsters if not m.is_alive]
            for monster in dead_monsters:
                self.active_monsters.remove(monster)

                # Award XP to party or player
                if hasattr(self, 'party') and self.party:
                    living_members = self.party.get_living_members()
                    if living_members:
                        xp_per_member = monster.xp_value // len(living_members)
                        for member in living_members:
                            level_up_msg = member.gain_xp(xp_per_member)
                            if level_up_msg:
                                messages.append(f"{member.name}: {level_up_msg}")
                        messages.append(f"Party gains {monster.xp_value} XP! ({xp_per_member} each)")
                    else:
                        # Party wiped out - no XP awarded
                        messages.append(f"The party has fallen! No XP awarded.")
                else:
                    level_up_msg = self.player.gain_xp(monster.xp_value)
                    messages.append(f"You gain {monster.xp_value} XP!")
                    if level_up_msg:
                        messages.append(level_up_msg)

            # Check if combat is over
            if not any(m.is_alive for m in self.active_monsters):
                self.in_combat = False
                messages.append("\n═══ VICTORY ═══")

                # Award boss treasure if applicable
                if self.current_encounter and self.current_encounter.is_boss:
                    treasure_msg = self._award_boss_treasure()
                    if treasure_msg:
                        messages.append(treasure_msg)

                self.current_encounter = None

        # Show monster status after spell if still in combat
        if self.in_combat and self.active_monsters:
            messages.append(self._format_monster_status())

        # Advance time (spell casting takes time)
        time_messages = self.time_tracker.advance_turn(self.player)
        messages.extend(time_messages)

        return {'success': result['success'], 'message': '\n'.join(messages)}

    def _handle_look(self, command: Command) -> Dict:
        """Handle looking around (quick glance, no time cost)"""

        messages = []

        # Show room description
        room_desc = self.current_room.on_enter(self.player.has_light(), self.player)
        messages.append(room_desc)

        # Show obvious items (no searching required)
        if self.current_room.items:
            items_list = ', '.join(self.current_room.items)
            messages.append(f"You see: {items_list}")

        # No time advancement - this is just a quick look
        return {'success': True, 'message': '\n'.join(messages)}

    def _handle_search(self, command: Command) -> Dict:
        """Handle searching (deliberate, time-consuming search for hidden items/traps)"""

        messages = []

        # Check for traps (deliberate searching can trigger them)
        encounter_msg = self._check_encounters('on_search')
        if encounter_msg:
            messages.append(encounter_msg)

        # List items in room
        if self.current_room.items:
            items_list = ', '.join(self.current_room.items)
            messages.append(f"You find: {items_list}")
        else:
            messages.append("You don't find anything interesting.")

        # Advance time (searching takes time)
        time_messages = self.time_tracker.advance_turn(self.player)
        messages.extend(time_messages)

        return {'success': True, 'message': '\n'.join(messages)}

    def _handle_open(self, command: Command) -> Dict:
        """Handle opening locked containers"""

        # Get encounters for this room
        room_encounters = self.dungeon.get_room_encounters(self.current_room.id)

        # Look for puzzle encounters (locked chests)
        locked_chest = None
        encounter_id = None
        for i, enc_data in enumerate(room_encounters):
            if enc_data.get('type') == 'puzzle' and enc_data.get('puzzle_type') == 'locked_chest':
                encounter_id = f"{self.current_room.id}_puzzle_{i}"
                # Check if already completed
                if encounter_id not in self.current_room.encounters_completed:
                    locked_chest = enc_data
                    break

        if not locked_chest:
            # Check if already opened
            if encounter_id and encounter_id in self.current_room.encounters_completed:
                return {'success': False, 'message': "The chest is already open and empty."}
            else:
                return {'success': False, 'message': "There's nothing here to open."}

        # Get difficulty
        difficulty = locked_chest.get('difficulty', 30)

        # Check if player is a thief with lockpicking skills
        if self.player.char_class == 'Thief' and hasattr(self.player, 'thief_skills'):
            # Thief can attempt to pick the lock
            open_locks_skill = self.player.thief_skills.get('open_locks', 0)

            # Roll percentile dice
            roll = DiceRoller.roll('1d100')

            # Adjust roll by difficulty
            success_chance = open_locks_skill - (difficulty - 30)  # Base 30 difficulty = no modifier

            messages = []
            messages.append(f"You carefully examine the lock and work your picks...")
            messages.append(f"[Open Locks: {success_chance}% | Rolled: {roll}]")

            if roll <= success_chance:
                # Success!
                messages.append("\n🔓 Click! The lock opens!")

                # Mark encounter as completed
                self.current_room.encounters_completed.append(encounter_id)

                # Give reward
                reward_id = locked_chest.get('reward')
                if reward_id == 'treasure_chest_1':
                    # Treasure chest reward
                    gold_found = 100 + DiceRoller.roll('3d20')
                    self.player.gold += gold_found
                    messages.append(f"\nInside the chest you find {gold_found} gold pieces!")

                    # Maybe add a random item
                    if DiceRoller.roll('1d6') >= 4:
                        from ..entities.player import Item
                        potion = Item(name="Potion of Healing", item_type="potion", weight=0.5,
                                    properties={'healing': '2d4+2'})
                        self.player.inventory.add_item(potion)
                        messages.append("You also find a Potion of Healing!")

                return {'success': True, 'message': '\n'.join(messages)}
            else:
                # Failed
                messages.append("\n❌ Try as you might, you can't pick the lock. Perhaps with more experience...")
                return {'success': False, 'message': '\n'.join(messages)}
        else:
            # Not a thief
            return {'success': False, 'message': "The chest is locked tight. You'd need a thief's skills to pick this lock."}

    def _handle_rest(self, command: Command) -> Dict:
        """Handle resting"""

        result = self.rest_system.attempt_rest(self.player, self.current_room.is_safe_for_rest)

        # If rest is successful, advance time by 8 hours (48 turns)
        if result['success']:
            messages = [result['narrative']]
            # Advance 48 turns (8 hours)
            for _ in range(48):
                time_messages = self.time_tracker.advance_turn(self.player)
                # Only show final time message, not all 48
                if time_messages and _ == 47:
                    messages.extend(time_messages)
            return {'success': True, 'message': '\n'.join(messages)}

        return {'success': result['success'], 'message': result['narrative']}

    def _handle_inventory(self, command: Command) -> Dict:
        """Show inventory with equipped items marked"""

        if not self.player.inventory.items:
            return {'success': True, 'message': "Your inventory is empty."}

        # Get equipped items for comparison
        equipped_weapon = self.player.equipment.weapon
        equipped_armor = self.player.equipment.armor
        equipped_shield = self.player.equipment.shield
        equipped_light = self.player.equipment.light_source

        # Build item list with equipped markers
        item_lines = []
        for item in self.player.inventory.items:
            marker = ""
            if equipped_weapon and item.name == equipped_weapon.name and id(item) == id(equipped_weapon):
                marker = " [EQUIPPED - WEAPON]"
            elif equipped_armor and item.name == equipped_armor.name and id(item) == id(equipped_armor):
                marker = " [EQUIPPED - ARMOR]"
            elif equipped_shield and item.name == equipped_shield.name and id(item) == id(equipped_shield):
                marker = " [EQUIPPED - SHIELD]"
            elif equipped_light and item.name == equipped_light.name and id(item) == id(equipped_light):
                turns_left = equipped_light.turns_remaining
                marker = f" [EQUIPPED - LIGHT: {turns_left} turns left]"

            item_lines.append(f"  - {item.name} ({item.weight} lbs){marker}")

        items_text = '\n'.join(item_lines)
        weight = self.player.inventory.current_weight
        max_weight = self.player.inventory.max_weight

        msg = f"═══ INVENTORY ═══\n{items_text}\n\nTotal Weight: {weight}/{max_weight} lbs"

        if self.player.inventory.is_encumbered:
            msg += "\n⚠️  You are ENCUMBERED!"

        return {'success': True, 'message': msg}

    def _handle_status(self, command: Command) -> Dict:
        """Show character status"""

        from ..ui.character_sheet import CharacterSheet
        sheet = CharacterSheet.format_character(self.player)
        return {'success': True, 'message': sheet}

    def _handle_spells(self, command: Command) -> Dict:
        """Show known spells and memorized spells"""

        if not self.player.spells_known and not self.player.spells_memorized:
            return {'success': True, 'message': "You don't know any spells."}

        lines = []
        lines.append("═══ SPELLBOOK ═══\n")

        # Show known spells
        if self.player.spells_known:
            lines.append("KNOWN SPELLS:")
            for spell in self.player.spells_known:
                lines.append(f"  {spell.name} (Level {spell.level}): {spell.description}")
            lines.append("")

        # Show memorized spells
        if self.player.spells_memorized:
            lines.append("MEMORIZED SPELLS:")
            for slot in self.player.spells_memorized:
                if slot.spell:
                    status = "USED" if slot.is_used else "READY"
                    lines.append(f"  [{status}] {slot.spell.name}")
                else:
                    lines.append(f"  [EMPTY] Level {slot.level} slot")
            lines.append("")

        return {'success': True, 'message': '\n'.join(lines)}

    def _handle_memorize(self, command: Command) -> Dict:
        """Memorize a spell into an empty slot"""

        if not command.target:
            return {'success': False, 'message': "Memorize what spell? Use: memorize <spell name>"}

        # Find the spell in known spells
        spell_name = command.target
        found_spell = None

        for spell in self.player.spells_known:
            if spell_name.lower() in spell.name.lower():
                found_spell = spell
                break

        if not found_spell:
            return {'success': False, 'message': f"You don't know a spell called '{spell_name}'."}

        # Find an empty slot of the correct level
        empty_slot = None
        for slot in self.player.spells_memorized:
            if slot.level == found_spell.level and slot.spell is None:
                empty_slot = slot
                break

        if not empty_slot:
            return {'success': False, 'message': f"You don't have any empty level {found_spell.level} spell slots!"}

        # Memorize the spell
        empty_slot.spell = found_spell
        empty_slot.is_used = False

        return {'success': True, 'message': f"You memorize {found_spell.name}."}

    def _handle_map(self, command: Command) -> Dict:
        """Show auto-map"""

        from ..world.automap import AutoMap
        automap = AutoMap()
        map_str = automap.generate_map(self.current_room.id, self.dungeon)
        return {'success': True, 'message': map_str}

    def _handle_directions(self, command: Command) -> Dict:
        """Show available directions/exits"""

        if not self.current_room.exits:
            return {'success': True, 'message': "There are no obvious exits from here. You may be trapped!"}

        # Build formatted list of exits
        exits_list = []
        for direction in ['north', 'south', 'east', 'west', 'up', 'down']:
            if direction in self.current_room.exits:
                exits_list.append(direction.capitalize())

        if exits_list:
            msg = "Available exits: " + ", ".join(exits_list)
        else:
            msg = "There are no obvious exits from here."

        return {'success': True, 'message': msg}

    def _handle_help(self, command: Command) -> Dict:
        """Show help"""

        from ..engine.parser import CommandParser
        parser = CommandParser()
        return {'success': True, 'message': parser.get_help_text()}

    def _handle_save(self, command: Command) -> Dict:
        """Save game"""

        from ..ui.save_system import SaveSystem
        save_system = SaveSystem()

        # Show existing saves
        saves = save_system.list_saves()

        print("\n" + "═" * 70)
        print("SAVE GAME")
        print("═" * 70)
        print()

        if saves:
            print("Existing saves:")
            for save in saves:
                print(f"  Slot {save['slot']}: {save['character_name']} - Level {save['level']} {save['class']}")
                if save.get('description'):
                    print(f"    Description: {save['description']}")
                print(f"    Saved: {save['timestamp']}")
            print()

        print("Available slots: 1, 2, 3")
        print("0. Cancel")
        print()

        while True:
            try:
                choice = input("Choose save slot (0-3): ").strip()

                if choice == '0':
                    return {'success': False, 'message': "Save cancelled."}

                slot = int(choice)
                if 1 <= slot <= 3:
                    # Check if slot has existing save
                    slot_occupied = any(s['slot'] == slot for s in saves)

                    if slot_occupied:
                        confirm = input(f"Slot {slot} already has a save. Overwrite? (y/n): ").strip().lower()
                        if confirm not in ['y', 'yes']:
                            continue

                    # Prompt for optional description
                    print()
                    description = input("Save description (optional, press Enter to skip): ").strip()

                    save_system.save_game(self, slot, description)
                    return {'success': True, 'message': f"Game saved to slot {slot}!"}
                else:
                    print("Invalid slot. Please choose 1, 2, or 3.")
            except ValueError:
                print("Please enter a valid number.")
            except KeyboardInterrupt:
                return {'success': False, 'message': "\nSave cancelled."}

    def _handle_load(self, command: Command) -> Dict:
        """Load game"""

        return {'success': False, 'message': "Load not yet implemented. Please restart and load from main menu."}

    def _handle_quit(self, command: Command) -> Dict:
        """Quit game"""

        self.is_active = False
        return {'success': True, 'message': "Thanks for playing Aerthos!"}

    def _check_encounters(self, trigger_type: str) -> Optional[str]:
        """Check for and trigger encounters"""

        # Get encounter data from dungeon
        room_encounter_data = self.dungeon.get_room_encounters(self.current_room.id)

        # Load encounters from room
        encounters = self.encounter_manager.load_room_encounters(
            {'id': self.current_room.id, 'encounters': room_encounter_data}
        )

        # Get triggered encounters
        triggered = self.encounter_manager.get_triggered_encounters(encounters, trigger_type)

        for encounter in triggered:
            # Check if already completed
            if encounter.encounter_id in self.current_room.encounters_completed:
                continue

            if isinstance(encounter, CombatEncounter):
                # Mark as completed so it doesn't trigger again
                self.current_room.encounters_completed.append(encounter.encounter_id)
                return self._start_combat(encounter)

        return None

    def _start_combat(self, encounter: CombatEncounter) -> str:
        """Start a combat encounter"""

        # Create monsters
        self.active_monsters = []
        for monster_id in encounter.monster_ids:
            monster = self._create_monster_from_id(monster_id)
            if monster:
                self.active_monsters.append(monster)

        self.in_combat = True
        self.current_encounter = encounter  # Track current encounter

        monster_names = ', '.join(m.name for m in self.active_monsters)
        return f"\n═══ COMBAT ═══\nYou encounter: {monster_names}!\n{self._format_monster_status()}"

    def _format_monster_status(self) -> str:
        """Format current monster HP/status for display"""
        if not self.active_monsters:
            return ""

        lines = ["\n--- Enemies ---"]
        for i, monster in enumerate(self.active_monsters, 1):
            if monster.is_alive:
                hp_percent = (monster.hp_current / monster.hp_max) * 100
                if hp_percent > 75:
                    status = "Healthy"
                elif hp_percent > 50:
                    status = "Injured"
                elif hp_percent > 25:
                    status = "Badly Wounded"
                else:
                    status = "Near Death"
                lines.append(f"{i}. {monster.name}: {monster.hp_current}/{monster.hp_max} HP ({status})")
            else:
                lines.append(f"{i}. {monster.name}: DEAD")

        return '\n'.join(lines)

    def _award_boss_treasure(self) -> Optional[str]:
        """Award treasure for defeating a boss"""

        # Get treasure data from current room
        if not self.dungeon.room_data or self.current_room.id not in self.dungeon.room_data:
            return None

        room_data = self.dungeon.room_data[self.current_room.id]
        treasure = room_data.get('treasure')

        if not treasure:
            return None

        messages = []
        messages.append("\n💰 The boss's treasure hoard is yours!")

        # Award gold
        gold = treasure.get('gold', 0)
        if gold > 0:
            self.player.gold += gold
            messages.append(f"   Gold: {gold} gp")

        # Award gems (convert to gold value, 10gp each on average)
        gems = treasure.get('gems', 0)
        if gems > 0:
            gem_value = gems * DiceRoller.roll('2d10')  # Random gem value
            self.player.gold += gem_value
            messages.append(f"   Gems: {gems} gems worth {gem_value} gp")

        # Award magic items (add to room items so player can pick them up)
        magic_items = treasure.get('magic_items', [])
        if magic_items:
            messages.append(f"   Magic Items: {', '.join(magic_items)}")
            for item_id in magic_items:
                # Add to room items
                self.current_room.add_item(item_id)

        return '\n'.join(messages)

    def _create_monster_from_id(self, monster_id: str) -> Optional[Monster]:
        """Create a monster instance from monster ID"""

        if not self.game_data:
            print("ERROR: GameData not loaded! Call load_game_data() first.")
            return None

        if monster_id not in self.game_data.monsters:
            print(f"WARNING: Monster '{monster_id}' not found in game data.")
            return None

        data = self.game_data.monsters[monster_id]

        # Roll HP
        hp = DiceRoller.roll(data['hit_dice'])

        monster = Monster(
            name=data['name'],
            race=monster_id,
            char_class='Monster',
            level=1,
            hp_current=hp,
            hp_max=hp,
            ac=data['ac'],
            thac0=data['thac0'],
            size=data['size'],
            hit_dice=data['hit_dice'],
            damage=data['damage'],
            treasure_type=data.get('treasure_type', 'None'),
            xp_value=data['xp_value'],
            movement=data['movement'],
            morale=data['morale'],
            special_abilities=data.get('special_abilities', []),
            ai_behavior=data.get('ai_behavior', 'aggressive'),
            description=data['description']
        )

        return monster

    def _create_item_from_name(self, item_name: str) -> Optional[Item]:
        """Create an item instance from name"""

        if not self.game_data:
            print("ERROR: GameData not loaded! Call load_game_data() first.")
            return None

        # Find item in database
        item_data = None
        item_key = None

        search_lower = item_name.lower().replace('_', ' ')

        # Try exact match on key first
        if item_name in self.game_data.items:
            item_data = self.game_data.items[item_name]
            item_key = item_name
        else:
            # Try matching on display name or key with flexible matching
            for key, data in self.game_data.items.items():
                key_normalized = key.lower().replace('_', ' ')
                name_normalized = data['name'].lower()

                if (key_normalized == search_lower or
                    name_normalized == search_lower or
                    search_lower in key_normalized or
                    search_lower in name_normalized):
                    item_data = data
                    item_key = key
                    break

        if not item_data:
            return None

        # Create appropriate item type
        if item_data['type'] == 'weapon':
            return Weapon(
                name=item_data['name'],
                weight=item_data['weight'],
                damage_sm=item_data['damage_sm'],
                damage_l=item_data['damage_l'],
                speed_factor=item_data['speed_factor'],
                magic_bonus=item_data.get('magic_bonus', 0),
                properties={'cost_gp': item_data.get('cost_gp', 0)},
                description=item_data.get('description', '')
            )
        elif item_data['type'] == 'armor':
            return Armor(
                name=item_data['name'],
                weight=item_data['weight'],
                ac_bonus=item_data['ac_bonus'],
                magic_bonus=item_data.get('magic_bonus', 0),
                properties={'cost_gp': item_data.get('cost_gp', 0)},
                description=item_data.get('description', '')
            )
        elif item_data['type'] == 'light_source':
            return LightSource(
                name=item_data['name'],
                weight=item_data['weight'],
                burn_time_turns=item_data['burn_time_turns'],
                light_radius=item_data['light_radius'],
                properties={'cost_gp': item_data.get('cost_gp', 0)},
                description=item_data.get('description', '')
            )
        else:
            return Item(
                name=item_data['name'],
                item_type=item_data['type'],
                weight=item_data['weight'],
                properties=item_data,
                description=item_data.get('description', '')
            )
