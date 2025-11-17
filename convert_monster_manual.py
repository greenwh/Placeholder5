#!/usr/bin/env python3
"""
Convert Monster Manual JSON to Aerthos game format
"""

import json
import re
from typing import Dict, Any, List, Optional


def parse_hit_dice(hd_string: str) -> tuple[str, int]:
    """
    Parse hit dice string and return game format + average HD for THAC0

    Examples:
        "1" -> ("1d8", 1)
        "6+1" -> ("6+1", 6)
        "1-4 Hit points" -> ("1d4", 1)
        "1-7 Hit points" -> ("1d8", 1)  # Less than 1 HD creatures
        "3 to 8" -> ("3d8", 3)
        "45-75hp" -> ("10d8", 10)
    """
    hd_string = str(hd_string).strip()

    # Handle hit point ranges like "1-4 Hit points" or "45-75 hit points"
    if "hit point" in hd_string.lower():
        match = re.search(r'(\d+)[-–](\d+)', hd_string)
        if match:
            low, high = int(match.group(1)), int(match.group(2))
            # For very low HP ranges (less than 1 HD creatures)
            if high <= 8:
                return ("1d8", 1)
            # For high HP ranges (like Beholder's 45-75), estimate HD
            avg_hp = (low + high) // 2
            est_hd = max(1, avg_hp // 5)
            return (f"{est_hd}d8", est_hd)

    # Handle HP ranges like "45-75hp"
    if "hp" in hd_string.lower():
        match = re.search(r'(\d+)[-–](\d+)', hd_string)
        if match:
            low, high = int(match.group(1)), int(match.group(2))
            avg_hp = (low + high) // 2
            # Estimate HD from average HP (avg d8 = 4.5)
            est_hd = max(1, avg_hp // 5)
            return (f"{est_hd}d8", est_hd)

    # Handle "11+" format (minimum HD)
    if hd_string.endswith('+'):
        base = hd_string.rstrip('+')
        if base.isdigit():
            num = int(base)
            return (f"{num}d8", num)

    # Handle "3 to 8" format
    if " to " in hd_string:
        match = re.search(r'(\d+)\s+to\s+(\d+)', hd_string)
        if match:
            low = int(match.group(1))
            return (f"{low}d8", low)

    # Handle "+X" modifier like "6+1"
    if "+" in hd_string and not hd_string.startswith("+"):
        match = re.match(r'(\d+)\+(\d+)', hd_string)
        if match:
            base = int(match.group(1))
            return (f"{base}+{match.group(2)}", base)

    # Handle simple number like "6"
    if hd_string.isdigit():
        num = int(hd_string)
        return (f"{num}d8", num)

    # Handle formats like "1-7" (use lower bound)
    match = re.match(r'(\d+)[-–](\d+)', hd_string)
    if match:
        low = int(match.group(1))
        return (f"{low}d8", low)

    # Default fallback
    return ("1d8", 1)


def calculate_thac0(hit_dice: int) -> int:
    """
    Calculate THAC0 based on Hit Dice (AD&D 1e monster progression)
    """
    # Base THAC0 is 20, decreases by 1 per HD
    # Minimum THAC0 is typically 1
    return max(1, 20 - (hit_dice - 1))


def parse_damage(damage_string: str) -> str:
    """
    Parse damage string to dice notation

    Examples:
        "1-6" -> "1d6"
        "1-8" -> "1d8"
        "1-10" -> "1d10"
        "8-32" -> "8d4" (approximation)
        "1-4 or by weapon" -> "1d4"
        "3-18 (+1-4 acid)" -> "3d6"
        "5-8/5-8/2-12" -> "1d4" (use first attack)
    """
    damage_string = str(damage_string).strip()

    # Handle multiple attacks separated by "/" - use the first one
    if "/" in damage_string:
        damage_string = damage_string.split("/")[0].strip()

    # Extract first damage range BEFORE checking for "by weapon"
    match = re.search(r'(\d+)[-–](\d+)', damage_string)
    if match:
        low, high = int(match.group(1)), int(match.group(2))
        damage_range = high - low + 1

        # Common damage die mappings
        # 1-3 -> 1d3, 1-4 -> 1d4, 1-6 -> 1d6, 1-8 -> 1d8, 1-10 -> 1d10, etc.
        if low == 1:
            # Single die damage
            if high == 3:
                return "1d3"
            elif high == 4:
                return "1d4"
            elif high == 6:
                return "1d6"
            elif high == 8:
                return "1d8"
            elif high == 10:
                return "1d10"
            elif high == 12:
                return "1d12"
            elif high == 20:
                return "1d20"

        # Multi-die damage (e.g., 2-8 = 2d4, 2-12 = 2d6, 3-18 = 3d6)
        if damage_range % 4 == 0 and (high - low + 1) == (low * 4):
            return f"{low}d4"
        elif damage_range % 6 == 0 and (high - low + 1) == (low * 6):
            return f"{low}d6"
        elif damage_range % 8 == 0 and (high - low + 1) == (low * 8):
            return f"{low}d8"

        # Try to find best fit
        # Calculate number of dice needed
        if damage_range <= 4:
            num_dice = max(1, low)
            return f"{num_dice}d4"
        elif damage_range <= 6:
            num_dice = max(1, low // 2 if low > 1 else 1)
            return f"{num_dice}d6"
        elif damage_range <= 8:
            num_dice = max(1, low // 2 if low > 1 else 1)
            return f"{num_dice}d8"
        elif damage_range <= 10:
            num_dice = max(1, low // 2 if low > 1 else 1)
            return f"{num_dice}d10"
        else:
            # For larger ranges, approximate with multiple d6
            num_dice = damage_range // 6
            return f"{num_dice}d6"

    # Handle "by weapon" or similar (only if no damage range found)
    if "by weapon" in damage_string.lower() or "weapon type" in damage_string.lower():
        return "1d6"  # Default weapon damage

    return "1d6"  # Default


def parse_armor_class(ac_string: str) -> int:
    """
    Parse armor class string, handling ranges and special cases

    Examples:
        "3" -> 3
        "Overall 2, underside 4" -> 2 (use best)
        "4 (base 5)" -> 4
    """
    ac_string = str(ac_string).strip()

    # Find all numbers in the string
    numbers = re.findall(r'-?\d+', ac_string)
    if numbers:
        # Convert to integers and return the best (lowest) AC
        return min(int(n) for n in numbers)

    return 10  # Default unarmored


def parse_size(size_string: str) -> str:
    """
    Extract size category from size string

    Examples:
        "L (8' tall)" -> "L"
        "M (6'+ tall)" -> "M"
        "S (3' tall)" -> "S"
    """
    size_string = str(size_string).strip()

    # Extract first letter if it's S, M, or L
    for char in size_string.upper():
        if char in ['S', 'M', 'L']:
            return char

    return "M"  # Default medium


def parse_movement(move_string: str) -> int:
    """
    Parse movement rate

    Examples:
        "12\"" -> 12
        "12\" (6\")" -> 12 (use first/best)
        "24\"" -> 24
    """
    move_string = str(move_string).strip()

    # Extract first number
    match = re.search(r'(\d+)', move_string)
    if match:
        return int(match.group(1))

    return 9  # Default movement


def parse_xp_value(xp_string: str) -> int:
    """
    Parse XP value from level/XP string

    Examples:
        "VIII/ 3550 + 20/hp" -> 3550
        "II/ 28 + 2/hp" -> 28
        "Variable" -> 0 (will be calculated elsewhere)
    """
    xp_string = str(xp_string).strip()

    if "variable" in xp_string.lower():
        return 0

    # Extract base XP value (before any "+")
    match = re.search(r'/\s*(\d+)', xp_string)
    if match:
        return int(match.group(1))

    return 0


def extract_special_abilities(monster_data: Dict[str, Any]) -> List[str]:
    """
    Extract special abilities from various fields
    """
    abilities = []

    # Parse special attacks
    special_attacks = str(monster_data.get('SPECIAL ATTACKS', '')).lower()
    if special_attacks and special_attacks != 'nil':
        if 'poison' in special_attacks:
            abilities.append('poison_attack')
        if 'paralysis' in special_attacks or 'paralyze' in special_attacks:
            abilities.append('paralysis_touch')
        if 'acid' in special_attacks:
            abilities.append('acid_attack')
        if 'breath' in special_attacks:
            abilities.append('breath_weapon')
        if 'petrif' in special_attacks:
            abilities.append('petrifying_gaze')
        if 'energy drain' in special_attacks or 'drain' in special_attacks:
            abilities.append('energy_drain')
        if 'constrict' in special_attacks:
            abilities.append('constriction')

    # Parse special defenses
    special_defenses = str(monster_data.get('SPECIAL DEFENSES', '')).lower()
    if special_defenses and special_defenses != 'nil':
        if 'magic weapon' in special_defenses or 'hit only by magic' in special_defenses:
            abilities.append('magic_to_hit')
        if 'silver' in special_defenses:
            abilities.append('silver_to_hit')
        if 'regenerat' in special_defenses:
            abilities.append('regeneration')
        if 'invisible' in special_defenses or 'invisibility' in special_defenses:
            abilities.append('invisibility')

    # Check alignment for undead
    alignment = str(monster_data.get('ALIGNMENT', '')).lower()
    description = str(monster_data.get('DESCRIPTION', '')).lower()

    if 'undead' in description or 'skeleton' in description or 'zombie' in description:
        abilities.extend(['undead', 'immune_to_sleep', 'immune_to_charm'])

    return list(set(abilities))  # Remove duplicates


def determine_ai_behavior(intelligence: str, alignment: str) -> str:
    """
    Determine AI behavior from intelligence and alignment
    """
    intel = str(intelligence).lower()
    align = str(alignment).lower()

    # Intelligent creatures get smarter AI
    if any(word in intel for word in ['very', 'high', 'exceptional', 'genius', 'supra-genius']):
        return 'intelligent'

    # Non-intelligent or animal intelligence is aggressive
    if 'non' in intel or 'animal' in intel:
        return 'aggressive'

    # Semi-intelligent might be defensive
    if 'semi' in intel:
        return 'defensive'

    # Good alignment might be defensive
    if 'good' in align:
        return 'defensive'

    # Evil alignment is typically aggressive
    if 'evil' in align:
        return 'aggressive'

    return 'aggressive'  # Default


def determine_morale(alignment: str, intelligence: str) -> int:
    """
    Estimate morale from alignment and intelligence
    """
    # Lawful creatures have higher morale
    if 'lawful' in str(alignment).lower():
        base = 9
    elif 'chaotic' in str(alignment).lower():
        base = 7
    else:
        base = 8

    # Intelligent creatures have better morale
    intel = str(intelligence).lower()
    if any(word in intel for word in ['very', 'high', 'exceptional']):
        base += 2
    elif 'semi' in intel or 'low' in intel:
        base += 0
    elif 'non' in intel or 'animal' in intel:
        base -= 1

    return max(1, min(12, base))  # Clamp between 1-12


def convert_monster(name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a Monster Manual entry to game format
    """
    # Parse hit dice
    hit_dice_str, hd_value = parse_hit_dice(data.get('HIT DICE', '1'))

    # Build monster entry
    monster = {
        'name': name.title(),
        'hit_dice': hit_dice_str,
        'ac': parse_armor_class(data.get('ARMOR CLASS', '10')),
        'thac0': calculate_thac0(hd_value),
        'damage': parse_damage(data.get('DAMAGE/ATTACK', '1-6')),
        'size': parse_size(data.get('SIZE', 'M')),
        'movement': parse_movement(data.get('MOVE', '9\"')),
        'morale': determine_morale(
            data.get('ALIGNMENT', 'Neutral'),
            data.get('INTELLIGENCE', 'Average')
        ),
        'treasure_type': data.get('TREASURE TYPE', 'Nil'),
        'xp_value': parse_xp_value(data.get('LEVEL/X.P. VALUE', '0')),
        'special_abilities': extract_special_abilities(data),
        'ai_behavior': determine_ai_behavior(
            data.get('INTELLIGENCE', 'Average'),
            data.get('ALIGNMENT', 'Neutral')
        ),
        'description': data.get('DESCRIPTION', '')
    }

    return monster


def main():
    """Convert Monster Manual to game format"""
    print("Loading Monster Manual data...")
    with open('monster_manual_monsters_resolved.json', 'r') as f:
        mm_data = json.load(f)

    print(f"Found {len(mm_data)} monsters in Monster Manual")

    # Convert all monsters
    game_monsters = {}
    for mm_name, mm_data in mm_data.items():
        # Create a game-friendly key (lowercase, underscores)
        game_key = mm_name.lower().replace(' ', '_').replace(',', '').replace('-', '_')

        # Convert the monster
        game_monsters[game_key] = convert_monster(mm_name, mm_data)

    # Save to new file
    output_file = 'aerthos/data/monsters_full.json'
    print(f"Writing {len(game_monsters)} monsters to {output_file}...")

    with open(output_file, 'w') as f:
        json.dump(game_monsters, f, indent=2)

    print("Conversion complete!")
    print(f"Output saved to: {output_file}")

    # Show some statistics
    print("\nStatistics:")
    print(f"  Total monsters: {len(game_monsters)}")
    print(f"  Monsters with special abilities: {sum(1 for m in game_monsters.values() if m['special_abilities'])}")
    print(f"  Undead creatures: {sum(1 for m in game_monsters.values() if 'undead' in m['special_abilities'])}")
    print(f"  Intelligent monsters: {sum(1 for m in game_monsters.values() if m['ai_behavior'] == 'intelligent')}")

    # Show sample conversions
    print("\nSample conversions:")
    for key in list(game_monsters.keys())[:5]:
        monster = game_monsters[key]
        print(f"\n{monster['name']}:")
        print(f"  HD: {monster['hit_dice']}, AC: {monster['ac']}, THAC0: {monster['thac0']}")
        print(f"  Damage: {monster['damage']}, XP: {monster['xp_value']}")
        if monster['special_abilities']:
            print(f"  Special: {', '.join(monster['special_abilities'])}")


if __name__ == '__main__':
    main()
