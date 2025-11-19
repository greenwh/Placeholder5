"""
Experience Point and Leveling System - AD&D 1e
Handles XP tracking, level advancement, and all progression mechanics
"""

import json
import random
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


class ExperienceSystem:
    """Manages XP tracking and level advancement"""

    def __init__(self):
        """Load level progression data"""
        data_path = Path(__file__).parent.parent / 'data' / 'level_progression.json'
        with open(data_path, 'r') as f:
            self.progression = json.load(f)

    def get_xp_for_level(self, char_class: str, level: int) -> int:
        """Get XP required for a specific level"""
        if char_class not in self.progression:
            return 0

        xp_table = self.progression[char_class]['xp_table']

        # Level 1 is index 0
        if level <= len(xp_table):
            return xp_table[level - 1]

        # Beyond the table, calculate
        xp_per_level = self.progression[char_class]['xp_per_level_after_max']
        last_xp = xp_table[-1]
        additional_levels = level - len(xp_table)
        return last_xp + (xp_per_level * additional_levels)

    def get_level_from_xp(self, char_class: str, xp: int) -> int:
        """Determine level based on current XP"""
        if char_class not in self.progression:
            return 1

        xp_table = self.progression[char_class]['xp_table']

        # Check table first
        for level in range(len(xp_table) - 1, -1, -1):
            if xp >= xp_table[level]:
                return level + 1

        # Shouldn't happen, but return 1 if no match
        return 1

    def can_level_up(self, char_class: str, current_level: int, current_xp: int) -> bool:
        """Check if character has enough XP to level up"""
        xp_needed = self.get_xp_for_level(char_class, current_level + 1)
        return current_xp >= xp_needed

    def get_thac0(self, char_class: str, level: int) -> int:
        """Get THAC0 for class and level"""
        if char_class not in self.progression:
            return 20

        thac0_table = self.progression[char_class]['thac0_table']
        if level <= len(thac0_table):
            return thac0_table[level - 1]

        # If beyond table, return last value
        return thac0_table[-1]

    def get_level_title(self, char_class: str, level: int) -> str:
        """Get the title for this class and level"""
        if char_class not in self.progression:
            return "Adventurer"

        titles = self.progression[char_class]['level_titles']
        if level <= len(titles):
            return titles[level - 1]

        # Beyond defined titles
        return f"{titles[-1]} ({level}th level)"

    def get_spell_slots(self, char_class: str, level: int) -> Dict[int, int]:
        """Get spell slots by level for this class and level"""
        if char_class not in self.progression:
            return {}

        if 'spell_slots' not in self.progression[char_class]:
            return {}

        slots = {}
        spell_data = self.progression[char_class]['spell_slots']

        for spell_level, slot_list in spell_data.items():
            spell_level_int = int(spell_level)
            if level <= len(slot_list):
                slots[spell_level_int] = slot_list[level - 1]
            else:
                slots[spell_level_int] = slot_list[-1]

        return slots

    def get_attacks_per_round(self, char_class: str, level: int) -> float:
        """Get number of attacks per round (can be 1, 1.5, or 2)"""
        if char_class not in self.progression:
            return 1.0

        attack_data = self.progression[char_class]['attacks_per_round']

        for level_range, attacks in attack_data.items():
            if '-' in level_range:
                low, high = map(int, level_range.split('-'))
                if low <= level <= high:
                    return attacks
            else:
                if level == int(level_range):
                    return attacks

        return 1.0

    def get_backstab_multiplier(self, char_class: str, level: int) -> int:
        """Get backstab damage multiplier for thieves/assassins"""
        if char_class not in self.progression:
            return 1

        if 'backstab_multiplier' not in self.progression[char_class]:
            return 1

        multiplier_data = self.progression[char_class]['backstab_multiplier']

        for level_range, multiplier in multiplier_data.items():
            low, high = map(int, level_range.split('-'))
            if low <= level <= high:
                return multiplier

        return 1

    def roll_hp_for_level(self, char_class: str, level: int, constitution_mod: int) -> int:
        """
        Roll HP for a new level
        Returns HP gained (including CON modifier)
        """
        if char_class not in self.progression:
            return 1

        hit_die = self.progression[char_class]['hit_die']
        max_hd_level = self.progression[char_class]['max_hd_level']
        hp_after_max = self.progression[char_class]['hp_after_max']

        # Determine die type
        die_size = int(hit_die[1:])  # "d10" -> 10

        # Before max HD level: roll the die
        if level <= max_hd_level:
            roll = random.randint(1, die_size)
            # Add CON modifier (minimum 1 HP per level)
            return max(1, roll + constitution_mod)
        else:
            # After max HD level: fixed bonus (no CON mod for most classes after max HD)
            return hp_after_max

    def calculate_xp_award(self, monster_hd: float, treasure_gp: int, special_bonus: int = 0) -> int:
        """
        Calculate XP award for encounter

        Args:
            monster_hd: Hit dice of defeated monsters
            treasure_gp: Gold piece value of treasure
            special_bonus: Additional XP for clever solutions, roleplaying, etc.

        Returns:
            Total XP earned
        """
        # Simplified XP calculation
        # In AD&D 1e, XP for monsters depends on HD and special abilities
        # For now, use simplified: 100 XP per HD
        monster_xp = int(monster_hd * 100)

        # Treasure is 1 XP per 1 GP
        treasure_xp = treasure_gp

        return monster_xp + treasure_xp + special_bonus

    def apply_xp_bonus(self, base_xp: int, bonus_percentage: int) -> int:
        """Apply prime requisite XP bonus"""
        if bonus_percentage <= 0:
            return base_xp

        bonus = int(base_xp * (bonus_percentage / 100.0))
        return base_xp + bonus

    def level_up_character(self, character, ability_system) -> Dict[str, Any]:
        """
        Level up a character

        Args:
            character: The character object to level up
            ability_system: AbilityScoreSystem instance for looking up modifiers

        Returns:
            Dictionary with level up results
        """
        old_level = character.level
        new_level = old_level + 1

        # Check if can level up
        if not self.can_level_up(character.char_class, old_level, character.xp):
            return {
                'success': False,
                'message': f"Not enough XP to reach level {new_level}. Need {self.get_xp_for_level(character.char_class, new_level)} XP."
            }

        # Update level
        character.level = new_level

        # Roll HP
        is_fighter_class = character.char_class in ['Fighter', 'Ranger', 'Paladin']
        con_mod = ability_system.get_hp_adjustment(character.constitution, is_fighter_class)
        hp_gained = self.roll_hp_for_level(character.char_class, new_level, con_mod)
        character.hp_max += hp_gained
        character.hp_current += hp_gained  # Full heal on level up

        # Update THAC0
        new_thac0 = self.get_thac0(character.char_class, new_level)
        character.thac0 = new_thac0

        # Update title
        character.title = self.get_level_title(character.char_class, new_level)

        # Update spell slots if applicable
        if hasattr(character, 'spell_slots'):
            character.spell_slots = self.get_spell_slots(character.char_class, new_level)

            # Apply wisdom bonus spells for clerics
            if character.char_class in ['Cleric', 'Druid'] and hasattr(character, 'wisdom'):
                bonus_spells = ability_system.get_bonus_spells(character.wisdom)
                for spell_level, bonus_count in bonus_spells.items():
                    spell_level_int = int(spell_level)
                    if spell_level_int in character.spell_slots:
                        character.spell_slots[spell_level_int] += bonus_count

        # Update saving throws (will be handled by saving throw system)
        # This is a placeholder - full implementation in saving_throws.py

        # Special ability checks
        special_abilities_gained = []

        # Monk AC improvement
        if character.char_class == 'Monk' and 'ac_progression' in self.progression['Monk']:
            ac_table = self.progression['Monk']['ac_progression']
            if str(new_level) in ac_table:
                character.ac = ac_table[str(new_level)]
                special_abilities_gained.append(f"AC improved to {character.ac}")

        # Backstab multiplier
        if character.char_class in ['Thief', 'Assassin']:
            new_multiplier = self.get_backstab_multiplier(character.char_class, new_level)
            old_multiplier = self.get_backstab_multiplier(character.char_class, old_level)
            if new_multiplier > old_multiplier:
                special_abilities_gained.append(f"Backstab multiplier increased to x{new_multiplier}")

        # Fighter multiple attacks
        if character.char_class in ['Fighter', 'Ranger', 'Paladin', 'Monk']:
            new_attacks = self.get_attacks_per_round(character.char_class, new_level)
            old_attacks = self.get_attacks_per_round(character.char_class, old_level)
            if new_attacks > old_attacks:
                special_abilities_gained.append(f"Attacks per round increased to {new_attacks}")

        return {
            'success': True,
            'old_level': old_level,
            'new_level': new_level,
            'hp_gained': hp_gained,
            'new_hp_max': character.hp_max,
            'new_thac0': new_thac0,
            'new_title': character.title,
            'special_abilities': special_abilities_gained
        }


# Global instance
experience_system = ExperienceSystem()
