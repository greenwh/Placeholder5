"""
Treasure Generation System

Implements AD&D 1e treasure generation per DMG p. 121.
Generates coins, gems, jewelry, and magic items based on treasure types.
"""

import json
import random
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class TreasureHoard:
    """Container for generated treasure"""
    copper: int = 0
    silver: int = 0
    electrum: int = 0
    gold: int = 0
    platinum: int = 0
    gems: List[Dict] = field(default_factory=list)
    jewelry: List[Dict] = field(default_factory=list)
    magic_items: List[str] = field(default_factory=list)

    def total_value_gp(self) -> int:
        """Calculate total value in gold pieces"""
        total = 0
        total += self.copper // 100  # 100 cp = 1 gp
        total += self.silver // 10   # 10 sp = 1 gp
        total += self.electrum // 2  # 2 ep = 1 gp
        total += self.gold           # 1 gp = 1 gp
        total += self.platinum * 5   # 1 pp = 5 gp

        for gem in self.gems:
            total += gem["value"]

        for item in self.jewelry:
            total += item["value"]

        return total

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "coins": {
                "copper": self.copper,
                "silver": self.silver,
                "electrum": self.electrum,
                "gold": self.gold,
                "platinum": self.platinum
            },
            "gems": self.gems,
            "jewelry": self.jewelry,
            "magic_items": self.magic_items,
            "total_value_gp": self.total_value_gp()
        }


class TreasureGenerator:
    """
    AD&D 1e Treasure Generation

    Generates treasure per DMG tables based on treasure type.
    Handles individual and lair treasures.
    """

    def __init__(self, treasure_tables_path: Optional[Path] = None):
        """
        Initialize treasure generator

        Args:
            treasure_tables_path: Path to treasure_tables.json (optional)
        """
        if treasure_tables_path is None:
            base_dir = Path(__file__).parent.parent
            treasure_tables_path = base_dir / "data" / "treasure_tables.json"

        with open(treasure_tables_path, 'r') as f:
            data = json.load(f)
            self.treasure_types = data["treasure_types"]
            self.gem_values = data["gem_values"]
            self.jewelry_values = data["jewelry_values"]

    def _parse_treasure_entry(self, entry_str: str) -> Tuple[str, int]:
        """
        Parse treasure table entry like '1-8 :50%' or '2-12'

        Returns:
            (dice_formula, percentage_chance)
        """
        if entry_str == "nil" or not entry_str:
            return None, 0

        # Handle "100%" entries (always appears)
        if ":100%" in entry_str:
            dice_part = entry_str.split(':')[0].strip()
            return dice_part, 100

        # Handle percentage entries like "1-8 :50%"
        if ':' in entry_str:
            parts = entry_str.split(':')
            dice_part = parts[0].strip()
            pct_part = parts[1].strip().rstrip('%')
            return dice_part, int(pct_part)

        # Handle individual treasure like "3-18"
        if re.match(r'\d+-\d+', entry_str):
            return entry_str, 100

        return None, 0

    def _roll_dice(self, formula: str) -> int:
        """
        Roll dice from formula like '1-8' (means 1d8) or '2-12' (means 2d12)

        Returns:
            Result of roll
        """
        if not formula or formula == "nil":
            return 0

        # Parse "1-8" as "1d8"
        match = re.match(r'(\d+)-(\d+)', formula)
        if match:
            num_dice = int(match.group(1))
            die_size = int(match.group(2))
            return sum(random.randint(1, die_size) for _ in range(num_dice))

        return 0

    def _roll_for_coins(self, entry_str: str, is_thousands: bool = True) -> int:
        """
        Roll for coins from treasure table entry

        Args:
            entry_str: Entry like "1-8 :50%" or "3-18"
            is_thousands: If True, multiply result by 1000

        Returns:
            Number of coins
        """
        dice_formula, percentage = self._parse_treasure_entry(entry_str)

        if not dice_formula:
            return 0

        # Check percentage chance
        if percentage < 100:
            if random.randint(1, 100) > percentage:
                return 0

        # Roll the dice
        result = self._roll_dice(dice_formula)

        # Multiply by 1000 if this is thousands
        if is_thousands:
            result *= 1000

        return result

    def _generate_gem(self) -> Dict:
        """Generate a single gem"""
        roll = random.randint(1, 100)

        for entry in self.gem_values:
            # Parse range like "01-20"
            range_parts = entry["roll_d100"].split('-')
            min_roll = int(range_parts[0])
            max_roll = int(range_parts[1])

            if min_roll <= roll <= max_roll:
                gem_type = random.choice(entry["types"])
                value = entry["value_gp"]

                # Add variation (50% to 150% of base value)
                variation = random.randint(50, 150) / 100
                final_value = int(value * variation)

                return {
                    "type": gem_type,
                    "value": final_value,
                    "description": f"a {gem_type} worth {final_value}gp"
                }

        # Fallback (shouldn't happen)
        return {"type": "quartz", "value": 10, "description": "a quartz worth 10gp"}

    def _generate_jewelry(self) -> Dict:
        """Generate a single piece of jewelry"""
        roll = random.randint(1, 100)

        for entry in self.jewelry_values:
            range_parts = entry["roll_d100"].split('-')
            min_roll = int(range_parts[0])
            max_roll = int(range_parts[1])

            if min_roll <= roll <= max_roll:
                item_type = random.choice(entry["types"])
                base_value = entry["base_value_gp"]

                # Add variation (80% to 120% of base value)
                variation = random.randint(80, 120) / 100
                final_value = int(base_value * variation)

                return {
                    "type": item_type,
                    "value": final_value,
                    "description": f"a {item_type} worth {final_value}gp"
                }

        # Fallback
        return {"type": "silver necklace", "value": 100, "description": "a silver necklace worth 100gp"}

    def _roll_for_gems(self, entry_str: str) -> List[Dict]:
        """Roll for gems from treasure table entry"""
        dice_formula, percentage = self._parse_treasure_entry(entry_str)

        if not dice_formula:
            return []

        # Check percentage chance
        if percentage < 100:
            if random.randint(1, 100) > percentage:
                return []

        # Roll for number of gems
        num_gems = self._roll_dice(dice_formula)

        # Generate gems
        return [self._generate_gem() for _ in range(num_gems)]

    def _roll_for_jewelry(self, entry_str: str) -> List[Dict]:
        """Roll for jewelry from treasure table entry"""
        dice_formula, percentage = self._parse_treasure_entry(entry_str)

        if not dice_formula:
            return []

        # Check percentage chance
        if percentage < 100:
            if random.randint(1, 100) > percentage:
                return []

        # Roll for number of pieces
        num_pieces = self._roll_dice(dice_formula)

        # Generate jewelry
        return [self._generate_jewelry() for _ in range(num_pieces)]

    def generate_individual_treasure(self, treasure_type: str, num_individuals: int = 1) -> TreasureHoard:
        """
        Generate treasure for individual monsters

        Treasure types K, L, M, N are for individuals (3-18 silver each, etc.)

        Args:
            treasure_type: Letter code (K, L, M, N)
            num_individuals: Number of monsters

        Returns:
            TreasureHoard with coins per individual
        """
        if treasure_type not in self.treasure_types:
            return TreasureHoard()

        table = self.treasure_types[treasure_type]
        hoard = TreasureHoard()

        # Individual treasures are typically just coins
        if "silver_individual" in table:
            per_individual = self._roll_for_coins(table["silver_individual"], is_thousands=False)
            hoard.silver = per_individual * num_individuals

        if "electrum_individual" in table:
            per_individual = self._roll_for_coins(table["electrum_individual"], is_thousands=False)
            hoard.electrum = per_individual * num_individuals

        if "gold_individual" in table:
            per_individual = self._roll_for_coins(table["gold_individual"], is_thousands=False)
            hoard.gold = per_individual * num_individuals

        if "platinum_individual" in table:
            per_individual = self._roll_for_coins(table["platinum_individual"], is_thousands=False)
            hoard.platinum = per_individual * num_individuals

        return hoard

    def generate_lair_treasure(self, treasure_type: str) -> TreasureHoard:
        """
        Generate treasure for a monster lair

        Args:
            treasure_type: Letter code (A-Z)

        Returns:
            Full TreasureHoard with coins, gems, jewelry, and magic items
        """
        if treasure_type not in self.treasure_types:
            return TreasureHoard()

        table = self.treasure_types[treasure_type]
        hoard = TreasureHoard()

        # Roll for coins (thousands)
        if table.get("copper_thousands") != "nil":
            hoard.copper = self._roll_for_coins(table["copper_thousands"], is_thousands=True)

        if table.get("silver_thousands") != "nil":
            hoard.silver = self._roll_for_coins(table["silver_thousands"], is_thousands=True)

        if table.get("electrum_thousands") != "nil":
            hoard.electrum = self._roll_for_coins(table["electrum_thousands"], is_thousands=True)

        if table.get("gold_thousands") != "nil":
            hoard.gold = self._roll_for_coins(table["gold_thousands"], is_thousands=True)

        if table.get("platinum_hundreds") != "nil":
            # Platinum is in hundreds, not thousands
            platinum_hundreds = self._roll_for_coins(table["platinum_hundreds"], is_thousands=False)
            hoard.platinum = platinum_hundreds * 100

        # Roll for gems
        if table.get("gems") != "nil":
            hoard.gems = self._roll_for_gems(table["gems"])

        # Roll for jewelry
        if table.get("jewelry") != "nil":
            hoard.jewelry = self._roll_for_jewelry(table["jewelry"])

        # Magic items (TODO: implement when magic item tables are ready)
        # For now, just note that magic items would appear
        for key in table:
            if key.startswith("magic_") and table[key] != "nil":
                # Placeholder - will implement later
                pass

        return hoard

    def generate_treasure(self, treasure_type_str: str, num_monsters: int = 1, is_lair: bool = False) -> TreasureHoard:
        """
        Main entry point for treasure generation

        Args:
            treasure_type_str: Treasure type like "C", "Individuals K, Lair C", etc.
            num_monsters: Number of monsters (for individual treasure calculation)
            is_lair: If True, generate lair treasure instead of individual

        Returns:
            Complete TreasureHoard
        """
        # Handle "Nil" or empty treasure
        if not treasure_type_str or treasure_type_str.lower() == "nil":
            return TreasureHoard()

        # Parse compound treasure types like "Individuals K, Lair C"
        if "," in treasure_type_str:
            parts = treasure_type_str.split(',')
            individual_part = None
            lair_part = None

            for part in parts:
                part = part.strip()
                if "Individual" in part:
                    # Extract letter after "Individuals"
                    match = re.search(r'Individual[s]?\s+([A-Z])', part)
                    if match:
                        individual_part = match.group(1)
                elif "Lair" in part:
                    match = re.search(r'Lair\s+([A-Z])', part)
                    if match:
                        lair_part = match.group(1)

            # Generate appropriate treasure
            if is_lair and lair_part:
                return self.generate_lair_treasure(lair_part)
            elif individual_part:
                return self.generate_individual_treasure(individual_part, num_monsters)
            else:
                return TreasureHoard()

        # Single treasure type
        treasure_type = treasure_type_str.strip().upper()

        # K, L, M, N are individual treasures
        if treasure_type in ['K', 'L', 'M', 'N']:
            return self.generate_individual_treasure(treasure_type, num_monsters)
        else:
            # All others are lair treasures (can still be used for individuals if needed)
            return self.generate_lair_treasure(treasure_type)


# Convenience functions
def generate_treasure(treasure_type: str, num_monsters: int = 1, is_lair: bool = False) -> Dict:
    """
    Generate treasure and return as dictionary

    Args:
        treasure_type: Treasure type code
        num_monsters: Number of monsters
        is_lair: If True, generate lair treasure

    Returns:
        Dictionary with treasure details
    """
    generator = TreasureGenerator()
    hoard = generator.generate_treasure(treasure_type, num_monsters, is_lair)
    return hoard.to_dict()


if __name__ == "__main__":
    # Test treasure generation
    print("="*60)
    print("AD&D 1e Treasure Generation Test")
    print("="*60)

    generator = TreasureGenerator()

    print("\n1. Individual Goblin Treasure (Type K - 3-18 sp each):")
    print("   5 goblins slain:")
    goblin_treasure = generator.generate_treasure("Individuals K", num_monsters=5, is_lair=False)
    print(f"   Silver: {goblin_treasure.silver} sp")
    print(f"   Total Value: {goblin_treasure.total_value_gp()} gp")

    print("\n2. Goblin Lair Treasure (Type C):")
    lair_treasure = generator.generate_treasure("Individuals K, Lair C", num_monsters=0, is_lair=True)
    result = lair_treasure.to_dict()
    print(f"   Coins: {result['coins']}")
    print(f"   Gems: {len(result['gems'])} gems worth {sum(g['value'] for g in result['gems'])} gp")
    print(f"   Jewelry: {len(result['jewelry'])} pieces worth {sum(j['value'] for j in result['jewelry'])} gp")
    print(f"   Total Value: {result['total_value_gp']} gp")

    print("\n3. Dragon Hoard (Type H - massive treasure):")
    dragon_treasure = generator.generate_lair_treasure("H")
    result = dragon_treasure.to_dict()
    print(f"   Copper: {result['coins']['copper']}")
    print(f"   Silver: {result['coins']['silver']}")
    print(f"   Electrum: {result['coins']['electrum']}")
    print(f"   Gold: {result['coins']['gold']}")
    print(f"   Platinum: {result['coins']['platinum']}")
    print(f"   Gems: {len(result['gems'])}")
    print(f"   Jewelry: {len(result['jewelry'])}")
    print(f"   TOTAL VALUE: {result['total_value_gp']} gp !!!")
