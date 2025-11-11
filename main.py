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
    print("1. New Game")
    print("2. Load Game")
    print("3. Quit")
    print()

    while True:
        choice = input("Choose an option (1-3): ").strip()
        if choice in ['1', '2', '3']:
            return choice
        print("Invalid choice. Please enter 1, 2, or 3.")


def start_new_game(game_data: GameData) -> tuple:
    """Start a new game with character creation"""

    # Character creation
    creator = CharacterCreator(game_data)
    player = creator.create_character()

    # Show character sheet
    print("\n" + CharacterSheet.format_character(player))
    input("Press Enter to enter the dungeon...")
    print()

    # Load dungeon
    print("Loading the dungeon...")
    try:
        dungeon = Dungeon.load_from_file('aerthos/data/dungeons/starter_dungeon.json')
        print(f"✓ Loaded: {dungeon.name}")
    except Exception as e:
        print(f"✗ Error loading dungeon: {e}")
        return None, None

    print()

    return player, dungeon


def load_saved_game(game_data: GameData) -> tuple:
    """Load a saved game"""

    save_system = SaveSystem()
    saves = save_system.list_saves()

    if not saves:
        print("\nNo saved games found!")
        input("Press Enter to return to main menu...")
        return None, None

    print("\n═" * 70)
    print("SAVED GAMES")
    print("═" * 70)
    print()

    for save in saves:
        print(f"Slot {save['slot']}: {save['character_name']} - Level {save['level']} {save['class']}")
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
            # Quit
            print("\nFarewell, adventurer!")
            break


if __name__ == '__main__':
    main()
