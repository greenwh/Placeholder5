"""
Monster scaling utilities for party-level appropriate encounters
"""

import re
from typing import List, Dict, Optional
import json


class MonsterScaler:
    """
    Handles monster selection based on party level and hit dice

    Implements AD&D 1e encounter design guidelines where monsters
    are selected based on hit dice appropriate for party level.
    """

    def __init__(self, monsters_data_path: str = "aerthos/data/monsters.json"):
        """
        Initialize with monster data

        Args:
            monsters_data_path: Path to monsters.json file
        """
        with open(monsters_data_path, 'r') as f:
            self.monsters = json.load(f)

    @staticmethod
    def parse_hit_dice(hd_string: str) -> float:
        """
        Parse hit dice string into numeric value

        Examples:
            "1d4" -> 1.0
            "1d8" -> 1.0
            "2d8" -> 2.0
            "4+1" -> 4.5
            "4+3" -> 4.5
            "1+1d8" -> 1.5
            "4-7d8" -> 5.5
            "45-75hp" -> 12.0

        Args:
            hd_string: Hit dice string from monster data

        Returns:
            Effective hit dice as float
        """
        # Handle special HP range format (e.g., "45-75hp")
        if 'hp' in hd_string.lower():
            # Extract HP range and convert to effective HD
            hp_range = hd_string.lower().replace('hp', '').strip()
            if '-' in hp_range:
                # Range format: "45-75"
                parts = hp_range.split('-')
                min_hp = int(parts[0])
                max_hp = int(parts[1])
                avg_hp = (min_hp + max_hp) / 2
                # Convert to HD (assuming ~5 HP per HD average)
                return avg_hp / 5.0
            else:
                # Single HP value
                return int(hp_range) / 5.0

        # Pattern: XdY or X+Y or X+YdZ or X-YdZ
        if '+' in hd_string:
            # Has bonus (e.g., "4+1" or "1+1d8")
            parts = hd_string.split('+')
            if 'd' in parts[0]:
                # Format: "1d8+1" (unlikely but handle it)
                base = int(parts[0].split('d')[0])
            else:
                # Format: "4+1" or base of "1+1d8"
                base = int(parts[0])

            # Any bonus adds 0.5 to effective HD
            return float(base) + 0.5
        elif 'd' in hd_string:
            # Could be "2d8" or "4-7d8"
            base_part = hd_string.split('d')[0]
            if '-' in base_part:
                # Range format: "4-7d8"
                parts = base_part.split('-')
                min_hd = int(parts[0])
                max_hd = int(parts[1])
                return (min_hd + max_hd) / 2.0
            else:
                # Simple format: "2d8"
                return float(base_part)
        else:
            # Just a number
            return float(hd_string)

    def get_monster_hd(self, monster_id: str) -> float:
        """
        Get the hit dice for a specific monster

        Args:
            monster_id: Monster identifier (e.g., "kobold")

        Returns:
            Effective hit dice as float, or 1.0 if not found
        """
        if monster_id not in self.monsters:
            return 1.0

        hd_string = self.monsters[monster_id].get('hit_dice', '1d8')
        return self.parse_hit_dice(hd_string)

    def get_monsters_by_hd_range(self, min_hd: float, max_hd: float) -> List[str]:
        """
        Get all monsters within a hit dice range

        Args:
            min_hd: Minimum hit dice (inclusive)
            max_hd: Maximum hit dice (inclusive)

        Returns:
            List of monster IDs within the HD range
        """
        suitable_monsters = []

        for monster_id, monster_data in self.monsters.items():
            hd = self.parse_hit_dice(monster_data.get('hit_dice', '1d8'))
            if min_hd <= hd <= max_hd:
                suitable_monsters.append(monster_id)

        return suitable_monsters

    def get_encounter_difficulty_range(self, party_level: int, party_size: int = 4) -> tuple:
        """
        Calculate appropriate HD range for encounters

        AD&D 1e guidelines:
        - Level 1: 0.5-1.5 HD monsters
        - Level 2: 1-2 HD monsters
        - Level 3: 1.5-3 HD monsters
        - Level 4+: 2-5 HD monsters

        Adjusts based on party size (more members = tougher encounters)

        Args:
            party_level: Average party level
            party_size: Number of party members (default 4)

        Returns:
            Tuple of (min_hd, max_hd)
        """
        # Base ranges by level
        if party_level == 1:
            min_hd = 0.5
            max_hd = 1.5
        elif party_level == 2:
            min_hd = 1.0
            max_hd = 2.0
        elif party_level == 3:
            min_hd = 1.5
            max_hd = 3.5
        elif party_level == 4:
            min_hd = 2.0
            max_hd = 4.5
        else:  # Level 5+
            min_hd = 2.5
            max_hd = 6.0

        # Adjust for party size
        if party_size <= 3:
            # Small party - reduce max difficulty
            max_hd = max_hd * 0.8
        elif party_size >= 6:
            # Large party - can handle tougher encounters
            max_hd = max_hd * 1.2

        return (min_hd, max_hd)

    def get_monster_pool_for_party(self, party_level: int, party_size: int = 4) -> List[str]:
        """
        Get appropriate monster pool for a party

        Args:
            party_level: Average party level
            party_size: Number of party members

        Returns:
            List of monster IDs appropriate for the party
        """
        min_hd, max_hd = self.get_encounter_difficulty_range(party_level, party_size)
        monsters = self.get_monsters_by_hd_range(min_hd, max_hd)

        # Ensure we always have some monsters
        if not monsters:
            # Fallback to basic monsters
            monsters = ['kobold', 'goblin', 'giant_rat', 'skeleton']

        return monsters

    def get_boss_for_party(self, party_level: int, party_size: int = 4) -> str:
        """
        Select an appropriate boss monster for the party

        Boss should be at the high end of the difficulty range

        Args:
            party_level: Average party level
            party_size: Number of party members

        Returns:
            Monster ID for boss encounter
        """
        min_hd, max_hd = self.get_encounter_difficulty_range(party_level, party_size)

        # Boss should be at high end of range
        boss_min_hd = max(min_hd, max_hd - 1.0)

        bosses = self.get_monsters_by_hd_range(boss_min_hd, max_hd)

        # Prefer specific boss-worthy monsters
        preferred_bosses = ['ogre', 'wight', 'troll', 'gargoyle', 'wraith',
                           'young_dragon_white', 'basilisk', 'minotaur']

        available_preferred = [m for m in preferred_bosses if m in bosses]

        if available_preferred:
            return available_preferred[0]
        elif bosses:
            # Return highest HD monster from available
            bosses_with_hd = [(m, self.get_monster_hd(m)) for m in bosses]
            bosses_with_hd.sort(key=lambda x: x[1], reverse=True)
            return bosses_with_hd[0][0]
        else:
            # Fallback
            return 'ogre'

    def calculate_party_level(self, characters: List[Dict]) -> int:
        """
        Calculate average party level

        Args:
            characters: List of character dictionaries with 'level' key

        Returns:
            Average level (rounded to nearest int)
        """
        if not characters:
            return 1

        total_level = sum(char.get('level', 1) for char in characters)
        avg_level = total_level / len(characters)

        return max(1, round(avg_level))
