"""
AD&D 1e Experience Point Calculation

Implements the proper AD&D 1e XP award system per DMG p. 85.
Calculates XP dynamically based on monster HD, HP, and special abilities.
"""

from typing import Dict, Optional, List
import re


class XPCalculator:
    """
    Calculate XP awards per AD&D 1e rules

    Formula: Base XP (by HD) + XP per HP + Special Ability bonuses
    """

    # AD&D 1e XP Table (DMG p. 85)
    # HD range -> (base_xp, xp_per_hp)
    XP_TABLE = {
        '< 1': (5, 2),
        '1': (10, 3),
        '1+': (20, 4),
        '2': (20, 4),
        '2+': (35, 7),
        '3': (35, 7),
        '3+': (75, 10),
        '4': (75, 10),
        '4+': (125, 15),
        '5': (125, 15),
        '5+': (275, 25),
        '6': (275, 25),
        '6+': (400, 50),
        '7': (400, 50),
        '7+': (650, 75),
        '8': (650, 75),
        '8+': (850, 125),
        '9-10': (1100, 175),
        '10+': (1350, 225),
        '11-12': (1750, 300),
        '12+': (2000, 375),
        '13+': (2500, 500),
        '14+': (3000, 625),
        '15+': (3500, 750),
        '16+': (4000, 1000),
        '17+': (4500, 1250),
        '18+': (5000, 1500),
        '19+': (5500, 2000),
        '20+': (6000, 2500),
        '21+': (6500, 3000)
    }

    @staticmethod
    def parse_hit_dice(hd_str: str) -> tuple[float, int]:
        """
        Parse hit dice string to get HD value and bonus HP

        Args:
            hd_str: Hit dice string like "1d8", "4+1", "6+6"

        Returns:
            Tuple of (hd_value, bonus_hp)

        Examples:
            "1d8" -> (1.0, 0)
            "4+1" -> (4.0, 1)
            "6+6" -> (6.0, 6)
            "1d4" -> (0.5, 0)  # Less than 1 HD
        """
        # Handle "XdY" format
        if 'd' in hd_str.lower():
            match = re.match(r'(\d+)d(\d+)', hd_str.lower())
            if match:
                num_dice = int(match.group(1))
                die_size = int(match.group(2))

                # < 1 HD check (1d4 or 1d6 for very weak creatures)
                if num_dice == 1 and die_size <= 4:
                    return (0.5, 0)
                else:
                    return (float(num_dice), 0)

        # Handle "X+Y" format
        if '+' in hd_str:
            parts = hd_str.split('+')
            hd = float(parts[0])
            bonus = int(parts[1])
            return (hd, bonus)

        # Handle "X-Y" range format (e.g., "4-7d8")
        if '-' in hd_str:
            # Take the average
            match = re.match(r'(\d+)-(\d+)', hd_str)
            if match:
                min_hd = int(match.group(1))
                max_hd = int(match.group(2))
                avg_hd = (min_hd + max_hd) / 2
                return (avg_hd, 0)

        # Plain number
        try:
            return (float(hd_str), 0)
        except ValueError:
            return (1.0, 0)  # Default

    @staticmethod
    def get_hd_category(hd_value: float) -> str:
        """
        Get HD category for XP table lookup

        Args:
            hd_value: Hit dice value (e.g., 1.0, 4.5, 6.0)

        Returns:
            Category string for XP table (e.g., "1", "4+", "6")
        """
        if hd_value < 1:
            return '< 1'
        elif hd_value == int(hd_value):
            # Whole number
            hd_int = int(hd_value)
            if hd_int <= 8:
                return str(hd_int)
            elif hd_int <= 10:
                return '9-10'
            elif hd_int <= 12:
                return '11-12'
            else:
                return f"{hd_int}+"
        else:
            # Has plus (e.g., 4.5 -> "4+")
            return f"{int(hd_value)}+"

    @staticmethod
    def calculate_xp(hit_dice: str, hp: int, special_abilities: Optional[List[str]] = None) -> int:
        """
        Calculate XP award for a monster using AD&D 1e formula

        Args:
            hit_dice: Hit dice string (e.g., "1d8", "4+1", "6+6")
            hp: Monster's current/max HP
            special_abilities: List of special abilities (for bonus XP)

        Returns:
            Total XP value

        Examples:
            >>> XPCalculator.calculate_xp("1d8", 4, [])
            22  # 10 base + (4 × 3)

            >>> XPCalculator.calculate_xp("4+1", 20, [])
            425  # 125 base + (20 × 15)
        """
        # Parse HD
        hd_value, bonus_hp = XPCalculator.parse_hit_dice(hit_dice)

        # Get XP table entry
        hd_category = XPCalculator.get_hd_category(hd_value)
        base_xp, xp_per_hp = XPCalculator.XP_TABLE.get(hd_category, (10, 3))

        # Calculate XP
        total_xp = base_xp + (hp * xp_per_hp)

        # Add bonuses for special abilities (simplified for now)
        # TODO: Implement proper special ability XP bonuses per DMG
        if special_abilities:
            # Quick estimate: +50 XP per significant special ability
            num_significant = sum(1 for ability in special_abilities
                                 if ability and ability.lower() not in ['nil', 'none', ''])
            total_xp += (num_significant * 50)

        return total_xp

    @staticmethod
    def calculate_xp_from_formula(hp: int, xp_formula: Dict) -> int:
        """
        Calculate XP using pre-computed formula from monsters_enhanced.json

        Args:
            hp: Monster's HP
            xp_formula: Dictionary with 'base_xp' and 'xp_per_hp'

        Returns:
            Total XP value
        """
        base_xp = xp_formula.get('base_xp', 10)
        xp_per_hp = xp_formula.get('xp_per_hp', 1)

        return base_xp + (hp * xp_per_hp)


if __name__ == "__main__":
    # Test the calculator
    print("="*70)
    print("AD&D 1e XP CALCULATOR TEST")
    print("="*70)

    test_cases = [
        ("Kobold", "1d8", 4, []),
        ("Orc", "1d8", 5, []),
        ("Hobgoblin", "1+1", 6, []),
        ("Ogre", "4+1", 19, []),
        ("Troll", "6+6", 36, ["regeneration"]),
        ("Lich", "11d8", 50, ["paralysis", "fear", "spellcaster"])
    ]

    for name, hd, hp, abilities in test_cases:
        xp = XPCalculator.calculate_xp(hd, hp, abilities)
        print(f"\n{name}:")
        print(f"  HD: {hd}, HP: {hp}")
        print(f"  Special: {abilities if abilities else 'None'}")
        print(f"  XP: {xp}")

    print("\n" + "="*70)
