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


def main():
    """Main game function"""

    display = Display()
    display.show_title()

    print("Welcome to Aerthos, brave adventurer!")
    print()
    print("This is a faithful recreation of Advanced Dungeons & Dragons 1st Edition")
    print("in text adventure form. Prepare for lethal combat, resource management,")
    print("and classic dungeon crawling!")
    print()

    input("Press Enter to begin your adventure...")
    print()

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
        return

    print()

    # Initialize game state
    game_state = GameState(player, dungeon)
    game_state.load_game_data()

    # Initialize parser
    parser = CommandParser()

    # Display starting room
    print("═" * 70)
    print("YOUR ADVENTURE BEGINS...")
    print("═" * 70)
    print()

    room_desc = game_state.current_room.on_enter(player.has_light(), player)
    display.show_message(room_desc)

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
                from aerthos.ui.save_system import SaveSystem
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


if __name__ == '__main__':
    main()
