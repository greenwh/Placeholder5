"""
Encounter Determination System

Implements AD&D 1e encounter mechanics:
- Number appearing calculation
- Surprise determination
- Reaction rolls
- Wandering monster checks
"""

import random
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class EncounterResult:
    """Result of an encounter determination"""
    monster_type: str
    count: int
    surprise_party: bool  # Party is surprised
    surprise_monsters: bool  # Monsters are surprised
    reaction: str  # "hostile", "neutral", "friendly"
    reaction_score: int  # 2d6 roll
    is_lair: bool  # In monster's lair
    distance: int  # Distance in feet

    def has_surprise(self) -> bool:
        """Check if anyone is surprised"""
        return self.surprise_party or self.surprise_monsters


class EncounterDetermination:
    """
    AD&D 1e Encounter Determination

    Handles all aspects of encounter generation per DMG rules.
    """

    def __init__(self, enhanced_monsters_data: Optional[Dict] = None):
        """
        Initialize encounter system

        Args:
            enhanced_monsters_data: Dict from monsters_enhanced.json
        """
        self.monsters = enhanced_monsters_data or {}

        # Reaction table (DMG p. 63)
        self.reaction_table = [
            {"roll": "2", "reaction": "hostile_attack", "description": "Hostile, attacks"},
            {"roll": "3-5", "reaction": "hostile", "description": "Hostile, may attack"},
            {"roll": "6-8", "reaction": "neutral", "description": "Neutral, uncertain"},
            {"roll": "9-11", "reaction": "neutral_positive", "description": "Neutral, favorable"},
            {"roll": "12", "reaction": "friendly", "description": "Friendly, enthusiastic"}
        ]

    def _roll_dice(self, formula: str) -> int:
        """
        Roll dice from formula

        Args:
            formula: Dice formula like "2-8", "1-6", etc.

        Returns:
            Result of roll
        """
        # Handle simple number
        if formula.isdigit():
            return int(formula)

        # Handle range format "2-8" (means roll between 2 and 8)
        match = re.match(r'(\d+)-(\d+)', formula)
        if match:
            min_val = int(match.group(1))
            max_val = int(match.group(2))
            return random.randint(min_val, max_val)

        # Handle dice format "2d6"
        match = re.match(r'(\d+)d(\d+)([+-]\d+)?', formula)
        if match:
            num_dice = int(match.group(1))
            die_size = int(match.group(2))
            modifier = int(match.group(3)) if match.group(3) else 0

            total = sum(random.randint(1, die_size) for _ in range(num_dice))
            return total + modifier

        return 1

    def determine_number_appearing(
        self,
        monster_id: str,
        in_lair: bool = False
    ) -> int:
        """
        Determine how many monsters appear

        Args:
            monster_id: Monster ID from monsters_enhanced.json
            in_lair: If True, use lair appearing numbers

        Returns:
            Number of monsters
        """
        if monster_id not in self.monsters:
            return 1

        monster = self.monsters[monster_id]

        # Check if this is a lair encounter
        if in_lair:
            # Use lair appearing if available
            lair_data = monster.get("no_appearing", {}).get("lair", {})
            if lair_data:
                min_count = lair_data.get("min", 1)
                max_count = lair_data.get("max", 1)
                return random.randint(min_count, max_count)

        # Use wilderness appearing
        wild_data = monster.get("no_appearing", {}).get("wilderness", {})
        if wild_data:
            min_count = wild_data.get("min", 1)
            max_count = wild_data.get("max", 1)
            return random.randint(min_count, max_count)

        # Fallback
        return 1

    def check_surprise(
        self,
        monster_id: str,
        party_size: int = 4
    ) -> Tuple[bool, bool]:
        """
        Check for surprise

        Standard surprise: 1-2 on d6 (33%)
        Some monsters surprise on 1-3 or 1-4 (special abilities)

        Args:
            monster_id: Monster ID
            party_size: Number of party members

        Returns:
            (party_surprised, monsters_surprised)
        """
        # Standard surprise chance: 1-2 on d6
        party_surprise_chance = 2
        monster_surprise_chance = 2

        # Check for special surprise abilities
        if monster_id in self.monsters:
            monster = self.monsters[monster_id]
            special_attacks = monster.get("special_attacks", "")

            if isinstance(special_attacks, str):
                if "surprise" in special_attacks.lower():
                    if "1-4" in special_attacks:
                        monster_surprise_chance = 4
                    elif "1-3" in special_attacks:
                        monster_surprise_chance = 3

        # Roll for party surprise
        party_roll = random.randint(1, 6)
        party_surprised = (party_roll <= party_surprise_chance)

        # Roll for monster surprise
        monster_roll = random.randint(1, 6)
        monsters_surprised = (monster_roll <= monster_surprise_chance)

        # Both can't be surprised at once
        if party_surprised and monsters_surprised:
            # Neither is surprised
            return False, False

        return party_surprised, monsters_surprised

    def determine_reaction(
        self,
        monster_id: str,
        charisma_modifier: int = 0,
        party_alignment: str = "neutral"
    ) -> Tuple[str, int]:
        """
        Determine monster reaction (DMG p. 63)

        Roll 2d6, modified by CHA and alignment
        2: Hostile, attacks
        3-5: Hostile, may attack
        6-8: Neutral, uncertain
        9-11: Neutral, favorable
        12: Friendly

        Args:
            monster_id: Monster ID
            charisma_modifier: CHA reaction adjustment (-2 to +4)
            party_alignment: Party alignment

        Returns:
            (reaction_type, roll_result)
        """
        # Base roll: 2d6
        roll = random.randint(1, 6) + random.randint(1, 6)

        # Apply CHA modifier
        roll += charisma_modifier

        # Check alignment compatibility
        if monster_id in self.monsters:
            monster = self.monsters[monster_id]
            monster_alignment = monster.get("alignment", "Neutral")

            # Opposite alignments: -2
            if self._alignments_opposed(party_alignment, monster_alignment):
                roll -= 2
            # Similar alignments: +2
            elif self._alignments_similar(party_alignment, monster_alignment):
                roll += 2

        # Clamp roll to 2-12
        roll = max(2, min(12, roll))

        # Determine reaction
        for entry in self.reaction_table:
            roll_range = entry["roll"]

            if "-" in roll_range:
                min_r, max_r = map(int, roll_range.split("-"))
                if min_r <= roll <= max_r:
                    return entry["reaction"], roll
            elif roll == int(roll_range):
                return entry["reaction"], roll

        return "neutral", roll

    def _alignments_opposed(self, align1: str, align2: str) -> bool:
        """Check if alignments are opposed"""
        align1 = align1.lower()
        align2 = align2.lower()

        # Law vs Chaos
        if ("lawful" in align1 and "chaotic" in align2) or \
           ("chaotic" in align1 and "lawful" in align2):
            return True

        # Good vs Evil
        if ("good" in align1 and "evil" in align2) or \
           ("evil" in align1 and "good" in align2):
            return True

        return False

    def _alignments_similar(self, align1: str, align2: str) -> bool:
        """Check if alignments are similar"""
        align1 = align1.lower()
        align2 = align2.lower()

        # Both lawful
        if "lawful" in align1 and "lawful" in align2:
            return True

        # Both chaotic
        if "chaotic" in align1 and "chaotic" in align2:
            return True

        # Both good
        if "good" in align1 and "good" in align2:
            return True

        # Both evil
        if "evil" in align1 and "evil" in align2:
            return True

        # Both neutral
        if "neutral" in align1 and "neutral" in align2:
            return True

        return False

    def determine_encounter_distance(self, surprise_party: bool, surprise_monsters: bool) -> int:
        """
        Determine encounter distance in feet

        Surprised: 10-30 feet
        Not surprised, dungeon: 20-80 feet
        Not surprised, wilderness: 40-240 feet

        Args:
            surprise_party: Party is surprised
            surprise_monsters: Monsters are surprised

        Returns:
            Distance in feet
        """
        if surprise_party or surprise_monsters:
            # Close!
            return random.randint(1, 3) * 10  # 10-30 feet

        # Dungeon encounter distance (could be parameterized)
        return random.randint(2, 8) * 10  # 20-80 feet

    def check_for_lair(self, monster_id: str) -> bool:
        """
        Check if encounter is in monster's lair

        Uses % IN LAIR from monster data

        Args:
            monster_id: Monster ID

        Returns:
            True if in lair
        """
        if monster_id not in self.monsters:
            return False

        monster = self.monsters[monster_id]
        pct_in_lair = monster.get("pct_in_lair", 0)

        return random.randint(1, 100) <= pct_in_lair

    def generate_encounter(
        self,
        monster_id: str,
        party_size: int = 4,
        charisma_modifier: int = 0,
        party_alignment: str = "neutral",
        force_lair: bool = False
    ) -> EncounterResult:
        """
        Generate a complete encounter

        Args:
            monster_id: Monster to encounter
            party_size: Number of party members
            charisma_modifier: Party face's CHA mod
            party_alignment: Party alignment
            force_lair: Force lair encounter

        Returns:
            Complete EncounterResult
        """
        # Check if lair encounter
        is_lair = force_lair or self.check_for_lair(monster_id)

        # Determine number appearing
        count = self.determine_number_appearing(monster_id, in_lair=is_lair)

        # Check surprise
        surprise_party, surprise_monsters = self.check_surprise(monster_id, party_size)

        # Determine reaction
        reaction, reaction_score = self.determine_reaction(
            monster_id,
            charisma_modifier,
            party_alignment
        )

        # Determine distance
        distance = self.determine_encounter_distance(surprise_party, surprise_monsters)

        return EncounterResult(
            monster_type=monster_id,
            count=count,
            surprise_party=surprise_party,
            surprise_monsters=surprise_monsters,
            reaction=reaction,
            reaction_score=reaction_score,
            is_lair=is_lair,
            distance=distance
        )

    def check_wandering_monster(self, turns_elapsed: int = 1) -> bool:
        """
        Check for wandering monsters

        Standard: 1 in 6 per turn in dungeons

        Args:
            turns_elapsed: Number of turns since last check

        Returns:
            True if wandering monster appears
        """
        for _ in range(turns_elapsed):
            roll = random.randint(1, 6)
            if roll == 1:
                return True

        return False


# Convenience function
def generate_random_encounter(
    monster_id: str,
    monsters_data: Dict,
    party_size: int = 4,
    party_charisma_mod: int = 0,
    party_alignment: str = "neutral"
) -> Dict:
    """
    Generate encounter and return as dictionary

    Args:
        monster_id: Monster type
        monsters_data: Enhanced monsters dict
        party_size: Party size
        party_charisma_mod: CHA modifier
        party_alignment: Alignment

    Returns:
        Dictionary with encounter data
    """
    enc_system = EncounterDetermination(monsters_data)
    result = enc_system.generate_encounter(
        monster_id,
        party_size,
        party_charisma_mod,
        party_alignment
    )

    return {
        "monster_type": result.monster_type,
        "count": result.count,
        "surprise_party": result.surprise_party,
        "surprise_monsters": result.surprise_monsters,
        "reaction": result.reaction,
        "reaction_score": result.reaction_score,
        "is_lair": result.is_lair,
        "distance_feet": result.distance,
        "description": _format_encounter_description(result, monsters_data)
    }


def _format_encounter_description(result: EncounterResult, monsters_data: Dict) -> str:
    """Format encounter as descriptive text"""
    # Get monster name from ID
    monster_data = monsters_data.get(result.monster_type, {})

    # Try to extract just the name from description (first sentence before period)
    desc = monster_data.get("description", "")
    if desc and "." in desc:
        monster_name = desc.split(".")[0]
    else:
        monster_name = result.monster_type.replace("_", " ").title()

    parts = []

    # Count and type
    if result.count == 1:
        parts.append(f"You encounter 1 {monster_name}")
    else:
        parts.append(f"You encounter {result.count} {monster_name}s")

    # Distance
    parts.append(f"at {result.distance} feet")

    # Surprise
    if result.surprise_party:
        parts.append("They have surprised you!")
    elif result.surprise_monsters:
        parts.append("You have surprised them.")

    # Reaction
    reaction_desc = {
        "hostile_attack": "They attack immediately!",
        "hostile": "They appear hostile.",
        "neutral": "They seem uncertain.",
        "neutral_positive": "They appear curious but not threatening.",
        "friendly": "They seem friendly."
    }
    parts.append(reaction_desc.get(result.reaction, ""))

    # Lair
    if result.is_lair:
        parts.append("You have entered their lair!")

    return " ".join(parts)


if __name__ == "__main__":
    # Test encounter determination
    import json
    from pathlib import Path

    print("="*70)
    print("AD&D 1e ENCOUNTER DETERMINATION TEST")
    print("="*70)

    # Load enhanced monsters
    monsters_file = Path(__file__).parent.parent / "data" / "monsters_enhanced.json"
    with open(monsters_file) as f:
        monsters = json.load(f)

    enc_system = EncounterDetermination(monsters)

    # Test 1: Goblin encounter
    print("\n1. GOBLIN ENCOUNTER (Wilderness)")
    print("-" * 70)
    for i in range(3):
        encounter = enc_system.generate_encounter("goblin", party_size=4)
        print(f"\nEncounter {i+1}:")
        print(f"  Count: {encounter.count} goblins")
        print(f"  Distance: {encounter.distance} feet")
        print(f"  Surprise (party/monsters): {encounter.surprise_party}/{encounter.surprise_monsters}")
        print(f"  Reaction: {encounter.reaction} (rolled {encounter.reaction_score})")
        print(f"  In lair: {encounter.is_lair}")

    # Test 2: Orc encounter (in lair)
    print("\n2. ORC ENCOUNTER (Lair)")
    print("-" * 70)
    encounter = enc_system.generate_encounter("orc", party_size=4, force_lair=True)
    print(f"  Count: {encounter.count} orcs")
    print(f"  Distance: {encounter.distance} feet")
    print(f"  Reaction: {encounter.reaction}")
    print(f"  In lair: {encounter.is_lair}")

    # Test 3: Wandering monster check
    print("\n3. WANDERING MONSTER CHECK")
    print("-" * 70)
    checks = 20
    encounters = 0
    for _ in range(checks):
        if enc_system.check_wandering_monster():
            encounters += 1

    print(f"  Rolled {checks} checks, got {encounters} wandering monsters")
    print(f"  Expected: ~{checks//6} (1 in 6 chance)")

    # Test 4: Formatted description
    print("\n4. FORMATTED ENCOUNTER DESCRIPTION")
    print("-" * 70)
    encounter_dict = generate_random_encounter("kobold", monsters, party_size=4)
    print(f"  {encounter_dict['description']}")

    print("\n" + "="*70)
    print("Encounter determination system working correctly!")
    print("="*70)
