"""
Central game state manager - coordinates all game systems
"""

import json
import random
from typing import Dict, List, Optional, Union
from pathlib import Path

from ..entities.player import PlayerCharacter, Item, Weapon, Armor, Shield, LightSource, Spell
from ..entities.monster import Monster
from ..world.dungeon import Dungeon
from ..world.multilevel_dungeon import MultiLevelDungeon
from ..world.room import Room
from ..world.encounter import EncounterManager, CombatEncounter, TrapEncounter, PuzzleEncounter
from ..engine.combat import CombatResolver, DiceRoller
from ..engine.time_tracker import TimeTracker, RestSystem
from ..systems.magic import MagicSystem
from ..systems.skills import SkillResolver
from ..systems.saving_throws import SavingThrowResolver
from ..systems.monster_abilities import MonsterSpecialAbilities
from ..systems.narrator import DMNarrator, NarrativeContext
from ..engine.parser import Command


class GameData:
    """Holds all loaded game data"""

    def __init__(self):
        self.classes = {}
        self.races = {}
        self.monsters = {}
        # Note: items.json is deprecated - use specialized systems:
        # - ArmorSystem for armor.json
        # - Weapon system for weapons.json
        # - Equipment system for equipment.json
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

        # Note: items.json is deprecated - use specific databases:
        # - armor.json (via ArmorSystem)
        # - weapons.json (via weapon system)
        # - equipment.json (for general equipment)

        with open(f"{data_dir}/spells.json") as f:
            data.spells = json.load(f)

        return data


class GameState:
    """Central game state manager"""

    def __init__(self, player: PlayerCharacter, dungeon: Union[Dungeon, MultiLevelDungeon]):
        self.player = player
        self.dungeon = dungeon

        # Multi-level support
        self.is_multilevel = isinstance(dungeon, MultiLevelDungeon)
        self.current_level = 1 if self.is_multilevel else 0  # 0 for single-level

        # Get starting room
        if self.is_multilevel:
            current_dungeon = dungeon.get_current_dungeon()
            self.current_room = current_dungeon.get_start_room() if current_dungeon else None
        else:
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
        self.monster_abilities = MonsterSpecialAbilities()
        self.narrator = DMNarrator()

        # Combat state
        self.active_monsters: List[Monster] = []
        self.in_combat = False
        self.current_encounter: Optional[CombatEncounter] = None

        # Game data
        self.game_data: Optional[GameData] = None

    def load_game_data(self, data_dir: str = "aerthos/data") -> None:
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
            'defend': self._handle_defend,
            'wait': self._handle_wait,
            'take': self._handle_take,
            'drop': self._handle_drop,
            'use': self._handle_use,
            'equip': self._handle_equip,
            'unequip': self._handle_unequip,
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
            'formation': self._handle_formation,
            'stairs_up': self._handle_stairs_up,
            'stairs_down': self._handle_stairs_down,
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
        """Handle movement (both horizontal and stairs)"""

        if self.in_combat:
            return {'success': False, 'message': "You can't flee while in combat!"}

        direction = command.target
        if not direction:
            return {'success': False, 'message': "Move where? (north, south, east, west, up, down)"}

        # Handle multi-level vs single-level dungeons
        if self.is_multilevel:
            # MultiLevelDungeon.move() returns (room, level, error_msg)
            result = self.dungeon.move(self.current_room.id, direction)
            new_room, new_level, error_msg = result

            if not new_room:
                msg = error_msg if error_msg else f"You can't go {direction} from here."
                return {'success': False, 'message': msg}

            # Update room and level
            self.current_room = new_room
            self.current_level = new_level

            # Check if we changed levels (for stair movement)
            level_change_msg = None
            if direction in ['up', 'u', 'stairs_up']:
                level_change_msg = f"You ascend the stairs to Level {new_level}.\n"
            elif direction in ['down', 'd', 'stairs_down']:
                level_change_msg = f"You descend the stairs to Level {new_level}.\n"

        else:
            # Regular Dungeon.move() returns Optional[Room]
            new_room = self.dungeon.move(self.current_room.id, direction)

            if not new_room:
                return {'success': False, 'message': f"You can't go {direction} from here."}

            # Move successful
            self.current_room = new_room
            level_change_msg = None

        # Advance time
        time_messages = self.time_tracker.advance_turn(self.player)

        # Get room description
        room_desc = self.current_room.on_enter(self.player.has_light(), self.player)

        # Check for encounters
        encounter_msg = self._check_encounters('on_enter')

        messages = []
        if level_change_msg:
            messages.append(level_change_msg)
        messages.append(room_desc)
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
                # Check if monster has special abilities and randomly uses them (30% chance)
                used_special = False
                if hasattr(monster, 'special_abilities') and monster.special_abilities:
                    if random.random() < 0.3:  # 30% chance to use special ability
                        ability = random.choice(monster.special_abilities)
                        try:
                            ability_result = self.monster_abilities.use_ability(
                                monster, ability, [self.player]
                            )
                            messages.append(ability_result.message)

                            # Apply damage if any
                            if ability_result.damage > 0:
                                # Check for saving throw
                                if ability_result.save_allowed:
                                    save_result = self.save_resolver.make_save(
                                        self.player,
                                        ability_result.save_type
                                    )
                                    if save_result['success']:
                                        # Save for half damage
                                        damage = ability_result.damage // 2
                                        messages.append(f"{self.player.name} makes their save! Damage reduced to {damage}.")
                                    else:
                                        damage = ability_result.damage
                                        messages.append(f"{self.player.name} fails their save!")
                                else:
                                    damage = ability_result.damage

                                died = self.player.take_damage(damage)
                                if died:
                                    messages.append("\n═══ YOU HAVE DIED ═══")
                                    self.is_active = False
                                    return {'success': False, 'message': '\n'.join(messages)}

                            used_special = True
                        except Exception:
                            # If special ability fails, fall back to normal attack
                            pass

                # Normal attack if no special ability used
                if not used_special:
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

    def _handle_defend(self, command: Command) -> Dict:
        """Handle defensive stance in combat - applies to active character only"""

        if not self.in_combat:
            return {'success': False, 'message': "You're not in combat."}

        messages = [f"{self.player.name} takes a defensive stance, focusing on blocking incoming attacks."]

        # Apply defensive bonus (improve AC temporarily for this round)
        # In AD&D 1e, defending gives -2 AC bonus (better AC)
        original_ac = self.player.ac
        improved_ac = self.player.ac - 2  # Temporary AC improvement
        self.player.ac = improved_ac
        messages.append(f"{self.player.name}'s AC improves from {original_ac} to {improved_ac} for this round.")

        # Monsters attack
        for monster in self.active_monsters:
            if monster.is_alive:
                monster_result = self.combat_resolver.attack_roll(monster, self.player)
                messages.append(monster_result['narrative'])

                if monster_result['defender_died']:
                    messages.append("\n═══ YOU HAVE DIED ═══")
                    self.is_active = False
                    self.player.ac = original_ac  # Restore AC
                    return {'success': False, 'message': '\n'.join(messages)}

        # Restore original AC after the round
        self.player.ac = original_ac

        # Show monster status
        if self.in_combat and self.active_monsters:
            messages.append(self._format_monster_status())

        # Advance time
        time_messages = self.time_tracker.advance_turn(self.player)
        messages.extend(time_messages)

        return {'success': True, 'message': '\n'.join(messages)}

    def _handle_wait(self, command: Command) -> Dict:
        """Handle passing turn / waiting"""

        if not self.in_combat:
            # Out of combat, just pass time
            messages = ["You wait and observe your surroundings."]
            time_messages = self.time_tracker.advance_turn(self.player)
            messages.extend(time_messages)
            return {'success': True, 'message': '\n'.join(messages)}

        # In combat, skip turn but monsters still attack
        messages = ["You hold your action and wait."]

        # Monsters attack
        for monster in self.active_monsters:
            if monster.is_alive:
                monster_result = self.combat_resolver.attack_roll(monster, self.player)
                messages.append(monster_result['narrative'])

                if monster_result['defender_died']:
                    messages.append("\n═══ YOU HAVE DIED ═══")
                    self.is_active = False
                    return {'success': False, 'message': '\n'.join(messages)}

        # Show monster status
        if self.in_combat and self.active_monsters:
            messages.append(self._format_monster_status())

        # Advance time
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
            self.player.equipment.armor = item
            # Recalculate AC based on armor and shield
            self.player.ac = item.ac
            if self.player.equipment.shield:
                self.player.ac -= self.player.equipment.shield.ac_bonus
            return {'success': True, 'message': f"You equip the {item.name}."}
        elif isinstance(item, Shield):
            self.player.equipment.shield = item
            # Recalculate AC
            if self.player.equipment.armor:
                self.player.ac = self.player.equipment.armor.ac - item.ac_bonus
            else:
                self.player.ac = 10 - item.ac_bonus
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

    def _handle_unequip(self, command: Command) -> Dict:
        """Handle unequipping items - removes from equipment and adds back to inventory"""

        if not command.target:
            return {'success': False, 'message': "Unequip what?"}

        # Check what's equipped and try to match
        target_lower = command.target.lower()

        # Check weapon
        if self.player.equipment.weapon and target_lower in self.player.equipment.weapon.name.lower():
            weapon = self.player.equipment.weapon
            self.player.equipment.weapon = None
            # Add back to inventory (it's already there, just not equipped)
            # Note: Equipped items stay in inventory in AD&D 1e
            return {'success': True, 'message': f"You unequip the {weapon.name}."}

        # Check armor
        if self.player.equipment.armor and target_lower in self.player.equipment.armor.name.lower():
            armor = self.player.equipment.armor
            self.player.equipment.armor = None
            # Recalculate AC
            self.player.ac = 10  # Base AC
            if self.player.equipment.shield:
                self.player.ac -= self.player.equipment.shield.ac_bonus
            return {'success': True, 'message': f"You remove the {armor.name}."}

        # Check shield
        if self.player.equipment.shield and target_lower in self.player.equipment.shield.name.lower():
            shield = self.player.equipment.shield
            self.player.equipment.shield = None
            # Recalculate AC
            if self.player.equipment.armor:
                self.player.ac = self.player.equipment.armor.ac
            else:
                self.player.ac = 10
            return {'success': True, 'message': f"You unequip the {shield.name}."}

        # Check light source
        if self.player.equipment.light_source and target_lower in self.player.equipment.light_source.name.lower():
            light = self.player.equipment.light_source
            self.player.equipment.light_source = None
            return {'success': True, 'message': f"You extinguish the {light.name}."}

        return {'success': False, 'message': f"You don't have {command.target} equipped."}

    def _handle_cast(self, command: Command) -> Dict:
        """Handle casting spells"""

        if not command.target:
            return {'success': False, 'message': "Cast what spell?"}

        # Parse spell name and optional target from command
        # Examples: "cast cure" or "cast cure thorin" or "cast cure light wounds on thorin" or "cast magic missile goblin"
        full_command = command.target
        spell_name = full_command
        target_name = None

        # Check for prepositions that separate spell from target
        # This is more reliable than just checking the last word
        prepositions = [' on ', ' at ', ' to ']
        for prep in prepositions:
            if prep in full_command.lower():
                parts = full_command.lower().split(prep, 1)
                spell_name = parts[0].strip()
                target_name = parts[1].strip() if len(parts) > 1 else None
                break

        # If no preposition found, check if last word is a party member name (for beneficial spells)
        if not target_name:
            parts = full_command.split()
            if len(parts) > 1 and hasattr(self, 'party') and self.party:
                potential_target = parts[-1]
                # Check if it matches a party member - but be careful not to match spell words
                # Only match if the name is reasonably unique (at least 3 chars and not a common spell word)
                if len(potential_target) >= 3:
                    spell_words = ['cure', 'light', 'wounds', 'magic', 'missile', 'protection', 'evil', 'bless']
                    if potential_target.lower() not in spell_words:
                        for member in self.party.members:
                            if potential_target.lower() in member.name.lower():
                                target_name = potential_target
                                spell_name = ' '.join(parts[:-1])
                                break

        # Determine if this is a beneficial spell (healing/buff) or harmful spell
        # Support abbreviated spell names (e.g., "c" for "cure")
        spell_name_lower = spell_name.lower()
        beneficial_spells = ['cure', 'heal', 'bless', 'protection', 'shield', 'aid']

        # Check both directions: "cure" in "cure light wounds" OR "c" in "cure"
        is_beneficial = any(
            keyword in spell_name_lower or spell_name_lower in keyword
            for keyword in beneficial_spells
        )

        # Build targets list
        if is_beneficial:
            # Beneficial spells should ONLY target party members (or caster if no target specified)
            # They should NEVER target monsters, even in combat
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
                # No specific target, use caster (self.player is the active character who is casting)
                targets = [self.player]
        else:
            # Harmful spells target monsters
            if not self.active_monsters:
                return {'success': False, 'message': "There are no enemies to target!"}

            # If specific target specified, find it by name
            if target_name:
                target_char = None
                for monster in self.active_monsters:
                    if target_name.lower() in monster.name.lower():
                        target_char = monster
                        break

                if target_char:
                    targets = [target_char]
                else:
                    return {'success': False, 'message': f"No enemy named '{target_name}' found."}
            else:
                # No specific target, use all monsters for area spells or first for single-target
                # The spell handler will decide if it's area-effect or single-target
                targets = self.active_monsters

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

    def _handle_formation(self, command: Command) -> Dict:
        """Handle formation commands (party-based gameplay)"""

        # Check if party object exists
        if not hasattr(self, 'party') or self.party is None:
            return {
                'success': False,
                'message': "Formation commands are only available in party-based gameplay."
            }

        from ..entities.party import Party

        # Ensure we have a Party object
        if not isinstance(self.party, Party):
            return {
                'success': False,
                'message': "Formation commands are only available in party-based gameplay."
            }

        # Parse formation command variations
        # "formation" - show current formation
        # "formation <name> front" - move character to front
        # "formation <name> back" - move character to back
        # "formation default" - auto-assign by class

        if not command.target:
            # Show current formation
            from ..ui.character_sheet import CharacterSheet
            roster = CharacterSheet.format_party_roster(self.party)
            return {'success': True, 'message': roster}

        target_lower = command.target.lower()

        # Handle "formation default"
        if target_lower == 'default':
            # Auto-assign formation based on class
            for i, member in enumerate(self.party.members):
                # Fighters and Clerics in front, Magic-Users and Thieves in back
                if member.char_class in ['Fighter', 'Cleric', 'Dwarf']:
                    self.party.formation[i] = 'front'
                else:  # Magic-User, Thief, Elf, Halfling
                    self.party.formation[i] = 'back'

            from ..ui.character_sheet import CharacterSheet
            roster = CharacterSheet.format_party_roster(self.party)
            return {
                'success': True,
                'message': "Formation reset to default positions.\n\n" + roster
            }

        # Handle "formation <name> <position>"
        # Parse target to extract name and position
        parts = target_lower.split()

        if len(parts) < 2:
            return {
                'success': False,
                'message': "Usage: formation <character name> <front|back>"
            }

        # Last word should be position, everything else is name
        position = parts[-1]
        name = ' '.join(parts[:-1])

        if position not in ['front', 'back']:
            return {
                'success': False,
                'message': "Position must be 'front' or 'back'."
            }

        # Find character by name (case-insensitive)
        member_index = None
        for i, member in enumerate(self.party.members):
            if member.name.lower() == name:
                member_index = i
                break

        if member_index is None:
            return {
                'success': False,
                'message': f"No party member named '{name}' found."
            }

        # Update formation
        self.party.formation[member_index] = position
        member_name = self.party.members[member_index].name

        return {
            'success': True,
            'message': f"{member_name} moved to {position} line."
        }

    def _handle_stairs_up(self, command: Command) -> Dict:
        """Handle ascending stairs to previous dungeon level"""

        if self.in_combat:
            return {'success': False, 'message': "You can't use stairs while in combat!"}

        if not self.is_multilevel:
            return {'success': False, 'message': "There are no stairs here. This dungeon has only one level."}

        # MultiLevelDungeon.move() handles stairs and returns (new_room, new_level_number, message)
        new_room, new_level, error_msg = self.dungeon.move(self.current_room.id, "stairs_up")

        if not new_room:
            # Move failed - either no stairs or at top level
            msg = error_msg if error_msg else "You can't go up from here."
            return {'success': False, 'message': msg}

        # Move successful - update room and level
        self.current_room = new_room
        self.current_level = new_level

        # Advance time
        time_messages = self.time_tracker.advance_turn(self.player)

        # Get room description
        room_desc = self.current_room.on_enter(self.player.has_light(), self.player)

        # Check for encounters
        encounter_msg = self._check_encounters('on_enter')

        messages = [f"You ascend the stairs to Level {new_level}.\n", room_desc]
        if encounter_msg:
            messages.append(encounter_msg)
        messages.extend(time_messages)

        return {'success': True, 'message': '\n\n'.join(messages)}

    def _handle_stairs_down(self, command: Command) -> Dict:
        """Handle descending stairs to next dungeon level"""

        if self.in_combat:
            return {'success': False, 'message': "You can't use stairs while in combat!"}

        if not self.is_multilevel:
            return {'success': False, 'message': "There are no stairs here. This dungeon has only one level."}

        # MultiLevelDungeon.move() handles stairs and returns (new_room, new_level_number, message)
        new_room, new_level, error_msg = self.dungeon.move(self.current_room.id, "stairs_down")

        if not new_room:
            # Move failed - either no stairs or at bottom level
            msg = error_msg if error_msg else "You can't go down from here."
            return {'success': False, 'message': msg}

        # Move successful - update room and level
        self.current_room = new_room
        self.current_level = new_level

        # Advance time
        time_messages = self.time_tracker.advance_turn(self.player)

        # Get room description
        room_desc = self.current_room.on_enter(self.player.has_light(), self.player)

        # Check for encounters
        encounter_msg = self._check_encounters('on_enter')

        messages = [f"You descend the stairs to Level {new_level}.\n", room_desc]
        if encounter_msg:
            messages.append(encounter_msg)
        messages.extend(time_messages)

        return {'success': True, 'message': '\n\n'.join(messages)}

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
        """
        Create an item instance from name

        Note: Simple item factory for common dungeon loot.
        For complex items, use specialized systems (ArmorSystem, etc.)
        """

        # Normalize name for matching
        search_lower = item_name.lower().replace('_', ' ')

        # Common item templates (name patterns -> item creation)
        # Weights are in pounds (10 GP = 1 lb)

        # Torches
        if 'torch' in search_lower:
            return LightSource(
                name="Torch",
                weight=0.1,  # 1 GP
                burn_time_turns=6,
                light_radius=30,
                description="A wooden stick wrapped in oil-soaked cloth."
            )

        # Rations
        if 'ration' in search_lower or 'food' in search_lower:
            return Item(
                name="Rations (1 day)",
                item_type="consumable",
                weight=0.1,  # 1 GP
                properties={'healing': '0'},
                description="Preserved food for one day."
            )

        # Healing potions
        if 'potion' in search_lower and 'heal' in search_lower:
            return Item(
                name="Potion of Healing",
                item_type="consumable",
                weight=0.05,  # 0.5 GP
                properties={'healing': '2d4+2'},
                description="A red liquid that heals 2d4+2 hit points."
            )

        # Gold/coins
        if 'gold' in search_lower or 'coin' in search_lower or 'gp' in search_lower:
            return Item(
                name="Gold Coins",
                item_type="treasure",
                weight=0.1,  # 10 coins = 1 lb
                properties={'value_gp': 10},
                description="A handful of gold coins."
            )

        # Generic treasure
        if 'gem' in search_lower or 'jewel' in search_lower:
            return Item(
                name="Gem",
                item_type="treasure",
                weight=0.01,
                properties={'value_gp': 50},
                description="A precious gemstone."
            )

        # Rope
        if 'rope' in search_lower:
            return Item(
                name="Rope (50 ft)",
                item_type="equipment",
                weight=0.5,  # 5 GP
                description="50 feet of sturdy hemp rope."
            )

        # Backpack
        if 'backpack' in search_lower or 'pack' in search_lower:
            return Item(
                name="Backpack",
                item_type="container",
                weight=2.0,  # 20 GP
                properties={'capacity_gp': 400},
                description="A leather backpack with straps."
            )

        # Default: create generic item
        return Item(
            name=item_name,
            item_type="treasure",
            weight=0.1,
            description=f"A {item_name}."
        )
