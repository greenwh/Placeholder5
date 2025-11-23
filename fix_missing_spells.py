#!/usr/bin/env python3
"""
Fix existing characters that are missing spells
"""

from pathlib import Path
from aerthos.storage.character_roster import CharacterRoster
from aerthos.engine.game_state import GameData
from aerthos.ui.character_creation import CharacterCreator

def fix_character_spells():
    """Add missing spells to characters that should have them"""

    game_data = GameData.load_all()
    roster = CharacterRoster()
    creator = CharacterCreator(game_data)

    print("Loading all characters...")
    characters_data = roster.list_characters()

    if not characters_data:
        print("No characters found in roster.")
        return

    for char_data in characters_data:
        char_id = char_data['id']
        char_name = char_data['name']
        char_class = char_data['char_class']

        # Only fix spellcasting classes
        if char_class not in ['Magic-User', 'Illusionist', 'Cleric', 'Druid', 'Bard']:
            print(f"Skipping {char_name} ({char_class}) - not a spellcaster")
            continue

        # Load full character
        character = roster.load_character(character_id=char_id)

        if not character:
            print(f"Error loading {char_name}")
            continue

        # Check if missing spells
        if len(character.spells_known) == 0:
            print(f"\nFixing {char_name} ({char_class}) - missing spells!")

            # Add spells using the character creator method
            creator._add_starting_spells(character, char_class)

            # Add spell slots if missing
            if len(character.spells_memorized) == 0:
                class_data = game_data.classes[char_class]
                if 'spell_slots_level_1' in class_data:
                    num_slots = class_data['spell_slots_level_1'][0]
                    if num_slots > 0:
                        for _ in range(num_slots):
                            character.add_spell_slot(1)
                        print(f"  Added {num_slots} spell slot(s)")

            print(f"  Added {len(character.spells_known)} spell(s)")

            # Save back to roster
            roster.save_character(character, character_id=char_id)
            print(f"  ✓ {char_name} updated!")
        else:
            print(f"✓ {char_name} ({char_class}) already has {len(character.spells_known)} spells")

if __name__ == "__main__":
    print("=" * 70)
    print("AERTHOS - Fix Missing Spells")
    print("=" * 70)
    print()
    print("This script will add missing starting spells to characters")
    print("in your Character Roster.")
    print()

    fix_character_spells()

    print()
    print("=" * 70)
    print("Done!")
