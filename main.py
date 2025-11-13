#!/usr/bin/env python3
"""
AERTHOS - Advanced Dungeons & Dragons 1e Text Adventure
Main entry point for the game
"""

import sys
from aerthos.world.dungeon import Dungeon
from aerthos.engine.game_state import GameState, GameData
from aerthos.engine.parser import CommandParser
from aerthos.ui.display import Display
from aerthos.ui.character_creation import CharacterCreator
from aerthos.ui.character_sheet import CharacterSheet
from aerthos.ui.save_system import SaveSystem
from aerthos.entities.player import PlayerCharacter
from aerthos.entities.party import Party
from aerthos.generator.dungeon_generator import DungeonGenerator
from aerthos.generator.config import DungeonConfig, EASY_DUNGEON, STANDARD_DUNGEON, HARD_DUNGEON
from aerthos.storage.character_roster import CharacterRoster
from aerthos.storage.party_manager import PartyManager
from aerthos.storage.scenario_library import ScenarioLibrary
from aerthos.storage.session_manager import SessionManager


def show_main_menu(display: Display) -> str:
    """Show main menu and get user choice"""

    display.show_title()

    print("Welcome to Aerthos, brave adventurer!")
    print()
    print("This is a faithful recreation of Advanced Dungeons & Dragons 1st Edition")
    print("in text adventure form. Prepare for lethal combat, resource management,")
    print("and classic dungeon crawling!")
    print()
    print("═" * 70)
    print()
    print("QUICK PLAY")
    print("  1. New Game (Quick Play - create temp character & dungeon)")
    print("  2. Load Game (Quick Save)")
    print()
    print("PERSISTENT MANAGEMENT")
    print("  3. Character Roster (create, view, delete characters)")
    print("  4. Party Manager (create, view, delete parties)")
    print("  5. Scenario Library (save, view, delete dungeons)")
    print("  6. Session Manager (create, load, delete game sessions)")
    print()
    print("  9. Quit")
    print()

    while True:
        choice = input("Choose an option (1-6, 9): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6', '9']:
            return choice
        print("Invalid choice. Please enter 1-6 or 9.")


def choose_dungeon_type() -> str:
    """Ask player to choose between fixed or generated dungeon"""

    print("\n" + "═" * 70)
    print("DUNGEON SELECTION")
    print("═" * 70)
    print()
    print("1. The Abandoned Mine (Fixed - 10 rooms, recommended for first game)")
    print("2. Generate Random Dungeon (Easy - 8 rooms)")
    print("3. Generate Random Dungeon (Standard - 12 rooms)")
    print("4. Generate Random Dungeon (Hard - 15 rooms)")
    print("5. Custom Generated Dungeon (Advanced)")
    print()

    while True:
        choice = input("Choose dungeon (1-5): ").strip()
        if choice in ['1', '2', '3', '4', '5']:
            return choice
        print("Invalid choice. Please enter 1-5.")


def start_new_game(game_data: GameData) -> tuple:
    """Start a new game with character creation"""

    # Character creation
    creator = CharacterCreator(game_data)
    player = creator.create_character()

    # Show character sheet
    print("\n" + CharacterSheet.format_character(player))
    input("Press Enter to continue...")
    print()

    # Choose dungeon
    dungeon_choice = choose_dungeon_type()

    print("\nLoading the dungeon...")

    try:
        if dungeon_choice == '1':
            # Fixed starter dungeon
            dungeon = Dungeon.load_from_file('aerthos/data/dungeons/starter_dungeon.json')
            print(f"✓ Loaded: {dungeon.name}")

        else:
            # Generate dungeon
            generator = DungeonGenerator(game_data)

            if dungeon_choice == '2':
                config = EASY_DUNGEON
                print("✓ Generating Easy Dungeon...")
            elif dungeon_choice == '3':
                config = STANDARD_DUNGEON
                print("✓ Generating Standard Dungeon...")
            elif dungeon_choice == '4':
                config = HARD_DUNGEON
                print("✓ Generating Hard Dungeon...")
            else:  # '5' - Custom
                config = create_custom_config()
                print("✓ Generating Custom Dungeon...")

            dungeon_data = generator.generate(config)
            dungeon = Dungeon.load_from_generator(dungeon_data)
            print(f"✓ Generated: {dungeon.name}")

            if config.seed:
                print(f"  Seed: {config.seed} (use this seed to replay this exact dungeon)")

    except Exception as e:
        print(f"✗ Error loading/generating dungeon: {e}")
        import traceback
        traceback.print_exc()
        return None, None

    print()

    return player, dungeon


def create_custom_config() -> DungeonConfig:
    """Create a custom dungeon configuration"""

    print("\n" + "═" * 70)
    print("CUSTOM DUNGEON GENERATOR")
    print("═" * 70)
    print()

    # Number of rooms
    while True:
        try:
            num_rooms = int(input("Number of rooms (5-30, default 12): ") or "12")
            if 5 <= num_rooms <= 30:
                break
            print("Please enter a number between 5 and 30.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Layout type
    print("\nLayout style:")
    print("1. Linear (straight path)")
    print("2. Branching (main path with side branches)")
    print("3. Network (complex with loops)")
    layout_choice = input("Choose layout (1-3, default 2): ").strip() or "2"
    layout_map = {'1': 'linear', '2': 'branching', '3': 'network'}
    layout_type = layout_map.get(layout_choice, 'branching')

    # Theme
    print("\nDungeon theme:")
    print("1. Mine")
    print("2. Crypt")
    print("3. Cave")
    print("4. Ruins")
    print("5. Sewer")
    theme_choice = input("Choose theme (1-5, default 1): ").strip() or "1"
    theme_map = {'1': 'mine', '2': 'crypt', '3': 'cave', '4': 'ruins', '5': 'sewer'}
    theme = theme_map.get(theme_choice, 'mine')

    # Seed (optional)
    seed_input = input("\nEnter seed for fixed dungeon (leave blank for random): ").strip()
    seed = int(seed_input) if seed_input else None

    # Difficulty
    print("\nDifficulty:")
    print("1. Easy (lethality 0.8)")
    print("2. Normal (lethality 1.0)")
    print("3. Hard (lethality 1.3)")
    diff_choice = input("Choose difficulty (1-3, default 2): ").strip() or "2"
    diff_map = {'1': 0.8, '2': 1.0, '3': 1.3}
    lethality = diff_map.get(diff_choice, 1.0)

    return DungeonConfig(
        seed=seed,
        num_rooms=num_rooms,
        layout_type=layout_type,
        dungeon_theme=theme,
        party_level=1,
        lethality_factor=lethality,
        combat_frequency=0.6,
        trap_frequency=0.2,
        treasure_frequency=0.4,
        magic_item_chance=0.1
    )


def load_saved_game(game_data: GameData) -> tuple:
    """Load a saved game"""

    save_system = SaveSystem()
    saves = save_system.list_saves()

    if not saves:
        print("\nNo saved games found!")
        input("Press Enter to return to main menu...")
        return None, None

    print("\n" + "═" * 70)
    print("SAVED GAMES")
    print("═" * 70)
    print()

    for save in saves:
        print(f"Slot {save['slot']}: {save['character_name']} - Level {save['level']} {save['class']}")
        if save.get('description'):
            print(f"  Description: {save['description']}")
        print(f"  Saved: {save['timestamp']}")
        print()

    print("0. Cancel")
    print()

    while True:
        choice = input(f"Choose save slot (0-{len(saves)}): ").strip()

        if choice == '0':
            return None, None

        try:
            slot = int(choice)
            if 1 <= slot <= 3:
                save_data = save_system.load_game(slot)
                if save_data:
                    print(f"\nLoading save slot {slot}...")
                    player, dungeon = restore_game_from_save(save_data, game_data)
                    if player and dungeon:
                        print("✓ Game loaded successfully!")
                        print()
                        return player, dungeon
                    else:
                        print("✗ Error restoring game state")
                        input("Press Enter to return to main menu...")
                        return None, None
                else:
                    print(f"Save slot {slot} is empty.")
            else:
                print("Invalid slot number.")
        except ValueError:
            print("Please enter a valid number.")


def restore_game_from_save(save_data: dict, game_data: GameData) -> tuple:
    """Restore player and dungeon from save data"""

    try:
        # Restore player
        player_data = save_data['player']

        # Create player character
        player = PlayerCharacter(
            name=player_data['name'],
            race=player_data['race'],
            char_class=player_data['char_class'],
            level=player_data['level'],
            strength=player_data['strength'],
            dexterity=player_data['dexterity'],
            constitution=player_data['constitution'],
            intelligence=player_data['intelligence'],
            wisdom=player_data['wisdom'],
            charisma=player_data['charisma'],
            strength_percentile=player_data.get('strength_percentile', 0),
            hp_current=player_data['hp_current'],
            hp_max=player_data['hp_max'],
            ac=player_data['ac'],
            thac0=player_data['thac0'],
            xp=player_data['xp'],
            xp_to_next_level=player_data['xp_to_next_level']
        )

        player.gold = player_data['gold']
        player.conditions = player_data.get('conditions', [])

        # Restore thief skills if applicable
        if player_data.get('thief_skills'):
            player.thief_skills = player_data['thief_skills']

        # Restore spells if applicable
        from aerthos.entities.player import Spell, SpellSlot

        if player_data.get('spells_known'):
            for spell_name in player_data['spells_known']:
                # Find spell in game data by name
                for spell_id, spell_data in game_data.spells.items():
                    if spell_data['name'] == spell_name:
                        spell = Spell(
                            name=spell_data['name'],
                            level=spell_data['level'],
                            school=spell_data['school'],
                            casting_time=spell_data['casting_time'],
                            range=spell_data['range'],
                            duration=spell_data['duration'],
                            area_of_effect=spell_data['area'],
                            saving_throw=spell_data['saving_throw'],
                            components=spell_data['components'],
                            description=spell_data['description'],
                            class_availability=spell_data['class_availability']
                        )
                        player.spells_known.append(spell)
                        break

        if player_data.get('spells_memorized'):
            for slot_data in player_data['spells_memorized']:
                slot = SpellSlot(level=slot_data['level'])

                # Restore the memorized spell if there was one
                if slot_data.get('spell'):
                    spell_name = slot_data['spell']
                    # Find the spell in spells_known
                    for spell in player.spells_known:
                        if spell.name == spell_name:
                            slot.spell = spell
                            slot.is_used = slot_data.get('is_used', False)
                            break

                player.spells_memorized.append(slot)

        # Restore inventory
        from aerthos.entities.player import Weapon, Armor, LightSource, Item

        inventory_names = player_data.get('inventory', [])
        for item_name in inventory_names:
            item = create_item_from_data(item_name, game_data)
            if item:
                player.inventory.add_item(item)

        # Restore equipped items
        equipped_weapon_name = player_data.get('equipped_weapon')
        equipped_armor_name = player_data.get('equipped_armor')
        equipped_shield_name = player_data.get('equipped_shield')
        equipped_light_name = player_data.get('equipped_light')

        # Find and equip items from inventory
        if equipped_weapon_name:
            for item in player.inventory.items:
                if isinstance(item, Weapon) and item.name == equipped_weapon_name:
                    player.equip_weapon(item)
                    break

        if equipped_armor_name:
            for item in player.inventory.items:
                if isinstance(item, Armor) and item.name == equipped_armor_name:
                    player.equip_armor(item)
                    break

        if equipped_shield_name:
            for item in player.inventory.items:
                if isinstance(item, Armor) and item.name == equipped_shield_name:
                    player.equipment.shield = item
                    break

        if equipped_light_name:
            for item in player.inventory.items:
                if isinstance(item, LightSource) and item.name == equipped_light_name:
                    player.equip_light(item)
                    break

        # Check if spellcaster needs starting spells and slots (for backwards compatibility)
        if player.char_class in ['Magic-User', 'Cleric']:
            needs_update = False

            # Check if missing spells
            if not player.spells_known:
                needs_update = True
                print(f"\n⚠️  Your {player.char_class} doesn't have any spells!")
                print("Adding starting spells to your character...")
                from aerthos.ui.character_creation import CharacterCreator
                creator = CharacterCreator(game_data)
                creator._add_starting_spells(player, player.char_class)
                print("✓ Starting spells added!")

            # Check if missing spell slots
            if not player.spells_memorized:
                needs_update = True
                print(f"Adding spell slots for level {player.level} {player.char_class}...")
                # Add appropriate number of spell slots for level
                num_slots = 1  # Level 1 spellcasters get 1 slot
                for _ in range(num_slots):
                    player.add_spell_slot(1)
                print(f"✓ Added {num_slots} level 1 spell slot(s)!")

            if needs_update:
                print("Use 'spells' to see your spells, 'memorize <spell>' to prepare them.\n")

        # Load dungeon
        dungeon = Dungeon.load_from_file('aerthos/data/dungeons/starter_dungeon.json')

        # Restore dungeon state
        dungeon_state = save_data['dungeon_state']
        room_states = dungeon_state.get('room_states', {})

        for room_id, state in room_states.items():
            if room_id in dungeon.rooms:
                room = dungeon.rooms[room_id]
                room.is_explored = state.get('is_explored', False)
                room.items = state.get('items', [])
                room.encounters_completed = state.get('encounters_completed', [])

        return player, dungeon

    except Exception as e:
        print(f"Error restoring save: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def create_item_from_data(item_name: str, game_data: GameData):
    """Helper function to create an item from name using game data"""

    from aerthos.entities.player import Weapon, Armor, LightSource, Item

    if not game_data or not item_name:
        return None

    # Find item in database
    item_data = None
    search_lower = item_name.lower().replace('_', ' ')

    # Try exact match on key or name
    for key, data in game_data.items.items():
        key_normalized = key.lower().replace('_', ' ')
        name_normalized = data['name'].lower()

        if (key_normalized == search_lower or
            name_normalized == search_lower or
            data['name'] == item_name):
            item_data = data
            break

    if not item_data:
        return None

    # Create appropriate item type
    if item_data['type'] == 'weapon':
        return Weapon(
            name=item_data['name'],
            weight=item_data['weight'],
            damage_sm=item_data['damage_sm'],
            damage_l=item_data['damage_l'],
            speed_factor=item_data['speed_factor'],
            properties={'cost_gp': item_data.get('cost_gp', 0)},
            description=item_data.get('description', '')
        )
    elif item_data['type'] == 'armor':
        return Armor(
            name=item_data['name'],
            weight=item_data['weight'],
            ac_bonus=item_data['ac_bonus'],
            properties={'cost_gp': item_data.get('cost_gp', 0)},
            description=item_data.get('description', '')
        )
    elif item_data['type'] == 'light_source':
        return LightSource(
            name=item_data['name'],
            weight=item_data['weight'],
            burn_time_turns=item_data['burn_time_turns'],
            light_radius=item_data.get('light_radius', 30)
        )
    else:
        # Generic item (consumables, etc.)
        return Item(
            name=item_data['name'],
            item_type=item_data['type'],
            weight=item_data['weight'],
            properties=item_data.get('properties', {}),
            description=item_data.get('description', '')
        )


def run_game(player: PlayerCharacter, dungeon: Dungeon, game_data: GameData,
             current_room_id: str = None, time_data: dict = None):
    """Run the main game loop"""

    display = Display()

    # Initialize game state
    game_state = GameState(player, dungeon)
    game_state.load_game_data()

    # Restore current room if loading
    if current_room_id:
        game_state.current_room = dungeon.get_room(current_room_id)
        if time_data:
            game_state.time_tracker.turns_elapsed = time_data.get('turns_elapsed', 0)
            game_state.time_tracker.total_hours = time_data.get('total_hours', 0)

    # Initialize parser
    parser = CommandParser()

    # Display starting room
    print("═" * 70)
    if current_room_id:
        print("CONTINUING YOUR ADVENTURE...")
    else:
        print("YOUR ADVENTURE BEGINS...")
    print("═" * 70)
    print()

    room_desc = game_state.current_room.on_enter(player.has_light(), player)
    display.show_message(room_desc)

    # Check for encounters in the room (important for loaded games)
    encounter_msg = game_state._check_encounters('on_enter')
    if encounter_msg:
        display.show_message(encounter_msg)

    print("Type 'help' for a list of commands.")
    print()

    # Main game loop
    while game_state.is_active:
        # Check if player is dead
        if not player.is_alive:
            display.show_death_screen(player.name)
            break

        # Get player input
        try:
            user_input = display.prompt_input("> ")

            if not user_input:
                continue

            # Parse command
            command = parser.parse(user_input)

            if command.action == 'invalid':
                print("I don't understand that command. Type 'help' for options.")
                print()
                continue

            # Execute command
            result = game_state.execute_command(command)

            # Display result
            if result.get('message'):
                display.show_message(result['message'])

        except KeyboardInterrupt:
            print("\n\nGame interrupted.")
            save_choice = input("Save before quitting? (y/n): ").lower()

            if save_choice == 'y':
                save_system = SaveSystem()
                save_system.save_game(game_state)
                print("Game saved!")

            print("\nThanks for playing Aerthos!")
            break

        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please report this bug. Type 'help' to continue.")
            import traceback
            traceback.print_exc()
            print()

    # End game
    if player.is_alive and not game_state.is_active:
        print("\nThanks for playing Aerthos!")
        print("May your dice always roll high!")


def manage_character_roster(game_data: GameData):
    """Character Roster management menu"""
    roster = CharacterRoster()

    while True:
        print("\n" + "═" * 70)
        print("CHARACTER ROSTER")
        print("═" * 70)
        print()
        print("1. Create New Character")
        print("2. List All Characters")
        print("3. View Character Details")
        print("4. Delete Character")
        print("5. Back to Main Menu")
        print()

        choice = input("Choose an option (1-5): ").strip()

        if choice == '1':
            # Create new character
            creator = CharacterCreator(game_data)
            character = creator.create_character()

            print("\n" + CharacterSheet.format_character(character))

            save = input("\nSave this character to roster? (y/n): ").strip().lower()
            if save == 'y':
                char_id = roster.save_character(character)
                print(f"✓ Character saved! ID: {char_id}")
            else:
                print("Character discarded.")

        elif choice == '2':
            # List all characters
            characters = roster.list_characters()
            if not characters:
                print("\nNo characters in roster.")
            else:
                print("\n" + "═" * 70)
                print(f"{'Name':<20} {'Race':<10} {'Class':<12} {'Level':<6} {'HP':<10} {'ID':<10}")
                print("─" * 70)
                for char in characters:
                    hp_display = f"{char['hp_current']}/{char['hp_max']}"
                    print(f"{char['name']:<20} {char['race']:<10} {char['char_class']:<12} "
                          f"{char['level']:<6} {hp_display:<10} {char['id']:<10}")
                print("═" * 70)

        elif choice == '3':
            # View character details
            name = input("\nEnter character name or ID: ").strip()
            character = roster.load_character(character_name=name)
            if not character:
                character = roster.load_character(character_id=name)

            if character:
                print("\n" + CharacterSheet.format_character(character))
                input("\nPress Enter to continue...")
            else:
                print(f"Character '{name}' not found.")

        elif choice == '4':
            # Delete character
            name_or_id = input("\nEnter character name or ID to delete: ").strip()

            # Find character in list to get the ID
            characters = roster.list_characters()
            char_found = None
            for char in characters:
                if char['name'].lower() == name_or_id.lower() or char['id'] == name_or_id:
                    char_found = char
                    break

            if char_found:
                char_name = char_found['name']
                char_id = char_found['id']
                confirm = input(f"Delete character '{char_name}' ({char_id})? (y/n): ").strip().lower()
                if confirm == 'y':
                    if roster.delete_character(char_id):
                        print("✓ Character deleted.")
                    else:
                        print("Character not found.")
            else:
                print(f"Character '{name_or_id}' not found.")

        elif choice == '5':
            break

        input("\nPress Enter to continue...")


def manage_parties(game_data: GameData):
    """Party Manager menu"""
    party_mgr = PartyManager()
    roster = CharacterRoster()

    while True:
        print("\n" + "═" * 70)
        print("PARTY MANAGER")
        print("═" * 70)
        print()
        print("1. Create New Party")
        print("2. List All Parties")
        print("3. View Party Details")
        print("4. Delete Party")
        print("5. Back to Main Menu")
        print()

        choice = input("Choose an option (1-5): ").strip()

        if choice == '1':
            # Create new party
            characters = roster.list_characters()
            if not characters:
                print("\nNo characters in roster! Create characters first.")
                continue

            party_name = input("\nEnter party name: ").strip()
            if not party_name:
                print("Party name required.")
                continue

            print("\nAvailable Characters:")
            for i, char in enumerate(characters, 1):
                print(f"{i}. {char['name']} ({char['race']} {char['char_class']} Level {char['level']})")

            char_ids = []
            formation = []

            print("\nSelect 1-6 characters (enter number, 'done' when finished):")
            while len(char_ids) < 6:
                choice_str = input(f"Character {len(char_ids)+1} (or 'done'): ").strip()
                if choice_str.lower() == 'done':
                    if len(char_ids) == 0:
                        print("Need at least 1 character!")
                        continue
                    break

                try:
                    idx = int(choice_str) - 1
                    if 0 <= idx < len(characters):
                        char_ids.append(characters[idx]['id'])

                        pos = input("  Formation (front/back): ").strip().lower()
                        formation.append(pos if pos in ['front', 'back'] else 'front')
                    else:
                        print("Invalid number.")
                except ValueError:
                    print("Invalid input.")

            if char_ids:
                party_id = party_mgr.save_party(party_name, char_ids, formation)
                print(f"\n✓ Party '{party_name}' created! ID: {party_id}")

        elif choice == '2':
            # List all parties
            parties = party_mgr.list_parties()
            if not parties:
                print("\nNo saved parties.")
            else:
                print("\n" + "═" * 70)
                print(f"{'Name':<25} {'Size':<6} {'Members':<30} {'ID':<10}")
                print("─" * 70)
                for party in parties:
                    # Extract member names from dict
                    member_names = [m['name'] for m in party['members'][:3]]
                    members_str = ', '.join(member_names)
                    if len(party['members']) > 3:
                        members_str += '...'
                    print(f"{party['name']:<25} {party['size']:<6} {members_str:<30} {party['id']:<10}")
                print("═" * 70)

        elif choice == '3':
            # View party details
            name = input("\nEnter party name or ID: ").strip()
            party_data = party_mgr.load_party(party_name=name)
            if not party_data:
                party_data = party_mgr.load_party(party_id=name)

            if party_data:
                print(f"\n{'═' * 70}")
                print(f"Party: {party_data['name']}")
                print(f"ID: {party_data['id']}")
                print(f"Created: {party_data['created']}")
                print(f"{'─' * 70}")
                for i, member in enumerate(party_data['party'].members):
                    formation = party_data['party'].formation[i] if i < len(party_data['party'].formation) else '?'
                    print(f"{i+1}. {member.name} ({member.race} {member.char_class} Lvl {member.level}) [{formation.upper()}]")
                    print(f"   HP: {member.hp_current}/{member.hp_max} | AC: {member.get_effective_ac()} | Gold: {member.gold}")
                print(f"{'═' * 70}")
            else:
                print(f"Party '{name}' not found.")

        elif choice == '4':
            # Delete party
            name_or_id = input("\nEnter party name or ID to delete: ").strip()

            # Try to find party by name or ID to get the actual ID
            party_data = party_mgr.load_party(party_name=name_or_id)
            if not party_data:
                party_data = party_mgr.load_party(party_id=name_or_id)

            if party_data:
                party_name = party_data['name']
                party_id = party_data['id']
                confirm = input(f"Delete party '{party_name}' ({party_id})? (y/n): ").strip().lower()
                if confirm == 'y':
                    if party_mgr.delete_party(party_id):
                        print("✓ Party deleted.")
                    else:
                        print("Party not found.")
            else:
                print(f"Party '{name_or_id}' not found.")

        elif choice == '5':
            break

        input("\nPress Enter to continue...")


def manage_scenarios(game_data: GameData):
    """Scenario Library menu"""
    library = ScenarioLibrary()

    while True:
        print("\n" + "═" * 70)
        print("SCENARIO LIBRARY")
        print("═" * 70)
        print()
        print("1. Generate & Save New Scenario")
        print("2. List All Scenarios")
        print("3. View Scenario Details")
        print("4. Delete Scenario")
        print("5. Back to Main Menu")
        print()

        choice = input("Choose an option (1-5): ").strip()

        if choice == '1':
            # Generate and save new scenario
            dungeon_choice = choose_dungeon_type()

            generator = DungeonGenerator(game_data)

            if dungeon_choice == '1':
                print("\nCannot save fixed starter dungeon. Use options 2-5 for procedural dungeons.")
                continue
            elif dungeon_choice == '2':
                config = EASY_DUNGEON
            elif dungeon_choice == '3':
                config = STANDARD_DUNGEON
            elif dungeon_choice == '4':
                config = HARD_DUNGEON
            else:  # '5'
                config = create_custom_config()

            print("\nGenerating dungeon...")
            dungeon_data = generator.generate(config)
            dungeon = Dungeon.load_from_generator(dungeon_data)

            print(f"✓ Generated: {dungeon.name}")
            print(f"  Rooms: {len(dungeon.rooms)}")
            if config.seed:
                print(f"  Seed: {config.seed}")

            scenario_name = input("\nEnter scenario name (or press Enter to use default): ").strip()
            if not scenario_name:
                scenario_name = dungeon.name

            description = input("Enter description (optional): ").strip()

            difficulty_map = {2: 'easy', 3: 'medium', 4: 'hard', 5: 'custom'}
            difficulty = difficulty_map.get(int(dungeon_choice), 'medium')

            scenario_id = library.save_scenario(dungeon, scenario_name, description, difficulty)
            print(f"\n✓ Scenario saved! ID: {scenario_id}")

        elif choice == '2':
            # List all scenarios
            scenarios = library.list_scenarios()
            if not scenarios:
                print("\nNo saved scenarios.")
            else:
                print("\n" + "═" * 70)
                print(f"{'Name':<25} {'Rooms':<7} {'Difficulty':<12} {'ID':<10}")
                print("─" * 70)
                for scenario in scenarios:
                    print(f"{scenario['name']:<25} {scenario['num_rooms']:<7} "
                          f"{scenario['difficulty']:<12} {scenario['id']:<10}")
                print("═" * 70)

        elif choice == '3':
            # View scenario details
            name = input("\nEnter scenario name or ID: ").strip()
            scenario_data = library.load_scenario(scenario_name=name)
            if not scenario_data:
                scenario_data = library.load_scenario(scenario_id=name)

            if scenario_data:
                print(f"\n{'═' * 70}")
                print(f"Scenario: {scenario_data['name']}")
                print(f"ID: {scenario_data['id']}")
                print(f"Difficulty: {scenario_data['difficulty']}")
                print(f"Rooms: {scenario_data['num_rooms']}")
                print(f"Description: {scenario_data.get('description', 'None')}")
                print(f"Created: {scenario_data['created']}")
                print(f"{'═' * 70}")
            else:
                print(f"Scenario '{name}' not found.")

        elif choice == '4':
            # Delete scenario
            name_or_id = input("\nEnter scenario name or ID to delete: ").strip()

            # Try to find scenario by name or ID to get the actual ID
            scenario = library.load_scenario(name_or_id)
            if scenario:
                scenario_name = scenario.get('name', 'Unknown')
                scenario_id = scenario.get('id', name_or_id)
                confirm = input(f"Delete scenario '{scenario_name}' ({scenario_id})? (y/n): ").strip().lower()
                if confirm == 'y':
                    if library.delete_scenario(scenario_id):
                        print("✓ Scenario deleted.")
                    else:
                        print("Scenario not found.")
            else:
                print(f"Scenario '{name_or_id}' not found.")

        elif choice == '5':
            break

        input("\nPress Enter to continue...")


def manage_sessions(game_data: GameData):
    """Session Manager menu"""
    session_mgr = SessionManager()

    while True:
        print("\n" + "═" * 70)
        print("SESSION MANAGER")
        print("═" * 70)
        print()
        print("1. Create New Session (Solo Character or Party + Scenario)")
        print("2. List All Sessions")
        print("3. View Session Details")
        print("4. Load & Play Session")
        print("5. Delete Session")
        print("6. Back to Main Menu")
        print()

        choice = input("Choose an option (1-6): ").strip()

        if choice == '1':
            # Create new session
            print("\nSession Type:")
            print("1. Solo Character")
            print("2. Party")

            session_type = input("\nChoose session type (1-2): ").strip()

            party_id = None

            if session_type == '1':
                # Solo character session
                roster = session_mgr.party_manager.character_roster
                characters = roster.list_characters()

                if not characters:
                    print("\nNo characters available! Create a character first.")
                    continue

                print("\nAvailable Characters:")
                for i, char in enumerate(characters, 1):
                    print(f"{i}. {char['name']} ({char['race']} {char['char_class']} Lvl {char['level']}) [ID: {char['id']}]")

                char_choice = input(f"\nSelect character (1-{len(characters)}): ").strip()

                if not char_choice.isdigit():
                    print(f"Invalid input '{char_choice}'. Please enter a number.")
                    continue

                char_idx = int(char_choice) - 1
                if char_idx < 0 or char_idx >= len(characters):
                    print(f"Invalid selection. Please choose between 1 and {len(characters)}.")
                    continue

                try:
                    char_id = characters[char_idx]['id']

                    # Create a temporary solo party using the session manager's party manager
                    solo_party_name = f"Solo: {characters[char_idx]['name']}"
                    party_id = session_mgr.party_manager.save_party([char_id], ['front'], solo_party_name)
                    print(f"\n✓ Created solo party: {solo_party_name}")

                except Exception as e:
                    print(f"Error creating solo party: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

            elif session_type == '2':
                # Party session
                parties = session_mgr.party_manager.list_parties()

                if not parties:
                    print("\nNo saved parties! Create a party first.")
                    continue

                print("\nAvailable Parties:")
                for i, party in enumerate(parties, 1):
                    # Extract member names from dict
                    member_names = [m['name'] for m in party['members'][:3]]
                    members_str = ', '.join(member_names)
                    print(f"{i}. {party['name']} ({members_str}) [ID: {party['id']}]")

                party_choice = input(f"\nSelect party (1-{len(parties)}): ").strip()
                try:
                    party_idx = int(party_choice) - 1
                    party_id = parties[party_idx]['id']
                except (ValueError, IndexError):
                    print("Invalid selection.")
                    continue
            else:
                print("Invalid session type.")
                continue

            # Now select scenario
            scenarios = session_mgr.scenario_library.list_scenarios()
            if not scenarios:
                print("\nNo saved scenarios! Create a scenario first.")
                continue

            print("\nAvailable Scenarios:")
            for i, scenario in enumerate(scenarios, 1):
                print(f"{i}. {scenario['name']} ({scenario['difficulty']}, {scenario['num_rooms']} rooms) [ID: {scenario['id']}]")

            scenario_choice = input(f"\nSelect scenario (1-{len(scenarios)}): ").strip()
            try:
                scenario_idx = int(scenario_choice) - 1
                scenario_id = scenarios[scenario_idx]['id']
            except (ValueError, IndexError):
                print("Invalid selection.")
                continue

            session_name = input("\nEnter session name (or press Enter for default): ").strip()

            try:
                session_id = session_mgr.create_session(party_id, scenario_id, session_name or None)
                print(f"\n✓ Session created! ID: {session_id}")
                print("Use 'Load & Play Session' to start playing.")
            except Exception as e:
                print(f"Error creating session: {e}")

        elif choice == '2':
            # List all sessions
            sessions = session_mgr.list_sessions()
            if not sessions:
                print("\nNo saved sessions.")
            else:
                print("\n" + "═" * 70)
                print(f"{'Name':<30} {'Party':<20} {'Scenario':<15} {'ID':<10}")
                print("─" * 70)
                for session in sessions:
                    print(f"{session['name']:<30} {session['party_name']:<20} "
                          f"{session['scenario_name']:<15} {session['id']:<10}")
                print("═" * 70)

        elif choice == '3':
            # View session details
            name_or_id = input("\nEnter session name or ID: ").strip()

            # Find session by name or ID
            sessions = session_mgr.list_sessions()
            session_found = None
            for sess in sessions:
                if sess['name'].lower() == name_or_id.lower() or sess['id'] == name_or_id:
                    session_found = sess
                    break

            if session_found:
                session_id = session_found['id']
                session_data = session_mgr.load_session(session_id)

                print(f"\n{'═' * 70}")
                print(f"Session: {session_data['name']}")
                print(f"ID: {session_data['id']}")
                print(f"Party ID: {session_data['party_id']}")
                print(f"Scenario ID: {session_data['scenario_id']}")
                print(f"Created: {session_data['created']}")
                print(f"Last Played: {session_data['last_played']}")
                print(f"Progress: {session_data.get('turns_elapsed', 0)} turns, {session_data.get('total_hours', 0)} hours")
                print(f"{'═' * 70}")
            else:
                print(f"Session '{name_or_id}' not found.")

        elif choice == '4':
            # Load and play session
            name_or_id = input("\nEnter session name or ID to load: ").strip()

            # Find session by name or ID
            sessions = session_mgr.list_sessions()
            session_found = None
            for sess in sessions:
                if sess['name'].lower() == name_or_id.lower() or sess['id'] == name_or_id:
                    session_found = sess
                    break

            if not session_found:
                print(f"Session '{name_or_id}' not found.")
                continue

            session_id = session_found['id']
            session_data = session_mgr.load_session(session_id)

            if not session_data:
                print(f"Session '{name_or_id}' not found.")
                continue

            # Load party
            party_data = session_mgr.party_manager.load_party(party_id=session_data['party_id'])
            if not party_data:
                print("Error: Party not found!")
                continue

            # Load scenario
            scenario_data = session_mgr.scenario_library.load_scenario(scenario_id=session_data['scenario_id'])
            if not scenario_data:
                print("Error: Scenario not found!")
                continue

            # Create dungeon from scenario
            dungeon = session_mgr.scenario_library.create_dungeon_from_scenario(scenario_data)

            print(f"\n✓ Loaded session: {session_data['name']}")
            print(f"  Party: {party_data['name']}")
            print(f"  Scenario: {scenario_data['name']}")

            # Run game with party
            run_game_with_party(party_data['party'], dungeon, game_data,
                              session_data.get('current_room_id'),
                              {
                                  'turns_elapsed': session_data.get('turns_elapsed', 0),
                                  'total_hours': session_data.get('total_hours', 0)
                              },
                              session_id)  # Pass session_id
            return  # Exit to main menu after game

        elif choice == '5':
            # Delete session
            name_or_id = input("\nEnter session name or ID to delete: ").strip()

            # Try to find session by ID (sessions are stored by ID)
            session_data = session_mgr.load_session(name_or_id)
            if session_data:
                session_name = session_data.get('name', 'Unknown')
                session_id = name_or_id
                confirm = input(f"Delete session '{session_name}' ({session_id})? (y/n): ").strip().lower()
                if confirm == 'y':
                    if session_mgr.delete_session(session_id):
                        print("✓ Session deleted.")
                    else:
                        print("Session not found.")
            else:
                print(f"Session '{name_or_id}' not found.")

        elif choice == '6':
            break

        input("\nPress Enter to continue...")


def run_game_with_party(party: Party, dungeon: Dungeon, game_data: GameData,
                        starting_room_id: str = None, time_data: dict = None,
                        session_id: str = None):
    """Run game with a party instead of single character"""
    # Set active player to first party member
    player = party.members[0] if party.members else None
    if not player:
        print("Error: Party has no members!")
        return

    # Create game state with party
    game_state = GameState(player, dungeon)
    game_state.party = party  # Add party to game state
    game_state.game_data = game_data  # Add game data to game state

    # Restore time tracking if provided
    if time_data:
        game_state.time_tracker.turns_elapsed = time_data.get('turns_elapsed', 0)
        game_state.time_tracker.total_hours = time_data.get('total_hours', 0)

    # Set starting room if provided
    if starting_room_id and starting_room_id in dungeon.rooms:
        game_state.current_room = dungeon.rooms[starting_room_id]

    # Run the game (use existing run_game logic)
    parser = CommandParser()
    display = Display()

    print("\n" + "═" * 70)
    print("ADVENTURE BEGINS!")
    print("═" * 70)
    print()

    # Show party roster
    print("YOUR PARTY:")
    for i, member in enumerate(party.members):
        formation = party.formation[i] if i < len(party.formation) else 'front'
        print(f"  {i+1}. {member.name} ({member.race} {member.char_class}) [{formation.upper()}]")
    print()

    # Enter starting room
    room_desc = game_state.current_room.on_enter(player.has_light(), player)
    display.show_message(room_desc)

    # Check for encounters in the room
    encounter_msg = game_state._check_encounters('on_enter')
    if encounter_msg:
        display.show_message(encounter_msg)

    print("Type 'help' for a list of commands.")
    print()

    # Standard game loop (similar to run_game function)
    session_mgr = SessionManager() if session_id else None

    while game_state.is_active and player.is_alive:
        try:
            # Show active character
            print(f"\n[Active: {player.name}]")

            user_input = display.prompt_input("> ")

            if not user_input:
                continue

            # Parse command
            command = parser.parse(user_input)

            if command.action == 'invalid':
                print("I don't understand that command. Type 'help' for options.")
                print()
                continue

            # Execute command
            result = game_state.execute_command(command)

            if result and result.get('message'):
                display.show_message(result['message'])

            # Check for death
            if not player.is_alive:
                display.show_death_screen(player.name)
                break

            # Save session state periodically
            if session_id and session_mgr and game_state.time_tracker.turns_elapsed % 10 == 0:
                session_mgr.save_session_state(session_id, game_state)

        except KeyboardInterrupt:
            print("\n\nGame interrupted!")

            if session_id and session_mgr:
                save = input("Save session before quitting? (y/n): ").strip().lower()
                if save == 'y':
                    session_mgr.save_session_state(session_id, game_state)
                    print("Session saved!")

            print("\nThanks for playing Aerthos!")
            break

        except Exception as e:
            print(f"\nAn error occurred: {e}")
            import traceback
            traceback.print_exc()

    if player.is_alive and not game_state.is_active:
        print("\nThanks for playing Aerthos!")
        print("May your dice always roll high!")


def main():
    """Main game function"""

    display = Display()

    # Load game data
    print("Loading game data...")
    try:
        game_data = GameData.load_all()
        print("✓ Game data loaded successfully")
    except Exception as e:
        print(f"✗ Error loading game data: {e}")
        print("\nMake sure you're running from the project root directory.")
        return

    print()

    while True:
        choice = show_main_menu(display)

        if choice == '1':
            # New Game
            player, dungeon = start_new_game(game_data)
            if player and dungeon:
                run_game(player, dungeon, game_data)
            break

        elif choice == '2':
            # Load Game
            result = load_saved_game(game_data)
            if result[0] and result[1]:  # player and dungeon
                player, dungeon = result
                save_system = SaveSystem()

                # Find which slot was loaded to get time data
                saves = save_system.list_saves()
                if saves:
                    # Get the save data for time tracking
                    for save in saves:
                        if save['character_name'] == player.name:
                            slot = save['slot']
                            save_data = save_system.load_game(slot)
                            time_data = {
                                'turns_elapsed': save_data.get('turns_elapsed', 0),
                                'total_hours': save_data.get('total_hours', 0)
                            }
                            run_game(player, dungeon, game_data,
                                   save_data['current_room_id'], time_data)
                            break
            # If load was cancelled or failed, loop back to menu

        elif choice == '3':
            # Character Roster
            manage_character_roster(game_data)

        elif choice == '4':
            # Party Manager
            manage_parties(game_data)

        elif choice == '5':
            # Scenario Library
            manage_scenarios(game_data)

        elif choice == '6':
            # Session Manager
            manage_sessions(game_data)

        elif choice == '9':
            # Quit
            print("\nFarewell, adventurer!")
            break


if __name__ == '__main__':
    main()
