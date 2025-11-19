"""
Racial Special Abilities System for AD&D 1e
Handles all racial special abilities from the Players Handbook
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from ..entities.character import Character


class RacialAbilitiesSystem:
    """Manages racial special abilities and level limits"""

    def __init__(self):
        """Load racial data from races.json"""
        data_path = Path(__file__).parent.parent / 'data' / 'races.json'
        with open(data_path, 'r') as f:
            self.races = json.load(f)

    def get_level_limit(self, race: str, char_class: str, **ability_scores) -> int:
        """
        Get maximum level for a race/class combination

        Args:
            race: Character race name
            char_class: Character class name
            **ability_scores: Ability scores (strength, intelligence, dexterity, etc.)

        Returns:
            Maximum level (999 = unlimited)
        """
        if race not in self.races:
            return 999  # Unknown race = no limit

        race_data = self.races[race]

        # Humans have no level limits
        if race == 'Human':
            return 999

        # Get base level limit
        level_limits = race_data.get('level_limits', {})
        base_limit = level_limits.get(char_class, 0)

        if base_limit == 0:
            return 0  # Class not allowed

        if base_limit == 999:
            return 999  # Unlimited

        # Check for ability score bonuses to level limit
        if 'level_limit_bonuses' in race_data:
            bonuses = race_data['level_limit_bonuses'].get(char_class, {})

            for ability, bonus_table in bonuses.items():
                ability_score = ability_scores.get(ability, 10)

                # bonus_table is like {17: 1, 18: 2}
                # Apply highest applicable bonus
                bonus = 0
                for threshold, bonus_value in sorted(bonus_table.items()):
                    if ability_score >= int(threshold):
                        bonus = max(bonus, bonus_value)

                base_limit += bonus

        return base_limit

    def get_saving_throw_bonus(self, race: str, constitution: int) -> int:
        """
        Calculate racial saving throw bonus

        Dwarves, Gnomes, and Halflings get +1 per 3.5 CON (rounded down)
        Maximum +5 at CON 18+

        Args:
            race: Character race
            constitution: CON score

        Returns:
            Bonus to saving throws (0-5)
        """
        if race not in self.races:
            return 0

        race_data = self.races[race]
        details = race_data.get('special_abilities_details', {})

        if 'saving_throw_bonus' not in details:
            return 0

        # Formula: 1 per 3.5 CON, max 5
        bonus = int(constitution / 3.5)
        max_bonus = details['saving_throw_bonus'].get('max', 5)

        return min(bonus, max_bonus)

    def get_infravision_range(self, race: str, bloodline: str = 'pure') -> int:
        """
        Get infravision range in feet

        Args:
            race: Character race
            bloodline: For Halflings - 'pure' (Stoutish) or 'mixed'

        Returns:
            Range in feet (0 if no infravision)
        """
        if race not in self.races:
            return 0

        race_data = self.races[race]
        details = race_data.get('special_abilities_details', {})

        if 'infravision' not in details:
            return 0

        infra_data = details['infravision']

        # Halflings have bloodline-dependent infravision
        if isinstance(infra_data, dict):
            if race == 'Halfling':
                return infra_data.get('stoutish' if bloodline == 'pure' else 'mixed', 0)

        return infra_data

    def get_sleep_charm_resistance(self, race: str) -> int:
        """
        Get resistance % to sleep and charm spells

        Args:
            race: Character race

        Returns:
            Resistance percentage (0-90)
        """
        if race not in self.races:
            return 0

        race_data = self.races[race]
        details = race_data.get('special_abilities_details', {})

        return details.get('sleep_charm_resistance', 0)

    def check_secret_door_detection(self, race: str, search_type: str = 'passive') -> int:
        """
        Get secret door detection chance

        Args:
            race: Character race
            search_type: 'passive', 'searching', or 'concealed'

        Returns:
            Detection percentage (0-50)
        """
        if race not in self.races:
            return 0

        race_data = self.races[race]
        details = race_data.get('special_abilities_details', {})

        if 'secret_door_detection' not in details:
            return 0

        detection = details['secret_door_detection']
        return detection.get(search_type, 0)

    def get_combat_bonus(self, race: str, target_type: str) -> int:
        """
        Get racial combat bonus against specific monster types

        Args:
            race: Character race
            target_type: Type of monster (e.g., 'goblin', 'orc')

        Returns:
            To-hit bonus (usually +1)
        """
        if race not in self.races:
            return 0

        race_data = self.races[race]
        details = race_data.get('special_abilities_details', {})

        if 'combat_bonus' not in details:
            return 0

        combat_data = details['combat_bonus']
        targets = combat_data.get('targets', [])

        if target_type.lower() in targets:
            return combat_data.get('to_hit_bonus', 0)

        return 0

    def get_ac_bonus_vs_giants(self, race: str, target_type: str) -> int:
        """
        Get AC bonus against large creatures

        Args:
            race: Character race
            target_type: Type of monster (e.g., 'giant', 'ogre')

        Returns:
            AC bonus (negative = better AC, e.g., -4)
        """
        if race not in self.races:
            return 0

        race_data = self.races[race]
        details = race_data.get('special_abilities_details', {})

        if 'ac_bonus_vs_giants' not in details:
            # Check for Halfling large creature bonus
            if 'ac_bonus_vs_large' in details:
                large_data = details['ac_bonus_vs_large']
                if target_type.lower() in large_data.get('targets', []):
                    return large_data.get('ac_bonus', 0)
            return 0

        giant_data = details['ac_bonus_vs_giants']
        targets = giant_data.get('targets', [])

        if target_type.lower() in targets:
            return giant_data.get('ac_bonus', 0)

        return 0

    def check_mining_detection(self, race: str, detection_type: str) -> Tuple[bool, int]:
        """
        Check for mining/underground detection abilities

        Args:
            race: Character race
            detection_type: Type of detection ('slope', 'new_construction', 'sliding_walls',
                          'stone_traps', 'depth', 'unsafe_walls', 'direction')

        Returns:
            Tuple of (has_ability, percentage_chance)
        """
        if race not in self.races:
            return False, 0

        race_data = self.races[race]
        details = race_data.get('special_abilities_details', {})

        if 'mining_detection' not in details:
            # Check for Halfling detection abilities
            if 'detection' in details:
                detect_data = details['detection']
                if detection_type in detect_data:
                    return True, detect_data[detection_type]
            return False, 0

        mining_data = details['mining_detection']

        if detection_type in mining_data:
            return True, mining_data[detection_type]

        return False, 0

    def get_surprise_chance(self, race: str, situation: str = 'alone_no_metal') -> int:
        """
        Get surprise chance for elves/halflings

        Args:
            race: Character race
            situation: 'alone_no_metal', 'advance_party_no_metal', or 'with_door'

        Returns:
            Surprise percentage (0-67)
        """
        if race not in self.races:
            return 0

        race_data = self.races[race]
        details = race_data.get('special_abilities_details', {})

        # Check for surprise ability
        if 'surprise' in details:
            surprise_data = details['surprise']
            return surprise_data.get(situation, 0)

        # Check for silent movement (Halfling)
        if 'silent_movement' in details:
            movement_data = details['silent_movement']
            return movement_data.get(situation, 0)

        return 0

    def get_missile_attack_bonus(self, race: str) -> int:
        """
        Get racial bonus to missile attacks (Halflings get +3)

        Args:
            race: Character race

        Returns:
            Missile attack bonus
        """
        if race not in self.races:
            return 0

        race_data = self.races[race]
        details = race_data.get('special_abilities_details', {})

        return details.get('missile_attack_bonus', 0)

    def can_speak_with_burrowing_animals(self, race: str) -> bool:
        """
        Check if race can speak with burrowing animals (Gnomes)

        Args:
            race: Character race

        Returns:
            True if ability exists
        """
        if race not in self.races:
            return False

        race_data = self.races[race]
        details = race_data.get('special_abilities_details', {})

        return details.get('speak_with_burrowing_animals', False)

    def apply_racial_abilities_to_character(self, character: Character):
        """
        Apply all applicable racial abilities to a character

        This updates the character with racial bonuses and special abilities.
        Should be called during character creation and level up.

        Args:
            character: Character to update
        """
        race = character.race

        if race not in self.races:
            return

        # Apply saving throw bonuses (Dwarf, Gnome, Halfling)
        save_bonus = self.get_saving_throw_bonus(race, character.constitution)
        if save_bonus > 0:
            # Apply to relevant saves
            character.save_poison -= save_bonus
            character.save_rod_staff_wand -= save_bonus
            character.save_spell -= save_bonus

            # Halflings also get bonus vs petrify/paralyze and breath
            if race == 'Halfling':
                character.save_petrify_paralyze -= save_bonus
                character.save_breath -= save_bonus

    def get_all_racial_abilities(self, race: str) -> Dict[str, Any]:
        """
        Get complete list of all racial abilities and their details

        Args:
            race: Character race

        Returns:
            Dictionary with all abilities and their details
        """
        if race not in self.races:
            return {}

        race_data = self.races[race]

        return {
            'special_abilities': race_data.get('special_abilities', []),
            'special_abilities_details': race_data.get('special_abilities_details', {}),
            'level_limits': race_data.get('level_limits', {}),
            'level_limit_bonuses': race_data.get('level_limit_bonuses', {}),
            'multi_class_options': race_data.get('multi_class_options', [])
        }

    def validate_character_level(self, race: str, char_class: str, level: int, **ability_scores) -> Tuple[bool, str]:
        """
        Check if a character level is valid for their race/class

        Args:
            race: Character race
            char_class: Character class
            level: Current or target level
            **ability_scores: Ability scores

        Returns:
            Tuple of (is_valid, error_message)
        """
        max_level = self.get_level_limit(race, char_class, **ability_scores)

        if max_level == 0:
            return False, f"{race} characters cannot be {char_class}s"

        if level > max_level:
            return False, f"{race} {char_class}s are limited to level {max_level}"

        return True, ""


# Global instance
racial_abilities_system = RacialAbilitiesSystem()
