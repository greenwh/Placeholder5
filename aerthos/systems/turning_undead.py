"""
Turning Undead System for AD&D 1e
Handles cleric/paladin ability to turn or destroy undead
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class TurningUndeadSystem:
    """Manages turning undead mechanics"""

    def __init__(self):
        """Load turning undead tables"""
        data_path = Path(__file__).parent.parent / 'data' / 'turning_undead.json'
        with open(data_path, 'r') as f:
            data = json.load(f)
            self.undead_types = data['undead_types']
            self.turning_table = data['turning_table']
            self.result_explanations = data['result_explanations']

    def get_effective_turning_level(self, char_class: str, level: int) -> int:
        """
        Get effective cleric level for turning undead

        Args:
            char_class: Character class (Cleric or Paladin)
            level: Character level

        Returns:
            Effective cleric level for turning (0 if cannot turn)
        """
        if char_class == 'Cleric':
            return level

        if char_class == 'Paladin':
            # Paladins turn as cleric 2 levels lower, starting at level 3
            if level < 3:
                return 0
            return level - 2

        return 0

    def can_turn_undead(self, char_class: str, level: int) -> bool:
        """
        Check if character can turn undead

        Args:
            char_class: Character class
            level: Character level

        Returns:
            True if character can turn undead
        """
        return self.get_effective_turning_level(char_class, level) > 0

    def attempt_turn(self, char_class: str, level: int, undead_type: str,
                    num_undead: int = 1) -> Dict:
        """
        Attempt to turn undead

        Args:
            char_class: Character class (Cleric or Paladin)
            level: Character level
            undead_type: Type of undead (Skeleton, Zombie, etc.)
            num_undead: Number of undead present

        Returns:
            Dictionary with result details:
            - success: bool
            - result_type: 'fail', 'turn', 'destroy'
            - num_affected: int
            - narrative: str
        """
        effective_level = self.get_effective_turning_level(char_class, level)

        if effective_level == 0:
            return {
                'success': False,
                'result_type': 'fail',
                'num_affected': 0,
                'narrative': f"{char_class}s cannot turn undead at this level"
            }

        # Get turning value from table
        level_str = str(min(effective_level, 20))
        if level_str not in self.turning_table:
            level_str = "1"

        turning_value = self.turning_table[level_str].get(undead_type, "-")

        # Handle different result types
        if turning_value == "-":
            # No effect
            return {
                'success': False,
                'result_type': 'fail',
                'num_affected': 0,
                'narrative': f"The {undead_type}(s) are too powerful to turn at this level"
            }

        elif turning_value == "T":
            # Automatic turn
            num_turned = min(self._roll_2d6(), num_undead)
            return {
                'success': True,
                'result_type': 'turn',
                'num_affected': num_turned,
                'duration': random.randint(3, 12),  # 3d4 rounds
                'narrative': f"Successfully turned {num_turned} {undead_type}(s)! They flee for {self._roll_3d4()} rounds."
            }

        elif turning_value == "D":
            # Automatic destroy
            num_destroyed = min(self._roll_2d6(), num_undead)
            return {
                'success': True,
                'result_type': 'destroy',
                'num_affected': num_destroyed,
                'narrative': f"Destroyed {num_destroyed} {undead_type}(s) with holy power!"
            }

        elif turning_value == "D*":
            # Enhanced destroy
            num_destroyed = min(self._roll_2d6() + random.randint(2, 8), num_undead)  # 2d6+2d4
            return {
                'success': True,
                'result_type': 'destroy',
                'num_affected': num_destroyed,
                'narrative': f"Utterly destroyed {num_destroyed} {undead_type}(s) with overwhelming holy power!"
            }

        else:
            # Numeric value - must roll
            required_roll = int(turning_value)
            roll = random.randint(1, 20)

            if roll >= required_roll:
                # Success - turn undead
                num_turned = min(self._roll_2d6(), num_undead)
                duration = self._roll_3d4()
                return {
                    'success': True,
                    'result_type': 'turn',
                    'num_affected': num_turned,
                    'duration': duration,
                    'roll': roll,
                    'required': required_roll,
                    'narrative': f"Rolled {roll} (needed {required_roll}+). Turned {num_turned} {undead_type}(s)! They flee for {duration} rounds."
                }
            else:
                # Failed to turn
                return {
                    'success': False,
                    'result_type': 'fail',
                    'num_affected': 0,
                    'roll': roll,
                    'required': required_roll,
                    'narrative': f"Rolled {roll} (needed {required_roll}+). Failed to turn the {undead_type}(s)!"
                }

    def get_turning_chart(self, char_class: str, level: int) -> Dict[str, str]:
        """
        Get turning chart for character's current level

        Args:
            char_class: Character class
            level: Character level

        Returns:
            Dictionary mapping undead type to turning value
        """
        effective_level = self.get_effective_turning_level(char_class, level)

        if effective_level == 0:
            return {}

        level_str = str(min(effective_level, 20))
        if level_str not in self.turning_table:
            level_str = "1"

        return self.turning_table[level_str].copy()

    def get_undead_hierarchy(self) -> List[str]:
        """
        Get list of undead types in order of power

        Returns:
            List of undead type names
        """
        return self.undead_types.copy()

    def explain_result(self, result_code: str) -> str:
        """
        Get explanation for a turning result code

        Args:
            result_code: Result code ('-', 'T', 'D', 'D*', or number)

        Returns:
            Explanation string
        """
        if result_code == "-":
            return self.result_explanations["-"]
        elif result_code == "T":
            return self.result_explanations["T"]
        elif result_code == "D":
            return self.result_explanations["D"]
        elif result_code == "D*":
            return self.result_explanations["D*"]
        else:
            return self.result_explanations["number"].replace("number", str(result_code))

    def _roll_2d6(self) -> int:
        """Roll 2d6"""
        return random.randint(1, 6) + random.randint(1, 6)

    def _roll_3d4(self) -> int:
        """Roll 3d4"""
        return random.randint(1, 4) + random.randint(1, 4) + random.randint(1, 4)

    def get_all_turning_data(self, char_class: str, level: int) -> Dict:
        """
        Get complete turning data for character

        Args:
            char_class: Character class
            level: Character level

        Returns:
            Dictionary with effective level, chart, and undead types
        """
        effective_level = self.get_effective_turning_level(char_class, level)

        return {
            'can_turn': effective_level > 0,
            'effective_level': effective_level,
            'turning_chart': self.get_turning_chart(char_class, level),
            'undead_types': self.undead_types.copy()
        }


# Global instance
turning_undead_system = TurningUndeadSystem()
