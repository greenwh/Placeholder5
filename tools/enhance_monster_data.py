"""
Monster Data Enhancement Tool

Processes Monster Manual JSON and creates enhanced monster data
with full AD&D statistics for authentic encounter generation.
"""

import json
import re
from pathlib import Path


def parse_appearing_range(appearing_str):
    """Parse NO. APPEARING string to get min/max values"""
    if not appearing_str or appearing_str == "Nil":
        return {"min": 0, "max": 0, "special": None}

    # Handle special cases
    if "varies" in appearing_str.lower():
        return {"min": 1, "max": 1, "special": "varies"}

    # Extract numeric range (e.g., "2-8", "1-6", "10-40")
    match = re.search(r'(\d+)-(\d+)', appearing_str)
    if match:
        return {"min": int(match.group(1)), "max": int(match.group(2)), "special": None}

    # Single number (e.g., "1")
    match = re.search(r'^(\d+)$', appearing_str)
    if match:
        num = int(match.group(1))
        return {"min": num, "max": num, "special": None}

    return {"min": 1, "max": 1, "special": appearing_str}


def parse_hit_dice(hd_str):
    """Parse HIT DICE string into components"""
    if not hd_str:
        return {"dice_count": 1, "dice_type": 8, "modifier": 0, "special": None}

    hd_str = str(hd_str).strip()

    # Handle "Hit points" format like "1-7 Hit points" (for weak monsters like goblins)
    if "hit point" in hd_str.lower():
        match = re.search(r'(\d+)-(\d+)', hd_str)
        if match:
            # Store as special format with HP range
            return {
                "dice_count": 1,
                "dice_type": "hp_range",
                "modifier": 0,
                "special": f"{match.group(1)}-{match.group(2)} hp"
            }

    # Handle "hp" format like "45-75 hp" (for powerful monsters)
    if "hp" in hd_str.lower() and "-" in hd_str:
        match = re.search(r'(\d+)-(\d+)', hd_str)
        if match:
            return {
                "dice_count": 1,
                "dice_type": "hp_range",
                "modifier": 0,
                "special": f"{match.group(1)}-{match.group(2)} hp"
            }

    # Handle range like "3 to 8"
    if " to " in hd_str:
        return {"dice_count": 1, "dice_type": 8, "modifier": 0, "special": hd_str}

    # Standard format: "4+1", "2-1", "6+6", etc.
    match = re.match(r'^(\d+)([+-])(\d+)$', hd_str)
    if match:
        dice_count = int(match.group(1))
        modifier = int(match.group(3)) if match.group(2) == '+' else -int(match.group(3))
        return {"dice_count": dice_count, "dice_type": 8, "modifier": modifier, "special": None}

    # Handle single digits or numbers like "16" (means 16d8)
    if hd_str.isdigit():
        return {"dice_count": int(hd_str), "dice_type": 8, "modifier": 0, "special": None}

    # Fallback
    return {"dice_count": 1, "dice_type": 8, "modifier": 0, "special": hd_str}


def parse_damage(damage_str):
    """Parse DAMAGE/ATTACK string"""
    if not damage_str:
        return []

    # Split multiple attacks (e.g., "1-3/1-3/2-8")
    attacks = damage_str.split('/')

    return [attack.strip() for attack in attacks]


def extract_frequency_percentage(freq_str):
    """Extract percentage from frequency string"""
    if not freq_str:
        return 0

    # "Common (65%)" -> 65
    match = re.search(r'\((\d+)%\)', freq_str)
    if match:
        return int(match.group(1))

    return 0


def parse_level_xp(level_xp_str):
    """Parse LEVEL/X.P. VALUE string"""
    if not level_xp_str:
        return {"dungeon_level": 1, "base_xp": 10, "xp_per_hp": 1}

    # Format: "I / 10 + 1 per hp" or "VIII/ 3550 + 20/hp"
    roman_to_int = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
        'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10
    }

    parts = level_xp_str.split('/')
    if len(parts) >= 2:
        level_str = parts[0].strip()
        xp_str = parts[1].strip()

        # Parse level (Roman numeral or "Variable")
        level = roman_to_int.get(level_str, 1)

        # Parse XP: "10 + 1 per hp" or "3550 + 20/hp"
        match = re.search(r'(\d+)\s*\+\s*(\d+)', xp_str)
        if match:
            base_xp = int(match.group(1))
            xp_per_hp = int(match.group(2))
            return {"dungeon_level": level, "base_xp": base_xp, "xp_per_hp": xp_per_hp}

        # Just base XP
        match = re.search(r'(\d+)', xp_str)
        if match:
            base_xp = int(match.group(1))
            return {"dungeon_level": level, "base_xp": base_xp, "xp_per_hp": 0}

    return {"dungeon_level": 1, "base_xp": 10, "xp_per_hp": 1}


def parse_intelligence(intel_str):
    """Parse intelligence string to category and score range"""
    if not intel_str:
        return {"category": "Animal", "score_range": "0-2"}

    intel_map = {
        "Non": {"category": "Non-intelligent", "score_range": "0"},
        "Animal": {"category": "Animal", "score_range": "0-2"},
        "Semi": {"category": "Semi-intelligent", "score_range": "2-4"},
        "Low": {"category": "Low", "score_range": "5-7"},
        "Average": {"category": "Average", "score_range": "8-10"},
        "High": {"category": "High", "score_range": "11-12"},
        "Very": {"category": "Very intelligent", "score_range": "13-14"},
        "Exceptional": {"category": "Exceptional", "score_range": "15-16"},
        "Genius": {"category": "Genius", "score_range": "17-18"},
        "Supra": {"category": "Supra-genius", "score_range": "19+"}
    }

    for key, value in intel_map.items():
        if key in intel_str:
            return value

    return {"category": "Animal", "score_range": "0-2"}


def enhance_monster_data(source_path, output_path):
    """
    Process Monster Manual JSON and create enhanced version

    Args:
        source_path: Path to monster_manual_monsters_resolved.json
        output_path: Path to save enhanced monsters.json
    """
    print(f"Loading Monster Manual data from {source_path}...")
    with open(source_path, 'r') as f:
        mm_data = json.load(f)

    enhanced_monsters = {}

    for monster_id, monster in mm_data.items():
        print(f"Processing: {monster_id}")

        # Parse numeric data
        appearing = parse_appearing_range(monster.get("NO. APPEARING", "1"))
        hit_dice = parse_hit_dice(monster.get("HIT DICE", "1"))
        damage = parse_damage(monster.get("DAMAGE/ATTACK", "1-6"))
        level_xp = parse_level_xp(monster.get("LEVEL/X.P. VALUE", ""))
        intelligence = parse_intelligence(monster.get("INTELLIGENCE", "Animal"))

        # Parse percentage in lair
        pct_in_lair = 0
        lair_str = monster.get("% IN LAIR", "Nil")
        if lair_str and lair_str != "Nil":
            match = re.search(r'(\d+)%', lair_str)
            if match:
                pct_in_lair = int(match.group(1))

        # Create enhanced entry
        enhanced = {
            # Core identity
            "name": monster.get("DESCRIPTION", monster_id).split('.')[0],  # First sentence
            "id": monster_id.lower().replace(", ", "_").replace(" ", "_"),

            # Encounter data
            "frequency": {
                "description": monster.get("FREQUENCY", "Uncommon"),
                "percentage": extract_frequency_percentage(monster.get("FREQUENCY", ""))
            },
            "no_appearing": {
                "wilderness": appearing,
                "lair": parse_appearing_range(monster.get("NO. APPEARING", "1"))  # Could be different
            },
            "pct_in_lair": pct_in_lair,

            # Combat stats
            "armor_class": monster.get("ARMOR CLASS", "10"),  # Keep as string for special cases
            "move": monster.get("MOVE", "12\""),
            "hit_dice": hit_dice,
            "num_attacks": len(damage) if damage else 1,
            "damage_per_attack": damage if damage else ["1-6"],

            # Abilities
            "special_attacks": monster.get("SPECIAL ATTACKS", "Nil"),
            "special_defenses": monster.get("SPECIAL DEFENSES", "Nil"),
            "magic_resistance": monster.get("MAGIC RESISTANCE", "Standard"),

            # Intelligence & Alignment
            "intelligence": intelligence,
            "alignment": monster.get("ALIGNMENT", "Neutral"),

            # Physical
            "size": monster.get("SIZE", "M"),

            # Psionic
            "psionic_ability": monster.get("PSIONIC ABILITY", "Nil"),

            # Treasure
            "treasure_type": monster.get("TREASURE TYPE", "Nil"),
            "resolved_treasure": monster.get("RESOLVED_TREASURE", None),

            # Experience
            "level_xp": level_xp,

            # Description
            "description": monster.get("DESCRIPTION", "")
        }

        enhanced_monsters[enhanced["id"]] = enhanced

    print(f"\nSaving enhanced data to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(enhanced_monsters, f, indent=2)

    print(f"\nEnhanced {len(enhanced_monsters)} monsters!")
    return enhanced_monsters


def main():
    """Main entry point"""
    base_dir = Path(__file__).parent.parent
    source_file = base_dir / "docs" / "game_enhancement_docs" / "monster_manual_monsters_resolved.json"
    output_file = base_dir / "aerthos" / "data" / "monsters_enhanced.json"

    if not source_file.exists():
        print(f"ERROR: Source file not found: {source_file}")
        return

    enhanced = enhance_monster_data(source_file, output_file)

    # Print sample
    print("\n" + "="*60)
    print("Sample Enhanced Monster (Goblin):")
    print("="*60)
    if "goblin" in enhanced:
        print(json.dumps(enhanced["goblin"], indent=2))


if __name__ == "__main__":
    main()
