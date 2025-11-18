"""
Class Special Abilities System for AD&D 1e
Handles all class-specific special abilities from the Players Handbook
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from ..entities.character import Character


class ClassAbilitiesSystem:
    """Manages class special abilities and progression"""

    def __init__(self):
        """Load class abilities data from class_abilities.json"""
        data_path = Path(__file__).parent.parent / 'data' / 'class_abilities.json'
        with open(data_path, 'r') as f:
            self.abilities = json.load(f)

    def get_backstab_multiplier(self, char_class: str, level: int) -> Tuple[int, int]:
        """
        Get backstab damage multiplier for Thief/Assassin

        Args:
            char_class: Character class (Thief or Assassin)
            level: Character level

        Returns:
            Tuple of (multiplier, to_hit_bonus)
        """
        if char_class not in ['Thief', 'Assassin']:
            return 1, 0

        backstab_data = self.abilities[char_class]['backstab']

        # Find appropriate level range
        for level_range, multiplier in backstab_data.items():
            if level_range == 'to_hit_bonus' or level_range == 'description':
                continue

            low, high = map(int, level_range.split('-'))
            if low <= level <= high:
                return multiplier, backstab_data['to_hit_bonus']

        # Default if beyond table
        return 5, backstab_data['to_hit_bonus']

    def get_monk_ac(self, level: int) -> int:
        """
        Get AC for monk at given level

        Args:
            level: Monk level

        Returns:
            Armor class (10 to -3)
        """
        if 'Monk' not in self.abilities:
            return 10

        ac_data = self.abilities['Monk']['ac_progression']
        level_str = str(min(level, 17))

        return ac_data.get(level_str, 10)

    def get_monk_movement(self, level: int) -> int:
        """
        Get movement rate for monk at given level

        Args:
            level: Monk level

        Returns:
            Movement rate in inches
        """
        if 'Monk' not in self.abilities:
            return 12

        move_data = self.abilities['Monk']['movement_progression']
        level_str = str(min(level, 17))

        return move_data.get(level_str, 12)

    def get_monk_damage(self, level: int, target_size: str = 'M') -> str:
        """
        Get open hand damage for monk at given level

        Args:
            level: Monk level
            target_size: 'S', 'M', or 'L'

        Returns:
            Damage dice string (e.g., "1d6", "2d8")
        """
        if 'Monk' not in self.abilities:
            return "1d2"

        if target_size == 'L':
            damage_data = self.abilities['Monk']['open_hand_damage_l']
        else:
            damage_data = self.abilities['Monk']['open_hand_damage_sm']

        # Find appropriate level range
        for level_range, damage in damage_data.items():
            if level_range == 'description':
                continue

            if '-' in level_range:
                low, high = map(int, level_range.split('-'))
                if low <= level <= high:
                    return damage
            else:
                if level == int(level_range):
                    return damage

        # Return last value if beyond table
        return "3d6" if target_size != 'L' else "6d6"

    def get_monk_attacks_per_round(self, level: int) -> float:
        """
        Get number of attacks per round for monk

        Args:
            level: Monk level

        Returns:
            Attacks per round (1.0 to 4.0)
        """
        if 'Monk' not in self.abilities:
            return 1.0

        attack_data = self.abilities['Monk']['attacks_per_round']

        # Find appropriate level range
        for level_range, attacks in attack_data.items():
            if level_range == 'description':
                continue

            if '-' in level_range:
                low, high = map(int, level_range.split('-'))
                if low <= level <= high:
                    return attacks
            else:
                if level == int(level_range):
                    return attacks

        return 4.0  # Level 16+

    def get_monk_special_ability(self, level: int) -> Dict[str, Any]:
        """
        Get special ability gained at this monk level

        Args:
            level: Monk level

        Returns:
            Dictionary with ability name and description, or empty dict
        """
        if 'Monk' not in self.abilities:
            return {}

        special_data = self.abilities['Monk']['special_abilities']

        # Map level to ability letter
        level_to_ability = {
            3: 'A', 4: 'B', 5: 'C', 6: 'D', 7: 'E',
            8: 'F', 9: 'G', 10: 'H', 11: 'I', 12: 'J',
            13: 'K', 14: 'L'
        }

        ability_letter = level_to_ability.get(level)
        if ability_letter and ability_letter in special_data:
            return special_data[ability_letter]

        return {}

    def get_multiple_attacks(self, char_class: str, level: int) -> float:
        """
        Get number of attacks per round for Fighter/Paladin/Ranger/Monk

        Args:
            char_class: Character class
            level: Character level

        Returns:
            Attacks per round (1.0, 1.5, 2.0, etc.)
        """
        if char_class == 'Monk':
            return self.get_monk_attacks_per_round(level)

        if char_class not in self.abilities:
            return 1.0

        if 'multiple_attacks' not in self.abilities[char_class]:
            return 1.0

        attack_data = self.abilities[char_class]['multiple_attacks']

        # Find appropriate level range
        for level_range, attacks in attack_data.items():
            if level_range == 'description':
                continue

            if '-' in level_range:
                low, high = map(int, level_range.split('-'))
                if low <= level <= high:
                    return attacks
            else:
                if level == int(level_range):
                    return attacks

        return 1.0

    def get_paladin_lay_on_hands(self, level: int) -> int:
        """
        Get HP cured by Paladin lay on hands

        Args:
            level: Paladin level

        Returns:
            HP cured (2 per level)
        """
        if 'Paladin' not in self.abilities:
            return 0

        lay_on_hands = self.abilities['Paladin']['lay_on_hands']
        return level * lay_on_hands['hp_per_level']

    def get_paladin_cure_disease_uses(self, level: int) -> int:
        """
        Get number of cure disease uses per week for Paladin

        Args:
            level: Paladin level

        Returns:
            Uses per week (1 per 5 levels)
        """
        if 'Paladin' not in self.abilities:
            return 0

        return max(1, level // 5)

    def get_ranger_giant_damage_bonus(self, level: int) -> int:
        """
        Get damage bonus vs giants for Ranger

        Args:
            level: Ranger level

        Returns:
            Bonus damage per hit (+1 per level)
        """
        if 'Ranger' not in self.abilities:
            return 0

        giant_data = self.abilities['Ranger']['giant_damage_bonus']
        return level * giant_data['bonus_per_level']

    def get_ranger_tracking_chance(self, level: int, environment: str = 'outdoor') -> int:
        """
        Get base tracking percentage for Ranger

        Args:
            level: Ranger level
            environment: 'outdoor' or 'underground'

        Returns:
            Base percentage (before modifiers)
        """
        if 'Ranger' not in self.abilities:
            return 0

        tracking_data = self.abilities['Ranger']['tracking']

        if environment == 'underground':
            return tracking_data['base_underground']
        else:
            return tracking_data['base_outdoor']

    def get_read_languages_chance(self, char_class: str, level: int) -> int:
        """
        Get chance to read languages for Thief/Assassin/Bard

        Args:
            char_class: Character class
            level: Character level

        Returns:
            Percentage chance (0-100)
        """
        if char_class not in self.abilities:
            return 0

        if 'read_languages' not in self.abilities[char_class]:
            return 0

        read_data = self.abilities[char_class]['read_languages']
        start_level = read_data['level']

        if level < start_level:
            return 0

        levels_above = level - start_level
        base_chance = read_data['base_chance']
        per_level = read_data['per_level_bonus']

        return base_chance + (levels_above * per_level)

    def has_ability(self, char_class: str, ability_name: str, level: int) -> bool:
        """
        Check if character has a specific ability at this level

        Args:
            char_class: Character class
            ability_name: Name of ability to check
            level: Character level

        Returns:
            True if ability is available
        """
        if char_class not in self.abilities:
            return False

        if ability_name not in self.abilities[char_class]:
            return False

        ability_data = self.abilities[char_class][ability_name]

        # Check if ability has a level requirement
        if isinstance(ability_data, dict):
            if 'level' in ability_data:
                return level >= ability_data['level']
            if 'start_level' in ability_data:
                return level >= ability_data['start_level']

        return True

    def get_all_abilities_at_level(self, char_class: str, level: int) -> List[Dict[str, Any]]:
        """
        Get list of all abilities available at this level

        Args:
            char_class: Character class
            level: Character level

        Returns:
            List of ability dictionaries with name, description, details
        """
        if char_class not in self.abilities:
            return []

        available = []

        for ability_name, ability_data in self.abilities[char_class].items():
            if not isinstance(ability_data, dict):
                continue

            # Check level requirement
            required_level = ability_data.get('level', ability_data.get('start_level', 1))

            if level >= required_level:
                ability_info = {
                    'name': ability_name,
                    'description': ability_data.get('description', ''),
                    'details': ability_data
                }
                available.append(ability_info)

        return available

    def apply_class_abilities_to_character(self, character: Character):
        """
        Apply all applicable class abilities to a character

        This updates the character with class bonuses and special abilities.
        Should be called during character creation and level up.

        Args:
            character: Character to update
        """
        char_class = character.char_class
        level = character.level

        if char_class not in self.abilities:
            return

        # Apply Monk AC progression
        if char_class == 'Monk':
            character.ac = self.get_monk_ac(level)

        # Apply multiple attacks
        if char_class in ['Fighter', 'Paladin', 'Ranger', 'Monk']:
            character.attacks_per_round = self.get_multiple_attacks(char_class, level)

        # Apply Paladin saving throw bonus (+2)
        if char_class == 'Paladin':
            character.save_poison -= 2
            character.save_rod_staff_wand -= 2
            character.save_petrify_paralyze -= 2
            character.save_breath -= 2
            character.save_spell -= 2

    def get_ability_description(self, char_class: str, ability_name: str) -> str:
        """
        Get description of a specific ability

        Args:
            char_class: Character class
            ability_name: Name of ability

        Returns:
            Description string
        """
        if char_class not in self.abilities:
            return ""

        if ability_name not in self.abilities[char_class]:
            return ""

        ability_data = self.abilities[char_class][ability_name]

        if isinstance(ability_data, dict):
            return ability_data.get('description', '')

        return str(ability_data)

    def get_all_class_abilities(self, char_class: str) -> Dict[str, Any]:
        """
        Get complete list of all class abilities

        Args:
            char_class: Character class

        Returns:
            Dictionary with all abilities and their details
        """
        if char_class not in self.abilities:
            return {}

        return self.abilities[char_class]


# Global instance
class_abilities_system = ClassAbilitiesSystem()
