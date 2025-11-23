"""
Merge monsters.json and monsters_enhanced.json

This script combines the best data from both files:
- From monsters.json: thac0, ai_behavior, xp_value, morale (gameplay critical)
- From monsters_enhanced.json: alignment, intelligence, magic_resistance, etc. (AD&D detail)

Output: monsters_merged.json for review before replacing monsters.json
"""

import json
from pathlib import Path
from typing import Dict, Any


# Default alignments for creatures missing from monsters_enhanced.json
DEFAULT_ALIGNMENTS = {
    'giant_rat': 'Neutral',
    'hellhound': 'Lawful Evil',
    'hill_giant': 'Chaotic Evil',
    'frost_giant': 'Chaotic Evil',
    'fire_giant': 'Lawful Evil',
    'red_dragon_young': 'Chaotic Evil',
    'black_dragon_adult': 'Chaotic Evil',
    'green_dragon_adult': 'Lawful Evil',
    'ki_rin': 'Lawful Good',  # Underscore version
    'neo_otyugh': 'Neutral',
    'portuguese_man_o_war_giant': 'Neutral',
    'pseudo_dragon': 'Neutral Good',
    'su_monster': 'Chaotic Evil',
    'will_o_wisp': 'Chaotic Evil'
}

# Mapping for name variations (underscore vs hyphen)
NAME_MAPPINGS = {
    'ki_rin': 'ki-rin',
    'neo_otyugh': 'neo-otyugh',
    'portuguese_man_o_war_giant': 'portuguese_man-o-war_giant',
    'pseudo_dragon': 'pseudo-dragon',
    'su_monster': 'su-monster',
    'will_o_wisp': 'will-o-wisp'
}


def merge_monster_data(basic_data: Dict, enhanced_data: Dict, monster_id: str) -> Dict:
    """
    Merge data for a single monster

    Args:
        basic_data: Data from monsters.json
        enhanced_data: Data from monsters_enhanced.json (may be None)
        monster_id: Monster identifier

    Returns:
        Merged monster data dictionary
    """
    merged = basic_data.copy()

    if enhanced_data:
        # Add valuable fields from enhanced data
        if 'alignment' in enhanced_data:
            merged['alignment'] = enhanced_data['alignment']

        if 'intelligence' in enhanced_data:
            merged['intelligence'] = enhanced_data['intelligence']

        if 'magic_resistance' in enhanced_data:
            merged['magic_resistance'] = enhanced_data['magic_resistance']

        if 'psionic_ability' in enhanced_data:
            merged['psionic_ability'] = enhanced_data['psionic_ability']

        if 'frequency' in enhanced_data:
            merged['frequency'] = enhanced_data['frequency']

        if 'no_appearing' in enhanced_data:
            merged['no_appearing'] = enhanced_data['no_appearing']

        if 'pct_in_lair' in enhanced_data:
            merged['pct_in_lair'] = enhanced_data['pct_in_lair']

        if 'num_attacks' in enhanced_data:
            merged['num_attacks'] = enhanced_data['num_attacks']

        # For special abilities, use enhanced version if more detailed
        if 'special_attacks' in enhanced_data:
            enhanced_attacks = enhanced_data['special_attacks']
            if enhanced_attacks and enhanced_attacks != 'Nil':
                merged['special_attacks'] = enhanced_attacks

        if 'special_defenses' in enhanced_data:
            enhanced_defenses = enhanced_data['special_defenses']
            if enhanced_defenses and enhanced_defenses != 'Nil':
                merged['special_defenses'] = enhanced_defenses

        # Add XP formula data for dynamic calculation
        if 'level_xp' in enhanced_data:
            merged['xp_formula'] = enhanced_data['level_xp']

    else:
        # Monster not in enhanced data - use defaults
        print(f"  ⚠ {monster_id} not in enhanced data, using defaults")

        if monster_id in DEFAULT_ALIGNMENTS:
            merged['alignment'] = DEFAULT_ALIGNMENTS[monster_id]
        else:
            merged['alignment'] = 'Neutral'  # Safest default

        # Add placeholder enhanced fields
        merged['intelligence'] = {'category': 'Average', 'score_range': '8-10'}
        merged['magic_resistance'] = 'Standard'
        merged['psionic_ability'] = 'Nil'
        merged['frequency'] = {'description': 'Uncommon (20%)', 'percentage': 20}
        merged['no_appearing'] = {'wilderness': {'min': 1, 'max': 10, 'special': None},
                                   'lair': {'min': 1, 'max': 10, 'special': None}}
        merged['pct_in_lair'] = 25
        merged['num_attacks'] = 1

        # Add default XP formula based on existing xp_value
        # We'll calculate base_xp and xp_per_hp from static XP as fallback
        merged['xp_formula'] = {
            'base_xp': basic_data.get('xp_value', 10),
            'xp_per_hp': 1,  # Default
            'dungeon_level': 1  # Default
        }

    return merged


def main():
    """Main merge process"""
    print("="*70)
    print("MONSTER DATA MERGE SCRIPT")
    print("="*70)

    # Load both files
    data_dir = Path(__file__).parent.parent / "aerthos" / "data"

    print("\nLoading monsters.json...")
    with open(data_dir / "monsters.json") as f:
        monsters_basic = json.load(f)
    print(f"  ✓ Loaded {len(monsters_basic)} monsters")

    print("\nLoading monsters_enhanced.json...")
    with open(data_dir / "monsters_enhanced.json") as f:
        monsters_enhanced = json.load(f)
    print(f"  ✓ Loaded {len(monsters_enhanced)} monsters")

    # Merge process
    print("\nMerging monster data...")
    merged_monsters = {}

    for monster_id, basic_data in monsters_basic.items():
        # Try to find matching enhanced data
        enhanced_data = None

        # Direct match
        if monster_id in monsters_enhanced:
            enhanced_data = monsters_enhanced[monster_id]
        # Try mapped name (underscore vs hyphen)
        elif monster_id in NAME_MAPPINGS:
            mapped_id = NAME_MAPPINGS[monster_id]
            if mapped_id in monsters_enhanced:
                enhanced_data = monsters_enhanced[mapped_id]

        # Merge the data
        merged_monsters[monster_id] = merge_monster_data(basic_data, enhanced_data, monster_id)

    print(f"  ✓ Merged {len(merged_monsters)} monsters")

    # Save to new file for review
    output_file = data_dir / "monsters_merged.json"
    print(f"\nSaving to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(merged_monsters, f, indent=2)
    print(f"  ✓ Saved successfully")

    # Summary
    print("\n" + "="*70)
    print("MERGE SUMMARY")
    print("="*70)

    # Check alignment coverage
    with_alignment = sum(1 for m in merged_monsters.values() if 'alignment' in m)
    print(f"Monsters with alignment: {with_alignment}/{len(merged_monsters)}")

    # Check intelligence coverage
    with_intelligence = sum(1 for m in merged_monsters.values() if 'intelligence' in m)
    print(f"Monsters with intelligence: {with_intelligence}/{len(merged_monsters)}")

    # Check what fields are now present
    all_fields = set()
    for monster_data in merged_monsters.values():
        all_fields.update(monster_data.keys())

    print(f"\nTotal unique fields in merged data: {len(all_fields)}")
    print(f"Fields: {sorted(all_fields)}")

    print("\n" + "="*70)
    print("✓ MERGE COMPLETE")
    print("="*70)
    print(f"\nReview the output file: {output_file}")
    print("If it looks good, backup monsters.json and replace it with monsters_merged.json")
    print("\nNext steps:")
    print("  1. Review monsters_merged.json")
    print("  2. Backup: cp monsters.json monsters_backup.json")
    print("  3. Replace: mv monsters_merged.json monsters.json")


if __name__ == "__main__":
    main()
